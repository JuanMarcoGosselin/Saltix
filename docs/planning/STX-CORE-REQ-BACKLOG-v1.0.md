# STX-CORE-REQ-BACKLOG-v1.0
# Backlog de Requisitos — Saltix

**Proyecto:** Saltix — Sistema de Control de Asistencia y Cálculo de Nómina  
**Versión:** 1.0  
**Fecha:** 2026-03-13  

---

## Dominio

**Administrativo, Financiero y de Precisión Matemática.**

El sistema se ubica en el ámbito administrativo por su capacidad para gestionar la información del personal docente, incluyendo altas, horarios y asistencias. Asimismo, forma parte del área financiera al generar pagos, impuestos, deducciones y reportes contables válidos. Respecto a la precisión matemática, todos los cálculos monetarios deben ser exactos y auditables, eliminando posibles errores por redondeo. El objetivo principal es transformar registros de asistencia en pagos legales de nómina, aplicando de manera automática las normas laborales e impuestos vigentes.

---

## Requerimientos Funcionales (RF)

### RF-01 — Registro de Empleados

El sistema permitirá registrar docentes con expediente único que incluya nombre, identificador, costo por hora, horario asignado, fecha de ingreso y estatus.

**Justificación:** Sin expediente no es posible asociar asistencias ni calcular pagos.

| Condición | Acción |
|---|---|
| Se registra empleado | Crear expediente único |
| Se ingresa costo por hora | Guardar salario base |
| Empleado desactivado | Excluir de nómina futura |

---

### RF-02 — Captura de Asistencia

El sistema funcionará como reloj checador virtual registrando entrada y salida y evaluando tolerancias.

**Justificación:** La nómina depende directamente de la asistencia registrada.

| Condición | Acción |
|---|---|
| Entrada dentro de tolerancia | Registrar asistencia válida |
| Entrada tardía | Registrar retardo |
| Sin registro | Registrar falta |

---

### RF-03 — Justificación de Incidencias

Solo jefatura podrá justificar faltas y retardos mediante validación.

**Justificación:** Evita sanciones incorrectas y permite revisión humana.

| Condición | Acción |
|---|---|
| Profesor solicita justificación | Enviar a jefatura |
| Jefatura aprueba | Convertir a asistencia |
| Jefatura rechaza | Mantener falta |

---

### RF-04 — Motor de Cálculo de Nómina

Procesa asistencias del periodo y calcula salario base, percepciones y deducciones.

**Justificación:** Garantiza uniformidad y evita errores humanos.

| Condición | Acción |
|---|---|
| Inicio periodo | Procesar asistencias |
| Horas válidas > 0 | Calcular salario base |
| Fin cálculo | Obtener salario bruto |

---

### RF-05 — Catálogo Configurable de Percepciones

El sistema permitirá definir percepciones editables como aguinaldo, primas y bonos.

**Justificación:** Las prestaciones cambian institucionalmente y no deben estar codificadas.

| Condición | Acción |
|---|---|
| Administrador crea percepción | Agregar al catálogo |
| Se modifica percepción | Aplicar en siguiente nómina |

---

### RF-06 — Clasificación Fiscal de Percepciones

Cada percepción deberá clasificarse como gravada, exenta o mixta.

**Justificación:** El ISR depende de esta clasificación.

| Condición | Acción |
|---|---|
| Percepción gravada | Sumar a base ISR |
| Percepción exenta | Excluir del ISR |

---

### RF-07 — Secuencia Obligatoria de Cálculo

La nómina seguirá un orden estricto de cálculo: base → percepciones → impuestos → deducciones → neto.

**Justificación:** Evita cálculo incorrecto de impuestos.

| Condición | Acción |
|---|---|
| Se calcula salario base | Sumar percepciones |
| Se obtiene bruto | Calcular ISR e IMSS |
| Aplicadas deducciones | Obtener neto |

---

### RF-08 — Evidencia Documental de Incidencias

