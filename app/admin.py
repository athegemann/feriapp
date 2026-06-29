"""Configuración del panel de administración para la app principal."""

from django.contrib import admin
from .models import Feria, Emprendedor, Inscripcion, Categoria, Sector

# TODO: reemplazar por @admin.register con list_display, list_filter, search_fields
@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'fecha_inicio', 'fecha_fin', 'ubicacion', 'capacidad_puestos', 'activa')
    list_filter = ('activa', 'categoria', 'fecha_inicio')
    search_fields = ('nombre', 'ubicacion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Emprendedor)
class EmprendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'rubro', 'usuario')
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