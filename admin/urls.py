from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="admin_dashboard"),
    path("usuarios/crear/", views.create_user, name="admin_create_user"),
    path("usuarios/editar/", views.update_user, name="admin_update_user"),
    path("planteles/crear/", views.create_plantel, name="admin_create_plantel"),
    path("planteles/editar/", views.update_plantel, name="admin_update_plantel"),
    path("departamentos/crear/", views.create_departamento, name="admin_create_departamento"),
    path("departamentos/editar/", views.update_departamento, name="admin_update_departamento"),
]
