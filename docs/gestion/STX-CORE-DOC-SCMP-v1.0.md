# STX-CORE-DOC-SCMP-v1.0
# Plan de Administración de la Configuración del Software (SCMP)
# Saltix — Sistema de Control de Asistencia y Cálculo de Nómina

**Estándar de referencia:** IEEE 828  
**Versión:** 1.0  
**Fecha de emisión:** 2026-03-18  
**Estado:** Línea Base — CONGELADO  

---

## Historial de Versiones

| Versión | Fecha | Autor | Descripción |
|---------|-------|-------|-------------|
| 1.0 | 2026-03-18 | Ivan Ramos de la Torre | Emisión inicial — Línea Base Sprint 1 |

---

## 1. Organización y Responsabilidades

### 1.1 Administrador de la Configuración (AC)

El **Administrador de la Configuración** es el guardián del repositorio y el responsable de garantizar la integridad, trazabilidad y consistencia de todos los elementos de configuración del software (SCIs) a lo largo del ciclo de vida del proyecto.

| Campo | Detalle |
|-------|---------|
| **Titular** | Iván Ramos de la Torre |
| **Rol en el equipo** | Team Leader |
| **Responsabilidades principales** | Administrar ramas y reglas de protección en GitHub; revisar y aprobar pull requests antes del merge a `main`; mantener el inventario de SCIs actualizado; ejecutar y verificar migraciones de base de datos; coordinar el proceso de congelamiento de líneas base |


---

### 1.2 Comité de Control de Cambios (CCB)

El CCB es el órgano colegiado con autoridad para aceptar, rechazar o diferir solicitudes de cambio que afecten la línea base congelada del proyecto.

#### Composición del CCB

| Miembro | Rol en el equipo | Voto |
|---------|-----------------|------|
| Ivan Ramos de la Torre | Team Leader | ✅ Voto |
| Juan Marco Gosselin Gamboa | QA / Backend / DBA | ✅ Voto |
| Patricio Dávila Assad | Backend | ✅ Voto |

> **Quórum mínimo:** 2 de 3 miembros deben estar presentes para que una votación sea válida.  
> **Aprobación:** Se requiere mayoría simple (2 votos a favor) para aceptar un cambio.  
> **Urgencia:** En caso de bug crítico en producción, el Administrador de la Configuración y el Team Leader pueden aprobar un hotfix de forma bilateral sin esperar al CCB completo, documentando la decisión en el acta correspondiente dentro de las 24 horas siguientes.

#### Proceso de solicitud de cambio

1. El desarrollador abre un **Issue** en el repositorio de GitHub describiendo el cambio propuesto, su justificación y los SCIs afectados.
2. El CCB evalúa el impacto en la línea base, el backlog y los sprints en curso.
3. El CCB emite su resolución (**Aprobado / Rechazado / Diferido**) como comentario oficial en el Issue, con la firma de los votantes.
4. Si el cambio es aprobado, se crea la rama correspondiente siguiendo la política de integración (ver sección 3).

---

## 2. Herramientas y Entorno

### 2.1 Repositorio Oficial

| Campo | Detalle |
|-------|---------|
| **Plataforma** | GitHub |
| **URL** | https://github.com/JuanMarcoGosselin/Saltix |
| **Rama principal (producción)** | `main` |
| **Modelo de ramificación** | Git Flow simplificado (ver sección 3) |
| **Rama protegida** | `main` — merge directo deshabilitado; requiere pull request aprobado |

### 2.2 Herramienta de Seguimiento de Tareas e Issues

| Campo | Detalle |
|-------|---------|
| **Plataforma** | Trello |
| **URL** | https://trello.com/b/ZWz953Fq/saltix |
| **Uso** | Gestión de sprints, backlog, asignación de tareas por área (Frontend, Backend, DBA, QA) y seguimiento de avance por checklist |
| **Gestión de bugs** | Issues de GitHub para defectos técnicos; tarjetas de Trello para incidencias de seguimiento general |

### 2.3 Entorno de Base de Datos

| Campo | Detalle |
|-------|---------|
| **Motor** | SQLite 3 (incluido en Python 3.12 estándar) |
| **Versión de Python** | 3.12 |
| **Versión de Django** | 6.0.3 |
| **Archivo de BD** | `db.sqlite3` — en la raíz del proyecto |
| **Ubicación del entorno** | **Local** en la máquina de cada desarrollador |
| **ORM** | Django ORM — todas las operaciones sobre la base de datos se realizan exclusivamente mediante migraciones y el ORM; se prohíbe la edición manual del archivo `db.sqlite3` |
| **Zona horaria configurada** | `America/Mexico_City` |
| **Precisión decimal** | `DecimalField` con `max_digits=12, decimal_places=4` para todos los campos monetarios (prohibido `FloatField` en cálculos financieros — ver RSK-01) |

#### Gestión de migraciones

