# STX-SPRINT-1-REPORT-v1.0
### Reporte de Sprint 1 — Saltix

---

## 1. Información del Sprint

- **Número de Sprint:** 1
- **Nombre del Sprint:** Arquitectura Base y Administración
- **Duración del Sprint:** 2 semanas
- **Fechas del Sprint:** 02/03/2026 – 15/03/2026
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

> Establecer la arquitectura base del sistema Saltix: definir el esquema completo de base de datos, implementar el sistema de autenticación y control de acceso por roles (RBAC), desarrollar el dashboard funcional del administrador con gestión de usuarios, planteles y departamentos, y crear las pantallas iniciales para cada rol (administrador, jefatura y profesor).

---

## 3. Trabajo Planeado (Sprint Backlog)

| Tarea / Historia de Usuario | Descripción | Responsable | Prioridad |
|-----------------------------|-------------|-------------|-----------|
| Diseño y migración de la base de datos | Modelado de todas las entidades del sistema: Usuario, Rol, Permiso, RolPermiso, Departamento, Plantel, Profesor, Horario, Asistencia, Incidencia, Nómina, Periodo, entre otras | Juan Marco Gosselin | Alta |
| Sistema de autenticación y RBAC | Login por email, redirección por rol, decoradores `requiere_rol` y `requiere_permiso` para control de acceso granular | Patricio Dávila / Juan Marco Gosselin | Alta |
| Dashboard de administración | Panel con métricas de empleados, planteles, departamentos y bitácora de actividad reciente | Patricio Dávila / Diego Serna | Alta |
| CRUD de usuarios y roles | Crear y editar usuarios asignando rol, datos de profesor y jefatura si corresponde | Patricio Dávila | Alta |
| Gestión de planteles y departamentos | Crear, editar y eliminar planteles y departamentos desde el panel admin | Patricio Dávila | Media |
| Pantallas iniciales por rol | Vista de dashboard básica para los roles: Jefatura y Profesor | Diego Serna / Katherine Guareño | Media |
| Sistema de notificaciones internas | Modelo `Notificacion` y marcado de leídas desde el panel admin | Patricio Dávila | Media |
| Bitácora de auditoría | Modelo `BitacoraAuditoria` con registro de cambios por usuario, fecha y valor anterior/nuevo | Juan Marco Gosselin | Media |
| Documentación base del proyecto | README, backlog de requisitos, contributing, diagrama ER, diagrama de componentes, wireframes y SCM | Ivan Ramos / Juan Marco Gosselin | Alta |

---

## 4. Trabajo Completado

| Tarea | Responsable | Estado |
|-------|-------------|--------|
| Esquema completo de base de datos (20+ modelos, 16 migraciones) | Juan Marco Gosselin | Completado |
| Autenticación por email con redirección por rol | Patricio Dávila / Juan Marco Gosselin | Completado |
| Decoradores RBAC (`requiere_rol`, `requiere_permiso`) | Juan Marco Gosselin | Completado |
| Dashboard del administrador con métricas y bitácora | Patricio Dávila / Diego Serna | Completado |
| CRUD de usuarios (crear, editar, asignación de rol y datos de profesor/jefatura) | Patricio Dávila | Completado |
| Gestión de permisos por rol desde panel admin | Patricio Dávila | Completado |
| CRUD de planteles | Patricio Dávila | Completado |
| CRUD de departamentos (con asignación de jefe y plantel) | Patricio Dávila | Completado |
| Sistema de notificaciones internas (crear, marcar leída / todas leídas) | Patricio Dávila | Completado |
| Modelo de bitácora de auditoría | Juan Marco Gosselin | Completado |
| Pantalla inicial del rol Jefatura | Diego Serna / Katherine Guareño | Completado |
| Pantalla inicial del rol Profesor | Diego Serna / Katherine Guareño | Completado |
| Backlog de requisitos (24 RF / 6 RNF) | Ivan Ramos / Juan Marco Gosselin | Completado |
| Diagrama entidad-relación, diagrama de componentes y wireframes | Juan Marco Gosselin / Katherine Guareño | Completado |
| Documentación SCM Fases 3 y 4, README y contributing | Ivan Ramos | Completado |

