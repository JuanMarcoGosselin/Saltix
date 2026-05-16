# STX-SPRINT-4-REPORT-v1.0
### Reporte de Sprint 4 - Saltix

---

## 1. Informacion del Sprint

- **Numero de Sprint:** 4
- **Nombre del Sprint:** Cierre funcional de Nomina, Reportes y Notificaciones
- **Fechas objetivo:** 2026-04-06 al 2026-04-19
- **Fecha de actualizacion del reporte:** 2026-05-15
- **Version del documento:** 1.0
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
| Completar regeneracion y conceptos de nomina | Regenerar nominas, agregar/eliminar conceptos e ISR simplificado | Backend / Frontend | Alta |
| Mejorar dashboard de contabilidad | Mostrar periodo activo, historial filtrable de nominas cerradas/pagadas y vista de recibo | Frontend / Backend | Media |
| Completar reportes financieros | Vista previa, reporte administrativo, recibos PDF y consolidado PDF por periodo | Backend / Frontend | Alta |
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
| Regeneracion individual y masiva de nominas | Backend / Frontend | Completado |
| Conceptos adicionales de percepcion y deduccion | Backend / Frontend | Completado |
| ISR academico simplificado | Backend | Completado |
| Vista de generacion de nomina y preview de deducciones | Backend / Frontend | Completado |
| Vista previa de periodo con totales e inconsistencias | Backend / Frontend | Completado |
| Reporte administrativo de nomina por periodo con filtros | Backend / Frontend | Completado |
| Recibos individuales PDF para nominas cerradas o pagadas | Backend / Frontend | Completado |
| Reporte consolidado PDF del periodo | Backend / Frontend | Completado |
| Cierre de periodo con validacion de nominas generadas | Backend | Completado |
| Refactor de dashboard de profesor hacia servicio `Profesores.services.dashboard` | Backend | Completado |
| Refactor de asistencias en servicios de listados e incidencias | Backend | Completado |
| Justificaciones aprobadas mediante asistencia compensatoria | Backend | Completado |
| Registro de `CorreccionAsistencia` para trazabilidad de justificaciones | Backend | Completado |
| Faltas y retardos justificados excluidos de estadisticas y descuentos | Backend | Completado |
| Consultas JSON de jefatura filtradas por alcance departamental | Backend | Completado |
| Correccion manual y cancelacion institucional de asistencias por jefatura | Backend | Completado |
| Ajustes visuales en dashboard de contabilidad e historial de nominas separado | Frontend | Completado |
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

Contabilidad puede gestionar periodos generales, generar nomina con percepciones, deducciones y retardos descontables, revisar el detalle y cerrar periodos solo cuando todas las nominas del periodo estan cerradas o pagadas.

El modulo de Contabilidad/Nomina se completo con regeneracion individual y masiva, conceptos adicionales, detalle editable, cierre individual de nomina, bloqueo de periodos cerrados e ISR simplificado documentado. El inicio del dashboard queda enfocado en el periodo activo y el historial de nominas se separa en una seccion propia con filtros por periodo, profesor y estado para nominas cerradas o pagadas de periodos anteriores.

Tambien se completaron los reportes financieros: vista previa antes de cierre, reporte administrativo filtrable por periodo, recibos individuales PDF para nominas cerradas o pagadas y PDF consolidado del periodo. Los PDFs se generan bajo demanda con una utilidad interna simple, sin dependencias externas nuevas.

Tambien se agrego el sistema de notificaciones internas de Sprint 4 con campana, contador, dropdown, polling ligero, pagina dedicada y acciones para marcar notificaciones como leidas. Las integraciones cubren justificaciones, asistencia registrada, retardos, cambios de asistencia, cambios de horario, generacion y cierre de nomina, creacion y modificacion de usuarios.

Los dashboards de profesor, jefatura y contabilidad conservan la ultima seccion visitada al recargar, alineandose con el comportamiento del dashboard de admin. Cuando una URL incluye `?page=` o `#seccion`, esa seccion tiene prioridad para permitir enlaces directos desde notificaciones.

---

## 9. Documentacion Tecnica de Contabilidad/Nomina

