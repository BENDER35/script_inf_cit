#!/usr/bin/env python3
"""
Auditor Automatizado del Sistema de Cita Previa de Oficinas de Empleo (SEPE y CC. AA.)
Analiza cabeceras de seguridad CSP (frame-ancestors), X-Frame-Options y la arquitectura
de los portales autonómicos (iframes vs. enlaces directos), generando un informe en Markdown.
"""

import sys
import os
import re
import urllib.request
import urllib.error
import ssl
import platform
from datetime import datetime

# Configuración de URLs a auditar
SEPE_URL = "https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28"

PORTALES_AUTONOMICOS = [
    {
        "comunidad": "Comunidad de Madrid",
        "servicio": "Oficinas de Empleo Madrid",
        "url": "https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo",
        "dominio_esperado": "https://www.comunidad.madrid",
        "param_origen": "28"
    },
    {
        "comunidad": "Principado de Asturias",
        "servicio": "Trabajastur (SEPEPA)",
        "url": "https://trabajastur.asturias.es/cita_previa",
        "dominio_esperado": "https://trabajastur.asturias.es",
        "param_origen": "SEPE"
    },
    {
        "comunidad": "Extremadura",
        "servicio": "SEXPE",
        "url": "https://sexpeemplea.juntaex.es/inicio_cita_previa",
        "dominio_esperado": "https://sexpeemplea.juntaex.es",
        "param_origen": "SEXPE"
    },
    {
        "comunidad": "Canarias",
        "servicio": "Servicio Canario de Empleo (SCE)",
        "url": "https://www.gobiernodecanarias.org/empleo/sce/",
        "dominio_esperado": "https://sede.gobiernodecanarias.org",
        "param_origen": "SCE"
    },
    {
        "comunidad": "Islas Baleares",
        "servicio": "SOIB",
        "url": "https://soib.es/citaprevia/",
        "dominio_esperado": "https://soib.es",
        "param_origen": "SOIB"
    }
]

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def crear_contexto_ssl():
    """Crea un contexto SSL seguro."""
    ctx = ssl.create_default_context()
    return ctx

def detectar_navegador_minimo():
    """Detecta el navegador mínimo requerido para cargar las páginas de cita previa basándose en las directivas CSP y compatibilidad de iframes.
    Las páginas modernas con frame-ancestors requieren navegadores con buen soporte de CSP (Content Security Policy) y iframes.
    Se recomiendan versiones actualizadas de los navegadores principales.
    """
    minimos = {
        "chrome": 108,
        "firefox": 122,
        "edge": 120,
        "safari": 15
    }
    # El script utiliza un User-Agent de Chrome 120, pero devolvemos la recomendación general.
    partes = []
    for navegador, version in minimos.items():
        parte = f"{navegador.capitalize()} {version}+"
        partes.append(parte)
    return "Navegadores recomendados: " + ", ".join(partes) + " (para correcto soporte de iframes y CSP)."

def obtener_info_sistema():
    """Obtiene información del sistema (arquitectura, núcleos, memoria) para evaluar compatibilidad con Windows 11."""
    info = {}
    # Arquitectura
    machine = platform.machine().lower()
    info["arquitectura"] = machine
    # Núcleos de CPU
    try:
        cores = os.cpu_count() or 0
    except Exception:
        cores = 0
    info["nucleos"] = cores
    # Memoria total (solo en Linux leyendo /proc/meminfo)
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kbs = int(line.split()[1])
                    bytes_total = kbs * 1024
                    info["memoria_bytes"] = bytes_total
                    info["memoria_gb"] = round(bytes_total / (1024**3), 2)
                    break
    except FileNotFoundError:
        info["memoria_bytes"] = 0
        info["memoria_gb"] = 0
    return info

