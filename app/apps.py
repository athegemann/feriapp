"""Configuración de Django para la aplicación de ferias."""

from django.apps import AppConfig

class FeriasConfig(AppConfig):
    """Metadatos de registro de la aplicación en Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    verbose_name = "Ferias"