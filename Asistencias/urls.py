from django.urls import path

from . import views

app_name = "asistencias"

urlpatterns = [
    path("justificar/", views.justificar_asistencia, name="justificar_asistencia"),
    path("jefatura/asistencias/", views.listar_asistencias_jefatura, name="listar_asistencias_jefatura"),
    path("jefatura/incidencias/", views.listar_incidencias_jefatura, name="listar_incidencias_jefatura"),
    path("jefatura/incidencias/aprobar/", views.aprobar_incidencia, name="aprobar_incidencia"),
    path("jefatura/incidencias/rechazar/", views.rechazar_incidencia, name="rechazar_incidencia"),
    path("jefatura/asistencias/cancelar/", views.cancelar_asistencia_institucional, name="cancelar_asistencia_institucional"),
    path("jefatura/asistencias/corregir/", views.corregir_asistencia_jefatura, name="corregir_asistencia_jefatura"),
]

