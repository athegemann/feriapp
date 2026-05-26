"""Tests de comportamiento para el modelo Feria."""

from datetime import date
from django.test import TestCase
from app.models import Feria
from django.contrib.auth.models import User
from app.models import Emprendedor, Inscripcion

class FeriaModelTest(TestCase):
    """Verifica validaciones y operaciones básicas del modelo Feria."""

    def setUp(self):
        """Crea una feria base reutilizable para cada caso de prueba."""
        self.feria = Feria.objects.create(
            nombre="Feria de Invierno",
            categoria="Artesanías",
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
            "Tecnología",
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Centro Cultural",
            20,
        )
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Feria.validate(
            "",
            "Tecnología",
            date(2026, 9, 1),
            date(2026, 9, 3),
            "Centro Cultural",
            20,
        )
        self.assertTrue(len(errors) > 0)

    def test_validate_fecha_fin_anterior_a_inicio_retorna_error(self):
        errors = Feria.validate(
            "Feria",
            "Categoría",
            date(2026, 9, 10),
            date(2026, 9, 5),  # fin < inicio
            "Ubicación",
            10,
        )
        self.assertTrue(len(errors) > 0)

    def test_validate_capacidad_cero_retorna_error(self):
        errors = Feria.validate(
            "Feria",
            "Categoría",
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
            "Artesanías",
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
        feria, errors = Feria.new("", "", None, None, "", 0)
        self.assertIsNone(feria)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Feria.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.feria.update(
            "Feria de Invierno",
            "Artesanías",
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
        errors = self.feria.update("", "", None, None, "", 0)
        self.assertTrue(len(errors) > 0)
        self.feria.refresh_from_db()
        self.assertEqual(self.feria.nombre, "Feria de Invierno")  # sin cambios

    # TODO: agregar tests para Emprendedor e Inscripcion cuando los implementen:

class EmprendedorEInscripcionModelTest(TestCase):
    
    def setUp(self):
        """Prepara el entorno y los objetos comunes para todas las pruebas de este eje."""
        # Creamos los usuarios con la misma convención de nombres
        self.user_pedro = User.objects.create_user(username="Pedro", password="password123")
        self.user_jose = User.objects.create_user(username="Jose", password="password123")
        
        # Feria de prueba con capacidad limitada a 2 puestos
        self.feria_test = Feria.objects.create(
            nombre="Feria de Prueba",
            categoria="Manualidades",
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 8, 5),
            ubicacion="Gimnasio Municipal",
            capacidad_puestos=2
        )

        # Emprendedor base ya registrado en el sistema
        self.emprendedor = Emprendedor.objects.create(
            nombre="Pedro",
            apellido="Gimenez",
            email="pedro@feria.com",
            rubro="Madera",
            usuario=self.user_pedro
        )

    # --- TESTS DE VALIDACIÓN DE EMPRENDEDOR ---

    def test_validate_emprendedor_correcto_retorna_vacio(self):
        errors = Emprendedor.validate("Jose", "Gomez", "jose@feria.com", "Tejido", self.user_jose)
        self.assertEqual(errors, [])

    def test_validate_emprendedor_email_duplicado_retorna_error(self):
        errors = Emprendedor.validate("Jose", "Gomez", "pedro@feria.com", "Tejido", self.user_jose)
        self.assertIn("Ya existe un emprendedor registrado con este email.", errors)

    def test_new_crea_emprendedor_exitosamente(self):
        emp, errors = Emprendedor.new("Jose", "Gomez", "jose@feria.com", "Tejido", self.user_jose)
        self.assertEqual(errors, [])
        self.assertIsNotNone(emp)
        self.assertEqual(emp.nombre, "Jose")

    # --- TESTS DE VALIDACIÓN DE INSCRIPCIÓN ---

    def test_validate_puesto_excede_capacidad_retorna_error(self):
        # Intentamos usar el puesto 3 en una feria de capacidad máxima 2
        errors = Inscripcion.validate(self.emprendedor, self.feria_test, 3, "confirmada", self.user_pedro)
        self.assertIn("El número de puesto no puede exceder la capacidad de la feria (2).", errors)

    def test_puesto_unico_por_feria_evita_duplicados(self):
        # El emprendedor base (Pedro) ocupa el puesto 1
        Inscripcion.objects.create(
            emprendedor=self.emprendedor,
            feria=self.feria_test,
            numero_puesto=1,
            estado="confirmada"
        )
        
class EmprendedorEInscripcionModelTest(TestCase):
    
    def setUp(self):
        """Prepara el entorno y los objetos comunes para todas las pruebas de este eje."""
        # Creamos los usuarios con la misma convención de nombres
        self.user_pedro = User.objects.create_user(username="Pedro", password="password123")
        self.user_jose = User.objects.create_user(username="Jose", password="password123")
        
        # Feria de prueba con capacidad limitada a 2 puestos
        self.feria_test = Feria.objects.create(
            nombre="Feria de Prueba",
            categoria="Manualidades",
            fecha_inicio=date(2026, 8, 1),
            fecha_fin=date(2026, 8, 5),
            ubicacion="Gimnasio Municipal",
            capacidad_puestos=2
        )

        # Emprendedor base ya registrado en el sistema
        self.emprendedor = Emprendedor.objects.create(
            nombre="Pedro",
            apellido="Gimenez",
            email="pedro@feria.com",
            rubro="Madera",
            usuario=self.user_pedro
        )

    # TESTS DE VALIDACIÓN DE EMPRENDEDOR 

    def test_validate_emprendedor_correcto_retorna_vacio(self):
        errors = Emprendedor.validate("Jose", "Gomez", "jose@feria.com", "Tejido", self.user_jose)
        self.assertEqual(errors, [])

    def test_validate_emprendedor_email_duplicado_retorna_error(self):
        errors = Emprendedor.validate("Jose", "Gomez", "pedro@feria.com", "Tejido", self.user_jose)
        self.assertIn("Ya existe un emprendedor registrado con este email.", errors)

    def test_new_crea_emprendedor_exitosamente(self):
        emp, errors = Emprendedor.new("Jose", "Gomez", "jose@feria.com", "Tejido", self.user_jose)
        self.assertEqual(errors, [])
        self.assertIsNotNone(emp)
        self.assertEqual(emp.nombre, "Jose")

    # TESTS DE VALIDACIÓN DE INSCRIPCIÓN 

    def test_validate_puesto_excede_capacidad_retorna_error(self):
        # Intentamos usar el puesto 3 en una feria de capacidad máxima 2
        errors = Inscripcion.validate(self.emprendedor, self.feria_test, 3, "confirmada", self.user_pedro)
        self.assertIn("El número de puesto no puede exceder la capacidad de la feria (2).", errors)

    def test_puesto_unico_por_feria_evita_duplicados(self):
        # El emprendedor base (Pedro) ocupa el puesto 1
        Inscripcion.objects.create(
            emprendedor=self.emprendedor,
            feria=self.feria_test,
            numero_puesto=1,
            estado="confirmada"
        )
        
        # Creamos un segundo emprendedor (Jose) para intentar disputar el mismo puesto
        otro_emp = Emprendedor.objects.create(
            nombre="Jose", 
            apellido="Gomez", 
            email="jose@feria.com", 
            rubro="Tejido", 
            usuario=self.user_jose
        )
        
        # Validamos si nuestro método frena la inscripción duplicada en el puesto 1
        errors = Inscripcion.validate(otro_emp, self.feria_test, 1, "confirmada", self.user_jose)
        self.assertIn("El puesto 1 ya está ocupado en esta feria.", errors)

        
    # def test_tiene_lugar_false_cuando_llena(self): ...
    # def test_puestos_ocupados_cuenta_solo_confirmadas(self): ...