Las incidencias podrán adjuntar documentos comprobatorios.

**Justificación:** Permite auditorías y defensa legal.

| Condición | Acción |
|---|---|
| Se adjunta comprobante | Guardar evidencia |
| Auditoría | Mostrar evidencia |

---

### RF-09 — Unidad de Pago por Hora Clase

El pago se basará en hora clase programada válida, no hora reloj.

**Justificación:** Refleja el trabajo docente real.

| Condición | Acción |
|---|---|
| Clase cancelada institucionalmente | Pagar hora |
| Docente no asiste | No pagar hora |

---

### RF-10 — Recibo Legal de Nómina

El sistema generará recibo PDF con información fiscal completa.

**Justificación:** El recibo es comprobante oficial de pago.

| Condición | Acción |
|---|---|
| Nómina cerrada | Generar PDF |
| Profesor solicita | Permitir descarga |

---

### RF-11 — Entidad Departamento

El sistema deberá manejar una entidad "Departamento" a la cual estarán asignados los profesores y un jefe de departamento responsable.

**Justificación:** Permite control administrativo, validación de incidencias y organización institucional.

| Condición | Acción |
|---|---|
| Se crea departamento | Registrar departamento con jefe asignado |
| Profesor registrado | Asignar obligatoriamente a un departamento |
| Jefe cambia | Reasignar profesores automáticamente al nuevo jefe |

---

### RF-12 — Relación Jerárquica

Un jefe podrá tener múltiples profesores, pero cada profesor solo podrá pertenecer a un departamento activo a la vez.

**Justificación:** Evita conflictos de validación y cálculo de asistencia.

| Condición | Acción |
|---|---|
| Asignación múltiple detectada | Bloquear operación |
| Transferencia aprobada | Mover profesor al nuevo departamento |

---

### RF-13 — Transferencia de Profesores

El sistema permitirá transferir profesores entre departamentos conservando su historial.

**Justificación:** Evita pérdida de información laboral.

| Condición | Acción |
|---|---|
| Jefatura solicita transferencia | Registrar cambio de departamento |
| Transferencia aplicada | Mantener historial previo |

---

### RF-14 — Manejo de Planteles

El sistema deberá soportar múltiples planteles o sedes institucionales.

**Justificación:** El sistema UAG cuenta con más de una sede.

| Condición | Acción |
|---|---|
| Crear plantel | Registrar sede |
| Asignar profesor | Vincular a un plantel específico |

---

### RF-15 — Estados del Profesor

El profesor tendrá estados: activo, suspendido, baja temporal y baja definitiva.

**Justificación:** Controla el cálculo correcto de asistencias y pagos.

| Condición | Acción |
|---|---|
| Estado suspendido | Bloquear registros de asistencia |
| Baja temporal | No generar pago |
| Baja definitiva | Excluir de nómina |

---

### RF-16 — Reactivación

El sistema permitirá reactivar profesores dados de baja temporal conservando historial.

**Justificación:** Evita crear duplicados.

| Condición | Acción |
|---|---|
| Reactivar profesor | Restaurar estado activo |
| Consulta histórica | Mostrar nóminas previas |

---

### RF-17 — Configuración de Periodo

El contador podrá configurar periodos de nómina: semanal, quincenal o mensual.

**Justificación:** Las instituciones manejan diferentes esquemas de pago.

| Condición | Acción |
|---|---|
| Configurar periodo | Guardar tipo de nómina |
| Inicio periodo | Habilitar captura de asistencias |

---

### RF-18 — Control de Periodo Abierto

Solo podrá existir un periodo de nómina activo por plantel.

**Justificación:** Evita duplicidad de cálculos.

| Condición | Acción |
|---|---|
| Periodo activo existente | Bloquear creación |
| Periodo cerrado | Permitir nuevo periodo |

---

### RF-19 — Vista Previa de Nómina

El sistema generará una previsualización antes del cierre.

**Justificación:** Permite detectar errores antes de pagar.

