from django.db import models
from django.utils import timezone

class Usuario(models.Model): 
    email = models.EmailField(max_length= 254, unique=True)
    password = models.CharField(max_length= 128)
    nombre = models.CharField(max_length= 50, blank= False, null = False)
    apellido = models.CharField(max_length= 50, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.TimeField(null= True, blank = True)
    rol_id = models.ForeignKey('Rol', on_delete=models.PROTECT, null=True, blank=True, related_name='users')

class Rol(models.Model): 
    nombre = models.CharField(max_length=50, blank=False, null=False)
    descripcion = models.TextField(max_length= 1000, blank= True, null=True)

class Departamnto(models.Model): 
    nombre = models.CharField(max_length=40)
    description = models.CharField(max_length=1000)
    jefe = models.ForeignKey("Usuario", on_delete=models.PROTECT) 
