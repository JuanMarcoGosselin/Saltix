# STX-SPRINT-3-REPORT-v2.0
### Reporte de Sprint 3 - Saltix

---

## 1. Informacion del Sprint

- **Numero de Sprint:** 3
- **Nombre del Sprint:** Gestion de Asistencias por Jefatura
- **Fechas objetivo:** 2026-04-06 al 2026-04-19
- **Fecha de actualizacion del reporte:** 2026-05-11
- **Version del documento:** 2.0
- **Proyecto:** Saltix - Sistema de Control de Asistencia y Calculo de Nomina

### Equipo

| Nombre | Rol |
|---|---|
| Ivan Ramos de la Torre | Team Leader / Backend |
| Juan Marco Gosselin Gamboa | DBA / Backend |
| Patricio Davila Assad | Backend |
| Diego Cristobal Gael Serna Dominguez | Frontend |
| Katherine Guadalupe Guareno Flores | Frontend / Design |

---

## 2. Objetivo del Sprint

Implementar el flujo operativo de jefatura para revisar asistencias, resolver incidencias y consultar solicitudes del profesorado sin alterar la arquitectura base del sistema.

En la revision v2.0 se alinea el reporte con el backlog vigente, especialmente con:

- **RF-03 - Justificacion de Incidencias**
- **RF-11 - Entidad Departamento**
- **RF-12 - Relacion Jerarquica**
- **RF-20 - Solicitud de Correccion**
- **RF-21 - Registro Manual Autorizado**
- **RF-22 - Flujo de Aprobacion**
- **RNF-01 - Control de Acceso por Roles**
- **RNF-03 - Bitacora de Auditoria**
- **RNF-04 - Inmutabilidad de Asistencia**

---

## 3. Cambios Implementados

### Backend

Se agregaron endpoints JSON en `Asistencias/views.py` para:

- listar asistencias para jefatura;
- listar incidencias para jefatura;
- aprobar incidencias;
- rechazar incidencias;
- cancelar asistencias institucionalmente;
- corregir asistencias con trazabilidad;
- listar incidencias del profesor autenticado.

La logica se organizo en servicios simples:

- `Asistencias/services/listados.py`
- `Asistencias/services/incidencias.py`

Tambien se agrego `Asistencias/utils.py` con helpers pequeños para profesor, fechas, paginacion y conversion simple a JSON.

### Incidencias y Correcciones

El flujo actualizado conserva la asistencia original intacta cuando se aprueba una incidencia:

1. El profesor crea una `Incidencia` en estado `PENDIENTE`.
2. Jefatura aprueba o rechaza la incidencia.
3. Si se aprueba, se crea una nueva asistencia `COMPENSATORIA`.
4. Se crea un registro `CorreccionAsistencia` que relaciona la asistencia original con la compensatoria.
5. La incidencia queda como `APROBADA`; la asistencia original no cambia de estado.
6. Si se rechaza, la incidencia queda como `RECHAZADA` y la falta original permanece sin cambios.

Este comportamiento reemplaza la lectura anterior de RF-03 donde la aprobacion convertia directamente la falta original en asistencia. La nueva interpretacion es consistente con **RNF-04 - Inmutabilidad de Asistencia**.

### Modelos y Migraciones

Se mantiene `CorreccionAsistencia` como relacion formal entre:

- `asistencia_original`
- `asistencia_compensatoria`
- `motivo`
- `aprobada_por`
- `fecha_aprobacion`

La migracion `Asistencias/0008_correccion_asistencia.py` retira relaciones duplicadas en `Asistencia` e `Incidencia`, dejando la compensacion documentada en el modelo dedicado.

### Frontend

Se conserva el dashboard de jefatura con:

- tabla de profesores del departamento;
- gestion de asistencias;
- gestion de solicitudes de justificacion;
- filtros por profesor, fecha y estado;
- acciones de aprobar, rechazar, cancelar y corregir.

El dashboard del profesor conserva el bloque de solicitudes enviadas y la integracion con el flujo de justificacion.

### Respuestas JSON

Las acciones principales responden con una estructura simple:

```json
{
  "ok": true,
  "message": "Operacion completada"
}
```

Los listados conservan `results`, `page`, `has_next` y `has_prev` porque el frontend los usa para render y paginacion.

---

## 4. Revision Contra Backlog

