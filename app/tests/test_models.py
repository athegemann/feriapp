"""Tests de comportamiento para los modelos de dominio."""

from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Categoria, Feria, Emprendedor, Inscripcion, Visitante

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
            categoria=self.categoria,  # Uso el objeto
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


# --- TESTS DE EMPRENDEDOR E INSCRIPCIÓN ---

class EmprendedorEInscripcionModelTest(TestCase):
    
    def setUp(self):
        """Prepara el entorno y los objetos comunes para todas las pruebas de este eje."""
        # Creamos los usuarios con la misma convención de nombres
        self.user_pedro = User.objects.create_user(username="Pedro", password="password123")
        self.user_jose = User.objects.create_user(username="Jose", password="password123")
        
        # Corrección de integración: Pablito pasaba un string, ahora creamos la categoría
        self.categoria_test = Categoria.objects.create(nombre="Manualidades")

        # Feria de prueba con capacidad limitada a 2 puestos
        self.feria_test = Feria.objects.create(
            nombre="Feria de Prueba",
            categoria=self.categoria_test,
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
        
        # Creamos un segundo emprendedor (Jose) para intentar disputar el mismo puesto
        otro_emp = Emprendedor.objects.create(
            nombre="Jose", 
            apellido="Gomez", 
            email="jose@feria.com", 
            rubro="Tejido", 
            usuario=self.user_jose
        )
        
        # Validamos si nuestro metodo frena la inscripción duplicada en el puesto 1
        errors = Inscripcion.validate(otro_emp, self.feria_test, 1, "confirmada", self.user_jose)
        self.assertIn("El puesto 1 ya está ocupado en esta feria.", errors)

# --- Tests de visitante: ---

class VisitanteModelTest(TestCase):
    
    def setUp(self):
        # Usuarios base para los tests
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        
        # Visitante valido
        self.visitante_data = {
            "nombre": "Juan",
            "apellido": "Perez",
            "email": "juan.perez@example.com",
            "usuario": self.user1
        }

    # Metodo __str__()
    def test_str_valid(self):
        visitante, errors = Visitante.new(**self.visitante_data)
        self.assertEqual(str(visitante), "Juan Perez")
    
    # Metodo validate()
    def test_validate_success(self):
        errors = Visitante.validate(**self.visitante_data)
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_fields(self):
        errors = Visitante.validate(nombre="", apellido=" ", email="", usuario=None)
        
        self.assertIn("El nombre es obligatorio.", errors)
        self.assertIn("El apellido es obligatorio.", errors)
        self.assertIn("El email es obligatorio.", errors)
        self.assertIn("El usuario asociado es obligatorio.", errors)
        self.assertEqual(len(errors), 4)

    def test_validate_duplicate_email_and_user(self):
        # Creamos el primer visitante
        Visitante.new(**self.visitante_data)
        
        # Valida los mismos datos de nuevo (sin pasar instance_id)
        errors = Visitante.validate(**self.visitante_data)
        
        self.assertIn("Ya existe un visitante registrado con este email.", errors)
        self.assertIn("Este usuario ya esta vinculado a otro visitante.", errors)
        self.assertEqual(len(errors), 2)

    def test_new_success(self):
        visitante, errors = Visitante.new(
            nombre="  Maria", 
            apellido="  Gomez", 
            email="  maria.gomez@example.com", 
            usuario=self.user1
        )
        
        self.assertEqual(len(errors), 0)
        self.assertIsNotNone(visitante)

        # Comprobamos los strip()
        self.assertEqual(visitante.nombre, "Maria")
        self.assertEqual(visitante.apellido, "Gomez")
        self.assertEqual(visitante.email, "maria.gomez@example.com")
        self.assertEqual(Visitante.objects.count(), 1)
    
    # Metodo update()
    def test_update_success(self):
        visitante, _ = Visitante.new(**self.visitante_data)
        
        errors = visitante.update(
            nombre="Juan Carlos",
            apellido="Perez",
            email="juan.carlos@example.com",
            usuario=self.user1
        )
        
        self.assertEqual(len(errors), 0)
        visitante.refresh_from_db()
        self.assertEqual(visitante.nombre, "Juan Carlos")
        self.assertEqual(visitante.email, "juan.carlos@example.com")

    def test_update_same_email_and_user(self):
        visitante, _ = Visitante.new(**self.visitante_data)
        
        # Actualizamos manteniendo el mismo email y usuario
        errors = visitante.update(
            nombre="Juan Modificado",
            apellido="Perez",
            email=self.visitante_data["email"],
            usuario=self.visitante_data["usuario"]
        )
        
        self.assertEqual(len(errors), 0)
        visitante.refresh_from_db()
        self.assertEqual(visitante.nombre, "Juan Modificado")
    
    def test_update_duplicate_email_failure(self):
        # Creamos dos visitantes distintos
        visitante1, _ = Visitante.new(**self.visitante_data)
        visitante2, _ = Visitante.new(
            nombre="Ana", 
            apellido="Sanchez", 
            email="ana@example.com", 
            usuario=self.user2
        )
        
        # Intentamos actualizar el visitante2 con el email del visitante1
        errors = visitante2.update(
            nombre="Ana",
            apellido="Sanchez",
            email=self.visitante_data["email"],  # Colision de email
            usuario=self.user2
        )
        
        self.assertIn("Ya existe un visitante registrado con este email.", errors)
        
        # Verificamos que no se haya guardado el cambio
        visitante2.refresh_from_db()
        self.assertEqual(visitante2.email, "ana@example.com")