| Regla | Descripción |
|-------|-------------|
| Generación | Solo el DBA (Juan Marco Gosselin) genera y versiona archivos de migración en ramas de desarrollo |
| Revisión | Toda migración que modifique modelos críticos (`Nomina`, `Asistencia`, `Usuario`) debe ser revisada por el CCB antes de mergearse |
| Respaldo previo | Antes de ejecutar `python manage.py migrate` en cualquier entorno que no sea desarrollo limpio, se debe conservar una copia del `db.sqlite3` anterior |
| Rollback | En caso de migración fallida: `python manage.py migrate <app> <migration_anterior> --fake`, restaurar respaldo y corregir (ver RSK-04) |

### 2.4 Stack Tecnológico Completo

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Lenguaje backend | Python | 3.12 |
| Framework web | Django | 6.0.3 |
| Base de datos | SQLite | 3.x (bundled) |
| Servidor ASGI/WSGI | Django dev server (desarrollo) | — |
| Control de versiones | Git + GitHub | 2.x |
| Gestión de dependencias | pip + `requirements.txt` | 24.x |
| Entorno virtual | venv | Estándar Python |

---

## 3. Política de Integración

### 3.1 Regla de Paso a Producción

> **Ningún desarrollador puede fusionar código a la rama `main` sin que antes se cumplan las siguientes tres condiciones:**
>
> **Condición 1 — Revisión de pares aprobada.**  
> El pull request debe contar con al menos una aprobación explícita de otro miembro del equipo distinto al autor. Si el cambio afecta modelos de base de datos, lógica de nómina o el sistema de control de acceso (RBAC), la revisión debe ser realizada o validada por el Administrador de la Configuración.
>
> **Condición 2 — Suite de QA completada sin fallos.**  
> Todos los casos de prueba definidos en `STX-CORE-DOC-CASOS-PRUEBA-v1.0.xlsx` correspondientes al módulo modificado deben haber sido ejecutados y reportados como **PASS** por el responsable de QA (Juan Marco Gosselin) en el mismo ciclo del pull request. No se permite merge con casos en estado FAIL o sin ejecutar.
>
> **Condición 3 — Ausencia de conflictos de migración.**  
> Si el PR incluye nuevas migraciones de Django, estas deben haber sido ejecutadas exitosamente sobre una base de datos limpia (`python manage.py migrate`) sin errores ni advertencias. El DBA debe dejar constancia de esto como comentario en el pull request antes de que se proceda al merge.

---

### 3.2 Modelo de Ramificación (Git Flow Simplificado)

```
main
 └── develop
      ├── feature/nombre-funcionalidad
      ├── fix/descripcion-del-bug
      └── hotfix/descripcion-urgente   →  merge directo a main (solo emergencias, aprobado por CCB)
```

| Rama | Propósito | Quién crea | Merge destino |
|------|-----------|------------|---------------|
| `main` | Código estable y aprobado — línea base | — | — |
| `develop` | Integración continua del sprint en curso | AC / Team Leader | `main` (al cierre del sprint, vía PR) |
| `feature/*` | Desarrollo de una funcionalidad nueva | Cualquier desarrollador | `develop` (vía PR con revisión) |
| `fix/*` | Corrección de defecto detectado en revisión | Desarrollador asignado | `develop` (vía PR) |
| `hotfix/*` | Corrección urgente sobre `main` | AC / Team Leader | `main` y `develop` (aprobación bilateral CCB) |

#### Convención de nombres de ramas

```
feature/stx-<modulo>-<descripcion-corta>
fix/stx-<modulo>-<descripcion-corta>
hotfix/stx-<modulo>-<descripcion-corta>

Ejemplos:
  feature/stx-asistencias-reloj-checador
  fix/stx-admin-conflicto-migracion
  hotfix/stx-rbac-acceso-no-autorizado
```

---

### 3.3 Convención de Commits

Todo commit debe seguir el formato:

```
<tipo>(<módulo>): <descripción en imperativo, máximo 72 caracteres>

Tipos válidos:
  feat     → nueva funcionalidad
  fix      → corrección de bug
  docs     → cambio en documentación
  refactor → mejora de código sin cambio funcional
  test     → adición o corrección de pruebas
  chore    → tareas de mantenimiento (migraciones, dependencias)

Ejemplos:
  feat(asistencias): agregar validación de tolerancia en registro de entrada
  fix(admin): corregir conflicto de nombre reservado en urls.py
  chore(db): generar migración para modelo SolicitudCorreccion
  docs(scmp): emitir SCMP v1.0 línea base Sprint 1
```

---

### 3.4 Identificación de SCIs Bajo Control de Configuración

Todos los artefactos listados a continuación forman parte de la línea base y están sujetos al proceso de cambio descrito en este SCMP:

