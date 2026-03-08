from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Usuario


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Usuario
    list_display = [
        "email",
        "password",
        "nombre",
        "apellido",
        "is_active",
        "date_joined",
        "last_login",
        "rol_id",
    ]


admin.site.register(Usuario, CustomUserAdmin)