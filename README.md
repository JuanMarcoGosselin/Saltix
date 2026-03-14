# Saltix — Sistema de Control de Asistencia y Cálculo de Nómina

Sistema administrativo-financiero para la gestión de asistencia del personal docente y generación automática de nómina, aplicando normas laborales e impuestos vigentes.

---

## Descripción del Sistema

Saltix transforma registros de asistencia en pagos legales de nómina. El sistema cubre tres dominios:

- **Administrativo:** gestión del personal docente (altas, horarios, asistencias, incidencias).
- **Financiero:** generación de pagos, impuestos, deducciones y reportes contables.
- **Precisión matemática:** cálculos monetarios exactos y auditables.

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 / Django 6.0.3 |
| Base de datos | SQLite (desarrollo) |
| Frontend | HTML + CSS + JS (sin framework) |
| Control de versiones | Git |

---

## Estructura del Proyecto

```
Saltix/
├── core/               # Planteles, bitácora de auditoría, notificaciones
├── users/              # Usuarios, roles, permisos, departamentos
├── Profesores/         # Profesores, horarios, transferencias
├── Asistencias/        # Asistencias, incidencias, correcciones
├── Contabilidad/       # Nómina, periodos, conceptos, recibos
├── admin/              # Dashboard administrador
├── jefatura/           # Dashboard jefatura
├── Saltix/             # Configuración del proyecto Django
├── docs/               # Documentación del proyecto (ver abajo)
└── manage.py
```

---

## Documentación del Proyecto

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

---

## Plan de Proyecto

El plan de proyecto vive en Trello:  
🔗 **[https://trello.com/b/ZWz953Fq/saltix]**

---

## Instalación y Ejecución Local

```bash
# 1. Clonar el repositorio
git clone <https://github.com/JuanMarcoGosselin/Saltix>
cd Saltix

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Correr el servidor
python manage.py runserver
```

---

## Convención de Nombres de Artefactos

```
[PROYECTO]-[MODULO]-[TIPO]-[NOMBRE]-v[VERSION].[EXT]
```

Ver el detalle completo en [`contributing.md`](contributing.md).

---

## Módulos del Sistema

| Módulo | Descripción |
|---|---|
| `core` | Planteles, bitácora de auditoría, notificaciones |
| `users` | Autenticación, roles, permisos, departamentos |
| `Profesores` | Alta de profesores, horarios, transferencias entre departamentos |
| `Asistencias` | Registro de asistencias, incidencias, solicitudes de corrección |
| `Contabilidad` | Periodos de nómina, cálculo, conceptos fiscales, recibos PDF |
| `admin` | Panel del administrador del sistema |
| `jefatura` | Panel de jefatura de departamento |