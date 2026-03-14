# STX-CORE-RSK-MATRIZ-RIESGOS-v1.0

**Proyecto:** Saltix — Sistema de Control de Asistencia y Cálculo de Nómina  
**Versión:** 1.0  
**Fecha:** 2026-03-13

---

## Instrucciones de Uso

- **Probabilidad:** 1=Muy baja, 2=Baja, 3=Media, 4=Alta, 5=Muy alta
- **Impacto:** 1=Muy bajo, 2=Bajo, 3=Medio, 4=Alto, 5=Muy alto
- **Nivel de Riesgo:** Probabilidad × Impacto
- **Semáforo:** 1-4 = 🟢 Verde, 5-9 = 🟡 Amarillo, 10-25 = 🔴 Rojo

---

## Matriz de Riesgos

| ID | Categoría | Descripción del Riesgo | Prob. | Impacto | Nivel | Semáforo | Responsable | Plan de Mitigación | Plan de Contingencia |
|---|---|---|:---:|:---:|:---:|:---:|---|---|---|
| RSK-01 | Técnico | Error en el cálculo de nómina por uso incorrecto de tipos de datos flotantes en operaciones monetarias. | 3 | 5 | 15 | 🔴 ROJO | Equipo Backend | Usar exclusivamente DecimalField con 4 decimales; prohibir operaciones con float en cálculos de pago. | Revisión manual del cálculo afectado; reversión del periodo si ya fue cerrado. |
| RSK-02 | Técnico | Falla del reloj checador que impide registrar asistencias automáticamente. | 4 | 4 | 16 | 🔴 ROJO | Líder Técnico | Implementar flujo de registro manual como respaldo desde la primera versión. | El administrador registra asistencias manualmente; se documenta la incidencia en la bitácora. |
| RSK-03 | Técnico | Pérdida de datos por falta de respaldos de la base de datos SQLite en producción. | 3 | 5 | 15 | 🔴 ROJO | Líder Técnico | Configurar respaldos automáticos diarios del archivo db.sqlite3; documentar proceso de restauración. | Restaurar último respaldo disponible; registrar datos perdidos con fecha y hora del incidente. |
| RSK-04 | Técnico | Migración fallida de Django al modificar modelos críticos (Nomina, Asistencia) en producción. | 3 | 4 | 12 | 🔴 ROJO | DBA | Probar todas las migraciones en entorno de desarrollo antes de aplicar en producción; mantener respaldo previo a cada migrate. | Revertir migración con `migrate --fake`; restaurar respaldo de BD; corregir y reaplicar. |
| RSK-05 | Técnico | Vulnerabilidad de acceso por control de roles insuficiente en vistas del sistema. | 2 | 5 | 10 | 🔴 ROJO | Equipo Backend | Implementar decoradores de verificación de rol en cada vista; revisar en code review. | Bloquear el acceso al módulo afectado hasta corregir; revisar logs de acceso para detectar uso indebido. |
| RSK-06 | Negocio | Cambio en la legislación fiscal (ISR, IMSS) que afecte el cálculo de nómina durante el desarrollo. | 2 | 4 | 8 | 🟡 AMARILLO | Líder de Proyecto | Diseñar el catálogo de conceptos fiscales como configurable para adaptarse sin cambios en el código. | Actualizar el catálogo de conceptos y re-calcular nóminas afectadas del periodo vigente. |
| RSK-07 | Negocio | Requisitos de nómina incompletos o ambiguos que generen re-trabajo en el módulo de Contabilidad. | 4 | 3 | 12 | 🔴 ROJO | Product Owner | Validar RF-14 a RF-18 con el cliente antes de implementar; hacer demos tempranas del cálculo de nómina. | Iterar sobre los requisitos; ajustar el módulo en el sprint siguiente con prioridad alta. |
| RSK-08 | Equipo | Ausencia de un miembro clave del equipo durante una fase crítica del proyecto. | 3 | 3 | 9 | 🟡 AMARILLO | Líder de Proyecto | Documentar el código con docstrings; mantener el tablero de Trello actualizado para que cualquier miembro pueda retomar. | Redistribuir tareas entre el equipo; ajustar fechas de entrega si es necesario. |
| RSK-09 | Equipo | Falta de experiencia con Django en algún miembro del equipo que ralentice el desarrollo. | 3 | 2 | 6 | 🟡 AMARILLO | Líder de Proyecto | Asignar tareas de menor complejidad al inicio; hacer sesiones cortas de revisión de código en equipo. | Reasignar la tarea a un miembro con más experiencia; usar pair programming. |
| RSK-10 | Alcance | El alcance del módulo de nómina crece por solicitudes de funciones no contempladas (scope creep). | 3 | 3 | 9 | 🟡 AMARILLO | Product Owner | Congelar el backlog para la fase actual; documentar las solicitudes nuevas como ítems del siguiente sprint. | Negociar con el cliente la postergación de funciones al siguiente release. |