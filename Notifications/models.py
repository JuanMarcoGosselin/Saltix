from django.conf import settings
from django.db import models


class Notificacion(models.Model):
    TIPOS = [
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("danger", "Danger"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    titulo = models.CharField(max_length=120)
    mensaje = models.TextField(max_length=1000)
    tipo = models.CharField(max_length=10, choices=TIPOS, default="info")
    url = models.CharField(max_length=255, blank=True)
    leida = models.BooleanField(default=False)
    archivada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada_en", "-id"]
        indexes = [
            models.Index(fields=["usuario", "leida", "archivada"]),
            models.Index(fields=["usuario", "creada_en"]),
        ]

    def __str__(self):
        return f"{self.usuario} | {self.titulo}"
