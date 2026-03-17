# STX-CORE-ARC-COMPONENTES-v1.0
# Diagrama de Componentes / Arquitectura — Saltix

**Proyecto:** Saltix  
**Versión:** 1.0  
**Fecha:** 2026-03-13  

---

## Vista General del Sistema

```mermaid
graph TD
    subgraph Cliente["🌐 Cliente (Navegador)"]
        UI_LOGIN["Login\nlogin.html"]
        UI_ADMIN["Dashboard Admin\ndashboard_admin_v2.html"]
        UI_JEF["Dashboard Jefatura\ndashboard_jefatura_v2.html"]
        UI_PROF["Dashboard Profesor\ndashboard_profesor.html"]
    end

    subgraph Django["⚙️ Backend Django 6.0.3"]
        subgraph Apps["Aplicaciones"]
            APP_USERS["users\nUsuario, Rol, Permiso\nDepartamento"]
            APP_CORE["core\nPlantel, BitacoraAuditoria\nNotificacion"]
            APP_PROF["Profesores\nProfesor, Horario\nTransferenciaDepartamento"]
            APP_ASIS["Asistencias\nAsistencia, Incidencia\nSolicitudCorreccion"]
            APP_CONT["Contabilidad\nNomina, Periodo\nCatalogoConcepto"]
            APP_ADMIN["admin\n(Panel administrador)"]
            APP_JEF["jefatura\n(Panel jefatura)"]
        end

        subgraph Transversal["Servicios Transversales"]
            AUTH["Autenticación\nAbstractBaseUser"]
            AUDITORIA["Bitácora\nBitacoraAuditoria"]
            NOTIF["Notificaciones\nNotificacion"]
            PERMISOS["Control de Acceso\nRol + Permiso"]
        end
    end

    subgraph DB["🗄️ Base de Datos"]
        SQLITE["SQLite\n(desarrollo)\ndb.sqlite3"]
    end

    subgraph Archivos["📁 Almacenamiento de Archivos"]
        EVIDENCIAS["Evidencias de incidencias\nmedia/incidencias/"]
        RECIBOS["Recibos de nómina PDF\nmedia/recibos/"]
    end

    %% Conexiones cliente → Django
    UI_LOGIN -->|POST login| AUTH
    UI_ADMIN -->|HTTP requests| APP_ADMIN
    UI_JEF -->|HTTP requests| APP_JEF
    UI_PROF -->|HTTP requests| APP_PROF

    %% Conexiones entre apps
    APP_ADMIN -->|gestiona| APP_USERS
    APP_ADMIN -->|gestiona| APP_PROF
    APP_ADMIN -->|gestiona| APP_ASIS
    APP_ADMIN -->|gestiona| APP_CONT
    APP_JEF -->|revisa| APP_ASIS
    APP_JEF -->|consulta| APP_PROF
    APP_PROF -->|consulta| APP_ASIS

    APP_ASIS -->|referencia| APP_PROF
    APP_CONT -->|lee| APP_ASIS
    APP_CONT -->|lee| APP_PROF
    APP_USERS -->|provee auth| AUTH

    %% Servicios transversales
    APP_ASIS -->|escribe| AUDITORIA
    APP_CONT -->|escribe| AUDITORIA
    APP_ASIS -->|genera| NOTIF
    APP_CONT -->|genera| NOTIF
    AUTH -->|verifica| PERMISOS

    %% Conexiones a BD
    APP_USERS -->|ORM| SQLITE
    APP_CORE -->|ORM| SQLITE
    APP_PROF -->|ORM| SQLITE
    APP_ASIS -->|ORM| SQLITE
    APP_CONT -->|ORM| SQLITE

    %% Archivos
    APP_ASIS -->|sube archivos| EVIDENCIAS
    APP_CONT -->|genera PDF| RECIBOS
```

---

## Descripción de los Módulos

| Módulo | Responsabilidad principal | Depende de |
|---|---|---|
| `users` | Autenticación, roles, permisos, departamentos | `core` (Plantel) |
| `core` | Planteles, bitácora de auditoría, notificaciones | — |
| `Profesores` | Alta/baja de profesores, horarios, transferencias | `users`, `core` |
| `Asistencias` | Registro de asistencia, incidencias, correcciones | `Profesores`, `users`, `core` |
| `Contabilidad` | Nómina, periodos, conceptos fiscales, recibos | `Profesores`, `Asistencias`, `core` |
| `admin` | Vistas y lógica del panel administrador | todos los módulos |
| `jefatura` | Vistas y lógica del panel de jefatura | `Profesores`, `Asistencias` |

---

## Flujo Principal: Cálculo de Nómina

```mermaid
sequenceDiagram
    actor Admin
    participant Contabilidad
    participant Asistencias
    participant Profesores
    participant DB

    Admin->>Contabilidad: Crear Periodo (plantel, tipo, fechas)
    Contabilidad->>DB: INSERT Periodo (estado=ABIERTO)

    Admin->>Contabilidad: Generar Vista Previa
    Contabilidad->>Asistencias: GET Asistencias del periodo
    Asistencias->>DB: SELECT por fecha y profesor
    Contabilidad->>Profesores: GET costo_por_hora por profesor
    Contabilidad->>DB: INSERT VistaPreviaNomina

    Admin->>Contabilidad: Cerrar Periodo
    Contabilidad->>DB: INSERT Nomina + DetalleNomina por profesor
    Contabilidad->>DB: UPDATE Periodo (estado=CERRADO)
    Contabilidad->>DB: INSERT ReciboNomina (PDF)
    Contabilidad->>DB: INSERT Notificacion (tipo=RECIBO) por profesor
```