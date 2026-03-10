from django.contrib import admin

from .models import Plantel, BitacoraAuditoria, Notificacion


@admin.register(Plantel)
class PlantelAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "direccion")


@admin.register(BitacoraAuditoria)
class BitacoraAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "modelo", "accion", "fecha")
    list_filter = ("modelo", "accion")
    search_fields = ("usuario__email", "modelo", "accion")
    list_select_related = ("usuario",)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tipo", "leida", "fecha")
    list_filter = ("tipo", "leida")
    search_fields = ("usuario__email", "mensaje")
    list_select_related = ("usuario",)
