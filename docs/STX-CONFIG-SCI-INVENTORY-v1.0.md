# Inventario de SCIs
**Proyecto:** Saltix — Sistema de Control de Asistencia y Cálculo de Nómina  
**Versión del documento:** 1.0  
**Fecha:** 2026-03-13  
**Convención de nombres:** `[PROYECTO]-[MODULO]-[TIPO]-[NOMBRE]-v[VERSION].[EXT]`

---


| # | Nombre del Archivo | Descripción | Responsable |
|---|---|---|---|
| 1.1 | `STX-CORE-PLN-PLAN-PROYECTO-v1.0` | Plan de Proyecto. **Vive en Trello** como tablero del equipo. Contiene el backlog de sprints, fechas de entrega por fase, asignación de tareas y seguimiento de avance. El link al tablero debe registrarse en el `README.md` del repositorio. | Líder de Proyecto |
| 1.2 | `STX-CORE-RSK-MATRIZ-RIESGOS-v1.0.md` | Matriz de Riesgos. **Vive en el repositorio** bajo la carpeta `/docs/gestion/`. Identifica riesgos del proyecto (técnicos, de equipo, de negocio), su probabilidad, impacto, nivel resultante y plan de mitigación. | Líder de Proyecto |

---


| # | Nombre del Archivo | Descripción | Responsable |
|---|---|---|---|
| 2.1 | `STX-CORE-REQ-BACKLOG-v1.0.md` | Backlog de Requisitos (Product Backlog). **Vive en el repositorio** bajo `/docs/planning/`. Contiene los requerimientos funcionales (RF) y no funcionales (RNF) del sistema, organizados como historias de usuario por módulo: Profesores, Asistencias y Contabilidad/Nómina. Incluye criterios de aceptación para cada ítem. | Product Owner / Líder de Proyecto |
| 2.2 | `STX-DB-DER-MODELO-v1.0.md` | Diagrama Entidad-Relación. **Vive en el repositorio** bajo `/docs/diseno/`. Modela las entidades principales del sistema: `Profesor`, `Horario`, `Asistencia`, `Incidencia`, `Nomina`, `Periodo`, `DetalleNomina`, `CatalogoConcepto` y sus relaciones. Se genera a partir de los modelos Django actuales en las apps `Profesores`, `Asistencias` y `Contabilidad`. | Arquitecto / Desarrollador Backend |
| 2.3 | `STX-CORE-ARC-COMPONENTES-v1.0.md` | Diagrama de Componentes / Arquitectura. **Vive en el repositorio** bajo `/docs/diseno/`. Muestra la descomposición del sistema en sus módulos Django (`core`, `users`, `Profesores`, `Asistencias`, `Contabilidad`, `admin`, `jefatura`) y cómo se comunican entre sí, incluyendo el frontend y la base de datos SQLite/PostgreSQL. | Arquitecto / Líder Técnico |
| 2.4 | `STX-UI-DOC-WIREFRAMES-v1.0` | Prototipos de Pantalla (Wireframes). **Viven en el repositorio** bajo `/docs/diseno/wireframes/` como archivos HTML de alta fidelidad. Incluye las pantallas actualmente desarrolladas: `login.html`, `dashboard_admin_v2.html`, `dashboard_jefatura_v2.html` y `dashboard_profesor.html`. Cualquier nueva pantalla se agrega a esta misma carpeta siguiendo la misma convención. | Diseñador UI / Desarrollador Frontend |

---


```
Saltix/
└── docs/
├── gestion/
│   └── STX-CORE-RSK-MATRIZ-RIESGOS-v1.0.md
├── planning/
│   └── STX-CORE-REQ-BACKLOG-v1.0.md
└── diseno/
    ├── STX-DB-DER-MODELO-v1.0.md
    ├── STX-CORE-ARC-COMPONENTES-v1.0.md
    └── wireframes/
        ├── STX-UI-DOC-WIREFRAMES-dashboard-v1.0.jpeg
        └── STX-UI-DOC-WIREFRAMES-dashboard-nomina-v1.0.jpeg
```