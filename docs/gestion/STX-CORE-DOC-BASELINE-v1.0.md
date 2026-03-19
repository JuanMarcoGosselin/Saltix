# STX-CORE-DOC-BASELINE-v1.0
# Documento de Línea Base — Saltix
# Sistema de Control de Asistencia y Cálculo de Nómina

**Estándar de referencia:** IEEE 828 (SCMP) / IEEE 830 (SRS)  
**Versión:** 1.0  
**Fecha de congelamiento:** 2026-03-18  
**Estado:** CONGELADO — Línea Base Funcional  
**Repositorio:** https://github.com/JuanMarcoGosselin/Saltix  
**Elaboró (SCMP):** Iván Ramos de la Torre  

---

## Historial de Versiones

| Versión | Fecha | Autor | Descripción |
|---------|-------|-------|-------------|
| 1.0 | 2026-03-18 | Iván Ramos de la Torre | Emisión inicial — Línea Base Sprint 1 |

---

## Equipo de Desarrollo — Sprint 1

| Nombre | Rol | Firma |
|--------|-----|-------|
| Iván Ramos de la Torre | Team Leader / AC | ___________________________ |
| Juan Marco Gosselin Gamboa | QA / Backend / DBA / ACM | ___________________________ |
| Patricio Dávila Assad | Backend | ___________________________ |
| Diego Cristóbal Gael Serna Domínguez | Frontend | ___________________________ |
| Katherine Guadalupe Guareño Flores | Frontend / Design | ___________________________ |

---

## FASE 1: Plan de Administración de la Configuración (SCMP)

*Basado en el estándar IEEE 828-2012. Establece las reglas de gobierno del universo de configuración del proyecto Saltix.*

---

### 1.1 Organización y Responsabilidades

#### Administrador de la Configuración (AC)

El Administrador de la Configuración es el guardián del repositorio y el responsable de garantizar la integridad, trazabilidad y consistencia de todos los SCIs a lo largo del ciclo de vida del proyecto.

| Campo | Titular | Responsabilidades Clave |
|-------|---------|------------------------|
| Administrador de la Configuración (AC) | **Iván Ramos de la Torre** | Administrar ramas y reglas de protección en GitHub; revisar y aprobar PRs antes del merge a `main`; mantener el inventario de SCIs; coordinar el proceso de congelamiento de líneas base. |
| Administrador de la Configuración del Proyecto (ACM) | **Juan Marco Gosselin Gamboa** | Gestión de migraciones de BD (rol DBA); ejecución de la suite de QA; soporte técnico al AC en la revisión de PRs que afecten modelos críticos. |

---

#### Comité de Control de Cambios (CCB)

El CCB es el órgano colegiado con autoridad para aceptar, rechazar o diferir solicitudes de cambio que afecten la línea base congelada.

| Miembro | Rol en el Proyecto | Voto |
|---------|--------------------|------|
| Iván Ramos de la Torre | Team Leader / AC | ✅ Sí — Voto de desempate |
| Juan Marco Gosselin Gamboa | QA / Backend / DBA / ACM | ✅ Sí |
| Patricio Dávila Assad | Backend | ✅ Sí |

> **Quórum mínimo:** 2 de 3 miembros.  
> **Aprobación:** Mayoría simple (2 votos a favor).  
> **Urgencia:** En caso de bug crítico en producción, el AC (Iván Ramos) y el ACM (Juan Marco Gosselin) pueden aprobar un hotfix de forma bilateral sin esperar al CCB completo, documentando la decisión dentro de las 24 horas siguientes.

##### Proceso de solicitud de cambio ante el CCB

1. El desarrollador abre un **Issue** en GitHub (etiqueta `change-request`) describiendo el cambio, su justificación y los SCIs afectados.
2. El CCB evalúa el impacto en la línea base, el backlog y los sprints en curso.
3. El CCB emite su resolución (**Aprobado / Rechazado / Diferido**) como comentario oficial en el Issue, con la firma de los votantes.
4. Si el cambio es aprobado, se crea la rama correspondiente siguiendo la política de integración (ver sección 1.3).

---

### 1.2 Herramientas y Entorno

#### 2.1 Repositorio Oficial

