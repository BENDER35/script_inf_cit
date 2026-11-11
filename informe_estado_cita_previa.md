# Informe de Auditoría: Estado de Cita Previa de Empleo (SEPE y CC. AA.)

> **Auditoría generada automáticamente el:** 11/11/2026 a las 20:23:07 CEST

Este informe analiza el estado de las directivas de seguridad web del Servicio Público de Empleo Estatal (SEPE) y la compatibilidad con los portales autonómicos de cita previa de empleo.

---

## 1. Estado del Servidor Central del SEPE (`citaprevia-sede.sepe.gob.es`)

* **Código HTTP:** `200`
* **X-Frame-Options:** `SAMEORIGIN`
* **Strict-Transport-Security (HSTS):** `max-age=31536000; includeSubDomains; preload`

### Directiva `Content-Security-Policy: frame-ancestors` (Lista Blanca):
```http
frame-ancestors 'self' https://sede.sepe.gob.es https://inaem.aragon.es https://www.comunidad.madrid https://empleacantabria.es https://sede.gobiernodecanarias.org https://trabajastur.asturias.es https://soib.es;
```

**Dominios autonómicos expresamente autorizados en el SEPE:**
- `https://sede.sepe.gob.es`
- `https://inaem.aragon.es`
- `https://www.comunidad.madrid`
- `https://empleacantabria.es`
- `https://sede.gobiernodecanarias.org`
- `https://trabajastur.asturias.es`
- `https://soib.es`

---

## 2. Estado de los Portales Autonómicos Auditados