| Condición | Acción |
|---|---|
| Solicitar vista previa | Calcular nómina sin cerrar |
| Error detectado | Permitir corrección |

---

### RF-20 — Solicitud de Corrección

El profesor podrá solicitar corrección de asistencia desde el sistema.

**Justificación:** Reduce conflictos administrativos.

| Condición | Acción |
|---|---|
| Profesor solicita corrección | Crear ticket de revisión |
| Jefatura aprueba | Actualizar incidencia |

---

### RF-21 — Registro Manual Autorizado

Solo jefatura podrá capturar asistencia manual si falla el sistema.

**Justificación:** Garantiza validez de registros.

| Condición | Acción |
|---|---|
| Falla del sistema | Habilitar captura manual |
| Registro manual | Guardar con bitácora |

---

### RF-22 — Flujo de Aprobación

Las modificaciones críticas seguirán flujo: solicitud → aprobación → aplicación.

**Justificación:** Evita cambios arbitrarios.

| Condición | Acción |
|---|---|
| Solicitud creada | Pendiente aprobación |
| Aprobada | Aplicar cambio |
| Rechazada | Cancelar operación |

---

### RF-23 — Consulta del Profesor

El profesor podrá ver su salario calculado, deducciones y recibos históricos.

**Justificación:** Transparencia laboral.

| Condición | Acción |
|---|---|
| Profesor accede | Mostrar su información |
| Solicita recibo | Permitir descarga |

---

### RF-24 — Reportes Administrativos

El sistema generará reportes de faltas, retardos, incidencias y nómina por periodo.

**Justificación:** Facilita supervisión académica.

| Condición | Acción |
|---|---|
| Jefe solicita reporte | Generar reporte |
| Periodo seleccionado | Filtrar información |

---

## Requerimientos No Funcionales (RNF)

### RNF-01 — Control de Acceso por Roles
**Tipo:** Seguridad

Implementación de permisos granulares por acción y rol.

**Justificación:** Protege información salarial confidencial.

| Condición | Acción |
|---|---|
| Usuario sin permiso | Denegar acceso |
| Usuario autorizado | Permitir operación |

---

### RNF-02 — Precisión Decimal
**Tipo:** Confiabilidad

Los cálculos se realizarán con 4 decimales internos y 2 para visualización.

**Justificación:** Evita inconsistencias fiscales.

| Condición | Acción |
|---|---|
| Cálculo interno | Usar 4 decimales |
| Mostrar recibo | Redondear a 2 decimales |

---

### RNF-03 — Bitácora de Auditoría
**Tipo:** Trazabilidad

Se registrarán cambios con usuario, fecha, valor anterior y nuevo.

**Justificación:** Permite auditoría y evidencia legal.

| Condición | Acción |
|---|---|
| Cambio en datos | Registrar evento |
| Intento de eliminación | Denegar |

---

### RNF-04 — Inmutabilidad de Asistencia
**Tipo:** Legal

La asistencia no podrá editarse directamente, solo mediante corrección compensatoria.

**Justificación:** Evita manipulación laboral.

| Condición | Acción |
|---|---|
| Modificar asistencia | Crear corrección |
| Consulta histórica | Mostrar registros |

---

### RNF-05 — Sistema de Notificaciones
**Tipo:** Usabilidad

El sistema enviará notificaciones internas y por correo sobre incidencias, cierre de nómina y recibos disponibles.

**Justificación:** Reduce incertidumbre del usuario.

| Condición | Acción |
|---|---|
| Falta registrada | Notificar profesor |
| Nómina cerrada | Notificar profesores |
| Justificación aprobada/rechazada | Enviar aviso |

---

### RNF-06 — Consistencia de Datos
**Tipo:** Integridad

El sistema impedirá operaciones que generen inconsistencias de nómina.

**Justificación:** Evita errores financieros.

| Condición | Acción |
|---|---|
| Datos incompletos | Bloquear cierre |
| Cambio de horario con asistencias | Advertir y recalcular |