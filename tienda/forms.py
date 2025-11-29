from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario

# Formulario para Registrarse (Crea el usuario y encripta la clave)
class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'telefono']
        # AQUÍ TRADUCIMOS LAS ETIQUETAS
        labels = {
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'telefono': 'Teléfono de contacto',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user

# Formulario para Iniciar Sesión (Valida correo y clave)
class LoginUsuarioForm(AuthenticationForm):
    username = forms.EmailField(label="Correo Electrónico")