| Requisito | Estado | Observacion |
|---|---|---|
| RF-03 - Justificacion de Incidencias | Cumplido con ajuste | El profesor envia incidencia y jefatura resuelve. La aprobacion crea asistencia compensatoria en lugar de modificar la original, alineado con RNF-04. |
| RF-08 - Evidencia Documental de Incidencias | Fuera de alcance actual | Existe el modelo `EvidenciaIncidencia`, pero el flujo de carga/consulta de archivos no fue desarrollado en Sprint 3. |
| RF-09 - Unidad de Pago por Hora Clase | Parcial | La cancelacion institucional existe como bandera en asistencia. La integracion completa con calculo de pago corresponde a nomina. |
| RF-11 - Entidad Departamento | Parcial | El dashboard de jefatura carga profesores por departamento asignado. Los endpoints JSON de `Asistencias` aun no aplican ese alcance por usuario. |
| RF-12 - Relacion Jerarquica | Parcial | La vista inicial respeta departamentos del jefe. Falta aplicar el mismo alcance en listados y acciones JSON. |
| RF-20 - Solicitud de Correccion | Parcial | Existe `SolicitudCorreccion` y correccion manual desde jefatura, pero no esta completo el flujo de ticket del profesor. |
| RF-21 - Registro Manual Autorizado | Parcial | Jefatura puede corregir registros existentes con bitacora. No hay captura manual completa para crear una asistencia desde cero por falla del sistema. |
| RF-22 - Flujo de Aprobacion | Cumplido | Las incidencias pasan por pendiente, aprobada o rechazada. |
| RNF-01 - Control de Acceso por Roles | Parcial | Los endpoints exigen rol, pero falta limitar por departamento/plantel en las consultas y acciones JSON. |
| RNF-03 - Bitacora de Auditoria | Parcial | La correccion manual genera `BitacoraAuditoria`. Cancelaciones y aprobaciones usan estado/modelo propio, pero no todas generan bitacora. |
| RNF-04 - Inmutabilidad de Asistencia | Parcial | La aprobacion de incidencia respeta la inmutabilidad con compensatoria. La correccion manual de jefatura aun edita campos de la asistencia original. |

---

## 5. Hallazgos de Revision

### Correcto

- El codigo actual es mas cercano a Django clasico y evita sobreingenieria.
- `Asistencias/views.py` quedo como capa delgada de request/response.
- La aprobacion de incidencias ya no modifica la asistencia original.
- `CorreccionAsistencia` deja trazabilidad explicita entre original y compensatoria.
- El frontend de jefatura sigue conectado a endpoints reales.
- Los filtros principales se mantienen simples y legibles.

### Brechas Pendientes

- `Asistencias/services/listados.py` no recibe `request.user`, por lo que no puede limitar registros al departamento de la jefatura.
- `listar_incidencias_jefatura` calcula `pending_total` global y no por alcance de jefatura.
- Las acciones `aprobar`, `rechazar`, `cancelar` y `corregir` validan rol, pero no validan propiedad departamental del registro.
- El reporte anterior mencionaba `Asistencias/services/jefatura.py`; esa estructura ya no aplica.
- La correccion manual sigue editando la asistencia original, lo que debe revisarse frente a RNF-04.

---

## 6. Estado Actual del Sprint

### Completado

- Dashboard de jefatura con datos reales del departamento.
- Vista de gestion de asistencias para jefatura.
- Vista de solicitudes de justificacion para jefatura.
- Endpoints JSON para consulta y resolucion de incidencias.
- Cancelacion institucional.
- Correccion manual con bitacora.
- Consulta de solicitudes enviadas en dashboard de profesor.
- Indices de `Incidencia` agregados en la migracion `0006`.
- Refactor simple de `Asistencias` con utils y services pequeños.

### Parcial

- Alcance departamental en endpoints JSON de jefatura.
- Conteo de pendientes por ambito real de jefatura.
- Cumplimiento estricto de inmutabilidad para correccion manual.
- Flujo completo de solicitud de correccion desde profesor.
- Registro manual desde cero por falla del sistema.
- Evidencias documentales de incidencias.

---

## 7. Conclusiones

Sprint 3 cumple el flujo principal de gestion de asistencias por jefatura, pero no debe documentarse como completamente cerrado contra todos los requisitos relacionados del backlog.

El cambio mas importante de la version 2.0 es la alineacion con **RNF-04 - Inmutabilidad de Asistencia**: aprobar una incidencia ya no altera la asistencia original, sino que crea una asistencia compensatoria y registra `CorreccionAsistencia`.

Para considerar Sprint 3 completamente alineado con el backlog, faltan principalmente controles de alcance por departamento en endpoints JSON y ajustar la correccion manual para no editar directamente la asistencia original.

---

## 8. Evidencia DBA

- **Migracion Sprint 3:** `Asistencias/0006_incidencia_asistencias_estado_a584f7_idx_and_more`
- **Indices de `Incidencia`:**
  - `estado`
  - `solicitante`
  - `fecha_solicitud`
  - `(asistencia, estado)`
- **Migracion posterior de correccion compensatoria:** `Asistencias/0008_correccion_asistencia`

---

## 9. Control de Version del Documento

| Version | Fecha | Descripcion |
|---|---|---|
| 1.0 | 2026-04-19 | Emision inicial del reporte de Sprint 3 |
| 1.1 | 2026-04-21 | Cierre operativo integrado DBA y estado final del sprint |
| 1.2 | 2026-05-11 | Actualizacion documental sin referencias a pruebas automatizadas |
| 2.0 | 2026-05-11 | Revision completa contra backlog y alineacion con correccion compensatoria |
