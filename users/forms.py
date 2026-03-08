from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from .models import Usuario

class CustomUserCreationForm(AdminUserCreationForm):   

    class Meta: 
        model = Usuario
        fields = ("email", "password", "nombre", "apellido", "is_active", "date_joined", "last_login", "rol_id")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ("username", "email")