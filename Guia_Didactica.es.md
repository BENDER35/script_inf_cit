# Guía Didáctica del Auditoría de Cita Previa

## Propósito
Esta guía te ayudará a entender los resultados del informe generado y cómo solucionar problemas de compatibilidad para acceder a las páginas de cita previa.

## Qué hace el auditor
1. **Comprueba las cabeceras CSP**: Verifica si el dominio de tu comunidad autónoma está en la lista blanca del SEPE en la directiva `frame-ancestors`. Si está, el iframe cargará sin bloqueos.
2. **Detecta el tipo de implementación**: Determina si el portal usa un iframe incrustado, un enlace directo (a pantalla completa) o un botón integrado.
3. **Evalúa el navegador**: Recomienda versiones mínimas de navegadores modernos para un correcto funcionamiento.
4. **Evalúa Windows 11**: Comprueba si tu hardware cumple los requisitos mínimos para Windows 11 (arquitectura 64-bit, 2+ núcleos, 4+ GB RAM, TPM 2.0, Secure Boot, partición GPT) y, de no ser así, sugiere alternativas con Linux.

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
El portal de la Comunidad de Madrid utiliza un `<iframe>` autorizado por la directiva `frame-ancestors` del SEPE. Si experimentas problemas de renderizado o bloqueos, se recomienda:
1. Asegurar tener un navegador actualizado (Chrome 108+, Firefox 122+, Edge 120+, Safari 15+).
2. Usar el enlace directo de bypass: https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28
3. Si el iframe sigue bloqueado, desactivar temporalmente extensiones de bloqueo de publicidad o scripts.

¡Éxito en tu auditoría!
