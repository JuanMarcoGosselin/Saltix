# STX-SPRINT-4-REPORT-v1.0
### Reporte de Sprint 4 - Saltix

---

## 1. Informacion del Sprint

- **Numero de Sprint:** 3
- **Nombre del Sprint:** Gestion de Asistencias por Jefatura
- **Fechas objetivo:** 2026-04-06 al 2026-04-19
- **Fecha de actualizacion del reporte:** 2026-05-11
- **Version del documento:** 2.0
- **Proyecto:** Saltix - Sistema de Control de Asistencia y Calculo de Nomina

### Miembros del Equipo

| Nombre | Rol |
|--------|-----|
| Ivan Ramos de la Torre | Team Leader |
| Juan Marco Gosselin Gamboa | DBA / QA / Backend |
| Patricio Davila Assad | Backend |
| Diego Cristobal Gael Serna Dominguez | Frontend |
| Katherine Guadalupe Guareno Flores | Frontend / Design |

---

## 2. Objetivo del Sprint

Cerrar las brechas funcionales detectadas al integrar asistencias, jefatura, profesores y contabilidad, manteniendo una arquitectura simple y consistente con Saltix.

El sprint consolida reglas de negocio para justificaciones, asistencias compensatorias, alcance departamental de jefatura, calculo de nomina desde asistencias, gestion de periodos, mejoras de dashboards y el sistema de notificaciones internas sin correo, WebSockets ni servicios externos.

---

## 3. Trabajo Planeado (Sprint Backlog)

| Tarea / Historia de Usuario | Descripcion | Responsable | Prioridad |
|-----------------------------|-------------|-------------|-----------|
| Consolidar modelo de profesor | Mantener un solo departamento y un solo plantel por profesor | Backend / DBA | Alta |
| Consolidar alcance de jefatura | Filtrar asistencias, incidencias y transferencias por departamento permitido | Backend | Alta |
| Redisenar aprobacion de justificaciones | Evitar modificar directamente la asistencia original y registrar compensatorias | Backend | Alta |
| Refactorizar servicios de asistencias | Separar listados, incidencias y utilidades para reducir complejidad de vistas | Backend | Alta |
| Implementar calculo de nomina | Calcular percepciones, deducciones y total neto desde asistencias del periodo | Backend | Alta |
| Gestionar periodos de nomina | Abrir, cerrar y validar periodos generales de nomina | Backend / Frontend | Alta |
| Mejorar dashboard de contabilidad | Mostrar periodos, nominas, pendientes, totales y vista de recibo | Frontend / Backend | Media |
| Mejorar dashboard de profesor | Optimizar consulta de asistencias, faltas, horario semanal y justificaciones | Frontend / Backend | Media |
| Persistir seccion activa de dashboards | Recordar la ultima seccion visitada por rol al recargar | Frontend | Media |
| Ajustar dashboard admin | Reflejar usuarios, permisos, planteles, departamentos y actividad reciente | Frontend / Backend | Media |
| Implementar notificaciones internas | Campana, contador, pagina de notificaciones, polling ligero e integraciones principales | Backend / Frontend | Alta |
| Actualizar documentacion | Reportar alcance, decisiones, pendientes y pruebas manuales del sprint | Team Leader | Alta |

---

## 4. Trabajo Completado

| Tarea | Responsable | Estado |
|-------|-------------|--------|
| Profesor asociado a un solo departamento y un solo plantel | Backend / DBA | Completado |
| Periodos de nomina generales, sin dependencia de plantel | Backend / DBA | Completado |
| Nomina con estado y calculo desde asistencias | Backend | Completado |
| Vista de generacion de nomina y preview de deducciones | Backend / Frontend | Completado |
| Cierre de periodo con validacion de nominas generadas | Backend | Completado |
| Refactor de dashboard de profesor hacia servicio `Profesores.services.dashboard` | Backend | Completado |
| Refactor de asistencias en servicios de listados e incidencias | Backend | Completado |
| Justificaciones aprobadas mediante asistencia compensatoria | Backend | Completado |
| Registro de `CorreccionAsistencia` para trazabilidad de justificaciones | Backend | Completado |
| Faltas y retardos justificados excluidos de estadisticas y descuentos | Backend | Completado |
| Consultas JSON de jefatura filtradas por alcance departamental | Backend | Completado |
| Correccion manual y cancelacion institucional de asistencias por jefatura | Backend | Completado |
| Ajustes visuales en dashboard de contabilidad | Frontend | Completado |
| Ajustes visuales y funcionales en dashboard de profesor | Frontend | Completado |
| Persistencia de seccion activa en dashboards por rol | Frontend | Completado |
| Ajustes menores en admin dashboard y permisos | Backend / Frontend | Completado |
| App `Notifications` con modelo, vistas, urls, helpers y admin | Backend | Completado |
| Campana de notificaciones con contador, dropdown y polling ligero en layout compartido | Frontend / Backend | Completado |
| Pagina `/notificaciones/` con listado y acciones de lectura | Frontend / Backend | Completado |
| Integraciones de notificaciones en justificaciones, asistencia, horario, nomina y usuarios | Backend | Completado |
| Documentacion del Sprint 4 en `docs/planning/sprints/` | Team Leader | Completado |

