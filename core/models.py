from django.db import models

class Plantel(models.Model):
    # Sede/plantel donde se asignan profesores y periodos.
    nombre = models.CharField(max_length=80)
    direccion = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

class BitacoraAuditoria(models.Model):
    # Bitacora simple de cambios para auditoria.
    usuario = models.ForeignKey("users.Usuario", on_delete=models.PROTECT)
    modelo = models.CharField(max_length=80)
    objeto_id = models.PositiveIntegerField()
    accion = models.CharField(max_length=40)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

class Notificacion(models.Model):
    # Notificaciones internas (y base para correo).
    TIPOS = [
        ("INCIDENCIA", "Incidencia"),
        ("NOMINA", "Nomina"),
        ("RECIBO", "Recibo"),
        ("SISTEMA", "Sistema"),
    ]

    usuario = models.ForeignKey("users.Usuario", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=TIPOS)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