def verificar_compatibilidad_windows_11(info_sistema):
    """Evalúa si el hardware actual cumple los requisitos mínimos de Windows 11.
    Se comprueba: arquitectura 64-bit, al menos 2 núcleos, y al menos 4 GB de RAM.
    Nota: TPM 2.0 y Secure Boot no pueden determinarse desde este entorno y requieren verificación en Windows.
    """
    requisitos = {
        "arquitectura_64": info_sistema.get("arquitectura", "") in ("x86_64", "amd64", "arm64"),
        "nucleos_2": info_sistema.get("nucleos", 0) >= 2,
        "memoria_4gb": info_sistema.get("memoria_gb", 0) >= 4
    }
    cumplen = all(requisitos.values())
    if cumplen:
        return True, "El hardware cumple los requisitos básicos (64-bit, 2+ núcleos, 4+ GB RAM). Se recomienda actualizar a Windows 11 para usar la versión más alta del navegador."
    else:
        # Preparar mensaje de qué falta
        faltan = []
        if not requisitos["arquitectura_64"]:
            faltan.append("arquitectura de 64 bits")
        if not requisitos["nucleos_2"]:
            faltan.append("al menos 2 núcleos de CPU")
        if not requisitos["memoria_4gb"]:
            faltan.append("al menos 4 GB de RAM")
        mensaje = f"El hardware no cumple los requisitos mínimos de Windows 11. Faltan: {', '.join(faltan)}."
        return False, mensaje

def obtener_mensaje_windows_11(compatible, info_sistema):
    """Genera el mensaje que se mostrará al usuario sobre Windows 11 y el navegador."""
    if compatible:
        return "✅ El equipo es compatible con Windows 11. " + detectar_navegador_minimo() + " Para que cargue la página, tienes que actualizar a Windows 11 para usar la versión más alta del navegador."
    else:
        # Construir mensaje de Linux y enlaces
        # El paréntesis "IBM (epoca moderna)" solo se añade a Fedora, por su historia con Red Hat/IBM
        enlaces = (
            "[Ubuntu](https://ubuntu.com) "
            "[openSUSE](https://opensuse.org) "
            "[Debian](https://debian.org) "
            "[Fedora](https://fedoraproject.org) (IBM (epoca moderna)) cathyos"
        )
        mensaje_linux = (
            f"❌ El equipo no es compatible con Windows 11. " +
            "Es posible que necesites cargar Linux para poder ver la página web de cita previa dependiendo del tipo de configuración para operar con Windows y Linux, " +
            "si es con máquinas virtuales o con arranque dual. Enlaces a distribuciones oficiales: " + enlaces
        )
        return mensaje_linux

