"""Tests de comportamiento para los modelos Categoria y Feria."""

from datetime import date
from django.test import TestCase
from app.models import Feria, Categoria

# --- TESTS DEL MODELO CATEGORIA ---

class CategoriaModelTest(TestCase):
    
    def test_validate_nombre_vacio(self):
        errores = Categoria.validate(nombre="")
        self.assertIn("El nombre de la categoria es obligatorio.", errores)

    def test_new_categoria_exitosa(self):
        categoria, errores = Categoria.new(nombre="Gastronomía", descripcion="Puestos de comida")
        self.assertEqual(errores, [])
        self.assertIsNotNone(categoria)
        self.assertEqual(categoria.nombre, "Gastronomía")
        self.assertEqual(Categoria.objects.count(), 1)

    def test_update_categoria_exitosa(self):
        categoria, _ = Categoria.new(nombre="Ropa")
        errores = categoria.update(nombre="Indumentaria", descripcion="Ropa local")
        self.assertEqual(errores, [])
        self.assertEqual(categoria.nombre, "Indumentaria")
        self.assertEqual(categoria.descripcion, "Ropa local")


# --- TESTS DEL MODELO FERIA (con ForeignKey) ---

class FeriaModelTest(TestCase):
    """Verifica validaciones y operaciones básicas del modelo Feria."""

    def setUp(self):
        """Crea una categoría y una feria base reutilizable para cada caso de prueba."""
        # 1 Creo el objeto Categoria primero
        self.categoria = Categoria.objects.create(nombre="Artesanías")

        # 2 pasa a Feria
        self.feria = Feria.objects.create(
            nombre="Feria de Invierno",
            categoria=self.categoria,  # Uso el objeto, no un string
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 7, 3),
            ubicacion="Plaza Central",
            capacidad_puestos=10,
        )

    # --- __str__ y métodos simples ---

    def test_str_retorna_nombre(self):
        self.assertEqual(str(self.feria), "Feria de Invierno")

    def test_activa_por_defecto(self):
        self.assertTrue(self.feria.activa)

    def test_puestos_disponibles_igual_a_capacidad_sin_inscripciones(self):
        self.assertEqual(self.feria.puestos_disponibles(), 10)

    def test_tiene_lugar_true_con_capacidad_libre(self):
        self.assertTrue(self.feria.tiene_lugar())

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = Feria.validate(
            "Tech Patagonia",
            self.categoria, # Uso el objeto
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Centro Cultural",
            20,
        )
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Feria.validate(
            "",
            self.categoria,
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Centro Cultural",
            20,
        )
        self.assertTrue(len(errors) > 0)

    def test_validate_fecha_fin_anterior_a_inicio_retorna_error(self):
        errors = Feria.validate(
            "Feria",
            self.categoria,
            date(2026, 9, 10),
            date(2026, 9, 5),  # fin < inicio
            "Ubicación",
            10,
        )
        self.assertTrue(len(errors) > 0)

    def test_validate_capacidad_cero_retorna_error(self):
        errors = Feria.validate(
            "Feria",
            self.categoria,
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Ubicación",
            0,
        )
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_feria_con_datos_validos(self):
        feria, errors = Feria.new(
            "Mercado de Diseño",
            self.categoria,
            date(2026, 8, 1),
            date(2026, 8, 3),
            "Muelle Turístico",
            15,
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(feria)
        self.assertEqual(feria.nombre, "Mercado de Diseño")
        self.assertTrue(Feria.objects.filter(nombre="Mercado de Diseño").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Feria.objects.count()
        # Paso None en vez de un string vacio para simular que falta el objeto
        feria, errors = Feria.new("", None, None, None, "", 0)
        self.assertIsNone(feria)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Feria.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.feria.update(
            "Feria de Invierno",
            self.categoria,
            date(2026, 7, 1),
            date(2026, 7, 3),
            "Parque Central",
            20,
        )
        self.assertEqual(errors, [])
        self.feria.refresh_from_db()
        self.assertEqual(self.feria.ubicacion, "Parque Central")
        self.assertEqual(self.feria.capacidad_puestos, 20)

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.feria.update("", None, None, None, "", 0)
        self.assertTrue(len(errors) > 0)
        self.feria.refresh_from_db()
        self.assertEqual(self.feria.nombre, "Feria de Invierno")  # sin cambios