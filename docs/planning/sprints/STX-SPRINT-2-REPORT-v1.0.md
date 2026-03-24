# STX-SPRINT-2-REPORT-v1.0
### Reporte de Sprint 2 — Saltix

---

## 1. Información del Sprint

- **Número de Sprint:** 2
- **Nombre del Sprint:** Gestión de Asistencias y Solicitudes de Justificación
- **Duración del Sprint:** 2 semanas
- **Fechas del Sprint:** 16/03/2026 – 05/04/2026
- **Nombre del Proyecto:** Saltix — Sistema de Control de Asistencia y Cálculo de Nómina

### Miembros del Equipo

| Nombre | Rol |
|--------|-----|
| Ivan Ramos de la Torre | Team Leader |
| Juan Marco Gosselin Gamboa | DBA / QA / Backend |
| Patricio Dávila Assad | Backend |
| Diego Cristóbal Gael Serna Domínguez | Frontend |
| Katherine Guadalupe Guareño Flores | Frontend / Design |

---

## 2. Objetivo del Sprint

> Implementar el módulo completo de registro y gestión de asistencias para profesores: lógica de registro con validación de horario y tolerancia, vistas de horario semanal e historial, sistema de solicitudes de justificación con validaciones robustas, y optimizaciones de base de datos mediante índices y restricción de unicidad. Conectar los resultados al dashboard del profesor para que muestre datos reales.

---

## 3. Trabajo Planeado (Sprint Backlog)

| Tarea / Historia de Usuario | Descripción | Responsable | Prioridad |
|-----------------------------|-------------|-------------|-----------|
| Vista de Registro de Asistencia para Profesores | Layout de registro con info del profesor, horario del día, botón por clase y confirmaciones visuales | Katherine / Cristóbal / Iván | Alta |
| Vista de Horarios del Profesor | Calendario semanal con días, bloques por clase, materia/grupo, resaltado del día actual y diseño responsive | Katherine / Cristóbal / Iván | Alta |
| Implementar lógica de registro de asistencia | Endpoint de registro con validación de rol, horario, duplicados, timestamp y respuesta al frontend | Iván / Patricio / Juan Marco | Alta |
| Validación de horarios de clase | Función reutilizable para verificar día/hora actual vs horario, con margen de tolerancia | Iván / Patricio / Juan Marco | Alta |
| Implementar consulta de historial de asistencias | Endpoint con filtro por rango de fechas, ordenamiento y paginación | Iván / Patricio / Juan Marco | Alta |
| Implementar creación de solicitudes de justificación | Endpoint para enviar solicitud de justificación con validaciones de rol, estado y duplicados | Iván / Patricio / Juan Marco | Alta |
| Consulta de solicitudes de justificación enviadas | Endpoint para listar solicitudes del profesor filtradas por usuario, fecha y estado | Iván / Patricio / Juan Marco | Media |
| Validación de datos en solicitudes de justificación | Validar fecha, motivo no vacío, longitud máxima y no duplicados por fecha | Iván / Patricio / Juan Marco | Media |
| Creación de índices para optimizar consultas de asistencias | Índices en tabla Asistencia (profesor, fecha, estado) | Juan Marco / Iván | Media |
| Validación de reglas para evitar duplicados de asistencia | UniqueConstraint, migración y verificación de bloqueo | Juan Marco / Iván | Alta |
| Pruebas QA del módulo completo | Pruebas funcionales y de validación de registro, justificaciones e historial | Juan Marco | Alta |

---

## 4. Trabajo Completado

