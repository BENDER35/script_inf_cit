# Guía Didáctica del Auditoría de Cita Previa

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

**Windows 10 con ESU no es para siempre:** caduca en **octubre de 2028**, el mismo día en que Microsoft finaliza el soporte de Microsoft Edge. Después pueden aparecer problemas de usabilidad, elementos rotos, fallos de OpenStreetMap, errores de certificados raíz, incompatibilidades, fallos del SMS de confirmación o cualquier otro error que impida usar la página. Si la página falla y la oficina de empleo no puede ayudarte, puedes perder el derecho a la cita previa gratuita en las oficinas que usen el 012 y atiendan por aforo. Las soluciones de Internet (Legacy Update, Extended Kernel) no son oficiales de Microsoft y pueden funcionar a medias o no funcionar, sobre todo el kernel extendido. En ese caso, instala **Linux** (arranque dual o máquina virtual si necesitas Windows) para recuperar el **acceso gratuito por Internet a la cita previa** de las oficinas de empleo que indican el **012** como teléfono para sacar cita previa sin necesidad de acceder a Internet. Así evitas la llamada al 012, que según la ley española es un número corto de pago.

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
