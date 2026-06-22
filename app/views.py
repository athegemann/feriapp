"""Vistas públicas de la aplicación de ferias."""
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Emprendedor, Inscripcion, Feria, Resena
from .forms import RegistroEmprendedorForm, InscripcionForm, FeriaForm, ResenaForm
from django.views.generic import ListView, TemplateView
from .models import Feria, Categoria
from datetime import timedelta
from django.views import View


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


class MiPerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'ferias/mi_perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        context['perfil_usuario'] = usuario
        context['perfil_emprendedor'] = getattr(usuario, 'emprendedor', None)
        context['perfil_visitante'] = getattr(usuario, 'visitante', None)

        if context['perfil_visitante']:
            context['rol_perfil'] = 'Visitante'
            context['cantidad_resenas'] = Resena.objects.filter(visitante=context['perfil_visitante']).count()
        elif context['perfil_emprendedor']:
            context['rol_perfil'] = 'Emprendedor'
            context['cantidad_resenas'] = Resena.objects.filter(feriante=context['perfil_emprendedor']).count()
        else:
            context['rol_perfil'] = 'Sin perfil asociado'
            context['cantidad_resenas'] = 0

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
    success_url = reverse_lazy('ferias:login') #Fix para redirigir al login después del registro
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
                messages.success(request, "La inscripción fue cancelada con exito")
            else:
                messages.error(request, errors[0])

        except Inscripcion.DoesNotExist:
            messages.error(request, "La inscripción solicitada no existe o no te pertenece")

    return redirect('ferias:mis_inscripciones')

class NuevaFeriaView(CreateView):
    model = Feria
    form_class = FeriaForm
    template_name = 'ferias/nueva_feria.html' 
    success_url = reverse_lazy('ferias:home')

    def form_valid(self, form):
        """
        Sobreescribimos form_valid para usar el patrón estricto new()
        en lugar del save() por defecto de Django.
        """
        datos = form.cleaned_data
        
        # Llamamos al método de clase que programaste
        feria, errores = Feria.new(
            nombre=datos['nombre'],
            categoria=datos['categoria'],
            fecha_inicio=datos['fecha_inicio'],
            fecha_fin=datos['fecha_fin'],
            ubicacion=datos['ubicacion'],
            capacidad_puestos=datos['capacidad_puestos']
        )

        if errores:
            # Si la validación de negocio falla (ej. fechas invertidas)
            for error in errores:
                messages.error(self.request, error)
            return self.form_invalid(form)

        # Si todo sale bien, simula el registro exitoso para la vista
        self.object = feria
        messages.success(self.request, "¡La feria se creó exitosamente!")
        return super().form_valid(form)


class NuevaResenaView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'ferias/nueva_resena.html'
    form_class = ResenaForm
    success_url = reverse_lazy('ferias:lista_ferias')
    success_message = "Tu reseña fue publicada con exito."

    def form_valid(self, form):
        try:
            visitante = self.request.user.visitante
        except ObjectDoesNotExist:
            form.add_error(None, "Necesitas tener un perfil de visitante para dejar una reseña.")
            return self.form_invalid(form)

        datos = form.cleaned_data
        resena, errors = Resena.new(
            feriante=datos['feriante'],
            visitante=visitante,
            puntaje=datos['puntaje'],
            comentario=datos.get('comentario', '')
        )

        if errors:
            for error in errors:
                messages.error(self.request, error)
            return self.form_invalid(form)

        self.object = resena
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)


class MisResenasView(LoginRequiredMixin, ListView):
    model = Resena
    template_name = 'ferias/mis_resenas.html'
    context_object_name = 'resenas'

    def dispatch(self, request, *args, **kwargs):
        try:
            request.user.emprendedor
        except ObjectDoesNotExist:
            messages.error(request, "Necesitas tener un perfil de emprendedor para ver tus reseñas.")
            return redirect('ferias:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Resena.objects
            .filter(feriante=self.request.user.emprendedor)
            .select_related('visitante', 'feriante')
            .order_by('-fecha_creacion')
        )

class ClonarFeriaView(View):
    """
    CBV para manejar la acción de clonar una feria.
    Solo acepta peticiones POST por seguridad.
    """
    def post(self, request, pk):
        # Buscamos la feria original que queremos clonar
        feria_original = get_object_or_404(Feria, pk=pk)
        
        # Para hacer el clon rápido con un solo clic, pateamos las fechas exactamente 1 año (365 días)
        # Esto automatiza la gestión anual de las ediciones de la municipalidad.
        nueva_fecha_inicio = feria_original.fecha_inicio + timedelta(days=365)
        nueva_fecha_fin = feria_original.fecha_fin + timedelta(days=365)
        
        # Llamamos a tu método de negocio complejo
        nueva_feria, errores = feria_original.clonar_edicion(
            nueva_fecha_inicio, 
            nueva_fecha_fin
            # No le pasamos nombre, así el modelo usa el nombre por defecto " - Nueva Edición"
        )
        
        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            messages.success(request, f"¡Edición clonada con éxito! Se creó: {nueva_feria.nombre}")
            
        # Redirigimos a la lista de ferias
        return redirect('ferias:lista_ferias')
    
# TODO: implementar las siguientes vistas...
# class DetalleFeriaView(DetailView): ...
# class ListaEmprendedoresView(ListView): ...
# class NuevaInscripcionView(CreateView): ...
# class CancelarInscripcionView(View): ...