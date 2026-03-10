from django.contrib import admin

from .models import (
    Asistencia,
    Incidencia,
    EvidenciaIncidencia,
    SolicitudCorreccion,
    CorreccionAsistencia,
)


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("profesor", "fecha", "estado", "tipo_registro", "justificada", "cancelada_institucional")
    list_filter = ("estado", "tipo_registro", "justificada", "cancelada_institucional")
    search_fields = ("profesor__usuario__nombre", "profesor__usuario__apellido")
    list_select_related = ("profesor", "horario")


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ("asistencia", "tipo", "estado", "solicitante", "aprobador", "fecha_solicitud")
    list_filter = ("tipo", "estado")
    search_fields = ("asistencia__profesor__usuario__nombre", "motivo")
    list_select_related = ("asistencia", "solicitante", "aprobador")


@admin.register(EvidenciaIncidencia)
class EvidenciaIncidenciaAdmin(admin.ModelAdmin):
    list_display = ("incidencia", "fecha_subida")
    search_fields = ("incidencia__motivo",)
    list_select_related = ("incidencia",)


@admin.register(SolicitudCorreccion)
class SolicitudCorreccionAdmin(admin.ModelAdmin):
    list_display = ("profesor", "estado", "fecha_solicitud", "aprobador")
    list_filter = ("estado",)
    search_fields = ("profesor__usuario__nombre", "motivo")
    list_select_related = ("profesor", "aprobador")


@admin.register(CorreccionAsistencia)
class CorreccionAsistenciaAdmin(admin.ModelAdmin):
    list_display = ("asistencia_original", "asistencia_compensatoria", "aprobada_por", "fecha_aprobacion")
    search_fields = ("motivo",)
    list_select_related = ("asistencia_original", "asistencia_compensatoria", "aprobada_por")