### 9.1 Resumen

Se completo el modulo de Contabilidad/Nomina para generar, revisar, regenerar, ajustar con conceptos, cerrar y pagar nominas de profesores por periodo quincenal.

La implementacion mantiene el estilo simple de Saltix, separa los calculos principales en `Contabilidad/utils.py` y protege las acciones de escritura para roles de Contabilidad y Administrador.

### 9.2 Archivos Creados

- `Contabilidad/migrations/0008_nomina_metricas_conceptos.py`
- `Contabilidad/templates/Contabilidad/vista_previa_periodo.html`
- `Contabilidad/templates/Contabilidad/reporte_periodo.html`
- `Contabilidad/templates/Contabilidad/recibo_nomina_print.html`
- `Contabilidad/templates/Contabilidad/reporte_periodo_print.html`

### 9.3 Archivos Modificados

- `Contabilidad/models.py`
- `Contabilidad/utils.py`
- `Contabilidad/views.py`
- `Contabilidad/urls.py`
- `Contabilidad/admin.py`
- `Contabilidad/templates/Contabilidad/dashboard.html`
- `Contabilidad/templates/Contabilidad/nomina_gen.html`
- `core/static/css/dashboard_contabilidad.css`
- `core/static/js/contabilidad_dashboard.js`
- `Profesores/services/dashboard.py`
- `Profesores/templates/Profesores/dashboard.html`
- `docs/planning/sprints/STX-SPRINT-4-REPORT-v1.0.md`

### 9.4 Modelos Modificados

`Nomina`

- Campos agregados: `horas_trabajadas`, `faltas`, `retardos`, `faltas_equivalentes`, `fecha_actualizacion`.
- Estado agregado: `cerrada`.
- Restriccion agregada: una nomina por profesor y periodo mediante `unique_nomina_profesor_periodo`.

`Periodo`

- Restriccion agregada para evitar duplicar mismo rango y tipo: `unique_periodo_rango_tipo`.

`DetalleNomina`

- Campos agregados: `descripcion`, `creado_en`.

### 9.5 Vistas y Flujo

- Dashboard de Contabilidad con inicio limpio para el periodo activo.
- Seccion separada de historial de nominas para consultar nominas cerradas o pagadas de periodos anteriores al periodo activo.
- Filtros de historial por periodo, profesor y estado.
- Generacion individual de nomina.
- Generacion masiva de nominas del periodo activo.
- Regeneracion individual y masiva.
- Detalle de nomina con metricas, conceptos, ISR y neto.
- Agregar y eliminar conceptos.
- Cerrar nomina individual.
- Cerrar periodo.
- Marcar nomina como pagada.

Todas las vistas de escritura requieren login y rol `contabilidad` o `administrador`.

### 9.6 URLs Agregadas

- `/contabilidad/nomina/<id>/`
- `/contabilidad/nomina/<id>/regenerar/`
- `/contabilidad/nomina/<id>/conceptos/agregar/`
- `/contabilidad/nomina/conceptos/<id>/eliminar/`
- `/contabilidad/nomina/<id>/cerrar/`
- `/contabilidad/generar-nominas/`
- `/contabilidad/regenerar-nominas/`
- `/contabilidad/periodo/<id>/`
- `/contabilidad/periodo/<id>/preview/`
- `/contabilidad/nomina/<id>/pdf/`
- `/contabilidad/nomina/<id>/print/`
- `/contabilidad/periodo/<id>/pdf/`
- `/contabilidad/periodo/<id>/print/`

### 9.7 Funciones Principales en `Contabilidad/utils.py`