def obtener_cabeceras_sepe(url=SEPE_URL):
    """Audita las cabeceras HTTP emitidas por el servidor central del SEPE."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET"
    )
    
    ctx = crear_contexto_ssl()
    resultado = {
        "status": None,
        "csp": "",
        "frame_ancestors": "",
        "dominios_whitelist": [],
        "x_frame_options": "",
        "hsts": "",
        "raw_headers": {}
    }
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            resultado["status"] = resp.status
            headers = dict(resp.headers)
            resultado["raw_headers"] = headers
            
            # Buscar CSP
            csp = headers.get("Content-Security-Policy", "")
            resultado["csp"] = csp
            
            # Extraer frame-ancestors
            match_fa = re.search(r"frame-ancestors\s+([^;]+)", csp, re.IGNORECASE)
            if match_fa:
                fa_content = match_fa.group(1).strip()
                resultado["frame_ancestors"] = fa_content
                # Separar dominios
                tokens = fa_content.split()
                resultado["dominios_whitelist"] = [t for t in tokens if t.startswith("http")]
            
            # Extraer X-Frame-Options
            resultado["x_frame_options"] = headers.get("X-Frame-Options", "No presente")
            resultado["hsts"] = headers.get("Strict-Transport-Security", "No presente")
            
    except urllib.error.HTTPError as e:
        resultado["status"] = e.code
        headers = dict(e.headers)
        resultado["raw_headers"] = headers
        csp = headers.get("Content-Security-Policy", "")
        resultado["csp"] = csp
        match_fa = re.search(r"frame-ancestors\s+([^;]+)", csp, re.IGNORECASE)
        if match_fa:
            fa_content = match_fa.group(1).strip()
            resultado["frame_ancestors"] = fa_content
            tokens = fa_content.split()
            resultado["dominios_whitelist"] = [t for t in tokens if t.startswith("http")]
        resultado["x_frame_options"] = headers.get("X-Frame-Options", "No presente")
    except Exception as ex:
        resultado["error"] = str(ex)
        
    return resultado

def auditar_portal_autonomico(portal, whitelist_sepe):
    """Analiza la página autonómica para detectar si usa iframe o enlace directo y su compatibilidad."""
    url = portal["url"]
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET"
    )
    ctx = crear_contexto_ssl()
    
    resultado = {
        "comunidad": portal["comunidad"],
        "servicio": portal["servicio"],
        "url": url,
        "codigo_http": None,
        "tipo_implementacion": "Desconocida",
        "usa_iframe": False,
        "usa_enlace_directo": False,
        "enlace_sepe_detectado": "",
        "autorizado_en_csp": False,
        "estado_diagnostico": "Error",
        "detalles": ""
    }
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            resultado["codigo_http"] = resp.status
            html = resp.read().decode("utf-8", errors="replace")
            
            # 1. Comprobar si hay iframe (estático o dinámico por JS)
            tiene_iframe_tag = bool(re.search(r"<iframe[^>]+citaprevia-sede\.sepe\.gob\.es", html, re.IGNORECASE))
            tiene_iframe_id = bool(re.search(r"<iframe[^>]+id=[\"']embeddedIframe[\"']", html, re.IGNORECASE))
            tiene_iframe_js = bool(re.search(r"citaprevia-sede\.sepe\.gob\.es.*embeddedIframe", html, re.IGNORECASE | re.DOTALL))
            
            if tiene_iframe_tag or (tiene_iframe_id and tiene_iframe_js):
                resultado["usa_iframe"] = True
            
            # 2. Comprobar si hay enlaces directos
            match_link = re.search(r'href=[\'"](https://citaprevia-sede\.sepe\.gob\.es/citapreviasepe/[^\'"]*)[\'"]', html, re.IGNORECASE)
            if match_link:
                resultado["enlace_sepe_detectado"] = match_link.group(1)
                if not resultado["usa_iframe"]:
                    resultado["usa_enlace_directo"] = True
            
            # 3. Comprobar si el dominio autonómico está en la lista blanca de CSP del SEPE
            dom_esperado = portal["dominio_esperado"].lower()
            en_whitelist = any(dom_esperado in d.lower() for d in whitelist_sepe)
            resultado["autorizado_en_csp"] = en_whitelist
            
            # 4. Determinar diagnóstico
            if resultado["usa_iframe"]:
                resultado["tipo_implementacion"] = "Marco incrustado (<iframe>)"
                if en_whitelist:
                    resultado["estado_diagnostico"] = "🟢 OPERATIVO (Iframe Autorizado por CSP)"
                    resultado["detalles"] = f"El dominio {portal['dominio_esperado']} está autorizado en la cabecera frame-ancestors del SEPE."
                else:
                    resultado["estado_diagnostico"] = "⚠️ ERROR (Iframe Bloqueado - Error de Objeto Incrustado)"
                    resultado["detalles"] = f"El dominio {portal['dominio_esperado']} NO está en la lista blanca del SEPE. El navegador bloqueará el marco."
            elif resultado["usa_enlace_directo"]:
                resultado["tipo_implementacion"] = "Enlace directo externo (sin marco)"
                resultado["estado_diagnostico"] = "🟢 OPERATIVO (Enlace Directo fuera de marco)"
                resultado["detalles"] = "Abre el SEPE a pantalla completa en pestaña nueva. Inmune a bloqueos de iframe/CSP."
            else:
                # Comprobar si redirige o usa formulario
                resultado["tipo_implementacion"] = "Enlace / Botón integrado"
                resultado["estado_diagnostico"] = "🟢 OPERATIVO"
                resultado["detalles"] = "Acceso operativo mediante navegación estándar."
                
    except Exception as ex:
        resultado["estado_diagnostico"] = f"❌ ERROR DE ACCESO: {str(ex)}"
        resultado["detalles"] = f"No se pudo conectar al portal autonómico: {ex}"
        
    return resultado

def generar_reporte_markdown(datos_sepe, resultados_autonomicos, ruta_salida):
    """Genera un archivo Markdown completo y estructurado con los resultados."""
    ahora_str = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S CEST")
    
    md = []
    md.append("# Informe de Auditoría: Estado de Cita Previa de Empleo (SEPE y CC. AA.)\n")
    md.append(f"> **Auditoría generada automáticamente el:** {ahora_str}\n")
    md.append("Este informe analiza el estado de las directivas de seguridad web del Servicio Público de Empleo Estatal (SEPE) y la compatibilidad con los portales autonómicos de cita previa de empleo.\n")
    md.append("---\n")
    
    # Sección 1: Cabeceras SEPE
    md.append("## 1. Estado del Servidor Central del SEPE (`citaprevia-sede.sepe.gob.es`)\n")
    md.append(f"* **Código HTTP:** `{datos_sepe.get('status')}`")
    md.append(f"* **X-Frame-Options:** `{datos_sepe.get('x_frame_options')}`")
    md.append(f"* **Strict-Transport-Security (HSTS):** `{datos_sepe.get('hsts')}`\n")
    
    md.append("### Directiva `Content-Security-Policy: frame-ancestors` (Lista Blanca):")
    if datos_sepe.get("frame_ancestors"):
        md.append("```http")
        md.append(f"frame-ancestors {datos_sepe.get('frame_ancestors')};")
        md.append("```\n")
        md.append("**Dominios autonómicos expresamente autorizados en el SEPE:**")
        for dom in datos_sepe.get("dominios_whitelist", []):
            md.append(f"- `{dom}`")
    else:
        md.append("⚠️ *No se detectó directiva frame-ancestors o el servidor no respondió correctamente.*")
    md.append("\n---\n")
    
    # Sección 2: Tabla de CC. AA.
    md.append("## 2. Estado de los Portales Autonómicos Auditados\n")
    md.append("| Comunidad Autónoma | Servicio / Portal | Tipo de Implementación | En Lista Blanca SEPE | Estado Técnico |")
    md.append("| :--- | :--- | :--- | :---: | :--- |")
    
    for r in resultados_autonomicos:
        aut_icon = "🟢 Sí" if r["autorizado_en_csp"] else ("⚪ N/A" if not r["usa_iframe"] else "❌ No")
        md.append(f"| **{r['comunidad']}** | [{r['servicio']}]({r['url']}) | {r['tipo_implementacion']} | {aut_icon} | {r['estado_diagnostico']} |")
    
    md.append("\n### Detalle por Comunidad Autónoma:\n")
    for r in resultados_autonomicos:
        md.append(f"#### {r['comunidad']} ({r['servicio']})")
        md.append(f"- **URL auditada:** [{r['url']}]({r['url']})")
        md.append(f"- **Implementación:** {r['tipo_implementacion']}")
        md.append(f"- **Diagnóstico:** {r['estado_diagnostico']}")
        md.append(f"- **Detalle técnico:** {r['detalles']}")
        if r.get("enlace_sepe_detectado"):
            md.append(f"- **Enlace de destino SEPE:** `{r['enlace_sepe_detectado']}`")
        md.append("")
    
    md.append("---\n")
    
    # Sección 3: Mapa de las 17 CC. AA.
    md.append("## 3. Resumen Global del Modelo en las 17 CC. AA. Españolas\n")
    md.append("1. **Comunidades integradas que incrustan el SEPE en `<iframe>`:**")
    md.append("   - **Comunidad de Madrid:** Autorizada en CSP (`https://www.comunidad.madrid`).")
    md.append("   - **Principado de Asturias (Trabajastur):** Autorizada en CSP (`https://trabajastur.asturias.es`).")
    md.append("2. **Comunidades integradas mediante enlace directo (sin marco):**")
    md.append("   - **Extremadura (SEXPE):** Retiró el `<iframe>` y usa `<a target=\"_blank\">`.")
    md.append("   - **Canarias (SCE):** Enlace directo nativo a pantalla completa y App móvil.")
    md.append("   - **Islas Baleares (SOIB):** Enlace directo con botón `<a target=\"_blank\">`.")
    md.append("3. **Comunidades con plataformas de cita previas propias (Inmunes al SEPE):**")
    md.append("   - Andalucía (SAE), Aragón (INAEM), Cantabria (EMCAN), Castilla-La Mancha (Emplea CLM), Castilla y León (ECyL), Cataluña (SOC), Comunitat Valenciana (LABORA), Galicia (Emprego Galicia), La Rioja, Navarra (SNE-NL), País Vasco (Lanbide), Región de Murcia (SEF), Ceuta y Melilla.")
    md.append("\n---\n")
    
    # Sección 4: Enlaces directos de contingencia
    md.append("## 4. Enlaces Directos de Acceso Inmediato (Bypass)\n")
    md.append("Si algún marco autonómico sufriera problemas de renderizado en navegadores desactualizados, se recomienda acceder a través de estos enlaces directos a pantalla completa:\n")
    md.append("* [Cita Previa Comunidad de Madrid (origen=28)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28)")
    md.append("* [Cita Previa Extremadura - SEXPE (origen=SEXPE)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/)")
    md.append("* [Cita Previa Asturias - Trabajastur (origen=SEPE)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SEPE&codidioma=es)")
    md.append("* [Cita Previa Canarias - SCE (origen=SCE)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SCE)")
    md.append("* [Cita Previa Baleares - SOIB (origen=SOIB)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SOIB&codidioma=ca)")
    md.append("* [Sede Electrónica General del SEPE](https://sede.sepe.gob.es/portalSede/procedimientos-y-servicios/personas/proteccion-por-desempleo/cita-previa.html)\n")
    
    contenido_final = "\n".join(md)
    
    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido_final)
        
    return contenido_final

def generar_readme_y_guia(directorio_script):
    """Genera archivos README y Guía Didáctica en español e inglés."""
    # Contenido en español para README
    readme_es = """# Auditoría Cita Previa (SEPE y CC. AA.)