| Campo | Detalle |
|-------|---------|
| Plataforma | GitHub |
| URL | https://github.com/JuanMarcoGosselin/Saltix |
| Rama principal (producción) | `main` |
| Modelo de ramificación | Git Flow simplificado (ver sección 1.4) |
| Rama protegida | `main` — merge directo deshabilitado; requiere pull request aprobado |

#### 2.2 Herramienta de Seguimiento

| Campo | Detalle |
|-------|---------|
| Plataforma | Trello + GitHub Issues |
| URL Trello | https://trello.com/b/ZWz953Fq/saltix |
| Uso | Sprints, backlog, asignación por área (Frontend, Backend, DBA, QA) y checklists |
| Gestión de bugs | Issues GitHub para defectos técnicos; tarjetas Trello para seguimiento general |

#### 2.3 Entorno de Base de Datos

| Campo | Detalle |
|-------|---------|
| Motor | SQLite 3.x (incluido en Python 3.12 estándar) |
| Versión Python | 3.12 |
| Versión Django | 6.0.3 |
| Archivo de BD | `db.sqlite3` — raíz del proyecto |
| Ubicación | Local en la máquina de cada desarrollador |
| ORM | Django ORM — prohibida la edición manual del archivo `db.sqlite3` |
| Zona horaria | `America/Mexico_City` |
| Precisión decimal | `DecimalField(max_digits=12, decimal_places=4)` para campos monetarios; prohibido `FloatField` |

**Reglas de migraciones:**

| Regla | Descripción |
|-------|-------------|
| Generación | Solo el DBA (Juan Marco Gosselin) genera y versiona archivos de migración |
| Revisión | Toda migración que modifique modelos críticos (`Nomina`, `Asistencia`, `Usuario`) debe ser revisada por el CCB antes del merge |
| Respaldo previo | Conservar copia de `db.sqlite3` antes de ejecutar `python manage.py migrate` en entornos no limpios |
| Rollback | `python manage.py migrate <app> <migration_anterior> --fake`, restaurar respaldo y corregir |

#### 2.4 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Lenguaje backend | Python | 3.12 |
| Framework web | Django | 6.0.3 |
| Base de datos | SQLite | 3.x |
| Control de versiones | Git + GitHub | 2.x |
| Gestión de dependencias | pip + `requirements.txt` | 24.x |
| Entorno virtual | venv | Estándar Python |

---

### 1.3 Política de Integración — Paso a Producción

> **Ningún desarrollador puede fusionar código a la rama `main` sin que antes se cumplan las tres condiciones siguientes:**

| # | Condición | Descripción | Responsable de verificar |
|---|-----------|-------------|--------------------------|
| C1 | Revisión de pares aprobada | Al menos una aprobación explícita de un miembro distinto al autor. Si el PR afecta modelos de BD, lógica de nómina o RBAC, debe ser validado por el AC (Iván Ramos). | AC / Iván Ramos de la Torre |
| C2 | Suite de QA completada sin fallos | Todos los casos de prueba de `STX-CORE-DOC-CASOS-PRUEBA-v1.0.xlsx` del módulo modificado deben ejecutarse y reportarse como **PASS**. No se permite merge con casos FAIL o sin ejecutar. | QA / Juan Marco Gosselin Gamboa |
| C3 | Ausencia de conflictos de migración | Si el PR incluye nuevas migraciones Django, deben ejecutarse exitosamente sobre BD limpia (`python manage.py migrate`) sin errores. El DBA deja constancia como comentario en el PR. | DBA / Juan Marco Gosselin Gamboa |

---

### 1.4 Modelo de Ramificación (Git Flow Simplificado)

```
main
 └── develop
      ├── feature/stx-<modulo>-<descripcion>
      ├── fix/stx-<modulo>-<descripcion>
      └── hotfix/stx-<modulo>-<descripcion>   →  merge directo a main (solo emergencias, CCB bilateral)
```

