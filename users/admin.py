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
        "nombre",
        "apellido",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
        "rol_id",
    ]
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos", {"fields": ("nombre", "apellido", "rol_id")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nombre", "apellido", "password1", "password2", "is_active", "is_staff", "rol_id"),
        }),
    )


admin.site.register(Usuario, CustomUserAdmin)
