from django.contrib import admin

from .models import (
    Nomina,
    Periodo,
    CatalogoConcepto,
    DetalleNomina,
    ReciboNomina,
    VistaPreviaNomina,
)


@admin.register(Nomina)
class NominaAdmin(admin.ModelAdmin):
    list_display = ("profesor", "periodo", "total_bruto", "total_neto", "fecha_de_generacion")
    list_filter = ("periodo",)
    search_fields = ("profesor__usuario__nombre", "profesor__usuario__apellido")
    list_select_related = ("profesor", "periodo")


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ("plantel", "tipo", "fecha_inicio", "fecha_fin", "estado")
    list_filter = ("plantel", "tipo", "estado")
    list_select_related = ("plantel",)


@admin.register(CatalogoConcepto)
class CatalogoConceptoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "clasificacion_fiscal", "activo")
    list_filter = ("tipo", "clasificacion_fiscal", "activo")
    search_fields = ("nombre",)


@admin.register(DetalleNomina)
class DetalleNominaAdmin(admin.ModelAdmin):
    list_display = ("nomina", "concepto", "monto")
    list_filter = ("concepto",)
    list_select_related = ("nomina", "concepto")


@admin.register(ReciboNomina)
class ReciboNominaAdmin(admin.ModelAdmin):
    list_display = ("nomina", "fecha_emision")
    list_filter = ("fecha_emision",)
    list_select_related = ("nomina",)


@admin.register(VistaPreviaNomina)
class VistaPreviaNominaAdmin(admin.ModelAdmin):
    list_display = ("periodo", "generado_por", "fecha_generacion")
    list_filter = ("periodo",)
    list_select_related = ("periodo", "generado_por")
