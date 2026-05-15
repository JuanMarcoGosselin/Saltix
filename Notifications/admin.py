from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "tipo", "leida", "archivada", "creada_en")
    list_filter = ("tipo", "leida", "archivada", "creada_en")
    search_fields = ("titulo", "mensaje", "usuario__email", "usuario__nombre", "usuario__apellido")