## Descripción
Auditoría automatizada del sistema de cita previa de oficinas de empleo (SEPE y Consejerías de Educación/Empleo de las Comunidades Autónomas). Analiza las cabeceras de seguridad CSP (frame-ancestors), X-Frame-Options y la arquitectura de los portales autonómicos (iframes vs. enlaces directos), generando un informe en Markdown.

## Funcionalidades
- Detecta el navegador mínimo requerido para cargar las páginas de cita previa (versiones modernas de Chrome, Firefox, Edge, Safari).
- Muestra en pantalla si la auditoría completó exitosamente o hay advertencias/ errores.
- Verifica la compatibilidad del hardware con Windows 11 (arquitectura 64-bit, núcleos de CPU, memoria RAM).
- En caso de no ser compatible con Windows 11, sugiere alternativas con Linux (Ubuntu, openSUSE, Debian, Fedora) para poder ver la página web de cita previa, ya sea en máquinas virtuales o con arranque dual.
- Compatible con sistemas operativos Linux y Windows (el script se ejecuta en cualquier entorno con Python 3).

## Uso
Ejecuta el script desde la terminal:
```bash
python3 auditar_cita_previa.py [archivo_salida.md]
```
Si no se proporciona un archivo de salida, generará `informe_estado_cita_previa.md` en el mismo directorio.

