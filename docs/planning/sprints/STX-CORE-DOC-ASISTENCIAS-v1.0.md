# STX-CORE-DOC-ASISTENCIAS-v1.0
## Documentación Técnica — Módulo de Asistencias (Sprint 2)

---

## 1. Descripción General

El módulo de Asistencias cubre el registro, consulta y justificación de asistencias de profesores. Se compone de dos apps Django:

- `Asistencias/` — modelos, endpoints y capa de servicios de negocio
- `Profesores/` — vistas del dashboard, registro de asistencia y utilidades de cálculo

---

## 2. Modelos

### 2.1 `Asistencia`
**App:** `Asistencias`  
**Tabla:** `Asistencias_asistencia`

Registra cada evento de entrada/salida de un profesor para un bloque de horario específico.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `profesor` | FK → `Profesores.Profesor` | Profesor al que pertenece el registro |
| `horario` | FK → `Profesores.Horario` | Bloque de horario asociado |
| `fecha` | DateField | Fecha del registro |
| `hora_entrada` | TimeField | Hora exacta de entrada |
| `hora_salida` | TimeField (nullable) | Hora exacta de salida |
| `estado` | CharField | `ASISTENCIA`, `RETARDO`, `FALTA`, `JUSTIFICADA` |
| `justificada` | BooleanField | `True` si fue aprobada por jefatura |
| `tolerancia_minutos` | PositiveSmallIntegerField | Minutos de retardo al momento de entrada |
| `tipo_registro` | CharField | `RELOJ` (normal) o `MANUAL` |
| `creado_por` | FK → `users.Usuario` | Usuario que creó el registro |
| `cancelada_institucional` | BooleanField | Clase cancelada por la institución |
| `fecha_registro` | DateTimeField (auto) | Timestamp exacto del registro |

**Propiedad calculada `color_clase`:** retorna la clase CSS correspondiente al estado (`presente`, `retardo`, `falta`, `justificada`, `inhabil`, `pendiente`).

---

### 2.2 `Incidencia`
**App:** `Asistencias`  
**Tabla:** `Asistencias_incidencia`

Solicitud de justificación enviada por un profesor para una falta o retardo.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `asistencia` | FK → `Asistencia` | Asistencia que se busca justificar |
| `motivo` | TextField (max 1000) | Descripción de la justificación |
| `tipo` | CharField | `FALTA` o `RETARDO` |
| `estado` | CharField | `PENDIENTE`, `APROBADA`, `RECHAZADA` |
| `solicitante` | FK → `users.Usuario` | Profesor que envió la solicitud |
| `aprobador` | FK → `users.Usuario` (nullable) | Jefatura/admin que resuelve |
| `fecha_solicitud` | DateTimeField (auto) | Timestamp de envío |
| `fecha_de_resolucion` | DateTimeField (nullable) | Timestamp de resolución |

---

### 2.3 `Horario`
**App:** `Profesores`  
**Tabla:** `Profesores_horario`

Bloque de clase programada para un profesor.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `profesor` | FK → `Profesor` | Profesor asignado |
| `dia_semana` | CharField | `LUN`, `MAR`, `MIE`, `JUE`, `VIE`, `SAB` |
| `hora_inicio` | TimeField | Inicio del bloque |
| `hora_fin` | TimeField | Fin del bloque |
| `aula` | CharField (max 10) | Identificador del aula |
| `es_hora_clase` | BooleanField | Si se paga o no |
| `activo` | BooleanField | Si el horario está vigente |

**Restricción de unicidad:** `UniqueConstraint(fields=["profesor", "dia_semana", "hora_inicio", "hora_fin"])` — evita duplicados de bloque.

**Índices:**
- `(profesor, dia_semana, activo)` — consultas de horario del día
- `(profesor, es_hora_clase, activo)` — cálculo de horas pagables
- `(dia_semana, es_hora_clase, activo)` — consultas globales por día

---

## 3. Endpoints

### 3.1 `GET /profesores/registro-asistencia/`
**Vista:** `Profesores.views.registro_asistencia`  
**Acceso:** Autenticado, rol `Profesor`  

Renderiza la vista de registro de asistencia del día actual.

**Contexto enviado al template:**

