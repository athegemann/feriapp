"""Definición de rutas públicas de la aplicación."""

from django.urls import path
from . import views

app_name = "ferias"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ferias/", views.ListaFeriasView.as_view(), name="lista_ferias"),
    # TODO:
    # path("ferias/<int:pk>/", views.DetalleFeriaView.as_view(), name="detalle_feria"),
    # path("ferias/nueva/", views.NuevaFeriaView.as_view(), name="nueva_feria"),
    # path("emprendedores/", views.ListaEmprendedoresView.as_view(), name="lista_emprendedores"),
    # path("inscripciones/nueva/", views.NuevaInscripcionView.as_view(), name="nueva_inscripcion"),
]
