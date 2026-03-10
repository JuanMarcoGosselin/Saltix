from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class CustomUserCreationForm(UserCreationForm):   

    class Meta: 
        model = Usuario
        fields = ("email", "nombre", "apellido", "is_active", "is_staff", "rol_id")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ("email", "nombre", "apellido", "is_active", "last_login", "rol_id")
