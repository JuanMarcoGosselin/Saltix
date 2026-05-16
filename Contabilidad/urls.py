from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="contabilidad_dashboard"),
    path("procesar-nomina/<int:profesor_id>/", views.procesar_nomina, name="procesar_nomina"),
    path("nomina/<int:nomina_id>/", views.detalle_nomina, name="detalle_nomina"),
    path("nomina/<int:nomina_id>/pdf/", views.recibo_nomina_pdf, name="recibo_nomina_pdf"),
    path("nomina/<int:nomina_id>/print/", views.recibo_nomina_print, name="recibo_nomina_print"),
    path("nomina/<int:nomina_id>/regenerar/", views.regenerar_nomina, name="regenerar_nomina"),
    path("nomina/<int:nomina_id>/conceptos/agregar/", views.agregar_concepto, name="agregar_concepto_nomina"),
    path("nomina/conceptos/<int:detalle_id>/eliminar/", views.eliminar_concepto, name="eliminar_concepto_nomina"),
    path("nomina/<int:nomina_id>/cerrar/", views.cerrar_nomina, name="cerrar_nomina"),
    path("generar-nominas/", views.generar_nominas, name="generar_nominas"),
    path("regenerar-nominas/", views.regenerar_nominas, name="regenerar_nominas"),
    path("abrir-periodo/", views.abrir_periodo, name="abrir_periodo"),
    path("periodo/<int:periodo_id>/", views.reporte_periodo, name="reporte_periodo"),
    path("periodo/<int:periodo_id>/preview/", views.vista_previa_periodo, name="vista_previa_periodo"),
    path("periodo/<int:periodo_id>/pdf/", views.reporte_periodo_pdf, name="reporte_periodo_pdf"),
    path("periodo/<int:periodo_id>/print/", views.reporte_periodo_print, name="reporte_periodo_print"),
    path("cerrar-periodo/<int:periodo_id>/", views.cerrar_periodo, name="cerrar_periodo"),
    path("pagar-nomina/<int:nomina_id>/", views.pagar_nomina, name="pagar_nomina"),
]
