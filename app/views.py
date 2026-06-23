"""Vistas públicas de la aplicación de ferias."""
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Emprendedor, Inscripcion, Feria, Resena, Categoria
from .forms import RegistroEmprendedorForm, RegistroVisitanteForm, InscripcionForm, FeriaForm, ResenaForm
from datetime import timedelta
from django.views import View
from django.utils import timezone


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


class PerfilUsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'ferias/perfil_usuario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = get_object_or_404(User, pk=self.kwargs['pk'])
        es_perfil_propio = self.request.user.pk == usuario.pk

        visitante_actual = None
        if self.request.user.is_authenticated:
            try:
                visitante_actual = self.request.user.visitante
            except ObjectDoesNotExist:
                pass
        context['visitante_actual'] = visitante_actual

        try:
            perfil_emprendedor = usuario.emprendedor
        except ObjectDoesNotExist:
            perfil_emprendedor = None

        try:
            perfil_visitante = usuario.visitante
        except ObjectDoesNotExist:
            perfil_visitante = None

        context['perfil_usuario'] = usuario
        context['perfil_emprendedor'] = perfil_emprendedor
        context['perfil_visitante'] = perfil_visitante
        context['es_perfil_propio'] = es_perfil_propio

        if context['perfil_visitante']:
            context['rol_perfil'] = 'Visitante'
            context['cantidad_resenas'] = Resena.objects.filter(visitante=context['perfil_visitante']).count()
        elif context['perfil_emprendedor']:
            context['rol_perfil'] = 'Emprendedor'
            
            resenas = Resena.objects.filter(feriante=context['perfil_emprendedor']).order_by('-fecha_creacion')
            context['cantidad_resenas'] = resenas.count()
            context['ultimas_resenas'] = resenas[:5]
            
            hoy = timezone.now().date()
            context['proximas_inscripciones'] = (
                Inscripcion.objects
                .filter(
                    emprendedor=context['perfil_emprendedor'],
                    feria__fecha_inicio__gte=hoy,
                    estado='confirmada'
                )
                .select_related('feria')
                .order_by('feria__fecha_inicio')
            )
        else:
            context['rol_perfil'] = 'Sin perfil asociado'
            context['cantidad_resenas'] = 0

        return context


class PerfilPropioRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('ferias:perfil_usuario', pk=request.user.pk)


class RegistroTipoView(TemplateView):
    template_name = 'ferias/registro_tipo.html'


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


class DetalleFeriaView(DetailView):
    model = Feria
    template_name = 'ferias/detalle_feria.html'
    context_object_name = 'feria'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        visitante_actual = None
        if self.request.user.is_authenticated:
            try:
                visitante_actual = self.request.user.visitante
            except ObjectDoesNotExist:
                pass
        context['visitante_actual'] = visitante_actual

        feria = self.object
        inscripciones_confirmadas = (
            Inscripcion.objects
            .filter(feria=feria, estado='confirmada')
            .select_related('emprendedor')
            .order_by('numero_puesto', 'emprendedor__apellido', 'emprendedor__nombre')
        )
        total_ocupados = inscripciones_confirmadas.count()
        capacidad = feria.capacidad_puestos or 0
        ocupacion_porcentaje = int((total_ocupados / capacidad) * 100) if capacidad else 0
        emprendedores_unicos = []
        vistos = set()
        for inscripcion in inscripciones_confirmadas:
            if inscripcion.emprendedor_id in vistos:
                continue
            vistos.add(inscripcion.emprendedor_id)
            emprendedores_unicos.append(inscripcion.emprendedor)

        context['inscripciones_confirmadas'] = inscripciones_confirmadas
        context['emprendedores'] = emprendedores_unicos
        context['total_ocupados'] = total_ocupados
        context['ocupacion_porcentaje'] = min(ocupacion_porcentaje, 100)
        context['puestos_disponibles'] = feria.puestos_disponibles()
        context['capacidad_total'] = capacidad
        return context

#Vista para registrar un nuevo emprendedor
class RegistroEmprendedorView(SuccessMessageMixin, CreateView):
    template_name = 'ferias/registro_emprendedor.html'
    form_class = RegistroEmprendedorForm
    success_message = "Tu perfil fue creado con éxito, ya podés iniciar sesión."

    def form_valid(self, form):
        self.object = form.save()
        usuario = self.object.usuario
        usuario_autenticado = authenticate(
            self.request,
            username=usuario.username,
            password=form.cleaned_data['password'],
        )

        if usuario_autenticado is not None:
            login(self.request, usuario_autenticado)

        messages.success(self.request, self.success_message)
        return redirect('ferias:perfil_usuario', pk=usuario.pk)



class RegistroVisitanteView(SuccessMessageMixin, CreateView):
    template_name = 'ferias/registro_visitante.html'
    form_class = RegistroVisitanteForm
    success_url = reverse_lazy('ferias:login')
    success_message = "Tu perfil de visitante fue creado con exito, ya puedes iniciar sesión."

    def form_valid(self, form):
        self.object = form.save()
        usuario = self.object.usuario
        usuario_autenticado = authenticate(
            self.request,
            username=usuario.username,
            password=form.cleaned_data['password'],
        )

        if usuario_autenticado is not None:
            login(self.request, usuario_autenticado)

        messages.success(self.request, self.success_message)
        return redirect('ferias:perfil_usuario', pk=usuario.pk)


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

class ListaResenasView(TemplateView):
    template_name = 'ferias/lista_resenas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_objetivo = get_object_or_404(User, pk=self.kwargs['pk'])
        
        context['es_perfil_propio'] = (self.request.user.is_authenticated and self.request.user.pk == usuario_objetivo.pk)

        try:
            perfil = usuario_objetivo.emprendedor
            context['tipo_perfil'] = 'emprendedor'
            context['perfil'] = perfil
            context['resenas'] = Resena.objects.filter(feriante=perfil).select_related('visitante').order_by('-fecha_creacion')
        except ObjectDoesNotExist:
            try:
                perfil = usuario_objetivo.visitante
                context['tipo_perfil'] = 'visitante'
                context['perfil'] = perfil
                context['resenas'] = Resena.objects.filter(visitante=perfil).select_related('feriante').order_by('-fecha_creacion')
            except ObjectDoesNotExist:
                context['tipo_perfil'] = None
                context['perfil'] = None
                context['resenas'] = []

        return context

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