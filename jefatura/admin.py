from django.contrib import admin

from .models import SolicitudAprobacion, SolicitudTransferencia


@admin.register(SolicitudAprobacion)
class SolicitudAprobacionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "estado", "solicitante", "aprobador", "fecha_solicitud")
    list_filter = ("tipo", "estado")
    search_fields = ("solicitante__email", "aprobador__email")
    list_select_related = ("solicitante", "aprobador")


@admin.register(SolicitudTransferencia)
class SolicitudTransferenciaAdmin(admin.ModelAdmin):
    list_display = ("profesor", "departamento_origen", "departamento_destino", "estado", "solicitante", "responsable", "fecha_solicitud")
    list_filter = ("estado", "departamento_origen", "departamento_destino")
    search_fields = ("profesor__usuario__nombre", "profesor__usuario__apellido", "motivo")
    list_select_related = ("profesor", "departamento_origen", "departamento_destino", "solicitante", "responsable")
