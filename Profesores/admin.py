from django.contrib import admin

from .models import Profesor, Horario, TransferenciaDepartamento


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rfc", "estado_laboral", "departamento", "plantel")
    list_filter = ("estado_laboral", "departamento", "plantel")
    search_fields = ("usuario__nombre", "usuario__apellido", "rfc", "curp")
    list_select_related = ("usuario", "departamento", "plantel")


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("profesor", "dia_semana", "hora_inicio", "hora_fin", "aula", "es_hora_clase")
    list_filter = ("dia_semana", "es_hora_clase")
    search_fields = ("profesor__usuario__nombre", "aula")
    list_select_related = ("profesor",)


@admin.register(TransferenciaDepartamento)
class TransferenciaDepartamentoAdmin(admin.ModelAdmin):
    list_display = ("profesor", "departamento_origen", "departamento_destino", "fecha", "aprobado_por")
    list_filter = ("departamento_origen", "departamento_destino")
    search_fields = ("profesor__usuario__nombre",)
    list_select_related = ("profesor", "departamento_origen", "departamento_destino", "aprobado_por")
