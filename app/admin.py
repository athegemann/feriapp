"""Configuración del panel de administración para la app principal."""

from django.contrib import admin
from .models import Feria, Emprendedor, Inscripcion, Categoria

# TODO: reemplazar por @admin.register con list_display, list_filter, search_fields
admin.site.register(Feria)

@admin.register(Emprendedor)
class EmprendedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'rubro', 'usuario')
    list_filter = ('rubro',)
    search_fields = ('nombre', 'apellido', 'email', 'rubro')

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('emprendedor', 'feria', 'numero_puesto', 'estado', 'fecha_inscripcion')
    list_filter = ('estado', 'feria', 'fecha_inscripcion')
    search_fields = ('emprendedor_nombre', 'emprendedor_apellido', 'feria_nombre', 'numero_puesto')