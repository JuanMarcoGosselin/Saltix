from django.db import models

class Asistencia(models.Model): 
    # Registro de asistencia por clase: entrada/salida, estado y si fue manual o normal.
    TIPO_REGISTRO = [
        ("RELOJ", "Reloj"),
        ("MANUAL", "Manual"),
    ]
    ESTADOS = [
        ("ASISTENCIA", "Asistencia"),
        ("RETARDO", "Retardo"),
        ("FALTA", "Falta"),
    ]

    profesor = models.ForeignKey("Profesores.Profesor", on_delete=models.PROTECT)
    fecha = models.DateField()
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=25, choices=ESTADOS)
    justificada = models.BooleanField(default=False)
    observaciones = models.TextField(max_length=1000, blank=True, null=True)
    horario = models.ForeignKey("Profesores.Horario", on_delete=models.CASCADE)
    tolerancia_minutos = models.PositiveSmallIntegerField(default=0)
    tipo_registro = models.CharField(max_length=10, choices=TIPO_REGISTRO, default="RELOJ")
    creado_por = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True)
    cancelada_institucional = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    bitacora = models.ForeignKey("core.BitacoraAuditoria", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.profesor} | {self.fecha} | {self.estado}"

class Incidencia(models.Model): 
    # Justificacion de faltas/retardos con su flujo de aprobacion.
    TIPOS = [
        ("FALTA", "Falta"),
        ("RETARDO", "Retardo"),
    ]
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    ]

    asistencia = models.ForeignKey("Asistencia", on_delete=models.CASCADE)
    motivo = models.TextField(max_length=1000)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="PENDIENTE")
    solicitante = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, related_name="incidencias_solicitadas")
    aprobador = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True, related_name="incidencias_aprobadas")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_de_resolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.asistencia} | {self.tipo} | {self.estado}"

class EvidenciaIncidencia(models.Model):
    # Evidencias adjuntas (archivos) para respaldar incidencias.
    incidencia = models.ForeignKey("Incidencia", on_delete=models.CASCADE)
    archivo = models.FileField(upload_to="incidencias/")
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia {self.incidencia_id}"

class SolicitudCorreccion(models.Model):
    # Solicitud del profesor para corregir un registro de asistencia.
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    ]

    profesor = models.ForeignKey("Profesores.Profesor", on_delete=models.PROTECT)
    asistencia = models.ForeignKey("Asistencia", on_delete=models.PROTECT)
    motivo = models.TextField(max_length=1000)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="PENDIENTE")
    aprobador = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.profesor} | {self.estado}"

class CorreccionAsistencia(models.Model):
    # Correccion por compensacion, no se edita la asistencia original.
    asistencia_original = models.ForeignKey("Asistencia", on_delete=models.PROTECT, related_name="correcciones")
    asistencia_compensatoria = models.ForeignKey("Asistencia", on_delete=models.PROTECT, related_name="compensaciones")
    motivo = models.TextField(max_length=1000)
    aprobada_por = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Correccion {self.asistencia_original_id}"
