# STX-SPRINT-3-REPORT-v1.0
### Reporte de Sprint 3 - Saltix

---

## 1. Informacion del Sprint

- **Numero de Sprint:** 3
- **Nombre del Sprint:** Gestion de Asistencias por Jefatura
- **Fechas objetivo:** 2026-04-06 al 2026-04-19
- **Proyecto:** Saltix - Sistema de Control de Asistencia y Calculo de Nomina

### Equipo

| Nombre | Rol |
|--------|-----|
| Ivan Ramos de la Torre | Team Leader / Backend |
| Juan Marco Gosselin Gamboa | DBA / QA / Backend |
| Patricio Davila Assad | Backend |
| Diego Cristobal Gael Serna Dominguez | Frontend |
| Katherine Guadalupe Guareno Flores | Frontend / Design |

---

## 2. Objetivo del Sprint

Implementar el flujo operativo de jefatura para revisar asistencias, resolver incidencias y consultar solicitudes del profesorado sin alterar la arquitectura base del sistema. La meta del sprint fue extender `Asistencias` como componente de negocio, mantener `jefatura` como capa de orquestacion y completar la primera ronda de pruebas automatizadas del modulo.

---

## 3. Cambios implementados

### Backend

- Se agregaron endpoints JSON para:
  - listar asistencias visibles para jefatura;
  - listar incidencias visibles para jefatura;
  - aprobar incidencias;
  - rechazar incidencias;
  - cancelar asistencias institucionalmente;
  - corregir asistencias con trazabilidad;
  - listar incidencias del profesor autenticado.
- Se centralizo la logica de scope, filtros, paginacion y serializacion en `Asistencias/services/jefatura.py`.
- Se mantuvo la estrategia actual de trabajo sobre la asistencia original:
  - el profesor crea una `Incidencia` en estado `PENDIENTE`;
  - jefatura resuelve la incidencia;
  - al aprobar, la asistencia original se actualiza a `JUSTIFICADA`;
  - al rechazar, la asistencia original permanece sin cambios.
- Se registro trazabilidad para correcciones manuales mediante `BitacoraAuditoria`.

### Frontend

- Se conecto `jefatura/dashboard.html` a datos reales del departamento asignado a la jefatura.
- Se implementaron filtros por profesor, fecha y estado para asistencias e incidencias.
- Se agregaron acciones de aprobar, rechazar, cancelar y corregir desde la interfaz.
- Se corrigio el comportamiento del contador de solicitudes pendientes para que use el total real del ambito de jefatura y no solo la pagina filtrada.
- Se extendio el dashboard del profesor con un bloque de solicitudes enviadas.

### DBA

- Se agregaron indices sobre `Incidencia` para:
  - `estado`
  - `solicitante`
  - `fecha_solicitud`
  - `(asistencia, estado)`
- La migracion generada fue `Asistencias/0006_incidencia_asistencias_estado_a584f7_idx_and_more`.

### QA

- Se agregaron pruebas automatizadas para:
  - scope de jefatura;
  - filtros de asistencias;
  - aprobacion y rechazo de incidencias;
  - validacion de incidencia ya resuelta;
  - cancelacion institucional duplicada;
  - consulta de incidencias del profesor;
  - correccion manual con trazabilidad;
  - render del dashboard de jefatura;
  - render del bloque de solicitudes enviadas del profesor.

---

## 4. Validacion ejecutada

- `python manage.py check` -> **OK**
- `python manage.py test Asistencias jefatura Profesores` -> **OK**
- `showmigrations Asistencias` -> migracion `0006` marcada como aplicada en el entorno validado

---

## 5. Hallazgos y fallas revisadas

Durante la revision del sprint se verificaron los siguientes riesgos funcionales:

- **Contador de pendientes en jefatura:** se detecto el riesgo de que el contador cambiara con base en la pagina filtrada y no en el total real pendiente. Se ajusto el endpoint de incidencias para retornar `pending_total` y el frontend ahora sincroniza el badge con ese valor.
- **Roles y alcance:** se confirmo que los endpoints de jefatura restringen acceso por rol y por alcance de departamento/plantel.
- **Confirmaciones al frontend:** se verifico que aprobar, rechazar, cancelar y corregir retornan respuestas JSON de confirmacion o error claro.
- **Migraciones:** se confirmo que la migracion de indices ya existe y aparece aplicada en el entorno actual.

No se detectaron errores de sistema en `check` ni fallos en la suite de pruebas automatizadas incluida.

---

## 6. Estado del Sprint

### Completado

- Frontend de gestion de asistencias para jefatura
- Frontend de solicitudes de justificacion para jefatura
- Backend de consulta y resolucion de incidencias
- Backend de correccion manual y cancelacion institucional
- Consulta de solicitudes enviadas del profesor
- Indices de base de datos del sprint
- Pruebas automatizadas base del modulo

### Pendiente de cierre operativo

- Evidencia formal de QA manual del checklist del sprint
- Registro formal de validacion de impacto de indices si el equipo lo requiere como evidencia separada de DBA

---

## 7. Conclusiones

Sprint 3 queda funcionalmente implementado con cambios minimos a la arquitectura original:

- `Asistencias` concentra la logica nueva del negocio;
- `jefatura` continua como capa de orquestacion/presentacion;
- `Profesores` solo se extiende para mostrar el estado de incidencias ya enviadas.

El sprint puede considerarse **completo en desarrollo** y **pendiente solo de cierre documental/operativo** si el equipo necesita evidencias manuales adicionales de QA y DBA.
