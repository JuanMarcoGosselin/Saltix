from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin): 
    # Usuario base del sistema para login y roles.
    email = models.EmailField(max_length=254, unique=True)
    nombre = models.CharField(max_length=50, blank=False, null=False)
    apellido = models.CharField(max_length=50, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    rol_id = models.ForeignKey('Rol', on_delete=models.PROTECT, null=True, blank=True, related_name='users')

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "apellido"]

    def __str__(self):
        return self.nombre

class Rol(models.Model): 
    # Rol funcional del sistema (admin, jefatura, profesor, etc).
    nombre = models.CharField(max_length=50, blank=False, null=False)
    descripcion = models.TextField(max_length=1000, blank=True, null=True)

class Permiso(models.Model):
    # Permiso granular por accion del sistema.
    codigo = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=255)

class RolPermiso(models.Model):
    # Relacion N:M entre rol y permiso.
    rol = models.ForeignKey("Rol", on_delete=models.CASCADE)
    permiso = models.ForeignKey("Permiso", on_delete=models.CASCADE)

class Departamento(models.Model): 
    # Departamento con jefe asignado y ligado a un plantel.
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=1000)
    jefe = models.ForeignKey("Usuario", on_delete=models.PROTECT)
    plantel = models.ForeignKey("core.Plantel", on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)
