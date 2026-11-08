# Auditoría Cita Previa (SEPE y CC. AA.)

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
- **Gestión de cita previa en la Comunidad de Madrid**: El script detecta si el portal madrileño usa iframe autorizado por CSP o enlace directo, y proporciona enlaces de bypass si es necesario.

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
- Los mensajes en consola indican el navegador mínimo recomendado, el estado general y la compatibilidad con Windows 11.
- **Para la Comunidad de Madrid**: Si el informe indica que el iframe está bloqueado por CSP, se recomienda usar los enlaces directos de bypass que aparecen en la sección 4 del informe, o acceder directamente a https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
- Si el hardware no es compatible con Windows 11, considera instalar Linux en máquinas virtuales (VirtualBox, VMware) o en modo dual-boot para acceder a las páginas de cita previa.

## Enlaces útiles
- [SEPE](https://sede.sepe.gob.es)
- Portales autonómicos incluidos en la auditoría.
- **Comunidad de Madrid**: https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo
  - Enlace directo de bypass: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
