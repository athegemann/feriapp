"""Vistas públicas de la aplicación de ferias."""
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import Emprendedor, Inscripcion
from .forms import RegistroEmprendedorForm, InscripcionForm
from django.views.generic import ListView, TemplateView
from .models import Feria, Categoria


class HomeView(TemplateView):
    """Vista de inicio. Por ahora vacía — completar con estadísticas."""

    template_name = "ferias/home.html"

    def get_context_data(self, **kwargs):
        """Agrega las estadísticas generales al contexto."""
        context = super().get_context_data(**kwargs)
        context['total_ferias'] = Feria.objects.count()
        context['ferias_activas'] = Feria.objects.filter(activa=True).count()
        context['total_categorias'] = Categoria.objects.count()
        return context


class ListaFeriasView(ListView):
    """Lista todas las ferias activas."""

    model = Feria
    template_name = "ferias/lista_ferias.html"
    context_object_name = "ferias"

    def get_queryset(self):
        """Retorna las ferias activas, filtradas por categoría si se solicita."""
        # la base que dejo el profe: solo ferias activas
        queryset = Feria.objects.filter(activa=True)
        
        # ID de la categoria si viene por la URL (ej: ?categoria=2)
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        """Agrega la lista de categorías para poder armar el menú de filtros en el HTML."""
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        # Envio el ID actual para saber que botón marcar como "activo" en el frontend
        context['categoria_actual'] = self.request.GET.get('categoria', '')
        return context

#Vista para registrar un nuevo emprendedor
class RegistroEmprendedorView(SuccessMessageMixin, CreateView):
    template_name = 'ferias/registro_emprendedor.html'
    form_class = RegistroEmprendedorForm
    success_url = reverse_lazy('login')
    success_message = "Tu perfil fue creado con éxito, ya podés iniciar sesión."

#Vista para ver mis inscripciones
class MisInscripcionesView(LoginRequiredMixin, ListView):
    model = Inscripcion
    template_name = 'ferias/mis_inscripciones.html'
    context_object_name = 'inscripciones'

    """Filtra para que el Emprendedor pueda ver sus inscripciones"""
    def get_queryset(self):
        return Inscripcion.objects.filter(emprendedor=self.request.user.emprendedor)
    
class NuevaInscripcionView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'ferias/nueva_inscripcion.html'
    form_class = InscripcionForm
    success_url = reverse_lazy('ferias:mis_inscripciones')
    success_message = "Tu inscripcion a la feria fue exitosa"

    def form_valid(self, form):
        emprendedor = self.request.user.emprendedor
        feria = form.cleaned_data['feria']
        numero_puesto = form.cleaned_data['numero_puesto']
        
        # se usa el filtro de seguridad del modelo
        nueva_inscrip, errors = Inscripcion.new(
            emprendedor=emprendedor,
            feria=feria,
            numero_puesto=numero_puesto,
            estado='confirmada',
            registrado_por=self.request.user
        )
        
        # detiene la operacion y envia el error a form 
        if errors:
            form.add_error(None, errors[0])
            return self.form_invalid(form)
            
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)
    
def cancelar_inscripcion_view(request, pk):
    if request.method == "POST" and request.user.is_authenticated:
        try: 
            inscripcion = Inscripcion.objects.get(pk=pk, emprendedor=request.user.emprendedor)
            
            errors = inscripcion.update(
                emprendedor=inscripcion.emprendedor,
                feria=inscripcion.feria,
                numero_puesto=inscripcion.numero_puesto,
                estado='cancelada',
                registrado_por=inscripcion.registrado_por
            )
            
            if not errors:
                messages.success(request, "La inscripción fue cancelada con éxito.")
            else:
                messages.error(request, errors[0])

        except Inscripcion.DoesNotExist:
            messages.error(request, "La inscripción solicitada no existe o no te pertenece.")

    return redirect('ferias:mis_inscripciones')
    
# TODO: implementar las siguientes vistas:
# class DetalleFeriaView(DetailView): ...
# class NuevaFeriaView(CreateView): ...
# class ListaEmprendedoresView(ListView): ...
# class NuevaInscripcionView(CreateView): ...
# class CancelarInscripcionView(View): ...