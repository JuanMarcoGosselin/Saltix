from django.contrib import admin

from .models import SolicitudAprobacion


@admin.register(SolicitudAprobacion)
class SolicitudAprobacionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "estado", "solicitante", "aprobador", "fecha_solicitud")
    list_filter = ("tipo", "estado")
    search_fields = ("solicitante__email", "aprobador__email")
    list_select_related = ("solicitante", "aprobador")
