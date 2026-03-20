from django.urls import path

from . import views

app_name = "asistencias"

urlpatterns = [
    path("justificar/", views.justificar_asistencia, name="justificar_asistencia"),
]