| Rama | Propósito | Quién crea | Merge destino |
|------|-----------|------------|---------------|
| `main` | Código estable — línea base | — | — |
| `develop` | Integración continua del sprint | AC / Team Leader | `main` (cierre de sprint, vía PR) |
| `feature/*` | Nueva funcionalidad | Cualquier desarrollador | `develop` (vía PR con revisión) |
| `fix/*` | Corrección de defecto | Desarrollador asignado | `develop` (vía PR) |
| `hotfix/*` | Corrección urgente en producción | AC / Team Leader | `main` y `develop` (aprobación bilateral CCB) |

**Convención de commits (Conventional Commits):**

```
<tipo>(<módulo>): <descripción en imperativo, máximo 72 caracteres>

Tipos válidos: feat | fix | docs | refactor | test | chore

Ejemplos:
  feat(asistencias): agregar validación de tolerancia en registro de entrada
  fix(admin): corregir conflicto de nombre reservado en urls.py
  chore(db): generar migración para modelo SolicitudCorreccion
  docs(scmp): emitir SCMP v1.0 línea base Sprint 1
```

---

## FASE 2: Congelamiento de la Línea Base Funcional

*La Línea Base Funcional es la "fotografía" oficial de los requerimientos aprobados al 18 de marzo de 2026.*

---

### 2.1 Inventario de la Línea Base (SCIs Congelados)

| SCI | Artefacto | Descripción | Estado QA | Versión / Ubicación |
|-----|-----------|-------------|:---------:|---------------------|
| SCI-01 | Código fuente Sprint 1 (53/53 tareas) | Apps Django: core, users, Profesores, Asistencias, Contabilidad, admin, jefatura | ✅ PASS | Commit `main` — `/` |
| SCI-02 | Migraciones (16 en 6 apps) | Historial de migraciones bajo control del DBA | ✅ PASS | v1.0 — `<app>/migrations/` |
| SCI-03 | `STX-CORE-REQ-BACKLOG-v1.0.md` | Backlog de 24 RF y 6 RNF (IEEE 830) | ✅ Revisado | v1.0 — `docs/planning/` |
| SCI-04 | `STX-DB-DER-MODELO-v1.0.md` | Diagrama Entidad-Relación (20+ modelos) | ✅ Revisado | v1.0 — `docs/diseno/` |
| SCI-05 | `STX-CORE-ARC-COMPONENTES-v1.0.md` | Diagrama de Componentes / Arquitectura Django | ✅ Revisado | v1.0 — `docs/diseno/` |
| SCI-06 | Wireframes (login, admin, jefatura, profesor) | Prototipos HTML de alta fidelidad | ✅ Revisado | v1.0 — `docs/diseno/wireframes/` |
| SCI-07 | `STX-CORE-RSK-MATRIZ-RIESGOS-v1.0.md` | Matriz de 10 riesgos identificados | ✅ Revisado | v1.0 — `docs/gestion/` |
| SCI-08 | `STX-CONFIG-SCI-INVENTORY-v1.0.md` | Inventario oficial de SCIs | ✅ Revisado | v1.0 — `docs/` |
| SCI-09 | `STX-CORE-DOC-SCMP-v1.0.md` | Plan de Administración de la Configuración | ✅ Revisado | v1.0 — `docs/gestion/` |
| SCI-10 | `STX-CORE-DOC-CASOS-PRUEBA-v1.0.xlsx` | Casos de prueba Sprint 1 | ✅ PASS | v1.0 — `docs/gestion/` |
| SCI-11 | `STX-SPRINT-1-REPORT-v1.0.md` | Reporte Sprint 1 | ✅ Emitido | v1.0 — `docs/planning/sprints/` |
| SCI-12 | `requirements.txt` | Dependencias: Django 6.0.3, sqlparse, tzdata, asgiref | ✅ Revisado | v1.0 — `/requirements.txt` |
| SCI-13 | `settings.py` | Configuración base (zona horaria, BD, apps instaladas) | ✅ Revisado | v1.0 — `Saltix/settings.py` |

---

### 2.2 Alcance Funcional de la Línea Base