---

## 5. Trabajo Pendiente

| Tarea | Motivo | Accion Siguiente |
|-------|--------|------------------|
| Tiempo real con WebSockets para notificaciones | Sprint 4 excluye WebSockets y arquitectura enterprise | Evaluar solo si polling no cubre la necesidad |
| Archivado visible de notificaciones | El campo `archivada` existe, pero la UI aun no expone accion | Agregar filtro y boton de archivar |
| Alcance fino de notificaciones por departamento | `notify_role("jefatura")` notifica al rol completo en algunos casos | Agregar helpers por departamento/plantel |
| Migracion de datos desde `core.Notificacion` | Se dejo intacto para no tocar migraciones historicas | Planear migracion o deprecacion controlada |
| Auditoria de intentos fallidos de login | No existe flujo propio de bloqueo o auditoria de login | Implementar solo si entra al alcance futuro |
| Pruebas automatizadas actualizadas | La rama elimina pruebas antiguas y prioriza validacion manual | Crear suite enfocada por modulo en Sprint 5 |

---

## 6. Problemas o Riesgos Encontrados

- Existian modelos y servicios con responsabilidades mezcladas en asistencias; se separaron servicios para reducir complejidad, pero aun requiere cobertura automatizada nueva.
- La nomina depende de que todas las asistencias del periodo esten completas y consistentes antes del cierre.
- El modelo historico `core.Notificacion` ya existia con una forma distinta; se creo `Notifications.Notificacion` para cumplir el alcance nuevo sin romper migraciones previas.
- Los datos de periodo y profesor cambiaron reglas de relacion, por lo que las migraciones deben validarse con datos reales antes de produccion.
- Las notificaciones internas usan polling ligero; no son tiempo real estricto y dependen del intervalo configurado.

---

## 7. Metricas del Sprint

- **Tareas Planeadas:** 11
- **Tareas Completadas:** 20
- **Tareas Restantes:** 6
- **Archivos impactados en rama `sprint-4` contra `main`:** 57
- **Balance tecnico de la rama `sprint-4`:** 3178 inserciones y 2545 eliminaciones
- **Apps principales impactadas:** `Asistencias`, `Contabilidad`, `Profesores`, `jefatura`, `admin`, `core`, `Notifications`

---

## 8. Resumen de la Revision del Sprint

Al cierre de Sprint 4, Saltix cuenta con un flujo mas integrado entre profesores, jefatura y contabilidad.

Los profesores pueden consultar su informacion de asistencia y solicitar justificaciones. Jefatura puede revisar incidencias dentro de su alcance, aprobar o rechazar solicitudes, cancelar asistencias institucionalmente y corregir registros. La aprobacion de justificaciones conserva la asistencia original y crea una asistencia compensatoria trazable.

Contabilidad puede gestionar periodos generales, generar nomina con percepciones, deducciones y faltas descontables, revisar el detalle y cerrar periodos cuando las nominas requeridas estan generadas.

Tambien se agrego el sistema de notificaciones internas de Sprint 4 con campana, contador, dropdown, polling ligero, pagina dedicada y acciones para marcar notificaciones como leidas. Las integraciones cubren justificaciones, asistencia registrada, retardos, cambios de asistencia, cambios de horario, generacion y cierre de nomina, creacion y modificacion de usuarios.

Los dashboards de profesor, jefatura y contabilidad conservan la ultima seccion visitada al recargar, alineandose con el comportamiento del dashboard de admin. Cuando una URL incluye `?page=` o `#seccion`, esa seccion tiene prioridad para permitir enlaces directos desde notificaciones.

---

## 9. Retrospectiva del Sprint

**Que salio bien**

- Se redujo complejidad moviendo logica de dashboards y asistencias hacia servicios.
- Se aclararon reglas de negocio importantes: alcance departamental, asistencia compensatoria y periodo general de nomina.
- Se avanzo en integracion real entre modulos sin introducir infraestructura innecesaria.
- La UI mantiene el estilo actual del proyecto y evita redisenos completos.
- El sistema de notificaciones quedo listo para crecer sin depender de correo, WebSockets ni servicios externos.

**Que se puede mejorar**

- Agregar pruebas automatizadas para los flujos criticos de justificaciones, nomina y notificaciones.
- Definir fechas y alcance formal del sprint antes del desarrollo para mejorar trazabilidad.
- Reducir deuda historica alrededor de modelos duplicados o heredados, como `core.Notificacion`.
- Afinar permisos y scopes por departamento para notificaciones y acciones administrativas.

**Acciones para el proximo sprint**

- Crear pruebas unitarias e integracion para incidencias, compensatorias y nomina.
- Agregar filtros y archivado para notificaciones.
- Revisar migraciones con datos reales y documentar pasos de despliegue.
- Formalizar historias de usuario por rol con criterios de aceptacion verificables.
- Evaluar limpieza o migracion del modelo historico `core.Notificacion`.
