"""Configuración del panel de administración para la app principal."""

from django import forms
from django.core.exceptions import ValidationError
from django.contrib import admin
from .models import Feria, Emprendedor, Inscripcion, Categoria, Resena, Sector, Visitante

# 1. Formulario personalizado para validar fechas y meter calendarios en el Admin
class FeriaAdminForm(forms.ModelForm):
    class Meta:
        model = Feria
        fields = '__all__'
        widgets = {
            # Forzamos a que en el admin también salgan los calendarios nativos
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        """Validación cronológica exclusiva para el panel de administración"""
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de finalización no puede ser anterior a la de inicio.")
        
        return cleaned_data


# 2. Registro de Feria con su formulario y diseño customizado
@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    form = FeriaAdminForm  # <-- Enlazamos el formulario que creamos arriba
    
    list_display = ('nombre', 'categoria', 'fecha_inicio', 'fecha_fin', 'ubicacion', 'capacidad_puestos', 'activa')
    list_filter = ('activa', 'categoria', 'fecha_inicio')
    search_fields = ('nombre', 'ubicacion')
    
    # Agrupamos los campos del formulario en secciones visuales bien organizadas
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'categoria', 'ubicacion')
        }),
        ('Fechas de la Edición', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Capacidad y Disponibilidad', {
            'fields': ('capacidad_puestos', 'activa')
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Emprendedor)
class EmprendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'rubro', 'telefono', 'usuario')
    list_filter = ('rubro',)
    search_fields = ('nombre', 'apellido', 'email', 'rubro')
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'telefono')
        }),
        ('Datos de Negocio', {
            'fields': ('rubro',)
        }),
        ('Credenciales de Acceso', {
            'fields': ('usuario',),
        }),
    )


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('emprendedor', 'feria', 'numero_puesto', 'estado', 'fecha_inscripcion')
    list_filter = ('estado', 'feria', 'fecha_inscripcion')
    search_fields = ('emprendedor_nombre', 'emprendedor_apellido', 'feria_nombre', 'numero_puesto')


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'feria', 'capacidad_puestos', 'tiene_conexion_electrica')
    list_filter = ('tiene_conexion_electrica', 'feria')
    search_fields = ('nombre', 'feria__nombre')

@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email')
    search_fields = ('nombre', 'apellido', 'email')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('feriante', 'visitante', 'puntaje', 'comentario')
    search_fields = ('feriante__nombre', 'visitante__nombre', 'puntaje')