| Variable | Descripción |
|----------|-------------|
| `profesor_nombre` | Nombre completo del profesor |
| `profesor_iniciales` | Iniciales para avatar |
| `horarios_hoy` | QuerySet de `Horario` del día actual (con atributos anotados) |
| `fecha_hoy` | Fecha actual |

Cada objeto en `horarios_hoy` tiene los atributos adicionales:
- `ya_registrada` (bool): si ya existe asistencia para ese bloque hoy
- `salida` (TimeField | None): hora de salida si ya fue registrada
- `asistencia_id` (int | None): ID de la asistencia existente

---

### 3.2 `POST /profesores/registrar-asistencia/`
**Vista:** `Profesores.views.asistencia_accion`  
**Acceso:** Autenticado, rol `Profesor`  
**Content-Type:** `application/json`

**Body:**
```json
{ "horario_id": 42 }
```

**Flujo:**
1. Obtiene al profesor vinculado al usuario autenticado.
2. Si no existe asistencia para `(profesor, horario, hoy)`:
   - Llama a `verificar_entrada(horario_id)` — ventana: `[inicio - 15min, inicio + 30min]`.
   - Si la hora actual supera `hora_inicio`, asigna estado `RETARDO` y calcula `tolerancia_minutos`.
   - Crea el registro con `hora_entrada = now()`.
3. Si existe asistencia sin `hora_salida`:
   - Llama a `verificar_salida(horario_id)` — ventana: `[fin - 10min, fin + 30min]`.
   - Actualiza `hora_salida = now()`.
4. Si ya existe entrada y salida: retorna error 400.

**Respuestas:**

| Escenario | HTTP | Body |
|-----------|------|------|
| Entrada registrada | 200 | `{"tipo": "entrada", "estado": "ASISTENCIA"\|"RETARDO", "asistencia_id": N}` |
| Salida registrada | 200 | `{"tipo": "salida", "message": "Salida registrada correctamente"}` |
| Fuera de ventana | 400 | `{"error": "Fuera del horario permitido..."}` |
| Ya registrado | 400 | `{"error": "Ya registraste entrada y salida..."}` |

---

### 3.3 `POST /profesores/justificar-asistencia/`
**Vista:** `Asistencias.views.justificar_asistencia`  
**Acceso:** Autenticado, roles `Profesor`, `jefatura`, `administrador`  
**Content-Type:** `application/json` o `multipart/form-data`

**Body:**
```json
{ "asistencia_id": 15, "motivo": "Incapacidad médica" }
```

**Flujo para rol Profesor:**
1. Filtra la asistencia a las propias del profesor autenticado.
2. Valida que `estado == "FALTA"` (solo se pueden justificar faltas).
3. Si ya existe una `Incidencia` en estado `PENDIENTE`, retorna `{"ok": true, "already": true, "pending": true}` sin crear duplicado.
4. Crea `Incidencia` con `estado = "PENDIENTE"`, `tipo = "FALTA"` y `solicitante = request.user`.

**Flujo para rol jefatura/administrador:**
- Marca directamente `asistencia.justificada = True` y `estado = "JUSTIFICADA"`.

**Validaciones:**
- `motivo` no puede estar vacío → 400
- `asistencia_id` debe ser entero válido → 400
- Asistencia no puede estar `cancelada_institucional` → 400
- Asistencia debe pertenecer al profesor autenticado (solo para rol Profesor) → 404

**Respuestas:**

| Escenario | HTTP | Body |
|-----------|------|------|
| Solicitud creada (Profesor) | 200 | `{"ok": true, "pending": true}` |
| Incidencia ya existente | 200 | `{"ok": true, "already": true, "pending": true}` |
| Justificada directamente (Jefatura) | 200 | `{"ok": true}` |
| Motivo vacío | 400 | `{"error": "El motivo de justificación es obligatorio."}` |
| Asistencia no es FALTA | 400 | `{"error": "Solo se pueden justificar faltas."}` |
| Profesor no encontrado | 403 | `{"error": "Profesor no encontrado."}` |
| Asistencia no encontrada | 404 | `{"error": "Asistencia no encontrada."}` |

---

### 3.4 `GET /profesores/` (Dashboard)
**Vista:** `Profesores.views.dashboard`  
**Acceso:** Autenticado

Renderiza el dashboard completo del profesor con horario semanal, KPIs del período y listado de faltas sin justificar con paginación.