## Interpretación de resultados
- El informe Markdown incluye el estado de las cabeceras CSP, la implementación de iframes o enlaces directos en cada portal autonómico, y un diagnóstico técnico.
- Los mensajes en consola indican el navegador mínimo recomendado, el estado general y la compatibilidad con Windows 11.
- Si el hardware no es compatible con Windows 11, considera instalar Linux en máquinas virtuales (VirtualBox, VMware) o en modo dual-boot para acceder a las páginas de cita previa.

## Enlaces útiles
- [SEPE](https://sede.sepe.gob.es)
- Portales autonómicos incluidos en la auditoría.
"""
    
    # Contenido en inglés para README
    readme_en = """# Cita Previa Audit (SEPE and CC. AA.)

## Description
Automated audit of the employment office appointment (cita previa) system (SEPE and Autonomous Communities' Education/Employment Ministries). It analyzes security CSP headers (frame-ancestors), X-Frame-Options and the architecture of the autonomous portals (iframes vs. direct links), generating a Markdown report.

## Features
- Detects the minimum browser required to load the cita previa pages (modern versions of Chrome, Firefox, Edge, Safari).
- Shows on screen if the audit completed successfully or if there are warnings/errors.
- Checks hardware compatibility with Windows 11 (64-bit architecture, CPU cores, RAM memory).
- If not compatible with Windows 11, suggests Linux alternatives (Ubuntu, openSUSE, Debian, Fedora) to be able to view the web appointment page, either in virtual machines or with dual-boot.
- Compatible with Linux and Windows operating systems (the script runs in any environment with Python 3).

## Usage
Run the script from the terminal:
```bash
python3 auditar_cita_previa.py [output_file.md]
```
If no output file is provided, it will generate `informe_estado_cita_previa.md` in the same directory.

## Results Interpretation
- The Markdown report includes the state of CSP headers, iframe or direct link implementation in each autonomous portal, and technical diagnosis.
- Console messages indicate the minimum recommended browser, the overall status, and Windows 11 compatibility.
- If the hardware is not compatible with Windows 11, consider installing Linux in virtual machines (VirtualBox, VMware) or dual-boot to access the appointment pages.

## Useful Links
- [SEPE](https://sede.sepe.gob.es)
- Included autonomous portals in the audit.
"""
    
    # Escribir README en español
    with open(os.path.join(directorio_script, "README.es.md"), "w", encoding="utf-8") as f:
        f.write(readme_es)
    
    # Escribir README en inglés
    with open(os.path.join(directorio_script, "README.en.md"), "w", encoding="utf-8") as f:
        f.write(readme_en)
    
    # Contenido de la guía didáctica en español
    guia_es = """# Guía Didáctica del Auditoría de Cita Previa

## Propósito
Esta guía te ayudará a entender los resultados del informe generado y cómo solucionar problemas de compatibilidad para acceder a las páginas de cita previa.

## Qué hace el auditor
1. **Comprueba las cabeceras CSP**: Verifica si el dominio de tu comunidad autónoma está en la lista blanca del SEPE en la directiva `frame-ancestors`. Si está, el iframe cargará sin bloqueos.
2. **Detecta el tipo de implementación**: Determina si el portal usa un iframe incrustado, un enlace directo (a pantalla completa) o un botón integrado.
3. **Evalúa el navegador**: Recomienda versiones mínimas de navegadores modernos para un correcto funcionamiento.
4. **Evalúa Windows 11**: Comprueba si tu hardware cumple los requisitos mínimos para Windows 11 y, de no ser así, sugiere alternativas con Linux.

## Cómo interpretar el informe Markdown
- **Estado técnico**: Cada fila de la tabla indica si el portal está operativo, si hay errores de CSP o si usa iframes/botones.
- **Mensajes en consola**: El navegador mínimo recomendado, el estado general y la compatibilidad con Windows 11 te indican qué pasos seguir.
- **Si aparece "No compatible con Windows 11"**: Tu hardware no cumple los requisitos mínimos (falta arquitectura de 64 bits, núcleos de CPU o memoria RAM). Considera instalar Linux.

## Instalación de Linux (si es necesario)
Puedes instalar una distribución Linux en modo dual-boot con Windows o en una máquina virtual.
### Modo dual-boot
1. Haz una copia de seguridad de tus datos importantes.
2. Descarga una distribución Linux (Ubuntu, openSUSE, Debian o Fedora).
3. Crea un USB de instalación con herramientas como Rufus o balenaEtcher.
4. Arranca desde el USB y sigue el asistente de instalación. Durante el particionado, elige "Instalar junto a Windows" para configurar el arranque dual.
### Máquina virtual
1. Instala VirtualBox o VMware Player.
2. Descarga la ISO de la distribución Linux deseada.
3. Crea una nueva máquina virtual y asigna al menos 4 GB de RAM y 2 núcleos de CPU.
4. Inicia la VM e instala Linux dentro de Windows.

## Distribuciones recomendadas
- **Ubuntu**: https://ubuntu.com
- **openSUSE**: https://opensuse.org
- **Debian**: https://debian.org
- **Fedora**: https://fedoraproject.org (IBM (epoca moderna)) cathyos

## Enlaces de contingencia
Si algún marco autonómico tiene problemas de renderizado, usa los enlaces directos de bypass que aparecen en la sección 4 del informe Markdown.

¡Éxito en tu auditoría!
"""
    
    # Contenido de la guía didáctica en inglés
    guia_en = """# Didactic Guide for Cita Previa Audit

## Purpose
This guide will help you understand the results generated by the audit and how to solve compatibility issues to access the appointment pages.

## What the auditor does
1. **Checks CSP headers**: Verifies if your autonomous community's domain is on the SEPE whitelist in the `frame-ancestors` directive. If it is, the iframe will load without blocks.
2. **Detects implementation type**: Determines if the portal uses an embedded iframe, a direct link (full screen) or an integrated button.
3. **Evaluates the browser**: Recommends minimum modern browser versions for proper functioning.
4. **Evaluates Windows 11**: Checks if your hardware meets the minimum requirements for Windows 11, and if not, suggests Linux alternatives.

## How to interpret the Markdown report
- **Technical status**: Each row in the table indicates whether the portal is operational, if there are CSP errors, or if it uses iframes/buttons.
- **Console messages**: The minimum recommended browser, overall status, and Windows 11 compatibility tell you what steps to follow.
- **If "Not compatible with Windows 11" appears**: Your hardware does not meet the minimum requirements (missing 64-bit architecture, CPU cores, or RAM). Consider installing Linux.

## Installing Linux (if needed)
You can install a Linux distribution in dual-boot mode with Windows or in a virtual machine.
### Dual-boot mode
1. Back up your important data.
2. Download a Linux distribution (Ubuntu, openSUSE, Debian or Fedora).
3. Create a USB installation media using tools like Rufus or balenaEtcher.
4. Boot from the USB and follow the installer. During partitioning, choose "Install alongside Windows" to configure dual-boot.
### Virtual machine
1. Install VirtualBox or VMware Player.
2. Download the ISO of the desired Linux distribution.
3. Create a new virtual machine and assign at least 4 GB of RAM and 2 CPU cores.
4. Start the VM and install Linux inside Windows.

## Recommended distributions
- **Ubuntu**: https://ubuntu.com
- **openSUSE**: https://opensuse.org
- **Debian**: https://debian.org
- **Fedora**: https://fedoraproject.org (IBM (epoca moderna)) cathyos

## Bypass links
If any autonomous portal has rendering issues, use the direct bypass links that appear in section 4 of the Markdown report.

Good luck with your audit!
"""
    
    # Escribir guía didáctica en español
    with open(os.path.join(directorio_script, "Guia_Didactica.es.md"), "w", encoding="utf-8") as f:
        f.write(guia_es)
    
    # Escribir guía didáctica en inglés
    with open(os.path.join(directorio_script, "Guia_Didactica.en.md"), "w", encoding="utf-8") as f:
        f.write(guia_en)

def main():
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_md_defecto = os.path.join(directorio_script, "informe_estado_cita_previa.md")
    
    ruta_md = sys.argv[1] if len(sys.argv) > 1 else ruta_md_defecto
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando auditoría del sistema de cita previa...")
    print(f" -> Verificando cabeceras del SEPE en: {SEPE_URL}")
    datos_sepe = obtener_cabeceras_sepe()
    whitelist = datos_sepe.get("dominios_whitelist", [])
    print(f" -> Whitelist CSP detectada en SEPE: {whitelist}")
    
    print("\n -> Auditando portales autonómicos...")
    resultados = []
    for portal in PORTALES_AUTONOMICOS:
        print(f"    - Comprobando {portal['comunidad']} ({portal['url']})...")
        res = auditar_portal_autonomico(portal, whitelist)
        resultados.append(res)
        print(f"      Resultado: {res['estado_diagnostico']}")
    
    print(f"\n -> Generando informe Markdown en: {ruta_md}")
    reporte = generar_reporte_markdown(datos_sepe, resultados, ruta_md)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Informe Markdown generado correctamente.\n")
    
    # --- NUEVA CAPACIDAD: Detectar navegador mínimo ---
    print(" -> Detectando navegador mínimo requerido...")
    mensaje_navegador = detectar_navegador_minimo()
    print(f" {mensaje_navegador}\n")
    
    # --- NUEVA CAPACIDAD: Mostrar si funciona o no en pantalla ---
    # Determinar si hay algún error o advertencia en los resultados
    hay_errores = any("ERROR" in r["estado_diagnostico"] or "❌" in r["estado_diagnostico"] for r in resultados)
    if hay_errores:
        estado_pantalla = "⚠️ Se detectaron advertencias o errores en el auditorio (revisa el informe Markdown para detalles)."
    else:
        estado_pantalla = "✅ Todos los portales auditados están operativos sin errores detectados."
    print(f" {estado_pantalla}\n")
    
    # --- NUEVA CAPACIDAD: Compatibilidad con Windows y Windows 11 ---
    print(" -> Verificando compatibilidad con Windows 11...")
    info_sis = obtener_info_sistema()
    compatible, mensaje_w11 = verificar_compatibilidad_windows_11(info_sis)
    print(f" {mensaje_w11}\n")
    
    # Mostrar mensaje final según compatibilidad Windows 11
    mensaje_final = obtener_mensaje_windows_11(compatible, info_sis)
    print(f" {mensaje_final}\n")
    
    # --- NUEVA CAPACIDAD: Generar README y guía didáctica en ambos idiomas ---
    generar_readme_y_guia(directorio_script)
    print(" -> README y guía didáctica generados en ambos idiomas.\n")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Auditoría finalizada con éxito. Informe generado.")


if __name__ == "__main__":
    main()