| Comunidad Autónoma | Servicio / Portal | Tipo de Implementación | En Lista Blanca SEPE | Estado Técnico |
| :--- | :--- | :--- | :---: | :--- |
| **Comunidad de Madrid** | [Oficinas de Empleo Madrid](https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo) | Marco incrustado (<iframe>) | 🟢 Sí | 🟢 OPERATIVO (Iframe Autorizado por CSP) |
| **Principado de Asturias** | [Trabajastur (SEPEPA)](https://trabajastur.asturias.es/cita_previa) | Enlace / Botón integrado | 🟢 Sí | 🟢 OPERATIVO |
| **Extremadura** | [SEXPE](https://sexpeemplea.juntaex.es/inicio_cita_previa) | Enlace directo externo (sin marco) | ⚪ N/A | 🟢 OPERATIVO (Enlace Directo fuera de marco) |
| **Canarias** | [Servicio Canario de Empleo (SCE)](https://www.gobiernodecanarias.org/empleo/sce/) | Enlace directo externo (sin marco) | 🟢 Sí | 🟢 OPERATIVO (Enlace Directo fuera de marco) |
| **Islas Baleares** | [SOIB](https://soib.es/citaprevia/) | Enlace directo externo (sin marco) | 🟢 Sí | 🟢 OPERATIVO (Enlace Directo fuera de marco) |
| **Andalucía** | [SAE](https://www.juntadeandalucia.es/empleo/y-trabajo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **Aragón** | [INAEM Aragón](https://www.aragon.es/empleo-y-formacion/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404:  |
| **Cantabria** | [EMCAN](https://www.cantabria.es/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **Castilla-La Mancha** | [Emplea CLM](https://www.jccm.es/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **Castilla y León** | [ECyL](https://www.encyclyldeempleo.com/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: <urlopen error [Errno -2] Name or service not known> |
| **Cataluña** | [SOC](https://soc.cat/ca/serveis/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: <urlopen error [Errno 104] Connection reset by peer> |
| **Galicia** | [Emprego Galicia](https://www.xunta.gal/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **La Rioja** | [Empleo La Rioja](https://www.larioja.org/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **Navarra** | [SNE-NL](https://www.navarra.es/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **País Vasco** | [Lanbide](https://lanbide.eus/empleo/y-formacion/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **Región de Murcia** | [SEF](https://www.murcia.es/empleo/y-formacion/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: No Encontrado |
| **Ceuta** | [SEPE Ceuta](https://www.ceuta.es/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |
| **Melilla** | [SEPE Melilla](https://www.melilla.es/empleo/cita-previa) | Desconocida | ⚪ N/A | ❌ ERROR DE ACCESO: HTTP Error 404: Not Found |

### Detalle por Comunidad Autónoma:

#### Comunidad de Madrid (Oficinas de Empleo Madrid)
- **URL auditada:** [https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo](https://www.comunidad.madrid/servicios/empleo/cita-previa-oficinas-empleo)
- **Implementación:** Marco incrustado (<iframe>)
- **Diagnóstico:** 🟢 OPERATIVO (Iframe Autorizado por CSP)
- **Detalle técnico:** El dominio https://www.comunidad.madrid está autorizado en la cabecera frame-ancestors del SEPE.
- **Enlace de destino SEPE:** `https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28`

#### Principado de Asturias (Trabajastur (SEPEPA))
- **URL auditada:** [https://trabajastur.asturias.es/cita_previa](https://trabajastur.asturias.es/cita_previa)
- **Implementación:** Enlace / Botón integrado
- **Diagnóstico:** 🟢 OPERATIVO
- **Detalle técnico:** Acceso operativo mediante navegación estándar.

#### Extremadura (SEXPE)
- **URL auditada:** [https://sexpeemplea.juntaex.es/inicio_cita_previa](https://sexpeemplea.juntaex.es/inicio_cita_previa)
- **Implementación:** Enlace directo externo (sin marco)
- **Diagnóstico:** 🟢 OPERATIVO (Enlace Directo fuera de marco)
- **Detalle técnico:** Abre el SEPE a pantalla completa en pestaña nueva. Inmune a bloqueos de iframe/CSP.
- **Enlace de destino SEPE:** `https://citaprevia-sede.sepe.gob.es/citapreviasepe/`

#### Canarias (Servicio Canario de Empleo (SCE))
- **URL auditada:** [https://www.gobiernodecanarias.org/empleo/sce/](https://www.gobiernodecanarias.org/empleo/sce/)
- **Implementación:** Enlace directo externo (sin marco)
- **Diagnóstico:** 🟢 OPERATIVO (Enlace Directo fuera de marco)
- **Detalle técnico:** Abre el SEPE a pantalla completa en pestaña nueva. Inmune a bloqueos de iframe/CSP.
- **Enlace de destino SEPE:** `https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SCE`

#### Islas Baleares (SOIB)
- **URL auditada:** [https://soib.es/citaprevia/](https://soib.es/citaprevia/)
- **Implementación:** Enlace directo externo (sin marco)
- **Diagnóstico:** 🟢 OPERATIVO (Enlace Directo fuera de marco)
- **Detalle técnico:** Abre el SEPE a pantalla completa en pestaña nueva. Inmune a bloqueos de iframe/CSP.
- **Enlace de destino SEPE:** `https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SOIB&#038;codidioma=ca`

#### Andalucía (SAE)
- **URL auditada:** [https://www.juntadeandalucia.es/empleo/y-trabajo/cita-previa](https://www.juntadeandalucia.es/empleo/y-trabajo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### Aragón (INAEM Aragón)
- **URL auditada:** [https://www.aragon.es/empleo-y-formacion/cita-previa](https://www.aragon.es/empleo-y-formacion/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: 
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: 

#### Cantabria (EMCAN)
- **URL auditada:** [https://www.cantabria.es/empleo/cita-previa](https://www.cantabria.es/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### Castilla-La Mancha (Emplea CLM)
- **URL auditada:** [https://www.jccm.es/empleo/cita-previa](https://www.jccm.es/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### Castilla y León (ECyL)
- **URL auditada:** [https://www.encyclyldeempleo.com/cita-previa](https://www.encyclyldeempleo.com/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: <urlopen error [Errno -2] Name or service not known>
- **Detalle técnico:** No se pudo conectar al portal autonómico: <urlopen error [Errno -2] Name or service not known>

#### Cataluña (SOC)
- **URL auditada:** [https://soc.cat/ca/serveis/empleo/cita-previa](https://soc.cat/ca/serveis/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: <urlopen error [Errno 104] Connection reset by peer>
- **Detalle técnico:** No se pudo conectar al portal autonómico: <urlopen error [Errno 104] Connection reset by peer>

#### Galicia (Emprego Galicia)
- **URL auditada:** [https://www.xunta.gal/empleo/cita-previa](https://www.xunta.gal/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### La Rioja (Empleo La Rioja)
- **URL auditada:** [https://www.larioja.org/empleo/cita-previa](https://www.larioja.org/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### Navarra (SNE-NL)
- **URL auditada:** [https://www.navarra.es/empleo/cita-previa](https://www.navarra.es/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### País Vasco (Lanbide)
- **URL auditada:** [https://lanbide.eus/empleo/y-formacion/cita-previa](https://lanbide.eus/empleo/y-formacion/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### Región de Murcia (SEF)
- **URL auditada:** [https://www.murcia.es/empleo/y-formacion/cita-previa](https://www.murcia.es/empleo/y-formacion/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: No Encontrado
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: No Encontrado

#### Ceuta (SEPE Ceuta)
- **URL auditada:** [https://www.ceuta.es/empleo/cita-previa](https://www.ceuta.es/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

#### Melilla (SEPE Melilla)
- **URL auditada:** [https://www.melilla.es/empleo/cita-previa](https://www.melilla.es/empleo/cita-previa)
- **Implementación:** Desconocida
- **Diagnóstico:** ❌ ERROR DE ACCESO: HTTP Error 404: Not Found
- **Detalle técnico:** No se pudo conectar al portal autonómico: HTTP Error 404: Not Found

---

## 3. Resumen Global del Modelo en las 17 CC. AA. Españolas

1. **Comunidades integradas que incrustan el SEPE en `<iframe>`:**
   - **Comunidad de Madrid:** Autorizada en CSP (`https://www.comunidad.madrid`).
   - **Principado de Asturias (Trabajastur):** Autorizada en CSP (`https://trabajastur.asturias.es`).
   - **Total detectadas con iframe autorizado:** 1
2. **Comunidades integradas mediante enlace directo (sin marco):**
   - **Extremadura (SEXPE):** Retiró el `<iframe>` y usa `<a target="_blank">`.
   - **Canarias (SCE):** Enlace directo nativo a pantalla completa y App móvil.
   - **Islas Baleares (SOIB):** Enlace directo con botón `<a target="_blank">`.
   - **Resto de comunidades:** 
3. **Comunidades con plataformas de cita previas propias (Inmunes al SEPE):**
   - Andalucía (SAE), Aragón (INAEM), Cantabria (EMCAN), Castilla-La Mancha (Emplea CLM), Castilla y León (ECyL), Cataluña (SOC), Comunitat Valenciana (LABORA), Galicia (Emprego Galicia), La Rioja, Navarra (SNE-NL), País Vasco (Lanbide), Región de Murcia (SEF), Ceuta y Melilla.

---

## 4. Enlaces Directos de Acceso Inmediato (Bypass)

Si algún marco autonómico sufriera problemas de renderizado en navegadores desactualizados, se recomienda acceder a través de estos enlaces directos a pantalla completa:

* [Cita Previa Comunidad de Madrid (origen=28)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=28)
* [Cita Previa Extremadura - SEXPE (origen=SEXPE)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/)
* [Cita Previa Asturias - Trabajastur (origen=SEPE)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SEPE&codidioma=es)
* [Cita Previa Canarias - SCE (origen=SCE)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SCE)
* [Cita Previa Baleares - SOIB (origen=SOIB)](https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=SOIB&codidioma=ca)
* [Sede Electrónica General del SEPE](https://sede.sepe.gob.es/portalSede/procedimientos-y-servicios/personas/proteccion-por-desempleo/cita-previa.html)

---

## 5. Soporte del Sistema Operativo y ESU (Windows 10)

```text
ℹ️  Sistema operativo Linux detectado: la comprobación de ESU de Windows 10
   no aplica. El soporte depende de la distribución y de su ciclo de vida.
```
