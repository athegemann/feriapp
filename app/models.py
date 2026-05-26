"""Modelos de dominio para la aplicación de ferias."""

from __future__ import annotations
from django.db import models

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
    # Extraemos categoria a ForeignKey como pedía el profe
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

        # Validamos que venga un objeto de categoría
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

    # TODO: Falta agregar los siguientes modelos:
    # class Emprendedor(models.Model): ...
    # class Inscripcion(models.Model): ...