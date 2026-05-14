from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class SolicitudAprobacion(models.Model):
    # Solicitudes que requieren aprobacion (justificaciones, correcciones, etc).
    TIPOS = [
        ("JUSTIFICACION", "Justificacion"),
        ("CORRECCION", "Correccion"),
        ("TRANSFERENCIA", "Transferencia"),
        ("CAPTURA_MANUAL", "Captura manual"),
    ]
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    ]

    tipo = models.CharField(max_length=15, choices=TIPOS)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="PENDIENTE")
    solicitante = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, related_name="solicitudes_creadas")
    aprobador = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True, related_name="solicitudes_aprobadas")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    referencia = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.tipo} | {self.estado}"


class SolicitudTransferencia(models.Model):
    # Flujo simple para mover un profesor entre departamento/plantel sin perder historial.
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
        ("CANCELADA", "Cancelada"),
    ]

    profesor = models.ForeignKey("Profesores.Profesor", on_delete=models.PROTECT, related_name="solicitudes_transferencia")
    departamento_origen = models.ForeignKey("users.Departamento", on_delete=models.PROTECT, related_name="transferencias_solicitadas")
    departamento_destino = models.ForeignKey("users.Departamento", on_delete=models.PROTECT, related_name="transferencias_recibidas")
    plantel_origen = models.ForeignKey("core.Plantel", on_delete=models.PROTECT, related_name="transferencias_salida")
    plantel_destino = models.ForeignKey("core.Plantel", on_delete=models.PROTECT, related_name="transferencias_entrada")
    motivo = models.TextField(max_length=1000)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="PENDIENTE")
    solicitante = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, related_name="transferencias_creadas")
    responsable = models.ForeignKey("users.Usuario", on_delete=models.PROTECT, null=True, blank=True, related_name="transferencias_resueltas")
    observaciones = models.TextField(max_length=1000, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profesor"],
                condition=models.Q(estado="PENDIENTE"),
                name="unique_transferencia_pendiente_profesor",
            ),
        ]
        indexes = [
            models.Index(fields=["estado", "fecha_solicitud"], name="jefatura_so_estado_283e9c_idx"),
            models.Index(fields=["profesor", "fecha_solicitud"], name="jefatura_so_profeso_4f327a_idx"),
            models.Index(fields=["departamento_origen", "estado"], name="jefatura_so_depart_20f539_idx"),
            models.Index(fields=["departamento_destino", "estado"], name="jefatura_so_depart_d49c74_idx"),
        ]

    def __str__(self):
        return f"{self.profesor} | {self.departamento_origen} -> {self.departamento_destino} | {self.estado}"