| Módulo | Entregable validado en Sprint 1 |
|--------|--------------------------------|
| Base de Datos | Esquema completo con 20+ modelos en apps `core`, `users`, `Profesores`, `Asistencias`, `Contabilidad` y `jefatura`. |
| Sistema RBAC | Autenticación por email, decoradores `requiere_rol` y `requiere_permiso`, redirección automática por rol. |
| Dashboard Administración | Métricas, CRUD de usuarios, roles, permisos, planteles, departamentos, notificaciones y bitácora de auditoría. |
| Pantallas Base | Dashboard de Jefatura y Profesor (estructura base, sin lógica funcional — pendiente Sprint 2). |
| Documentación | Backlog, diagramas, wireframes, matriz de riesgos, SCMP y reporte de sprint. |

---

### 2.3 Matriz de Trazabilidad — 5 Requisitos Críticos

| ID Req. | Descripción Breve | Módulo de Código Afectado | ID Caso de Prueba | Estado |
|---------|-------------------|--------------------------|-------------------|--------|
| RF-01 | Registro de Empleados con expediente único | `Profesores/models.py → Profesor`; `users/models.py → CustomUser` | CP-RF01-001, CP-RF01-002 | Congelado |
| RF-02 | Captura de Asistencia (reloj checador virtual) | `Asistencias/models.py → Asistencia`; `core/models.py → Configuracion` | CP-RF02-001, CP-RF02-002, CP-RF02-003 | Congelado |
| RF-04 | Motor de Cálculo de Nómina | `Contabilidad/models.py → Nomina, DetalleNomina, Periodo`; `Contabilidad/views.py` | CP-RF04-001, CP-RF04-002 | Congelado |
| RNF-01 | Control de Acceso por Roles (RBAC) | `users/models.py → Rol, Permiso`; `core/decorators.py` | CP-RNF01-001, CP-RNF01-002 | Congelado |
| RF-07 | Secuencia Obligatoria de Cálculo (base→percepciones→impuestos→deducciones→neto) | `Contabilidad/models.py → CatalogoConcepto`; `Contabilidad/views.py` (motor de nómina) | CP-RF07-001 | Congelado |

---

## FASE 3: Proceso de Control de Cambios

*Cualquier modificación a la Línea Base congelada deberá seguir este proceso formal sin excepciones.*

---

### 3.1 Formulario de Petición de Cambio (Change Request)

Se implementa como **Issue en GitHub** (etiqueta `change-request`) y tarjeta en la lista **Change Requests** del tablero de Trello. Los campos marcados con (*) son obligatorios.

---

**FORMULARIO DE PETICIÓN DE CAMBIO — STX-CR-YYYY-NNN**

| Campo | Valor |
|-------|-------|
| **CR-ID (*)** | `STX-CR-[AÑO]-[NNN]`  Ej: `STX-CR-2026-001` |
| **Fecha de Solicitud (*)** | DD/MM/AAAA |
| **Solicitante (*)** | Nombre completo y rol |
| **Descripción del Cambio (*)** | Qué se desea cambiar, añadir o eliminar del sistema o documentación. |
| **Justificación Comercial (*)** | Por qué es necesario y qué riesgo se corre si no se aplica. |
| **Nivel de Urgencia (*)** | ☐ Crítico (bloquea producción)  ☐ Alto (afecta core)  ☐ Medio  ☐ Bajo |
| **SCIs Afectados (*)** | Lista de SCI-IDs del Inventario (Sección 2.1) que se verían modificados. |
| **Estimación de Esfuerzo** | Horas de desarrollo + prueba + documentación. |
| **Impacto en Calendario** | Días adicionales al sprint actual o siguiente. |
| **Módulos de Código Impactados** | Archivos Django específicos (`models.py`, `views.py`, `migrations/`, etc.) |
| **Alternativas Evaluadas** | Otras soluciones exploradas y por qué se descartaron. |
| **Decisión del CCB** | ☐ APROBADO  ☐ RECHAZADO  ☐ DIFERIDO  ☐ REQUIERE MÁS INFORMACIÓN |
| **Fecha de Resolución del CCB** | DD/MM/AAAA — con firmas de los miembros que votaron. |

---

### 3.2 Flujo de Análisis de Impacto

