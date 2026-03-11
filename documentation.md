# Nomenclatura y Trazabilidad

## 1. Convención de Nombres

Para mantener orden y trazabilidad en los artefactos del proyecto, el equipo utilizará una convención de nombres estándar para todos los **SCIs (Software Configuration Items) que no sean código fuente**, como documentos, diagramas, reportes o prototipos.

### Fórmula de nomenclatura
[PROYECTO]-[MODULO]-[TIPO]-[NOMBRE]-v[VERSION].[EXT]


### Ejemplo
SISPROF-DB-DER-MODELO-v1.0.pdf


Donde:

- **PROYECTO** → Identificador del proyecto
- **MODULO** → Área del sistema a la que pertenece el archivo
- **TIPO** → Tipo de artefacto o documento
- **NOMBRE** → Descripción breve del contenido
- **VERSION** → Versión del documento
- **EXT** → Extensión del archivo

---

# Tabla de Abreviaturas

## Proyecto

| Abreviatura | Significado |
|-------------|-------------|
| SISPROF | Sistema de Gestión de Profesores |

---

## Módulos

| Abreviatura | Significado |
|-------------|-------------|
| CORE | Configuración central del sistema |
| USER | Gestión de usuarios |
| PROF | Gestión de profesores |
| ASIS | Sistema de asistencias |
| CONT | Contabilidad |
| ADMIN | Administración |
| JEF | Jefatura |
| DB | Base de datos |
| UI | Interfaz de usuario |

---

## Tipos de Documento

| Abreviatura | Significado |
|-------------|-------------|
| PLN | Planificación |
| REQ | Requisitos |
| UML | Diagramas UML |
| DER | Diagrama Entidad-Relación |
| ARC | Arquitectura |
| TST | Pruebas |
| RSK | Matriz de riesgos |
| DOC | Documento general |

---

# 2. Auditoría del Repositorio Actual

A continuación se muestran ejemplos de archivos con nomenclatura incorrecta actualmente en el repositorio y su correspondiente nombre según la nueva convención.

| Nombre Actual | Nombre Correcto |
|---------------|----------------|
| notas_profesores.docx | SISPROF-PROF-DOC-NOTAS-v1.0.docx |
| diagrama_db_final.pdf | SISPROF-DB-DER-MODELO-v1.0.pdf |


