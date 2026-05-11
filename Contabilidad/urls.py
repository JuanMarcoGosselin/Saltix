from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="contabilidad_dashboard"),
    path("reportes/nominas/", views.reporte_nominas_pdf, name="reporte_nominas_pdf"),
]
