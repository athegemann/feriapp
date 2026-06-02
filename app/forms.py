from django import forms
from django.contrib.auth.models import User
from django.db import transaction 
from .models import Emprendedor, Inscripcion

class RegistroEmprendedorForm(forms.ModelForm):
    """Formulario para registrar a un Usuario(django) y un emprendedor"""

    #Parte de usuario
    username = forms.CharField( max_length=150,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Gerardo42'})
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Mínimo 8 caracteres'})
    )

    #Parte de emprendedor
    nombre = forms.CharField(max_length= 100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )

    apellido = forms.CharField(max_length= 100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'})
    )


    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Tucorreo@gmail.com'})
    )

    rubro = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Gastronomía, Madera, Tejido'})
    )

    telefono = forms.CharField(
        max_length=50,
        required=False,
        label="Teléfono (Opcional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +54 2901 123456'})
    )

    class Meta:
        model = Emprendedor
        fields = ['nombre', 'apellido', 'email', 'rubro', 'telefono']

    def clean_username(self): 
        """Valida que el nombre de usuario no esté tomado en el sistema"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está registrado. Ingrese otro.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Se usa el metodo Validate de la clase Emprendedor para mantener la coherencia
        nombre = self.cleaned_data.get('nombre', 'temp') or 'temp'
        apellido = self.cleaned_data.get('apellido', 'temp') or 'temp'
        rubro = self.cleaned_data.get('rubro', 'temp') or 'temp'

        errors = Emprendedor.validate(
            nombre=nombre,
            apellido=apellido,
            email=email,
            rubro=rubro,
            usuario=None  # Evita que Django busque un usuario no guardado
        )
        # Buscar el error especifico de mail 
        for error in errors:
            if "email" in error.lower():
                raise forms.ValidationError(error)
        return email

    def save(self, commit=True):
        """ 
        Si algo falla creando el Emprendedor, no se crea el Usuario (viceversa),
        esto lo hace sobrescribiendo el guardado en una transaccion atomica
        """
        # Con atomic() asegura la consistencia de la BD si cae el servidor a mitad del proceso 
        with transaction.atomic():
            #  Se crea y se guarda el usuario primero
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password']
            )
            
            #  Se utiliza el método estricto .new() del modelo Emprendedor
            emprendedor, errors = Emprendedor.new(
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                email=self.cleaned_data['email'],
                rubro=self.cleaned_data['rubro'],
                usuario=user,
                telefono=self.cleaned_data.get('telefono', '')
            )
            
            if errors:
                # Si el modelo rechaza los datos por reglas de negocio, lanza una excepción para hacer rollback
                raise forms.ValidationError(errors[0])
                
            return emprendedor

class InscripcionForm(forms.ModelForm):
    """Formulario para que un emprendedor solicite un puesto"""
    class Meta: 
        model = Inscripcion
        fields = ['feria', 'numero_puesto']
        widgets = {
            'feria': forms.Select(attrs={'class': 'form-select'}),
            'numero_puesto': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Número de puesto'}),
        }