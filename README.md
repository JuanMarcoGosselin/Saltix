# Saltix — Sistema de Control de Asistencia y Cálculo de Nómina

**Stack:** Python 3.12 / Django 6.0.3 / SQLite  
**Plan de Proyecto:** 🔗 [Link al Trello](https://trello.com/b/ZWz953Fq/saltix)

---

## Instalación

### Requisitos previos

| Requisito | Versión |
|---|---|
| Python | 3.12+ |
| pip | 24.x |
| Git | 2.x |
| Base de datos | SQLite (incluida en Python) |

### Pasos

```bash
# 1. Clonar
git clone https://github.com/JuanMarcoGosselin/Saltix
cd Saltix

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Base de datos
python manage.py migrate

# 5. Superusuario
python manage.py createsuperuser

# 6. Servidor
python manage.py runserver

Acceder en http://127.0.0.1:8000/
```


### Problemas comunes

| Error | Solución |
|---|---|
| `No module named 'django'` | Activar el entorno virtual |
| `OperationalError` al iniciar | Ejecutar `python manage.py migrate` |
| `That port is already in use` | Usar `python manage.py runserver 8001` |
| `ALLOWED_HOSTS` error | Agregar el dominio en `settings.py` |

---

## Estructura del proyecto

```
Saltix/
├── core/            # Planteles, bitácora, notificaciones
├── users/           # Usuarios, roles, permisos, departamentos
├── Profesores/      # Profesores, horarios, transferencias
├── Asistencias/     # Asistencias, incidencias, correcciones
├── Contabilidad/    # Nómina, periodos, conceptos, recibos
├── admin/           # Panel administrador
├── jefatura/        # Panel jefatura
├── docs/            # Toda la documentación del proyecto
├── requirements.txt
└── contributing.md  # Convención de nombres y abreviaturas
```

---

## Documentación

| Documento | Ubicación |
|---|---|
| Convención de nombres y abreviaturas | [`contributing.md`](contributing.md) |
| Backlog de requisitos (24 RF / 6 RNF) | [`docs/planning/STX-CORE-REQ-BACKLOG-v1.0.md`](docs/planning/STX-CORE-REQ-BACKLOG-v1.0.md) |
| Matriz de riesgos | [`docs/gestion/STX-CORE-RSK-MATRIZ-RIESGOS-v1.0.md`](docs/gestion/STX-CORE-RSK-MATRIZ-RIESGOS-v1.0.md) |
| Diagrama Entidad-Relación | [`docs/diseno/STX-DB-DER-MODELO-v1.0.md`](docs/diseno/STX-DB-DER-MODELO-v1.0.md) |
| Diagrama de componentes | [`docs/diseno/STX-CORE-ARC-COMPONENTES-v1.0.md`](docs/diseno/STX-CORE-ARC-COMPONENTES-v1.0.md) |
| Wireframes | [`docs/diseno/wireframes/`](docs/diseno/wireframes/) |
| SCM Plan Fase 3 (branching, árbol, BD) | [`docs/gestion/STX-CORE-DOC-SCI-FASE3-v1.0.docx`](docs/gestion/STX-CORE-DOC-SCI-FASE3-v1.0.docx) |
| SCM Plan Fase 4 (pruebas, despliegue) | [`docs/gestion/STX-CORE-DOC-SCI-FASE4-v1.0.docx`](docs/gestion/STX-CORE-DOC-SCI-FASE4-v1.0.docx) |
| Casos de prueba | [`docs/gestion/STX-CORE-DOC-CASOS-PRUEBA-v1.0.xlsx`](docs/gestion/STX-CORE-DOC-CASOS-PRUEBA-v1.0.xlsx) |