| Tarea | Responsable | Estado |
|-------|-------------|--------|
| Diseñar layout de la página de registro de asistencia | Katherine / Cristóbal | Completado |
| Mostrar información básica del profesor | Katherine / Cristóbal | Completado |
| Mostrar horario del día correspondiente al profesor | Katherine / Cristóbal | Completado |
| Agregar botón Registrar asistencia por cada clase programada | Katherine / Cristóbal | Completado |
| Mostrar confirmación visual cuando una asistencia se registre | Katherine / Cristóbal | Completado |
| Mostrar mensaje si la asistencia ya fue registrada | Katherine / Cristóbal | Completado |
| Validar visualmente que no se pueda registrar asistencia fuera del horario permitido | Katherine / Cristóbal | Completado |
| Aplicar estilos consistentes con el layout general del sistema (Frontend) | Katherine / Cristóbal | Completado |
| Crear vista de horario semanal | Katherine / Cristóbal | Completado |
| Mostrar días de la semana | Katherine / Cristóbal | Completado |
| Mostrar bloques de horario por clase | Katherine / Cristóbal | Completado |
| Mostrar materia y grupo en cada bloque | Katherine / Cristóbal | Completado |
| Resaltar el día actual | Katherine / Cristóbal | Completado |
| Adaptar diseño para dispositivos móviles | Katherine / Cristóbal | Completado |
| Integrar estilos con el resto del sistema | Katherine / Cristóbal | Completado |
| Crear endpoint o vista para registrar asistencia | Iván / Juan Marco | Completado |
| Validar que el usuario tenga rol de profesor | Juan Marco | Completado |
| Obtener horario correspondiente al profesor |  Juan Marco | Completado |
| Verificar que la asistencia corresponde al día y hora actual | Iván / Juan Marco | Completado |
| Validar que no exista una asistencia registrada previamente para esa clase | Iván | Completado |
| Guardar la asistencia en la base de datos | Iván | Completado |
| Registrar timestamp exacto del registro | Patricio | Completado |
| Retornar respuesta de confirmación al frontend |  Patricio | Completado |
| Consultar horario del profesor en la base de datos | Juan Marco | Completado |
| Verificar coincidencia entre día actual y horario asignado | Patricio | Completado |
| Verificar que la hora actual esté dentro del rango permitido | Juan Marco | Completado |
| Definir margen de tolerancia para registro de asistencia | Juan Marco | Completado |
| Generar error si el registro se intenta fuera del horario permitido | Iván / Juan Marco | Completado |
| Crear función reutilizable para validación de horarios | Iván / Juan Marco | Completado |
| Crear endpoint para obtener asistencias del profesor |Patricio | Completado |
| Permitir filtro por rango de fechas | Patricio | Completado |
| Ordenar resultados por fecha | Patricio  | Completado |
| Preparar datos para consumo del frontend | Patricio | Completado |
| Manejar paginación en caso de muchos registros | Iván | Completado |
| Crear endpoint para enviar solicitud de justificación | Iván | Completado |
| Validar que el usuario sea profesor | Juan Marco | Completado |
| Asociar la solicitud con la asistencia o fecha correspondiente | Iván | Completado |
| Guardar motivo o descripción de la justificación | Iván  | Completado |
| Registrar fecha de envío de la solicitud | Iván / Patricio / Juan Marco | Completado |
| Guardar estado inicial de la solicitud (pendiente) | Iván | Completado |
| Crear endpoint para obtener solicitudes del profesor | Iván / Patricio| Completado |
| Filtrar solicitudes por usuario autenticado | Iván / Patricio | Completado |
| Mostrar fecha de la ausencia | Iván / Patricio | Completado |
| Mostrar motivo de la justificación | Iván | Completado |
| Mostrar estado actual de la solicitud | Iván | Completado |
| Ordenar resultados por fecha de envío | Iván | Completado |
| Validar que exista una fecha asociada a la solicitud | Iván | Completado |
| Validar que el motivo de la justificación no esté vacío | Iván | Completado |
| Limitar longitud máxima del mensaje | Iván | Completado |
| Verificar que no exista una solicitud duplicada para la misma fecha | Iván | Completado |
| Retornar errores claros al frontend en caso de validación fallida | Iván | Completado |
| Crear índice para profesor en tabla Asistencia | Juan Marco / Iván | Completado |
| Crear índice para fecha en tabla Asistencia | Juan Marco / Iván | Completado |
| Crear índice para estado en tabla Asistencia | Juan Marco / Iván | Completado |
| Validar impacto de los índices en consultas | Juan Marco / Iván | Completado |
| Definir combinación única de campos (profesor, fecha, horario) | Juan Marco / Iván | Completado |
| Crear UniqueConstraint en el modelo correspondiente | Juan Marco / Iván | Completado |
| Generar migración de Django | Juan Marco / Iván | Completado |
| Aplicar migración en base de datos | Juan Marco / Iván | Completado |
| Verificar que el sistema bloquee registros duplicados | Juan Marco / Iván | Completado |
| Pruebas funcionales del registro de asistencia | Juan Marco | Completado |
| Pruebas de validación contra registros duplicados | Juan Marco | Completado |
| Pruebas funcionales de envío de solicitudes de justificación | Juan Marco | Completado |
| Pruebas de validación de formulario de justificación | Juan Marco | Completado |
| Pruebas de consulta de historial de asistencias | Juan Marco | Completado |
| Pruebas de consulta de solicitudes de justificación | Juan Marco | Completado |

---

## 5. Trabajo Pendiente

