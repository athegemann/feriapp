"""Definición de rutas públicas de la aplicación."""
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "ferias"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ferias/", views.ListaFeriasView.as_view(), name="lista_ferias"),

    # Autenticación (Login, Logout y formulario de registros)
    path("login/", auth_views.LoginView.as_view(template_name="registro/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("registro/", views.RegistroEmprendedorView.as_view(), name="registro_emprendedor"),

    # Gestión de Inscripciones
    path("inscripciones/mis-inscripciones/", views.MisInscripcionesView.as_view(), name="mis_inscripciones"),
    path("inscripciones/nueva/", views.NuevaInscripcionView.as_view(), name="nueva_inscripcion"),
    path("inscripciones/<int:pk>/cancelar/", views.cancelar_inscripcion_view, name="cancelar_inscripcion"),

    # Gestion de Reseñas
    path("resenas/nueva/", views.NuevaResenaView.as_view(), name="nueva_resena"),
    
    # Gestión de Ferias (Tu Eje)
    path("ferias/nueva/", views.NuevaFeriaView.as_view(), name="nueva_feria"),
    path("ferias/<int:pk>/clonar/", views.ClonarFeriaView.as_view(), name="clonar_feria"),
    
    # TODO: Vistas de Javirulo (Social y Métricas)
    # path("ferias/<int:pk>/", views.DetalleFeriaView.as_view(), name="detalle_feria"),
    # path("emprendedores/", views.ListaEmprendedoresView.as_view(), name="lista_emprendedores"),
]