---

## 5. Trabajo Pendiente

| Tarea | Motivo | Acción Siguiente |
|-------|--------|------------------|
| Lógica funcional del dashboard de Jefatura | El sprint priorizó la arquitectura; la pantalla inicial existe pero sin datos reales | Implementar en Sprint 2 junto con el módulo de asistencias |
| Lógica funcional del dashboard de Profesor | Mismo motivo que Jefatura | Implementar en Sprint 2 una vez que el módulo de asistencias esté activo |
| Módulo de Asistencias (RF-02, RF-03, RF-08, RF-21) | Fuera del alcance del Sprint 1 | Sprint 2 |
| Módulo de Contabilidad / Nómina (RF-04 al RF-10, RF-17 al RF-19) | Fuera del alcance del Sprint 1 | Sprint 3 |
| Recibo de nómina en PDF (RF-10) | Requiere motor de cálculo completo | Sprint 3 o 4 |

---

## 6. Problemas o Riesgos Encontrados

- La app `admin` de Django tiene un nombre reservado que genera conflicto con el módulo personalizado `admin/`; se resolvió registrando el módulo como `panel-admin/` en las URLs principales.
- El modelo `Usuario` extiende `AbstractBaseUser` con autenticación por email, lo que requirió un `UsuarioManager` personalizado y configuración explícita de `USERNAME_FIELD`. Esto añadió complejidad inicial al setup del proyecto.
- La app `admin` no generó migraciones propias porque sus vistas consumen modelos de otros módulos directamente, lo que es correcto pero puede confundir en revisiones de código.

---

## 7. Métricas del Sprint

- **Tareas Planeadas:** 53 (Frontend: 9 · Backend: 33 · DBA: 6 · QA: 5)
- **Tareas Completadas:** 53 (100%)
- **Tareas Restantes:** 0

---

## 8. Resumen de la Revisión del Sprint

> Se presentó el sistema con autenticación funcional y redirección automática según el rol del usuario. El administrador accede a un dashboard operativo que muestra métricas de empleados, planteles, departamentos y actividad reciente de la bitácora. Desde el panel es posible crear y editar usuarios con asignación de rol, gestionar permisos por rol, administrar planteles y departamentos. Jefatura y Profesor cuentan con sus pantallas iniciales registradas y accesibles. La base de datos refleja el modelo completo del sistema con todos sus módulos (usuarios, profesores, asistencias, contabilidad, jefatura), garantizando que el Sprint 2 pueda construir funcionalidad sobre cimientos ya migrados y documentados.

---

## 9. Retrospectiva del Sprint

**¿Qué salió bien?**

- El diseño de la base de datos se realizó de forma integral desde el inicio, cubriendo todos los módulos del sistema (no solo los del Sprint 1), lo que evitará refactorizaciones mayores en sprints futuros.
- La implementación del RBAC mediante decoradores reutilizables (`requiere_rol`, `requiere_permiso`) resultó limpia y fácil de aplicar en cualquier vista sin duplicar lógica.
- La documentación fue generada en paralelo al código (backlog, ER, componentes, wireframes, SCM), manteniendo los artefactos actualizados desde el inicio.

**¿Qué se puede mejorar?**

- Las pantallas iniciales de Jefatura y Profesor quedaron sin lógica real; sería conveniente acordar desde el inicio qué datos mínimos debe mostrar cada dashboard para no entregar vistas completamente vacías.
- El módulo `admin` personalizado generó confusión por el nombre reservado de Django; se recomienda documentar este detalle en el README para evitar errores de configuración en nuevos entornos.

**Acciones para el próximo sprint:**

- Iniciar el Sprint 2 con el módulo de Asistencias (RF-02, RF-03, RF-08, RF-20, RF-21) y conectar los resultados al dashboard de Jefatura.
- Definir los datos que debe mostrar el dashboard del Profesor para que no quede como pantalla vacía al final del Sprint 2.