- `rango_quincenal()`
- `crear_periodo_actual()`
- `crear_periodo()`
- `cerrar_periodo()`
- `calcular_horas_profesor()`
- `contar_incidencias_periodo()`
- `calcular_descuentos_asistencia()`
- `calcular_isr()`
- `resumen_nomina()`
- `recalcular_totales_nomina()`
- `generar_nomina_profesor()`
- `generar_nominas_periodo()`
- `regenerar_nomina_profesor()`
- `regenerar_nominas_periodo()`
- `agregar_concepto_nomina()`
- `eliminar_concepto_nomina()`
- `cerrar_nomina()`
- `obtener_resumen_periodo()`
- `obtener_totales_periodo()`
- `detectar_inconsistencias_periodo()`
- `obtener_nominas_periodo()`
- `puede_generar_recibo()`
- `generar_contexto_recibo()`
- `generar_texto_recibo()`
- `generar_texto_reporte_periodo()`
- `simple_pdf()`
- `formato_moneda()`
- `get_profesores_sin_nomina_periodo()`

### 9.8 Reglas de Calculo

- Los periodos son quincenales: dia 1 al 15 y dia 16 al ultimo dia del mes.
- El sueldo bruto se calcula con horas trabajadas reales del periodo por costo por hora.
- Las horas trabajadas se calculan desde asistencias con entrada/salida y asistencias compensatorias.
- Las faltas justificadas no descuentan.
- Las faltas con incidencia aprobada no descuentan.
- Las faltas no justificadas se registran como incidencia de nomina, pero no se descuentan adicionalmente porque esas horas no se incluyen en el sueldo bruto.
- Los retardos no justificados se cuentan.
- Cada 3 retardos equivalen a una falta para nomina.
- En esta version academica, cada falta equivalente por retardos descuenta 1 hora sobre lo efectivamente percibido.
- Las percepciones adicionales aumentan el total de percepciones.
- Las deducciones adicionales aumentan el total de deducciones.
- ISR se guarda en `total_impuestos` y se resta del neto.
- El total de deducciones e ISR nunca puede exceder el total de percepciones.
- El neto se calcula como `total_percepciones - total_deducciones - total_impuestos`.

### 9.9 ISR Simplificado

La funcion `calcular_isr(base_gravable)` usa rangos simples para fines academicos.

No usa tablas fiscales oficiales y debe actualizarse si el sistema pasa a uso productivo real.

| Base gravable | Calculo |
|---------------|---------|
| Hasta 5000 | 0 |
| 5000.01 a 10000 | 10% sobre excedente |
| 10000.01 a 20000 | cuota 500 + 15% sobre excedente |
| Mas de 20000 | cuota 2000 + 20% sobre excedente |

### 9.10 Bloqueos Logicos

- Una nomina cerrada no puede modificarse.
- Una nomina pagada no puede modificarse.
- Un periodo cerrado no permite generar ni regenerar nominas.
- Un periodo abierto solo puede cerrarse si todas las nominas de profesores activos ya existen y estan cerradas o pagadas.
- Los conceptos no pueden agregarse ni eliminarse si la nomina no es editable.
- El monto de conceptos debe ser mayor a cero.
- Los recibos PDF individuales solo se generan para nominas cerradas o pagadas en Contabilidad/Admin.
- Profesor solo puede visualizar su propio recibo individual cuando la nomina esta pagada.

### 9.11 Reportes Financieros

Reportes implementados:

- Vista previa de periodo en `/contabilidad/periodo/<id>/preview/`.
- Reporte administrativo de nomina por periodo en `/contabilidad/periodo/<id>/`.
- Recibo individual PDF en `/contabilidad/nomina/<id>/pdf/`.
- Reporte consolidado PDF del periodo en `/contabilidad/periodo/<id>/pdf/`.
- Recibo visual imprimible en `/contabilidad/nomina/<id>/print/`.
- Reporte visual imprimible en `/contabilidad/periodo/<id>/print/`.

Las pantallas del sistema muestran unicamente la accion `Ver PDF`, que abre las vistas `print/` con HTML/CSS similar al sistema. Desde esas vistas el usuario puede guardar como PDF usando el navegador. Las rutas `pdf/` permanecen como respaldo tecnico de PDF simple bajo demanda.

La vista previa muestra:

- Periodo y estado.
- Total profesores incluidos.
- Total nominas generadas, pendientes, cerradas, pagadas y en proceso.
- Total bruto, percepciones, deducciones, ISR y neto.
- Inconsistencias detectadas.

Inconsistencias detectadas:

