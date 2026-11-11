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

Si la página falla y hablar con la oficina de empleo no surte efecto, el demandante de empleo puede perder el derecho a solicitar cita previa gratuita en las oficinas que usen el 012 y gestionen la cita previa y la atención por aforo. Las soluciones que se encuentran por Internet (Legacy Update, Extended Kernel) **no son oficiales de Microsoft**, están hechas por la comunidad y pueden funcionar a medias o no funcionar, especialmente el kernel extendido. En esos casos se recomienda instalar **Linux** (en arranque dual o en una máquina virtual si en algún momento se necesita Windows) para recuperar el **acceso gratuito por Internet a la cita previa** de las oficinas de empleo que indican el **012** como teléfono para sacar cita previa sin necesidad de acceder a Internet. Así se evita tener que llamar al 012, que según la ley española es un número corto de pago.

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
