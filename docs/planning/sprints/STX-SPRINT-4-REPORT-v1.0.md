# STX-SPRINT-4-REPORT-v1.0
### Reporte de Sprint 4 - Saltix

---

## 1. Objetivo

Cerrar las brechas funcionales detectadas al integrar asistencias, jefatura, profesores y contabilidad, manteniendo el estilo simple del proyecto.

---

## 2. Alcance Cerrado

- Cada profesor queda asociado a un solo departamento.
- Cada profesor queda asociado a un solo plantel.
- Cada jefatura queda asociada a un solo departamento.
- La jefatura consulta y resuelve asistencias e incidencias solo para profesores de su departamento.
- La aprobacion de justificaciones no modifica la asistencia original: crea una asistencia compensatoria y registra `CorreccionAsistencia`.
- Las faltas y retardos con incidencia aprobada no cuentan como faltas o retardos normales en estadisticas ni descuentos.
- La nomina es general y compartida. No existe una nomina independiente por plantel.
- El modelo de periodo ya no depende de plantel.

---

## 3. Reglas Confirmadas

### Asistencias y justificaciones

1. El profesor solicita justificacion sobre una falta o retardo.
2. La solicitud queda como `PENDIENTE`.
3. Jefatura aprueba o rechaza segun el alcance de su departamento.
4. Si aprueba, se crea una asistencia `COMPENSATORIA`.
5. La asistencia original conserva su estado historico.
6. La incidencia queda en `APROBADA` y se relaciona mediante `CorreccionAsistencia`.
7. Las estadisticas y nomina excluyen esas faltas/retardos del conteo sancionable.

### Departamentos y planteles

- `Profesor.departamento` y `Profesor.plantel` son relaciones unicas.
- Las pantallas deben mostrar un departamento y un plantel por profesor.
- Una jefatura solo puede tener un departamento a cargo.

### Nomina

- Solo se maneja un periodo activo general.
- Todos los planteles usan los mismos contadores y la misma logica contable.
- Ningun calculo de nomina debe depender de un plantel del periodo.

---

## 4. Pendientes de Sprints Previos Atendidos

| Pendiente | Estado Sprint 4 |
|---|---|
| Alcance departamental en endpoints JSON de jefatura | Cerrado |
| Conteo de pendientes por ambito real de jefatura | Cerrado |
| Evitar modificacion directa al aprobar justificaciones | Cerrado |
| Profesor con un solo departamento | Cerrado |
| Profesor con un solo plantel | Cerrado |
| Jefatura con un solo departamento | Cerrado |
| Periodos de nomina sin plantel | Cerrado en modelo y documentacion |

---

## 5. Notas

La migracion de datos debe conservar solo una relacion de departamento y una de plantel por profesor, y remover el campo heredado `Periodo.plantel`.
