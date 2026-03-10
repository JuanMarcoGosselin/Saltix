from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Usuario, Rol, Permiso, RolPermiso, Departamento


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


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion")
    search_fields = ("codigo", "descripcion")


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    list_display = ("rol", "permiso")
    list_filter = ("rol",)
    list_select_related = ("rol", "permiso")


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "jefe", "plantel", "activo")
    list_filter = ("plantel", "activo")
    search_fields = ("nombre", "jefe__email")
    list_select_related = ("jefe", "plantel")
