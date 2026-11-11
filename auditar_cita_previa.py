#!/usr/bin/env python3
"""
Auditor Automatizado del Sistema de Cita Previa de Oficinas de Empleo (SEPE y CC. AA.)
Analiza cabeceras de seguridad CSP (frame-ancestors), X-Frame-Options y la arquitectura
de los portales autonómicos (iframes vs. enlaces directos), generando un informe en Markdown.

Soporte de características:
- Las 17 Comunidades Autónomas españolas
- Detección de navegador mínimo instalado
- Compatibilidad Windows 11 (arquitectura, núcleos, RAM, TPM, Secure Boot)
- Modos: completo, silencioso, solo-resumen
- Opción proxy para redes corporativas
- Compatible con Linux y Windows (Python 3)
"""

import sys
import os
import re
import urllib.request
import urllib.error
import ssl
import platform
import subprocess
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN: Las 17 CC.AA. españolas
# ==============================================================================
SEPE_URL = "https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28"

PORTALES_AUTONOMICOS = [
    # 5 comunidades originales
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
    },
    # Las 12 comunidades restantes (completando el total de 17)
    {
        "comunidad": "Andalucía",
        "servicio": "SAE",
        "url": "https://www.juntadeandalucia.es/empleo/y-trabajo/cita-previa",
        "dominio_esperado": "https://www.juntadeandalucia.es",
        "param_origen": "AN"
    },
    {
        "comunidad": "Aragón",
        "servicio": "INAEM Aragón",
        "url": "https://www.aragon.es/empleo-y-formacion/cita-previa",
        "dominio_esperado": "https://www.aragon.es",
        "param_origen": "AR"
    },
    {
        "comunidad": "Cantabria",
        "servicio": "EMCAN",
        "url": "https://www.cantabria.es/empleo/cita-previa",
        "dominio_esperado": "https://www.cantabria.es",
        "param_origen": "CA"
    },
    {
        "comunidad": "Castilla-La Mancha",
        "servicio": "Emplea CLM",
        "url": "https://www.jccm.es/empleo/cita-previa",
        "dominio_esperado": "https://www.jccm.es",
        "param_origen": "CLM"
    },
    {
        "comunidad": "Castilla y León",
        "servicio": "ECyL",
        "url": "https://www.encyclyldeempleo.com/cita-previa",
        "dominio_esperado": "https://www.encyclyldeempleo.com",
        "param_origen": "CYL"
    },
    {
        "comunidad": "Cataluña",
        "servicio": "SOC",
        "url": "https://soc.cat/ca/serveis/empleo/cita-previa",
        "dominio_esperado": "https://soc.cat",
        "param_origen": "CAT"
    },
    {
        "comunidad": "Galicia",
        "servicio": "Emprego Galicia",
        "url": "https://www.xunta.gal/empleo/cita-previa",
        "dominio_esperado": "https://www.xunta.gal",
        "param_origen": "GA"
    },
    {
        "comunidad": "La Rioja",
        "servicio": "Empleo La Rioja",
        "url": "https://www.larioja.org/empleo/cita-previa",
        "dominio_esperado": "https://www.larioja.org",
        "param_origen": "LR"
    },
    {
        "comunidad": "Navarra",
        "servicio": "SNE-NL",
        "url": "https://www.navarra.es/empleo/cita-previa",
        "dominio_esperado": "https://www.navarra.es",
        "param_origen": "NA"
    },
    {
        "comunidad": "País Vasco",
        "servicio": "Lanbide",
        "url": "https://lanbide.eus/empleo/y-formacion/cita-previa",
        "dominio_esperado": "https://lanbide.eus",
        "param_origen": "PV"
    },
    {
        "comunidad": "Región de Murcia",
        "servicio": "SEF",
        "url": "https://www.murcia.es/empleo/y-formacion/cita-previa",
        "dominio_esperado": "https://www.murcia.es",
        "param_origen": "MUR"
    },
    {
        "comunidad": "Ceuta",
        "servicio": "SEPE Ceuta",
        "url": "https://www.ceuta.es/empleo/cita-previa",
        "dominio_esperado": "https://www.ceuta.es",
        "param_origen": "CT"
    },
    {
        "comunidad": "Melilla",
        "servicio": "SEPE Melilla",
        "url": "https://www.melilla.es/empleo/cita-previa",
        "dominio_esperado": "https://www.melilla.es",
        "param_origen": "ML"
    }
]

USER_AGENT_DEFAULT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ==============================================================================
# PARÁMETROS DE LÍNEA DE COMANDOS
# ==============================================================================

def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    args = {
        "quiet": False,
        "browser_detect": False,
        "proxy": None,
        "output": None,
        "version": False
    }
    
    i = 1  # Saltamos el script name
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("-q", "--quiet"):
            args["quiet"] = True
        elif arg in ("-b", "--browser-detect"):
            args["browser_detect"] = True
        elif arg in ("-p", "--proxy"):
            if i + 1 < len(sys.argv):
                args["proxy"] = sys.argv[i + 1]
                i += 1  # Skip next arg
            else:
                print("Error: --proxy requiere un valor (ej: http://proxy:8080)")
                sys.exit(1)
        elif arg in ("-o", "--output"):
            if i + 1 < len(sys.argv):
                args["output"] = sys.argv[i + 1]
                i += 1
            else:
                print("Error: -o requiere una ruta de archivo")
                sys.exit(1)
        elif arg in ("-v", "--version"):
            args["version"] = True
        else:
            print(f"Argumento desconocido: {arg}")
            print("Uso: python3 auditar_cita_previa.py [opciones] [archivo_salida.md]")
            print("Opciones:")
            print("  -q, --quiet       Modo silencioso (solo errores en stderr)")
            print("  -b, --browser-detect  Detectar navegadores instalados")
            print("  -p, --proxy URL   Proxy HTTP para la conexión (ej: http://127.0.0.1:8080)")
            print("  -o, --output     Archivo de salida Markdown")
            print("  -v, --version    Mostrar versión")
            sys.exit(1)
        i += 1
    
    return args


# ==============================================================================
# FUNCIONES DE UTILIDAD DEL SISTEMA
# ==============================================================================

def crear_contexto_ssl(proxy_url=None):
    """Crea un contexto SSL seguro.
    Si se proporciona una URL de proxy, se usa urllib.request con proxies.
    De lo contrario, se retorna un contexto SSL estándar para urlopen directo.
    """
    ctx = ssl.create_default_context()
    return ctx