| Tarea | Motivo | Acción Siguiente |
|-------|--------|------------------|
| Aprobación y rechazo de incidencias desde Jefatura | Fuera del alcance del Sprint 2; el flujo de resolución requiere el módulo de Jefatura activo | Sprint 3 |
| Vista de gestión de asistencias para Jefatura | No implementada; Jefatura no puede consultar ni modificar asistencias aún | Sprint 3 |
| Vista de solicitudes de justificación pendientes para Jefatura | Sin vista de revisión ni acciones de aprobación/rechazo | Sprint 3 |
| Visualización de solicitudes enviadas en el dashboard del profesor | La lista de incidencias del profesor no tiene vista propia | Sprint 3 |
| Módulo de Contabilidad / Nómina (RF-04 al RF-10) | Fuera del alcance del Sprint 2 | Sprint 4 |
| Recibo de nómina en PDF (RF-10) | Requiere motor de cálculo completo | Sprint 4 o 5 |

---

## 6. Problemas o Riesgos Encontrados

- El cálculo de RETARDO depende de la diferencia entre `timezone.now()` y el inicio del horario. Se identificó que el servidor debe estar configurado con zona horaria correcta (`America/Mexico_City`) para evitar discrepancias; esto está configurado en `settings.py`.
- El endpoint `justificar_asistencia` maneja dos flujos distintos (profesor vs. jefatura/administrador) dentro de la misma vista. Se recomienda separar en vistas distintas en un sprint futuro para reducir complejidad.
- La app `Asistencias/services/` no tenía `__init__.py` con re-exports explícitos al inicio del sprint, lo que generó errores de importación al consumirla desde `Profesores/views.py`. Se resolvió agregando los re-exports correspondientes.
- Los tests de QA se ejecutaron manualmente sobre base de datos de desarrollo. Aún no existe suite automatizada con `pytest` o `django.test.TestCase`; se recomienda implementarla en el Sprint 3.

---

## 7. Métricas del Sprint

- **Tareas Planeadas:** 65 (Frontend: 15 · Backend: 35 · DBA: 9 · QA: 6) — ítems de checklist del tablero Trello
- **Tareas Completadas:** 65 (100%)
- **Tareas Restantes:** 0

---

## 8. Resumen de la Revisión del Sprint

> Se entregó el módulo completo de asistencias para el rol Profesor. El profesor puede acceder a su vista de registro de asistencia, donde visualiza únicamente las clases programadas para el día actual. Al presionar el botón de registro, el sistema valida la ventana horaria permitida (15 min antes, 30 min después de la entrada; 10 min antes, 30 min después de la salida), registra el timestamp exacto, determina automáticamente si la asistencia es puntual o con retardo, y bloquea registros duplicados. El dashboard del profesor muestra el horario semanal con estados visuales por clase (presente, retardo, falta, justificada, pendiente) y KPIs del período vigente (horas trabajadas, salario estimado, estadísticas). El sistema de justificación permite al profesor enviar solicitudes de incidencia sobre faltas, que quedan en estado PENDIENTE hasta su resolución por jefatura. La base de datos cuenta con índices y restricción de unicidad en horarios para garantizar integridad y rendimiento.

---

## 9. Retrospectiva del Sprint

**¿Qué salió bien?**

- La capa de servicios (`Asistencias/services/`) permitió centralizar la lógica de negocio compleja (períodos, estados, estadísticas) y reutilizarla desde múltiples vistas sin duplicación.
- La separación entre `verificar_entrada` y `verificar_salida` como funciones reutilizables en `Profesores/utils.py` mantuvo el código limpio y fácil de testear.
- Los índices y la `UniqueConstraint` se agregaron de forma proactiva en la misma migración, evitando una deuda técnica que habría crecido con el volumen de datos.

**¿Qué se puede mejorar?**

- El endpoint `justificar_asistencia` mezcla lógica para dos roles distintos. Se recomienda refactorizar en vistas separadas para mejorar mantenibilidad.
- Los tests siguen siendo manuales. Sería conveniente iniciar la suite automatizada con `django.test.TestCase` desde el comienzo del Sprint 3.
- El margen de tolerancia está definido como constante hardcodeada en `utils.py` (15/30 min entrada, 10/30 min salida). Se recomienda moverlo a configuración del sistema o al modelo de Plantel para mayor flexibilidad.

**Acciones para el próximo sprint:**

- Sprint 3 — Gestión de Asistencias por Jefatura: implementar todas las acciones del rol Jefatura sobre asistencias (consulta global, filtros, correcciones manuales, aprobación/rechazo de incidencias, cancelación institucional de clases).
- Agregar la vista de solicitudes de justificación enviadas al dashboard del Profesor para cerrar el ciclo de comunicación.
- Comenzar la suite de tests automatizados con al menos cobertura del módulo de Asistencias.