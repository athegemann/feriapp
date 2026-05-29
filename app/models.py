"""Modelos de dominio para la aplicación de ferias."""

from __future__ import annotations
from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint

class Categoria(models.Model):
    """Representa una categoria tematica a la que pertenece una feria"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    @classmethod
    def validate(cls, nombre):
        """Valida los datos de la categoria, retorna una lista de errores"""
        errors = []
        if not nombre or not nombre.strip():
            errors.append("El nombre de la categoria es obligatorio.")
        return errors

    @classmethod
    def new(cls, nombre, descripcion=""):
        """Crea y persiste una nueva categoria si los datos son validos"""
        errors = cls.validate(nombre)
        if errors:
            return None, errors

        categoria = cls.objects.create(
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else ""
        )
        return categoria, []

    def update(self, nombre, descripcion=""):
        """Actualiza los datos de la categoria si son validos"""
        errors = self.__class__.validate(nombre)
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip() if descripcion else ""
        self.save()
        return []


class Feria(models.Model):
    """Representa una feria con su período, ubicación y capacidad disponible"""

    nombre = models.CharField(max_length=200)
    # categoria a ForeignKey como pedía el profe
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    ubicacion = models.CharField(max_length=200)
    capacidad_puestos = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["fecha_inicio"]

    def __str__(self):
        """Retorna una representación legible de la feria."""
        return self.nombre

    def puestos_ocupados(self):
        """Retorna la cantidad de inscripciones confirmadas."""
        if not hasattr(self, "inscripcion_set"):
            return 0
        return self.inscripcion_set.filter(estado="confirmada").count()

    def puestos_disponibles(self):
        """Retorna los puestos libres."""
        return self.capacidad_puestos - self.puestos_ocupados()

    def tiene_lugar(self):
        """Retorna True si quedan puestos disponibles."""
        return self.puestos_disponibles() > 0

    @classmethod
    def validate(
        cls, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
    ):
        """
        Valida los datos de la feria. Retorna una lista de errores.
        Si la lista está vacía, los datos son válidos.
        """
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")

        # Valida que venga un objeto de categoría
        if not categoria:
            errors.append("La categoría es obligatoria.")

        if not ubicacion or not ubicacion.strip():
            errors.append("La ubicación es obligatoria.")

        if capacidad_puestos is None or capacidad_puestos <= 0:
            errors.append("La capacidad de puestos debe ser mayor a cero.")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            errors.append("La fecha de fin no puede ser anterior a la fecha de inicio.")

        return errors

    @classmethod
    def new(
        cls, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
    ):
        """
        Crea y persiste una nueva feria si los datos son válidos.
        Retorna (instancia, errors). Si hay errores, instancia es None.
        """
        errors = cls.validate(
            nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
        )
        if errors:
            return None, errors

        feria = cls.objects.create(
            nombre=nombre.strip(),
            categoria=categoria, # Ya no lleva .strip() porque es ForeignKey
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            ubicacion=ubicacion.strip(),
            capacidad_puestos=capacidad_puestos,
        )
        return feria, []

    def update(
        self, nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
    ):
        """
        Actualiza los datos de la feria si los datos son válidos.
        Retorna una lista de errores. Si está vacía, la actualización fue exitosa.
        """
        errors = self.__class__.validate(
            nombre, categoria, fecha_inicio, fecha_fin, ubicacion, capacidad_puestos
        )
        if errors:
            return errors

        self.nombre = nombre.strip()
        self.categoria = categoria # Ya no lleva .strip() porque es un objeto ForeignKey
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.ubicacion = ubicacion.strip()
        self.capacidad_puestos = capacidad_puestos
        self.save()
        return []


class Emprendedor(models.Model):
    """Variables de La Clase Emprendedor"""
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rubro = models.CharField(max_length=100)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="emprendedor")

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rubro})"
    
    @classmethod
    def validate(cls, nombre, apellido, email, rubro, usuario, instance_id=None) -> list[str]:
        """validar los datos del Emprendedor"""
        errors = []

        if not nombre or not nombre.strip():
            errors.append("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            errors.append("El apellido es obligatorio.")
            
        if not email or not email.strip():
            errors.append("El email es obligatorio.")
        elif cls.objects.filter(email=email).exclude(id=instance_id).exists():
            errors.append("Ya existe un emprendedor registrado con este email.")
            
        if not rubro or not rubro.strip():
            errors.append("El rubro es obligatorio.")
            
        if not usuario:
            errors.append("El usuario asociado es obligatorio.")
        elif cls.objects.filter(usuario=usuario).exclude(id=instance_id).exists():
            errors.append("Este usuario ya está vinculado a otro emprendedor.")
            
        return errors
    
    @classmethod
    def new(cls, nombre, apellido, email, rubro, usuario, telefono=None):
        """Actua como filtro de seguridad: valida los datos primero y, solo si todo está perfecto, crea y guarda el nuevo Emprendedor en la base de datos"""
        errors = cls.validate(nombre, apellido, email, rubro, usuario)
        if errors:
            return None, errors
        
        """Elimina los espacios en blanco innecesarios de los atributos(strip()) """
        emprendedor = cls.objects.create(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip(),
            rubro=rubro.strip(),
            usuario=usuario,
            telefono=telefono.strip() if telefono else None
        )
        return emprendedor, []
    
    def update(self, nombre, apellido, email, rubro, usuario, telefono=None) -> list[str]:
        """Actualiza los datos de Los Emprendedores Existentes si estos son validos"""
        errors = self.__class__.validate(nombre, apellido, email, rubro, usuario, instance_id=self.id)
        if errors:
            return errors
        
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()
        self.rubro = rubro.strip()
        self.usuario = usuario
        self.telefono = telefono.strip() if telefono else None
        self.save()
        return []
    

class Inscripcion(models.Model):
    """Representa el estado de un Emprendedor en una feria"""
    ESTADO_Incrip = [
        ('confirmada', 'Confirmada'),
        ('lista_espera', 'En lista de espera'),
        ('cancelada', 'Cancelada'),
    ]

    emprendedor = models.ForeignKey(Emprendedor, on_delete=models.CASCADE)
    feria = models.ForeignKey(Feria, on_delete=models.CASCADE)
    numero_puesto = models.PositiveIntegerField()
    fecha_inscripcion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_Incrip, default='confirmada')
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    """Se crea la clase para que dos emprendedores no ocupen el mismo puesto en la misma feria"""
    class Meta:
        constraints = [
            UniqueConstraint(fields=["feria", "numero_puesto"], name="puesto_unico_por_feria")
        ]

    def __str__(self):
        return f"Inscripción de {self.emprendedor.nombre} - Puesto {self.numero_puesto} en {self.feria.nombre}"
    
    @classmethod
    def validate(cls, emprendedor, feria, numero_puesto, estado, registrado_por, instance_id=None) -> list[str]:
        """Verifica las reglas de negocio de la inscripción"""
        errors = []
        if not emprendedor:
            errors.append("El emprendedor es obligatorio.")
        if not feria:
            errors.append("La feria es obligatoria.")
        
        if numero_puesto is None or numero_puesto <= 0:
            errors.append("El número de puesto debe ser mayor a cero.")
        elif feria and numero_puesto > feria.capacidad_puestos:
            errors.append(f"El número de puesto no puede exceder la capacidad de la feria ({feria.capacidad_puestos}).")
        
        if feria and numero_puesto:
            # Validar que el puesto no est reservado por otra inscripcion activa (no cancelada)
            ocupado = cls.objects.filter(feria=feria, numero_puesto=numero_puesto).exclude(estado='cancelada')
            if instance_id:
                ocupado = ocupado.exclude(id=instance_id)
            if ocupado.exists():
                errors.append(f"El puesto {numero_puesto} ya está ocupado en esta feria.")

        # CORRECCION DE BUG: Estaba como dict(cls.ESTADO_CHOICES) pero la variable se llama ESTADO_Incrip
        if estado not in dict(cls.ESTADO_Incrip):
            errors.append("El estado especificado no es válido.")

        return errors

    @classmethod
    def new(cls, emprendedor, feria, numero_puesto, estado='confirmada', registrado_por=None):
        """Genera una nueva inscripción si pasa las validaciones de negocio"""
        errors = cls.validate(emprendedor, feria, numero_puesto, estado, registrado_por)
        if errors:
            return None, errors

        inscripcion = cls.objects.create(
            emprendedor=emprendedor,
            feria=feria,
            numero_puesto=numero_puesto,
            estado=estado,
            registrado_por=registrado_por
        )
        return inscripcion, []
    

    def update(self, emprendedor, feria, numero_puesto, estado, registrado_por) -> list[str]:
        """Actualiza los datos de la Inscripcion Existentes si estos son validos"""
        errors = self.__class__.validate(emprendedor, feria, numero_puesto, estado, registrado_por, instance_id=self.id)
        if errors:
            return errors

        self.emprendedor = emprendedor
        self.feria = feria
        self.numero_puesto = numero_puesto
        self.estado = estado
        self.registrado_por = registrado_por
        self.save()
        return []