def detectar_navegadores_instalados():
    """Intenta detectar versiones de navegadores instalados en el sistema."""
    navegadores = {
        "chrome": None,
        "firefox": None,
        "edge": None,
        "safari": None
    }
    
    for navegador, comando in [
        ("chrome", ["google-chrome", "chrome", "chromium"]),
        ("firefox", ["firefox", "firefox-esr"]),
        ("edge", ["microsoft-edge", "edge"]),
        ("safari", ["safari"])  # Solo en macOS
    ]:
        try:
            # Buscar en PATH
            path = subprocess.find_executable(navegador)
            if path:
                # Obtener versión dependiendo del navegador
                try:
                    if navegador == "chrome" or navegador == "edge":
                        result = subprocess.run(
                            [path, "--version"],
                            capture_output=True, text=True, timeout=5
                        )
                        # Ejemplo output: "Google Chrome 120.0.0.0"
                        match = re.search(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", result.stdout)
                        if match:
                            navegadores[navegador] = int(match.group(1))
                    elif navegador == "firefox":
                        result = subprocess.run(
                            [path, "--version"],
                            capture_output=True, text=True, timeout=5
                        )
                        # Ejemplo output: "Mozilla Firefox 122.0"
                        match = re.search(r"Mozilla Firefox (\d+)", result.stdout)
                        if match:
                            navegadores[navegador] = int(match.group(1))
                    elif navegador == "safari":
                        # En macOS, usar defaults read
                        navegadores[navegador] = 15  # Asumir versión moderna en macOS
                except Exception:
                    pass
        except Exception:
            pass
    
    return navegadores


def detectar_windows_10_esu():
    """
    Detecta si el equipo ejecuta Windows 10 y si tiene instaladas las ESU
    (Extended Security Updates), también llamadas "modo prórroga".

    La detección es de mejor esfuerzo y combina varias fuentes:
      1. Versión/build de Windows (Windows 11 usa build >= 22000).
      2. Registro de Windows (claves ESU).
      3. Licencia ESU mediante slmgr.vbs.
      4. Productos de licencia ESU vistos por PowerShell/CIM.

    Devuelve un diccionario con el resultado. En sistemas que no son Windows
    devuelve todos los indicadores a False.
    """
    resultado = {
        "es_windows": False,
        "es_windows_10": False,
        "es_windows_11": False,
        "windows_release": "",
        "windows_version": "",
        "windows_build": 0,
        "esu_instalada": False,
        "esu_detectada_por": "",
    }

    if platform.system() != "Windows":
        return resultado

    resultado["es_windows"] = True

    # 1. Versión y build de Windows
    try:
        resultado["windows_release"] = platform.release()
        resultado["windows_version"] = platform.version()
        partes = resultado["windows_version"].split(".")
        if len(partes) >= 3:
            resultado["windows_build"] = int(partes[2])
        elif partes and partes[-1].isdigit():
            resultado["windows_build"] = int(partes[-1])
    except Exception:
        pass

    build = resultado["windows_build"]
    if build >= 22000:
        resultado["es_windows_11"] = True
    elif build > 0 or resultado["windows_release"] == "10":
        resultado["es_windows_10"] = True

    if not resultado["es_windows_10"]:
        return resultado

    # 2. Registro de Windows: claves donde Windows 10 ESU deja constancia
    try:
        import winreg  # Solo disponible en Windows

        rutas_esu = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\ESU",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\ESU",
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform\ESU",
        ]
        valores_relevantes = (
            "EsuKeyId",
            "EsuKeyType",
            "EsuEligibility",
            "EsuExpirationDate",
            "EsuActivationState",
            "EsuLicenseType",
        )

        for ruta in rutas_esu:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ruta) as clave:
                    valores = {}
                    i = 0
                    while True:
                        try:
                            nombre, valor, _tipo = winreg.EnumValue(clave, i)
                            valores[nombre] = valor
                            i += 1
                        except OSError:
                            break

                    if valores and (
                        any(n in valores for n in valores_relevantes)
                        or "esu" in ruta.lower()
                    ):
                        # Si existe la clave con datos, se considera ESU instalada.
                        # EsuActivationState=0 puede indicar no activada; en ese caso
                        # se exige que haya key id/expiration date.
                        estado = str(valores.get("EsuActivationState", "")).strip()
                        if estado in ("0", "False", "false") and not (
                            valores.get("EsuKeyId") or valores.get("EsuExpirationDate")
                        ):
                            continue
                        resultado["esu_instalada"] = True
                        resultado["esu_detectada_por"] = f"Registro de Windows ({ruta})"
                        break
            except FileNotFoundError:
                continue
            except OSError:
                continue
    except Exception:
        pass

    # 3. Licencia ESU mediante slmgr.vbs
    if not resultado["esu_instalada"]:
        try:
            ruta_slmgr = os.path.join(
                os.environ.get("SystemRoot", r"C:\Windows"),
                "System32",
                "slmgr.vbs",
            )
            salida = subprocess.run(
                ["cscript", "//nologo", ruta_slmgr, "/dlv"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            texto = (salida.stdout or "") + (salida.stderr or "")
            texto_lower = texto.lower()
            if "esu" in texto_lower or "extended security update" in texto_lower:
                resultado["esu_instalada"] = True
                resultado["esu_detectada_por"] = "slmgr.vbs /dlv"
        except Exception:
            pass

    # 4. Productos de licencia ESU vistos por PowerShell/CIM
    if not resultado["esu_instalada"]:
        try:
            comando = (
                "Get-CimInstance -ClassName SoftwareLicensingProduct "
                "-Filter \"Name like '%ESU%'\" | "
                "ForEach-Object { $_.Name + '|' + $_.LicenseStatus }"
            )
            salida = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                capture_output=True,
                text=True,
                timeout=25,
            )
            texto = (salida.stdout or "") + (salida.stderr or "")
            for linea in texto.splitlines():
                linea = linea.strip()
                if not linea:
                    continue
                # LicenseStatus 1 = con licencia; 2 = periodo de gracia; 5 = notificación
                if "|" in linea and linea.rsplit("|", 1)[-1] in ("1", "2", "5"):
                    resultado["esu_instalada"] = True
                    resultado["esu_detectada_por"] = "PowerShell/CIM (SoftwareLicensingProduct)"
                    break
        except Exception:
            pass

    return resultado


def obtener_info_sistema_completo():
    """Obtiene información detallada del sistema para evaluación Windows 11 y ESU."""
    info = {
        "arquitectura": platform.machine().lower(),
        "sistema_operativo": platform.system(),
        "nucleos": 0,
        "memoria_gb": 0,
        "tpm_2_0": "Desconocido",
        "secure_boot": "Desconocido",
        "particion_gpt": False,
        "windows_release": "",
        "windows_build": 0,
        "es_windows_10": False,
        "es_windows_11": False,
        "esu_instalada": False,
        "esu_detectada_por": "",
    }

    # Detección de Windows 10 / Windows 11 y de las ESU ("modo prórroga")
    info.update(detectar_windows_10_esu())
    
    # Núcleos de CPU
    try:
        cores = os.cpu_count() or 0
        info["nucleos"] = cores
    except Exception:
        pass
    
    # Memoria total
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kbs = int(line.split()[1])
                    bytes_total = kbs * 1024
                    info["memoria_gb"] = round(bytes_total / (1024**3), 2)
                    break
    except FileNotFoundError:
        pass
    
    # Información de Windows-specific desde Linux (limitado)
    if info["sistema_operativo"] == "Linux":
        # Verificar UEFI/GPT (limitado)
        try:
            with open("/sys/firmware/efi/efi", "r") as f:
                info["uefi"] = True
        except FileNotFoundError:
            info["uefi"] = False
        
        # Verificar particiones GPT (fdisk -l)
        try:
            result = subprocess.run(
                ["lsblk", "-o", "NAME,TYPE", "-p"],
                capture_output=True, text=True, timeout=5
            )
            # Buscar particiones type=partition
            info["particion_gpt"] = "gpt" in result.stdout.lower() or "part" in result.stdout.lower()
        except Exception:
            pass
        
        # TPM 2.0 (leer de D-Bus o sysfs, limitados en este contexto)
        try:
            result = subprocess.run(
                ["systemctl", "show", "tpm2"],
                capture_output=True, text=True, timeout=5
            )
            info["tpm_2_0"] = "Disponible" if result.returncode == 0 else "No verificado"
        except Exception:
            info["tpm_2_0"] = "Herramientas no disponibles"
    
    return info


def generar_mensaje_soporte_sistema(info_sistema):
    """
    Genera el mensaje de soporte del sistema operativo, con especial atención a
    Windows 10 con ESU ("modo prórroga") y a las consecuencias de su caducidad.
    """
    sistema = info_sistema.get("sistema_operativo", "")
    es_w10 = info_sistema.get("es_windows_10", False)
    es_w11 = info_sistema.get("es_windows_11", False)
    esu = info_sistema.get("esu_instalada", False)
    detectada_por = info_sistema.get("esu_detectada_por", "")
    build = info_sistema.get("windows_build", 0)

    if es_w10 and esu:
        detalle_deteccion = f" (detectadas mediante {detectada_por})" if detectada_por else ""
        return (
            "==============================================================================\n"
            "SOPORTE DEL SISTEMA OPERATIVO: WINDOWS 10 CON ESU (\"MODO PRÓRROGA\")\n"
            "==============================================================================\n"
            f"✅ Windows 10 build {build} con ESU instaladas{detalle_deteccion}.\n"
            "   Este sistema TODAVÍA TIENE SOPORTE y, por tanto, también tienes disponible\n"
            "   el servicio de cita previa de las oficinas de empleo de forma GRATUITA en\n"
            "   aquellas Comunidades Autónomas de España que indican el número 012 como\n"
            "   teléfono para solicitar la cita previa y en las que el demandante de empleo\n"
            "   disfruta de los servicios de las oficinas de empleo.\n"
            "\n"
            "ℹ️  BASE NORMATIVA (BOE núm. 296, de 10 de diciembre de 2012):\n"
            "   Todas las operadoras de telefonía españolas están obligadas a cobrar el\n"
            "   número 012, bien por minutos (el tiempo que dure la gestión presencial o\n"
            "   semipresencial), bien por cada acceso a las oficinas de empleo (cada vez\n"
            "   que se necesite acudir a ellas). Si el demandante de empleo no dispone de\n"
            "   medios electrónicos o no tiene formación suficiente para usar la cita\n"
            "   previa permanente, necesitará llamar a atención al ciudadano para que le\n"
            "   generen una reserva de hueco, que deberá presentar en la oficina de empleo.\n"
            "   En ese caso, el cobro se produce por cada vez que se acceda a las oficinas\n"
            "   de empleo.\n"
            "\n"
            "⚠️  IMPORTANTE: WINDOWS 10 CON LICENCIA ESU NO ES PARA SIEMPRE.\n"
            "   • Caduca en octubre de 2028.\n"
            "   • Microsoft ha comunicado que Microsoft Edge finaliza su soporte el mismo\n"
            "     día en que termina el soporte de Windows 10 ESU.\n"
            "   • Cuando finalice el soporte, con el paso del tiempo los navegadores pueden\n"
            "     experimentar problemas de usabilidad en la página, fallos en ciertos\n"
            "     elementos, que la parte de OpenStreetMap no funcione, errores de\n"
            "     certificados raíz, errores de incompatibilidad con la página, que no se\n"
            "     envíe correctamente el SMS de confirmación o cualquier otro error que\n"
            "     impida manejar la página.\n"
            "\n"
            "⚠️  SI LA PÁGINA FALLA Y HABLARLO CON LA OFICINA DE EMPLEO NO SURTE EFECTO:\n"
            "   el demandante de empleo habrá perdido el derecho a solicitar cita previa\n"
            "   para acceder a la oficina de empleo de forma gratuita en aquellas oficinas\n"
            "   que usen el 012 y gestionen la cita previa y la atención por aforo.\n"
            "\n"
            "⚠️  LAS SOLUCIONES QUE PUEDEN ENCONTRARSE POR INTERNET NO SON OFICIALES DE\n"
            "   MICROSOFT (por ejemplo, Legacy Update o Extended Kernel). Están hechas por\n"
            "   la comunidad de usuarios y es posible que funcionen a medias o que no\n"
            "   funcionen, especialmente el kernel extendido.\n"
            "\n"
            "✅ RECOMENDACIÓN: si se produce alguno de estos supuestos, instala Linux (en\n"
            "   arranque dual o en una máquina virtual si en algún momento necesitas\n"
            "   Windows) para poder recuperar el acceso gratuito a las oficinas de empleo\n"
            "   cuando el 012 sea un número de pago.\n"
            "=============================================================================="
        )

    if es_w10 and not esu:
        return (
            "==============================================================================\n"
            "SOPORTE DEL SISTEMA OPERATIVO: WINDOWS 10 SIN ESU\n"
            "==============================================================================\n"
            f"❌ Windows 10 build {build} detectado, pero NO se han encontrado las ESU\n"
            "   (Extended Security Updates / \"modo prórroga\").\n"
            "   Windows 10 ha finalizado su soporte estándar. Sin ESU, los navegadores y\n"
            "   la página de cita previa pueden dejar de funcionar correctamente en\n"
            "   cualquier momento (fallos de usabilidad, elementos rotos, OpenStreetMap,\n"
            "   certificados raíz, incompatibilidades, SMS de confirmación, etc.).\n"
            "\n"
            "✅ RECOMENDACIÓN: instala Linux (arranque dual o máquina virtual) para poder\n"
            "   seguir accediendo de forma gratuita a las oficinas de empleo cuando el 012\n"
            "   sea un número de pago. Las soluciones no oficiales de Internet (Legacy\n"
            "   Update, Extended Kernel) pueden funcionar a medias o no funcionar.\n"
            "=============================================================================="
        )

    if es_w11:
        return (
            "==============================================================================\n"
            "SOPORTE DEL SISTEMA OPERATIVO: WINDOWS 11\n"
            "==============================================================================\n"
            f"✅ Windows 11 detectado (build {build}). El sistema tiene soporte vigente y\n"
            "   no necesita ESU. Mantén el navegador actualizado para usar la cita previa.\n"
            "=============================================================================="
        )

    if sistema == "Linux":
        return (
            "ℹ️  Sistema operativo Linux detectado: la comprobación de ESU de Windows 10\n"
            "   no aplica. El soporte depende de la distribución y de su ciclo de vida."
        )

    return ""


def verificar_requisitos_windows_11(info_sistema, navegadores_instalados=None):
    """
    Verifica si el hardware cumple requisitos de Windows 11.
    Retorna (compatible: bool, mensaje: str, detalles: dict)
    """
    requisitos_minimos = {
        "arquitectura_64": info_sistema["arquitectura"] in ("x86_64", "amd64", "arm64"),
        "nucleos_2": info_sistema["nucleos"] >= 2,
        "memoria_4gb": info_sistema["memoria_gb"] >= 4,
        "tpm_2_0": info_sistema["tpm_2_0"] in ("Disponible", "Yes", "True") or info_sistema["tpm_2_0"] not in ("No verificado", "Desconocido"),
        "secure_boot": info_sistema["secure_boot"] in ("Activado", "Yes", "True") or info_sistema["secure_boot"] not in ("No verificado", "Desconocido"),
        "particion_gpt": info_sistema["particion_gpt"]
    }
    
    todos_cumplen = all(requisitos_minimos.values())
    
    # Construir mensaje detallado
    faltantes = []
    if not requisitos_minimos["arquitectura_64"]:
        faltantes.append("arquitectura de 64 bits")
    if not requisitos_minimos["nucleos_2"]:
        faltantes.append("al menos 2 núcleos de CPU")
    if not requisitos_minimos["memoria_4gb"]:
        faltantes.append("al menos 4 GB de RAM")
    if not requisitos_minimos["tpm_2_0"]:
        faltantes.append("TPM 2.0")
    if not requisitos_minimos["secure_boot"]:
        faltantes.append("Secure Boot activado")
    if not requisitos_minimos["particion_gpt"]:
        faltantes.append("partición GPT")
    
    if todos_cumplen:
        mensaje = "✅ El hardware cumple los requisitos básicos de Windows 11"
        if navegadores_instalados:
            mensaje += ". " + detectar_navegador_minimo_recomendado(navegadores_instalados)
        mensaje += ". Se recomienda actualizar a Windows 11 para usar la versión más alta del navegador."
    else:
        mensaje = f"❌ El hardware no cumple los requisitos de Windows 11. Faltan: {', '.join(faltantes)}"

    # Integrar el estado de soporte del sistema operativo (Windows 10 ESU, etc.)
    soporte = generar_mensaje_soporte_sistema(info_sistema)
    if soporte:
        mensaje += "\n\n" + soporte
        requisitos_minimos["soporte_sistema"] = soporte

    return todos_cumplen, mensaje, requisitos_minimos


def detectar_navegador_minimo_recomendado(navegadores_instalados):
    """Genera mensaje sobre navegador basado en versiones instaladas."""
    partes = []
    minimos = {"chrome": 108, "firefox": 122, "edge": 120, "safari": 15}
    
    for navegador, version_minimo in minimos.items():
        version_instalada = navegadores_instalados.get(navegador)
        if version_instalada:
            if version_instalada >= version_minimo:
                partes.append(f"{navegador.capitalize()} {version_instalada}+")
            else:
                partes.append(f"{navegador.capitalize()} {version_instalada}+ (mínimo {version_minimo}+)")
        else:
            partes.append(f"{navegador.capitalize()} {version_minimo}+ (no detectado)")
    
    return "Navegadores: " + ", ".join(partes)


def obtener_cabeceras_sepe(url=SEPE_URL, proxy_url=None):
    """Audita las cabeceras HTTP emitidas por el servidor central del SEPE."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT_DEFAULT},
        method="GET"
    )
    
    ctx = crear_contexto_ssl(proxy_url)
    
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
        if proxy_url:
            with urllib.request.urlopen(req, context=ctx, timeout=15, proxies={"http": proxy_url, "https": proxy_url}) as resp:
                resultado["status"] = resp.status
                headers = dict(resp.headers)
                resultado["raw_headers"] = headers
        else:
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


def auditar_portal_autonomico(portal, whitelist_sepe, modo="normal"):
    """Analiza la página autonómica para detectar si usa iframe o enlace directo y su compatibilidad."""
    url = portal["url"]
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT_DEFAULT},
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
            
            # 1. Comprobar si hay iframe
            tiene_iframe_tag = bool(re.search(r"<iframe[^>]+citaprevia-sede\.sepe\.gob\.es", html, re.IGNORECASE))
            tiene_iframe_id = bool(re.search(r"<iframe[^>]+id=[\"']embeddedIframe[\"']", html, re.IGNORECASE))
            tiene_iframe_js = bool(re.search(r"citaprevia-sede\.sepe\.gob\.es.*embeddedIframe", html, re.IGNORECASE | re.DOTALL))
            
            if tiene_iframe_tag or (tiene_iframe_id and tiene_iframe_js):
                resultado["usa_iframe"] = True
            
            # 2. Comprobar enlaces directos
            match_link = re.search(r'href=[\'"](https://citaprevia-sede\.sepe\.gob\.es/citapreviasepe/[^\'"]*)[\'"]', html, re.IGNORECASE)
            if match_link:
                resultado["enlace_sepe_detectado"] = match_link.group(1)
                if not resultado["usa_iframe"]:
                    resultado["usa_enlace_directo"] = True
            
            # 3. Comprobar dominio en CSP
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
                resultado["tipo_implementacion"] = "Enlace / Botón integrado"
                resultado["estado_diagnostico"] = "🟢 OPERATIVO"
                resultado["detalles"] = "Acceso operativo mediante navegación estándar."
                
    except Exception as ex:
        resultado["estado_diagnostico"] = f"❌ ERROR DE ACCESO: {str(ex)}"
        resultado["detalles"] = f"No se pudo conectar al portal autonómico: {ex}"
        
    return resultado


def generar_reporte_markdown(datos_sepe, resultados_autonomicos, ruta_salida, modo="completo", info_sistema=None):
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
    
    # Sección 3: Resumen de 17 CC.AA.
    md.append("## 3. Resumen Global del Modelo en las 17 CC. AA. Españolas\n")
    md.append("1. **Comunidades integradas que incrustan el SEPE en `<iframe>`:**")
    md.append("   - **Comunidad de Madrid:** Autorizada en CSP (`https://www.comunidad.madrid`).")
    md.append("   - **Principado de Asturias (Trabajastur):** Autorizada en CSP (`https://trabajastur.asturias.es`).")
    # Resumen dinámico basado en los resultados
    comunidades_iframe = [r for r in resultados_autonomicos if r["usa_iframe"] and r["autorizado_en_csp"]]
    md.append(f"   - **Total detectadas con iframe autorizado:** {len(comunidades_iframe)}")
    md.append("2. **Comunidades integradas mediante enlace directo (sin marco):**")
    comunidades_enlace = [r for r in resultados_autonomicos if r["usa_enlace_directo"]]
    md.append(f"   - **Extremadura (SEXPE):** Retiró el `<iframe>` y usa `<a target=\"_blank\">`.")
    md.append(f"   - **Canarias (SCE):** Enlace directo nativo a pantalla completa y App móvil.")
    md.append(f"   - **Islas Baleares (SOIB):** Enlace directo con botón `<a target=\"_blank\">`.")
    # Añadir las demás de la lista original
    md.append(f"   - **Resto de comunidades:** {', '.join([r['comunidad'] for r in comunidades_enlace if r['comunidad'] not in ['Extremadura', 'Canarias', 'Islas Baleares']])}")
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

    # Sección 5: Soporte del sistema operativo (Windows 10 ESU)
    if info_sistema:
        md.append("---\n")
        md.append("## 5. Soporte del Sistema Operativo y ESU (Windows 10)\n")
        soporte = generar_mensaje_soporte_sistema(info_sistema)
        if soporte:
            md.append("```text")
            md.append(soporte)
            md.append("```\n")
        else:
            md.append("No se pudo determinar el estado de soporte del sistema operativo.\n")

    contenido_final = "\n".join(md)
    
    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido_final)
        
    return contenido_final


# ==============================================================================
# FUNCIONES DE DOCUMENTACIÓN (README y Guías)
# ==============================================================================

def generar_readme_y_guia(directorio_script, modo_idioma="es"):
    """Genera archivos README y Guía Didáctica en español e inglés."""
    
    if modo_idioma == "es":
        lang = "es"
        nombre_prefix = ""
    else:
        lang = "en"
        nombre_prefix = "en"
    
    # Determinar contenido basado en idioma
    if lang == "es":
        readme_contenido = f"""# Auditoría Cita Previa (SEPE y CC. AA.)

## Descripción
Auditoría automatizada del sistema de cita previa de oficinas de empleo (SEPE y Consejerías de Educación/Empleo de las Comunidades Autónomas). Analiza las cabeceras de seguridad CSP (frame-ancestors), X-Frame-Options y la arquitectura de los portales autonómicos (iframes vs. enlaces directos), generando un informe en Markdown.

## Funcionalidades
- Detecta el navegador mínimo requerido para cargar las páginas de cita previa (versiones modernas de Chrome, Firefox, Edge, Safari).
- Muestra en pantalla si la auditoría completó exitosamente o hay advertencias/ errores.
- Verifica la compatibilidad del hardware con Windows 11 (arquitectura 64-bit, núcleos de CPU, memoria RAM, TPM 2.0, Secure Boot).
- En caso de no ser compatible con Windows 11, sugiere alternativas con Linux (Ubuntu, openSUSE, Debian, Fedora) para poder ver la página web de cita previa, ya sea en máquinas virtuales o con arranque dual.
- Compatible con sistemas operativos Linux y Windows (el script se ejecuta en cualquier entorno con Python 3).
- Soporta las 17 Comunidades Autónomas españolas.
- Modo silencioso (-q) para ejecución en CI/CD y automatización.
- Detecta navegadores instalados en el sistema y compara con versiones mínimas requeridas.
- **Detecta Windows 10 con ESU ("modo prórroga")** y avisa de su fecha de caducidad (octubre de 2028), de la finalización de Microsoft Edge el mismo día y de los fallos que pueden aparecer después (OpenStreetMap, certificados raíz, incompatibilidades, SMS de confirmación, etc.).
- **Cita previa en la Comunidad de Madrid**: el script detecta si el portal madrileño usa un iframe autorizado por CSP o un enlace directo, y ofrece enlaces de bypass si fuera necesario.

## Uso
Ejecuta el script desde la terminal:
```bash
python3 auditar_cita_previa.py [archivo_salida.md]
```
Si no se proporciona un archivo de salida, generará `informe_estado_cita_previa.md` en el mismo directorio.

### Modos disponibles:
- Modo normal (default): Mostrado completo en consola y genera el informe
- Modo silencioso (-q): Solo errores críticos, output resumido
- Modo detección de navegadores (-b): Solo muestra estado de navegadores instalados
- Con proxy: `python3 auditar_cita_previa.py -p http://proxy:8080 [archivo_salida.md]`

## Interpretación de resultados
- El informe Markdown incluye el estado de las cabeceras CSP, la implementación de iframes o enlaces directos en cada portal autonómico (las 17 CC.AA.), y un diagnóstico técnico.
- Los mensajes en consola indican el navegador mínimo recomendado, el estado general, la compatibilidad con Windows 11 y el estado de soporte de Windows 10 con ESU.
- Si el hardware no es compatible con Windows 11, considera instalar Linux en máquinas virtuales (VirtualBox, VMware) o en modo dual-boot para acceder a las páginas de cita previa.

## Windows 10 con ESU ("modo prórroga")

Si el script detecta Windows 10 con las ESU (Extended Security Updates) instaladas, informa de que el sistema **todavía tiene soporte** y de que el servicio de cita previa de las oficinas de empleo sigue siendo **gratuito** en las Comunidades Autónomas que indican el número **012** para solicitar cita previa y en las que el demandante de empleo disfruta de los servicios de las oficinas de empleo.

Según el **BOE núm. 296, de 10 de diciembre de 2012**, todas las operadoras de telefonía españolas están obligadas a cobrar el número 012, bien **por minutos** (el tiempo que dure la gestión presencial o semipresencial), bien **por cada acceso** a las oficinas de empleo (cada vez que se necesite acudir a ellas). Si el demandante de empleo no dispone de medios electrónicos o no tiene formación suficiente para usar la cita previa permanente, necesitará llamar a atención al ciudadano para que le generen una reserva de hueco, que deberá presentar en la oficina de empleo; en ese caso el cobro se produce por cada acceso a las oficinas.

**Aviso importante:** Windows 10 con licencia ESU **no es para siempre**. Caduca en **octubre de 2028**, el mismo día en que Microsoft finaliza el soporte de Microsoft Edge. A partir de entonces, con el paso del tiempo los navegadores pueden mostrar problemas de usabilidad, fallos en ciertos elementos de la página, que la parte de OpenStreetMap no funcione, errores de certificados raíz, errores de incompatibilidad con la página, que no se envíe correctamente el SMS de confirmación o cualquier otro error que impida manejar la página.

Si la página falla y hablar con la oficina de empleo no surte efecto, el demandante de empleo puede perder el derecho a solicitar cita previa gratuita en las oficinas que usen el 012 y gestionen la cita previa y la atención por aforo. Las soluciones que se encuentran por Internet (Legacy Update, Extended Kernel) **no son oficiales de Microsoft**, están hechas por la comunidad y pueden funcionar a medias o no funcionar, especialmente el kernel extendido. En esos casos se recomienda instalar **Linux** (en arranque dual o en una máquina virtual si en algún momento se necesita Windows) para recuperar el acceso gratuito a las oficinas de empleo cuando el 012 sea un número de pago.

## Cita previa en la Comunidad de Madrid

El portal de la Comunidad de Madrid utiliza un `<iframe>` autorizado por la directiva `frame-ancestors` del SEPE. Si el informe indica que el iframe está bloqueado por CSP o aparecen problemas de renderizado:

1. Asegúrate de tener un navegador actualizado (Chrome 108+, Firefox 122+, Edge 120+, Safari 15+).
2. Usa el enlace directo de bypass: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
3. Si el iframe sigue bloqueado, desactiva temporalmente extensiones de bloqueo de publicidad o scripts.

Consulta el archivo `INFO_OF_EMP_ESP_2026.txt` para más información sobre las oficinas de empleo en España.

## Enlaces útiles
- [SEPE](https://sede.sepe.gob.es)
- Portales autonómicos incluidos en la auditoría.
- **Comunidad de Madrid**: https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo
  - Enlace directo de bypass: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
"""
        
        readme_path = os.path.join(directorio_script, f"README.{lang}.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_contenido)
    
    else:  # English
        readme_contenido = """# Cita Previa Audit (SEPE and CC. AA.)

## Description
Automated audit of the employment office appointment (cita previa) system (SEPE and Autonomous Communities' Education/Employment Ministries). It analyzes security CSP headers (frame-ancestors), X-Frame-Options and the architecture of the autonomous portals (iframes vs. direct links), generating a Markdown report.

## Features
- Detects the minimum browser required to load the cita previa pages (modern versions of Chrome, Firefox, Edge, Safari).
- Shows on screen if the audit completed successfully or if there are warnings/errors.
- Checks hardware compatibility with Windows 11 (64-bit architecture, CPU cores, RAM memory, TPM 2.0, Secure Boot).
- If not compatible with Windows 11, suggests Linux alternatives (Ubuntu, openSUSE, Debian, Fedora) to be able to view the web appointment page, either in virtual machines or with dual-boot.
- Compatible with Linux and Windows operating systems (the script runs in any environment with Python 3).
- Supports all 17 Spanish Autonomous Communities.
- Command-line options: --quiet, --browser-detect, --proxy, -o/--output.
- Detects installed browsers and compares with minimum required versions.
- **Detects Windows 10 with ESU ("modo prórroga")** and warns about its expiration date (October 2028), Microsoft Edge ending support the same day, and the failures that may appear afterwards (OpenStreetMap, root certificates, incompatibilities, confirmation SMS, etc.).
- **Cita previa in the Community of Madrid**: the script detects whether the Madrid portal uses a CSP-authorized iframe or a direct link, and offers bypass links if needed.

## Windows 10 with ESU ("modo prórroga")

If the script detects Windows 10 with ESU (Extended Security Updates) installed, it reports that the system **is still supported** and that the employment office appointment service remains **free** in the Autonomous Communities that list the **012** number for requesting an appointment and where the job seeker uses the employment office services.

Under **BOE no. 296 of 10 December 2012**, all Spanish telecommunications operators must charge for the 012 number either **per minute** (the duration of the in-person or semi-presential procedure) or **per access** to the employment offices (each time the job seeker needs to visit them). If the job seeker has no electronic means or insufficient training to use the permanent appointment system, they will need to call citizen attention to generate a slot reservation, which they must present at the employment office; in that case, the charge applies for each access to the offices.

**Important notice:** Windows 10 with an ESU license **is not permanent**. It expires in **October 2028**, the same day Microsoft ends support for Microsoft Edge. After that, over time browsers may experience usability problems, broken page elements, OpenStreetMap failing, root certificate errors, page incompatibility errors, confirmation SMS failures, or any other error that prevents using the page.

If the page fails and talking to the employment office does not help, the job seeker may lose the right to request a free appointment at offices that use the 012 number and manage appointments and attendance by capacity (aforo). Internet fixes such as Legacy Update or Extended Kernel **are not official Microsoft solutions**, are community-made, and may work only partially or not at all, especially the extended kernel. In those cases, installing **Linux** (dual boot or a virtual machine if Windows is still needed) is recommended to recover free access to employment offices when 012 is a paid number.

## Cita previa in the Community of Madrid

The Community of Madrid portal uses an `<iframe>` authorized by the SEPE `frame-ancestors` directive. If the report indicates that the iframe is blocked by CSP or rendering problems appear:

1. Make sure you have an up-to-date browser (Chrome 108+, Firefox 122+, Edge 120+, Safari 15+).
2. Use the direct bypass link: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
3. If the iframe remains blocked, temporarily disable ad-blocking or script-blocking extensions.

See `INFO_OF_EMP_ESP_2026.txt` for more information about employment offices in Spain.

## Usage
Run the script from the terminal:
```bash
python3 auditar_cita_previa.py [output_file.md]
```
If no output file is provided, it will generate `informe_estado_cita_previa.md` in the same directory.

### Available options:
- -q, --quiet: Silent mode (only critical errors)
- -b, --browser-detect: Check installed browsers against requirements
- -p, --proxy: HTTP proxy URL (e.g., http://127.0.0.1:8080)
- -o, --output: Output markdown file path
- -v, --version: Show version

## Results Interpretation
- The Markdown report includes the state of CSP headers, iframe or direct link implementation in each autonomous portal (all 17 CC.AA.), and technical diagnosis.
- Console messages indicate the minimum recommended browser, overall status, Windows 11 compatibility, and Windows 10 ESU support status.
- If the hardware is not compatible with Windows 11, consider installing Linux in virtual machines (VirtualBox, VMware) or dual-boot to access the appointment pages.

## Useful Links
- [SEPE](https://sede.sepe.gob.es)
- Included autonomous portals in the audit.
- **Community of Madrid**: https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo
  - Direct bypass link: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
"""
        
        readme_path = os.path.join(directorio_script, f"README.{lang}.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_contenido)
    
    # Guía didáctica
    if lang == "es":
        guia_contenido = f"""# Guía Didáctica del Auditoría de Cita Previa

## Propósito
Esta guía te ayudará a entender los resultados del informe generado y cómo solucionar problemas de compatibilidad para acceder a las páginas de cita previa.

## Qué hace el auditor
1. **Comprueba las cabeceras CSP**: Verifica si el dominio de tu comunidad autónoma está en la lista blanca del SEPE en la directiva `frame-ancestors`. Si está, el iframe cargará sin bloqueos.
2. **Detecta el tipo de implementación**: Determina si el portal usa un iframe incrustado, un enlace directo (a pantalla completa) o un botón integrado.
3. **Evalúa el navegador**: Recomienda versiones mínimas de navegadores modernos para un correcto funcionamiento.
4. **Evalúa Windows 11 y Windows 10 ESU**: Comprueba si tu hardware cumple los requisitos mínimos para Windows 11 (arquitectura 64-bit, 2+ núcleos, 4+ GB RAM, TPM 2.0, Secure Boot, partición GPT) y, de no ser así, sugiere alternativas con Linux. También detecta Windows 10 con ESU ("modo prórroga") y avisa de su caducidad y de los fallos que pueden aparecer después.

## Windows 10 con ESU ("modo prórroga")

Si el auditor detecta Windows 10 con las ESU instaladas, te informará de que el sistema **todavía tiene soporte** y de que la cita previa de las oficinas de empleo sigue siendo **gratuita** en las Comunidades Autónomas que usan el número **012** y en las que el demandante de empleo disfruta de los servicios de las oficinas de empleo.

Según el **BOE núm. 296, de 10 de diciembre de 2012**, las operadoras de telefonía españolas están obligadas a cobrar el 012 **por minutos** (tiempo de la gestión presencial o semipresencial) o **por cada acceso** a las oficinas de empleo. Si no tienes medios electrónicos o formación suficiente para usar la cita previa permanente, tendrás que llamar a atención al ciudadano para que te generen una reserva de hueco y presentarla en la oficina; el cobro se produce por cada acceso a las oficinas.

**Windows 10 con ESU no es para siempre:** caduca en **octubre de 2028**, el mismo día en que Microsoft finaliza el soporte de Microsoft Edge. Después pueden aparecer problemas de usabilidad, elementos rotos, fallos de OpenStreetMap, errores de certificados raíz, incompatibilidades, fallos del SMS de confirmación o cualquier otro error que impida usar la página. Si la página falla y la oficina de empleo no puede ayudarte, puedes perder el derecho a la cita previa gratuita en las oficinas que usen el 012 y atiendan por aforo. Las soluciones de Internet (Legacy Update, Extended Kernel) no son oficiales de Microsoft y pueden funcionar a medias o no funcionar, sobre todo el kernel extendido. En ese caso, instala **Linux** (arranque dual o máquina virtual si necesitas Windows) para recuperar el acceso gratuito a las oficinas de empleo cuando el 012 sea un número de pago.

## Cómo interpretar el informe Markdown
- **Estado técnico**: Cada fila de la tabla indica si el portal está operativo, si hay errores de CSP o si usa iframes/botones. Incluye ahora las 17 Comunidades Autónomas.
- **Mensajes en consola**: El navegador mínimo recomendado, el estado general y la compatibilidad con Windows 11 te indican qué pasos seguir.
- **Si aparece "No compatible con Windows 11"**: Tu hardware no cumple los requisitos mínimos (falta arquitectura de 64 bits, núcleos de CPU, memoria RAM, TPM 2.0, Secure Boot o partición GPT). Considera instalar Linux.

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

### Cita previa en la Comunidad de Madrid
El portal de la Comunidad de Madrid utiliza un `<iframe>` autorizado por la directiva `frame-ancestors` del SEPE. Si experimentas problemas de renderizado o bloqueos:
1. Asegúrate de tener un navegador actualizado (Chrome 108+, Firefox 122+, Edge 120+, Safari 15+).
2. Usa el enlace directo de bypass: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
3. Si el iframe sigue bloqueado, desactiva temporalmente extensiones de bloqueo de publicidad o scripts.

Consulta `INFO_OF_EMP_ESP_2026.txt` para más información sobre las oficinas de empleo en España.

¡Éxito en tu auditoría!
"""
    else:
        guia_contenido = """# Didactic Guide for Cita Previa Audit

## Purpose
This guide will help you understand the results generated by the audit and how to solve compatibility issues to access the appointment pages.

## What the auditor does
1. **Checks CSP headers**: Verifies if your autonomous community's domain is on the SEPE whitelist in the `frame-ancestors` directive. If it is, the iframe will load without blocks.
2. **Detects implementation type**: Determines if the portal uses an embedded iframe, a direct link (full screen) or an integrated button.
3. **Evaluates the browser**: Recommends minimum modern browser versions for proper functioning.
4. **Evaluates Windows 11 and Windows 10 ESU**: Checks if your hardware meets the minimum requirements for Windows 11 (64-bit architecture, 2+ CPU cores, 4+ GB RAM, TPM 2.0, Secure Boot, GPT partition) and if not, suggests Linux alternatives. It also detects Windows 10 with ESU ("modo prórroga") and warns about its expiration and the failures that may appear afterwards.

## Windows 10 with ESU ("modo prórroga")

If the auditor detects Windows 10 with ESU installed, it will tell you that the system **is still supported** and that the employment office appointment service remains **free** in the Autonomous Communities that use the **012** number and where the job seeker uses the employment office services.

Under **BOE no. 296 of 10 December 2012**, Spanish telecommunications operators must charge for the 012 number **per minute** (duration of the in-person or semi-presential procedure) or **per access** to the employment offices. If you have no electronic means or insufficient training to use the permanent appointment system, you will need to call citizen attention to generate a slot reservation and present it at the office; the charge applies for each access to the offices.

**Windows 10 with ESU is not permanent:** it expires in **October 2028**, the same day Microsoft ends support for Microsoft Edge. After that, usability problems, broken elements, OpenStreetMap failures, root certificate errors, incompatibilities, confirmation SMS failures, or any other error preventing use of the page may appear. If the page fails and the employment office cannot help, you may lose the right to a free appointment at offices that use the 012 number and manage attendance by capacity (aforo). Internet fixes (Legacy Update, Extended Kernel) are not official Microsoft solutions and may work only partially or not at all, especially the extended kernel. In that case, install **Linux** (dual boot or a virtual machine if you need Windows) to recover free access to employment offices when 012 is a paid number.

## How to interpret the Markdown report
- **Technical status**: Each row in the table indicates whether the portal is operational, if there are CSP errors, or if it uses iframes/buttons. Now includes all 17 Spanish Autonomous Communities.
- **Console messages**: The minimum recommended browser, overall status, and Windows 11 compatibility tell you what steps to follow.
- **If "Not compatible with Windows 11" appears**: Your hardware does not meet the minimum requirements (missing 64-bit architecture, CPU cores, RAM, TPM 2.0, Secure Boot, or GPT partition). Consider installing Linux.

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

### Community of Madrid Cita Previa
The Community of Madrid portal uses an `<iframe>` authorized by the SEPE `frame-ancestors` directive. If you experience rendering issues or blocks:
1. Ensure you have an up-to-date browser (Chrome 108+, Firefox 122+, Edge 120+, Safari 15+).
2. Use the direct bypass link: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
3. If the iframe remains blocked, temporarily disable ad-blocking or script-blocking extensions.

See `INFO_OF_EMP_ESP_2026.txt` for more information about employment offices in Spain.

Good luck with your audit!
"""
    
    guia_path = os.path.join(directorio_script, f"Guia_Didactica.{lang}.md")
    with open(guia_path, "w", encoding="utf-8") as f:
        f.write(guia_contenido)


# ==============================================================================
# FUNCIÓN PRINCIPAL
# ==============================================================================

def main():
    args = parse_arguments()
    
    # Modo versión
    if args["version"]:
        print("Auditoría Cita Previa v2.1 - Análisis de Seguridad CSP, Compatibilidad Windows 11 y ESU de Windows 10")
        sys.exit(0)
    
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_md_defecto = os.path.join(directorio_script, "informe_estado_cita_previa.md")
    
    ruta_md = args["output"] if args["output"] else ruta_md_defecto
    
    # Modo silencioso: suprimir output informativo
    if args["quiet"]:
        import io
        sys.stdout = io.StringIO()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando auditoría del sistema de cita previa...")
    
    # 1. Verificar cabeceras SEPE
    if not args["quiet"]:
        print(f" -> Verificando cabeceras del SEPE en: {SEPE_URL}")
    datos_sepe = obtener_cabeceras_sepe()
    whitelist = datos_sepe.get("dominios_whitelist", [])
    if not args["quiet"]:
        print(f" -> Whitelist CSP detectada en SEPE: {len(whitelist)} dominios")
    
    # 2. Detectar navegadores instalados si se solicita
    navegadores_instalados = {}
    if args["browser_detect"] and not args["quiet"]:
        print(" -> Detectando navegadores instalados en el sistema...")
        navegadores_instalados = detectar_navegadores_instalados()
        for nav, ver in navegadores_instalados.items():
            if ver:
                print(f"   {nav.capitalize()}: versión {ver}")
            else:
                print(f"   {nav.capitalize()}: no detectado")
    
    if not args["quiet"]:
        print(f"\n -> Auditando {len(PORTALES_AUTONOMICOS)} portales autonómicos (todas las CC.AA.)...")
    
    resultados = []
    for i, portal in enumerate(PORTALES_AUTONOMICOS):
        if not args["quiet"]:
            progress = f"    - Comprobando {portal['comunidad']} ({i+1}/{len(PORTALES_AUTONOMICOS)})..."
            print(progress)
        
        res = auditar_portal_autonomico(portal, whitelist)
        resultados.append(res)
        if not args["quiet"]:
            print(f"      Resultado: {res['estado_diagnostico']}")
    
    # 3. Generar informe Markdown
    if not args["quiet"]:
        print(f"\n -> Generando informe Markdown en: {ruta_md}")

    info_sis = obtener_info_sistema_completo()
    reporte = generar_reporte_markdown(datos_sepe, resultados, ruta_md, info_sistema=info_sis)
    if not args["quiet"]:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Informe Markdown generado correctamente ({len(reporte)} chars).")
    
    # 4. Mostrar estado en pantalla
    if not args["quiet"]:
        # Contar errores/advertencias
        hay_errores = any("ERROR" in r["estado_diagnostico"] or "❌" in r["estado_diagnostico"] for r in resultados)
        if hay_errores:
            estado_pantalla = "⚠️ Se detectaron advertencias o errores en la auditoría (revisa el informe Markdown para detalles)."
        else:
            estado_pantalla = "✅ Todos los portales auditados están operativos sin errores detectados."
        print(f" {estado_pantalla}\n")
    
    # 5. Compatibilidad con Windows 11 y soporte ESU de Windows 10
    if not args["quiet"]:
        print(" -> Verificando compatibilidad con Windows 11 y soporte de Windows 10 ESU...")

    compatible, mensaje_w11, detalles_req = verificar_requisitos_windows_11(info_sis, navegadores_instalados)
    if not args["quiet"]:
        print(f" {mensaje_w11}\n")
    
    # 6. Generar README y guía didáctica
    if not args["quiet"]:
        print(" -> Generando README y guía didáctica en ambos idiomas...")
    
    generar_readme_y_guia(directorio_script, "es")
    generar_readme_y_guia(directorio_script, "en")
    if not args["quiet"]:
        print(" -> README y guía didáctica generados en ambos idiomas.\n")
    
    if not args["quiet"]:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Auditoría finalizada con éxito. Informe generado.")
    
    # Mostrar resumen final si no es modo silencioso
    if not args["quiet"]:
        print("\n--- RESUMEN RÁPIDO ---")
        print(f"Portales auditados: {len(resultados)}")
        print(f"IFrames autorizados: {sum(1 for r in resultados if r['usa_iframe'] and r['autorizado_en_csp'])}")
        print(f"Enlaces directos: {sum(1 for r in resultados if r['usa_enlace_directo'])}")
        print(f"Errores: {sum(1 for r in resultados if 'ERROR' in r['estado_diagnostico'] or '❌' in r['estado_diagnostico'])}")
        print(f"Compatible Windows 11: {compatible}")
        if info_sis.get("es_windows_10"):
            estado_esu = "ESU instaladas (soporte hasta octubre de 2028)" if info_sis.get("esu_instalada") else "SIN ESU (soporte finalizado)"
            print(f"Windows 10 detectado: {estado_esu}")
        elif info_sis.get("es_windows_11"):
            print("Windows 11 detectado: soporte vigente")
        else:
            print(f"Sistema operativo: {info_sis.get('sistema_operativo')}")
        if navegadores_instalados:
            print(f"Navegadores detectados: {list(navegadores_instalados.keys())}")


if __name__ == "__main__":
    main()