| # | Paso | Descripción | Responsable |
|---|------|-------------|-------------|
| 1 | Apertura del Issue / Ticket CR | El solicitante abre Issue en GitHub (etiqueta `change-request`) y tarjeta en Trello con todos los campos del formulario. | Solicitante |
| 2 | Notificación al CCB | El AC (Iván Ramos) notifica al CCB. Plazo máximo de respuesta: 48 horas. | AC / Iván Ramos |
| 3 | Análisis de Impacto Técnico | El ACM (Juan Marco) analiza los SCIs afectados, estima esfuerzo real y determina riesgos de regresión. | ACM / Juan Marco Gosselin |
| 4 | Reunión del CCB | Los 3 miembros votan. Quórum de 2 y mayoría simple. Resultado documentado en el Issue de GitHub. | CCB completo |
| 5 | Notificación de Resolución | El AC notifica la decisión al solicitante y actualiza el estado del ticket. | AC / Iván Ramos |
| 6 | Apertura de Rama de Cambio | Si aprobado, se crea rama `change/STX-CR-YYYY-NNN` desde la última versión estable de `main`. | Desarrollador asignado |
| 7 | Implementación y Pruebas | Se implementa el cambio. El QA (Juan Marco) ejecuta la suite del módulo afectado. | Desarrollador + QA |
| 8 | Pull Request + Code Review | Se crea PR hacia `main` con referencia al CR-ID, cumpliendo C1 + C2 + C3 (Sección 1.3). | Desarrollador + Revisor |
| 9 | Merge y Etiquetado | El AC fusiona el PR y crea nuevo tag Git si el cambio altera la Línea Base. | AC / Iván Ramos |
| 10 | Actualización de Documentación | Los SCIs afectados se actualizan con nuevo número de versión. El Inventario (SCI-08) se actualiza. | Desarrollador + AC |
| 11 | Cierre del Ticket | El AC cierra el Issue en GitHub y mueve la tarjeta a **CRs Cerrados** en Trello. | AC / Iván Ramos |

---

## FASE 4: Acta de Congelamiento — Línea Base Sprint 1

**Proyecto:** Saltix — Sistema de Control de Asistencia y Cálculo de Nómina  
**Línea Base:** Sprint 1 — Arquitectura Base y Administración  
**Versión congelada:** v1.0  
**Fecha de congelamiento:** 2026-03-18  
**Repositorio:** https://github.com/JuanMarcoGosselin/Saltix  

---

### 4.1 Declaración Formal de Congelamiento

Los suscritos, miembros del equipo de desarrollo del proyecto **SALTIX**, declaramos formalmente que los elementos de configuración listados en el Inventario de la Línea Base (Sección 2.1 de este documento), correspondientes al cierre del Sprint 1, han sido revisados, validados y aprobados como **Línea Base v1.0** del proyecto.

A partir del **18 de marzo de 2026**, ningún cambio puede realizarse sobre estos artefactos sin pasar por el proceso formal del CCB descrito en la Sección 1.1 y la Fase 3 de este documento.

---

### 4.2 Cláusula de Alcance

> **CLÁUSULA DE ALCANCE:** Cualquier funcionalidad, módulo, pantalla, reporte, integración o comportamiento del sistema **no descrito explícitamente** en los documentos enumerados en el Inventario de la Línea Base (Sección 2.1) se considera **FUERA DE ALCANCE** de la entrega comprometida para el Sprint 1 y requerirá una Petición de Cambio formal con aprobación del CCB y una renegociación de tiempos antes de ser incorporada al sistema.

---

### 4.3 Firmas de Aprobación

| Miembro | Rol | Firma | Fecha |
|---------|-----|-------|-------|
| Iván Ramos de la Torre | Team Leader / AC | ___________________________ | 2026-03-18 |
| Juan Marco Gosselin Gamboa | QA / Backend / DBA / ACM | ___________________________ | 2026-03-18 |
| Patricio Dávila Assad | Backend | ___________________________ | 2026-03-18 |
| Diego Cristóbal Gael Serna Domínguez | Frontend | ___________________________ | 2026-03-18 |
| Katherine Guadalupe Guareño Flores | Frontend / Design | ___________________________ | 2026-03-18 |

---

*Este documento forma parte de la Línea Base v1.0 del proyecto Saltix y está sujeto a control de configuración conforme a lo establecido en el estándar IEEE 828.*

*STX-CORE-DOC-BASELINE-v1.0 | Saltix | 18 de marzo de 2026*