- Profesor sin RFC.
- Profesor sin costo por hora valido.
- Profesor sin horario activo.
- Profesor activo sin nomina.
- Sueldo neto negativo.
- Nomina incompleta.
- Periodo sin nominas.
- Ajustes manuales por conceptos agregados.

Reglas PDF:

- No se agregaron dependencias externas.
- Los PDFs descargables usan una utilidad interna simple basada en texto administrativo.
- Las vistas imprimibles usan HTML/CSS similar al sistema para generar PDFs visuales desde el navegador.
- Si el periodo esta abierto, el consolidado se marca como `Vista previa`.
- Si el periodo esta cerrado, el consolidado se marca como `Reporte oficial`.
- Los recibos individuales se bloquean para nominas abiertas.
- Profesor solo ve recibos e historial de pagos cuando la nomina esta pagada.

### 9.12 Notificaciones

Se integra con `Notifications.utils`:

- Contabilidad recibe aviso al generar o regenerar nominas.
- Profesor recibe aviso cuando su nomina esta disponible o actualizada.
- Admin recibe aviso si ocurre una inconsistencia importante durante procesos de nomina.

### 9.13 Pruebas Manuales Esperadas

1. Entrar como Contabilidad o Administrador.
2. Ir a Contabilidad > Periodos.
3. Crear periodo actual.
4. Ir a Inicio.
5. Confirmar que Inicio muestra solo la nomina del periodo activo, sin filtros.
6. Generar nomina individual de un profesor pendiente.
7. Abrir detalle de nomina.
8. Agregar una percepcion con monto positivo.
9. Agregar una deduccion con monto positivo.
10. Eliminar un concepto.
11. Confirmar que percepciones, deducciones, ISR y neto se recalculan.
12. Regenerar nomina individual.
13. Generar todas las nominas del periodo.
14. Regenerar todas las nominas del periodo.
15. Ir a Historial nominas.
16. Confirmar que se muestran las nominas cerradas o pagadas de periodos anteriores al actual.
17. Probar filtros de historial por periodo, profesor y estado.
18. Confirmar que faltas justificadas no descuentan.
19. Confirmar que faltas no justificadas no descuentan adicionalmente porque no forman parte de las horas trabajadas pagadas.
20. Confirmar que 3 retardos equivalen a 1 falta para nomina.
21. Cerrar una nomina.
22. Intentar agregar concepto a una nomina cerrada y confirmar bloqueo.
23. Intentar cerrar el periodo con alguna nomina en proceso y confirmar bloqueo.
24. Cerrar o pagar todas las nominas del periodo.
25. Cerrar periodo.
26. Intentar regenerar una nomina del periodo cerrado y confirmar bloqueo.
27. Abrir Reportes financieros.
28. Abrir vista previa de periodo y confirmar totales e inconsistencias.
29. Abrir reporte administrativo y filtrar por profesor y estado.
30. Visualizar recibo individual PDF visual de una nomina cerrada o pagada desde Contabilidad/Admin.
31. Intentar generar recibo PDF de una nomina abierta y confirmar bloqueo.
32. Visualizar PDF consolidado del periodo.
33. Confirmar que Profesor solo puede ver sus propios recibos pagados.

### 9.14 Limitaciones y Mejoras Futuras

Limitaciones actuales:

- El ISR es simplificado y academico.
- Los PDFs no sustituyen comprobantes fiscales oficiales.
- Las vistas visuales dependen del motor de impresion del navegador.
- Los PDFs se generan bajo demanda y no se persisten todavia en `ReciboNomina`.
- La equivalencia de retardos descuenta 1 hora por cada 3 retardos.
- No existe bitacora historica detallada de regeneraciones, solo `fecha_actualizacion`.
- Los conceptos usan un catalogo simple reutilizable por nombre y tipo.

Mejoras futuras recomendadas:

- Tablas ISR reales administrables por periodo fiscal.
- Recibos PDF.
- Historial de regeneraciones.
- Bitacora de cambios de conceptos.
- Flujo de aprobacion antes de pago.
- Exportacion contable por periodo.

---

## 10. Retrospectiva del Sprint

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