| ID SCI | Artefacto | Ubicación | Responsable |
|--------|-----------|-----------|-------------|
| SCI-01 | Código fuente del sistema (apps Django) | `/` en GitHub | AC |
| SCI-02 | Migraciones de base de datos | `<app>/migrations/` | DBA |
| SCI-03 | Backlog de requisitos | `docs/planning/STX-CORE-REQ-BACKLOG-v1.0.md` | Team Leader |
| SCI-04 | Diagrama Entidad-Relación | `docs/diseno/STX-DB-DER-MODELO-v1.0.md` | DBA |
| SCI-05 | Diagrama de componentes | `docs/diseno/STX-CORE-ARC-COMPONENTES-v1.0.md` | Team Leader |
| SCI-06 | Wireframes | `docs/diseno/wireframes/` | Frontend / Design |
| SCI-07 | Matriz de riesgos | `docs/gestion/STX-CORE-RSK-MATRIZ-RIESGOS-v1.0.md` | Team Leader |
| SCI-08 | Inventario de SCIs | `docs/STX-CONFIG-SCI-INVENTORY-v1.0.md` | AC |
| SCI-09 | Este documento (SCMP) | `docs/gestion/STX-CORE-DOC-SCMP-v1.0.md` | AC |
| SCI-10 | Casos de prueba | `docs/gestion/STX-CORE-DOC-CASOS-PRUEBA-v1.0.xlsx` | QA |
| SCI-11 | Reportes de sprint | `docs/planning/sprints/` | Team Leader |
| SCI-12 | `requirements.txt` | `/requirements.txt` | AC |
| SCI-13 | `settings.py` | `Saltix/settings.py` | AC |

---

## 4. Acta de Congelamiento — Línea Base Sprint 1

**Proyecto:** Saltix — Sistema de Control de Asistencia y Cálculo de Nómina  
**Línea Base:** Sprint 1 — Arquitectura Base y Administración  
**Versión congelada:** v1.0  
**Fecha de congelamiento:** 2026-03-18  
**Repositorio:** https://github.com/JuanMarcoGosselin/Saltix  

---

### Declaración de Congelamiento

Por medio del presente acta, el equipo de desarrollo de **Saltix** declara formalmente que los elementos de configuración listados a continuación han sido revisados, validados y aprobados como **Línea Base v1.0** del proyecto, correspondiente al cierre del Sprint 1.

A partir de esta fecha, **ningún cambio puede realizarse sobre estos artefactos sin pasar por el proceso formal del CCB** descrito en la sección 1.2 de este SCMP.

---

### Elementos Congelados

| SCI | Artefacto | Estado de QA | Versión |
|-----|-----------|:------------:|---------|
| SCI-01 | Código fuente — Sprint 1 (53/53 tareas completadas) | ✅ PASS | Commit en `main` |
| SCI-02 | Migraciones — 16 migraciones en 6 apps | ✅ PASS | v1.0 |
| SCI-03 | Backlog de requisitos (24 RF / 6 RNF) | ✅ Revisado | v1.0 |
| SCI-04 | Diagrama Entidad-Relación | ✅ Revisado | v1.0 |
| SCI-05 | Diagrama de componentes | ✅ Revisado | v1.0 |
| SCI-06 | Wireframes (login, admin, jefatura, profesor) | ✅ Revisado | v1.0 |
| SCI-07 | Matriz de riesgos (10 riesgos identificados) | ✅ Revisado | v1.0 |
| SCI-08 | Inventario de SCIs | ✅ Revisado | v1.0 |
| SCI-10 | Casos de prueba Sprint 1 | ✅ PASS | v1.0 |
| SCI-11 | Reporte Sprint 1 | ✅ Emitido | v1.0 |
| SCI-12 | `requirements.txt` | ✅ Revisado | v1.0 |
| SCI-13 | `settings.py` (configuración base) | ✅ Revisado | v1.0 |

---

### Alcance de la Línea Base

La Línea Base v1.0 comprende los siguientes módulos funcionales entregados y validados:

- **Base de datos:** esquema completo con 20+ modelos distribuidos en las apps `core`, `users`, `Profesores`, `Asistencias`, `Contabilidad` y `jefatura`.
- **Sistema RBAC:** autenticación por email, decoradores `requiere_rol` y `requiere_permiso`, redirección automática por rol.
- **Dashboard de administración:** métricas, CRUD de usuarios, roles, permisos, planteles, departamentos, notificaciones y bitácora de auditoría.
- **Pantallas iniciales:** dashboard de Jefatura y dashboard de Profesor (estructura base, sin lógica funcional aún).
- **Documentación:** backlog, diagramas, wireframes, matriz de riesgos, SCM y reporte de sprint.

---

### Firmas de Aprobación

| Miembro | Rol | Firma | Fecha |
|---------|-----|-------|-------|
| Ivan Ramos de la Torre | Team Leader | ___________________________ | 2026-03-18 |
| Juan Marco Gosselin Gamboa | Administrador de la Configuración | ___________________________ | 2026-03-18 |
| Patricio Dávila Assad | Backend | ___________________________ | 2026-03-18 |
| Diego Cristóbal Gael Serna Domínguez | Frontend | ___________________________ | 2026-03-18 |
| Katherine Guadalupe Guareño Flores | Frontend / Design | ___________________________ | 2026-03-18 |

---

*Este documento forma parte de la Línea Base v1.0 del proyecto Saltix y está sujeto a control de configuración conforme a lo establecido en el estándar IEEE 828.*