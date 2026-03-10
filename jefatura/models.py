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
