# STX-SPRINT-3-REPORT-v1.0
### Reporte de Sprint 3 - Saltix

---

## 1. Objetivo del Sprint

Implementar la gestion de asistencias por jefatura con cambios minimos sobre la arquitectura actual, manteniendo `Asistencias` como componente de negocio y `jefatura` como capa de orquestacion/presentacion.

---

## 2. Cambios implementados

- Endpoints nuevos en `Asistencias` para consulta, aprobacion, rechazo, cancelacion institucional y correccion manual.
- Servicios reutilizables en `Asistencias/services/jefatura.py` para scope, filtros, paginacion y serializacion.
- Dashboard de `jefatura` conectado a datos reales del departamento asignado.
- Dashboard del profesor extendido con la vista de solicitudes enviadas.
- Indices nuevos en `Incidencia` para optimizar consultas de Sprint 3.
- Suite inicial de pruebas automatizadas para backend, jefatura y profesor.

---

## 3. Paso a paso tecnico aplicado

1. Extender rutas en `Asistencias/urls.py`.
2. Implementar endpoints JSON en `Asistencias/views.py`.
3. Extraer filtros y alcance de jefatura a `Asistencias/services/jefatura.py`.
4. Agregar indices a `Incidencia` en `Asistencias/models.py`.
5. Renderizar datos reales en `jefatura/views.py` y `jefatura/dashboard.html`.
6. Agregar acciones JS para filtrar, aprobar, rechazar, cancelar y corregir.
7. Extender `Profesores/views.py` y `Profesores/dashboard.html` con solicitudes enviadas.
8. Agregar pruebas automatizadas en `Asistencias/tests.py`, `jefatura/tests.py` y `Profesores/tests.py`.

---

## 4. Pendiente del Sprint

- Generar y aplicar la migracion formal para los nuevos indices de `Incidencia`.
- Ejecutar QA manual completo sobre filtros y estados visuales.
- Validar si la correccion manual requiere endurecer aun mas la estrategia de inmutabilidad en un sprint futuro.