Soporta parámetros GET:
- `week_offset` (int): desplazamiento de semanas hacia atrás (0 = semana actual).
- `page` (int): página del listado de faltas.
- `partial=faltas`: retorna JSON con HTML renderizado de los partials (HTMX/AJAX).

---

## 4. Capa de Servicios (`Asistencias/services/`)

### 4.1 `estado.py`

| Función | Descripción |
|---------|-------------|
| `obtener_estado_clase(profesor, horario, fecha)` | Determina el estado de una clase: ASISTENCIA, RETARDO, FALTA, JUSTIFICADA o PENDIENTE. Usa prefetch si está disponible. |
| `obtener_color_estado(estado)` | Mapea estado a clase CSS (`presente`, `retardo`, `falta`, `justificada`, `pendiente`). |

### 4.2 `faltas.py`

| Función | Descripción |
|---------|-------------|
| `current_payroll_period(hoy)` | Retorna `DateRange` del período ABIERTO más reciente en `Contabilidad.Periodo`. Fallback a período simulado de 5 semanas. |
| `previous_payroll_period(current_inicio)` | Retorna el período CERRADO anterior al vigente. |
| `week_range(hoy, week_offset)` | Retorna `DateRange` de Lunes a Sábado de la semana desplazada. |
| `unjustified_absences_queryset(profesor, hoy, week_offset)` | Retorna el queryset de faltas sin justificar anotado con `tiene_incidencia_pendiente`. |
| `unjustified_absences_navigation(hoy)` | Retorna metadatos de navegación de semanas para el dashboard. |
| `period_stats(profesor, hoy)` | Retorna conteos de asistencias, retardos, faltas y justificadas del período vigente. |

---

## 5. Utilidades (`Profesores/utils.py`)

| Función | Descripción |
|---------|-------------|
| `obtener_horario_hoy(profesor)` | QuerySet de horarios activos del profesor para el día actual. |
| `verificar_entrada(horario_id)` | Verifica si el momento actual cae en la ventana de entrada `[inicio-15min, inicio+30min]`. |
| `verificar_salida(horario_id)` | Verifica si el momento actual cae en la ventana de salida `[fin-10min, fin+30min]`. |
| `dashboard_kpis(profesor, hoy, rango_periodo)` | Calcula horas trabajadas, horas esperadas y salario bruto del período. |
| `profesor_profile_context(profesor, hoy, horarios_clase)` | Construye el diccionario de contexto para el perfil del profesor en el dashboard. |
| `format_hours(minutes)` | Convierte minutos a horas con 1 decimal (sin cero final innecesario). |
| `format_money(amount)` | Formatea `Decimal` como string con separador de miles y 2 decimales. |

---

## 6. URLs

```
/profesores/                          → dashboard
/profesores/registro-asistencia/      → vista de registro (GET)
/profesores/registrar-asistencia/     → acción de registro (POST)
/profesores/justificar-asistencia/    → solicitud de justificación (POST)
/asistencias/justificar/              → justificación directa (POST, también disponible como endpoint independiente)
```

---

## 7. Migraciones Aplicadas en Sprint 2

| Migración | App | Descripción |
|-----------|-----|-------------|
| `Asistencias/0004_alter_asistencia_hora_salida` | Asistencias | `hora_salida` pasa a nullable/blank |
| `Asistencias/0005_alter_asistencia_estado_alter_asistencia_horario` | Asistencias | Estado amplía a 25 chars; horario cambia a `PROTECT` |
| `Profesores/0005_horario_activo` | Profesores | Campo `activo` en Horario |
| `Profesores/0006_alter_profesor_curp_...` | Profesores | Índices en Horario y Profesor; UniqueConstraint en Horario |

---

## 8. Notas de Configuración

- **Zona horaria:** `TIME_ZONE = "America/Mexico_City"` en `settings.py`. Crítico para el cálculo correcto de ventanas de registro.
- **Tolerancia hardcodeada:** entrada `[-15, +30]` min; salida `[-10, +30]` min. Definida en `Profesores/utils.py`. Candidata a migrar a configuración de Plantel en un sprint futuro.
- **Período de nómina:** si no existe un `Contabilidad.Periodo` con `estado="ABIERTO"`, el sistema usa un fallback simulado de 5 semanas hacia atrás (`SIMULATED_PAYROLL_WEEKS = 5` en `Asistencias/services/faltas.py`).