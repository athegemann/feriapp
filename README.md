# FeriApp 🏪

Sistema web de gestión de ferias y emprendedores desarrollado con Django 5.1+.  
Permite administrar ferias temáticas, gestionar inscripciones de emprendedores y controlar la disponibilidad de puestos, con autenticación de usuarios y panel de administración.

---

## IMPORTANTE

Antes de correr la pagina, recomedamos:

Luego de realizar las migraciones, ejecutar:
`python manage.py loaddata .\app\fixtures\base.json`
para cargar un set de datos base para comprobar el funcionamiento general de la pagina.

Ejecutar:
`python manage.py createsuperuser` con usuario `admin` mail `admin@gmail.com` y contrasena `admin1234` como pide la consigna del TP

## 🛠️ Stack

| Tecnología | Versión |
|------------|---------|
| Python | 3.13+ |
| Django | 5.1+ |
| Base de datos | SQLite (desarrollo) |
| Frontend | Bootstrap 5 |
| Tests | `django.test.TestCase` |
| Control de versiones | Git + GitHub |

---

## ✨ Funcionalidades

- 🔐 Registro, login y logout de usuarios
- 🗂️ Gestión de categorías y ferias
- 🧑‍💼 Gestión de emprendedores
- 📋 Inscripción a ferias con control de disponibilidad de puestos
- 📊 Panel de inicio con estadísticas generales
- 📈 Barra de ocupación por feria (Bootstrap progress bar)
- 🛠️ Panel de administración Django configurado
- 📱 Interfaz responsiva con Bootstrap 5

---

## 👥 Integrantes

| Nombre | Usuario GitHub |
|--------|---------------|
| Hegemann, Albaro | [@athegemann](https://github.com/athegemann) |
| Vargas, Eliam | [@TheLocios](https://github.com/thelocios) |
| Vasquez, Juan Pablo | [@sincejas](https://github.com/sincejas) |

---

## 🚀 Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/feriapp.git
cd feriapp
```

### 2. Crear y activar el entorno virtual

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario (para el panel admin)

```bash
python manage.py createsuperuser
```

### 6. Correr el servidor de desarrollo

```bash
python manage.py runserver
```

Accedé a [http://localhost:8000](http://localhost:8000)  
Panel admin: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 🧪 Correr los tests

```bash
# Todos los tests con detalle
python manage.py test -v 2

# Solo tests de modelos
python manage.py test ferias.tests.test_models -v 2

# Solo tests de vistas
python manage.py test ferias.tests.test_views -v 2
```

---

## 🔑 Credenciales de prueba

> ⚠️ Solo para uso del corrector en entorno de desarrollo local.

| Rol | Usuario | Contraseña |
|-----|---------|-----------|
| Superusuario / Admin | `admin` | `admin1234` |
| Usuario de prueba | `usuario_prueba` | `prueba1234` |

---

## 📁 Estructura del proyecto

```
feriapp/
├── feriapp/            # Configuración del proyecto Django
│   ├── settings.py
│   └── urls.py
├── ferias/             # App principal
│   ├── models.py       # Categoria, Feria, Emprendedor, Inscripcion
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── consultas.py    # Consultas ORM
│   └── tests/
│       ├── test_models.py
│       └── test_views.py
├── templates/
│   ├── base.html
│   └── registration/
├── static/
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## 🖼️ Capturas

### Inicio
![Pantalla de inicio](docs/screenshots/inicio.png)

### Detalle de feria
![Detalle de feria](docs/screenshots/feria_detalle.png)

### Panel de administración
![Admin](docs/screenshots/admin.png)

### Login
![Login](docs/screenshots/login.png)

---

## 🧩 Decisiones de diseño

> *(Mínimo 200 palabras — completar antes de la entrega final)*

Para este proyecto, se nos entrego el dominio de ferias y nos gusto la idea por lo que no lo intercambiamos con ningun compañero. Nos gusto mas que nada la idea de la organización de espacios para los feriantes.

Respecto a la disponibilidad de puestos, elijimos modelarla a traves de métodos dinamicos directamente en la clase Feria (como puestos_ocupados y puestos_disponibles) en lugar de usar estaticos en la base de datos o depender de complejas anotaciones ORM en cada vista. Esto garantiza que se calcule siempre en tiempo real consultando la cantidad exacta de inscripciones con estado "confirmada", evitando inconsistencias si un emprendedor cancela su participación.

En cuanto a las validaciones: Implementamos metodos de clase como validate() y new() en los modelos para asegurar la integridad de las reglas de negocio en la capa más baja (por ejemplo, asegurando que la fecha de fin no sea anterior a la de inicio).

El trabajo lo dividimos en ejes modulares utilizando Git y GitHub. 
Eliam se enfocó en el desarrollo del eje Core (diseñando los modelos de Ferias y Sectores, junto con sus correspondientes Vistas Basadas en Clases). 
Pablo se encargó del eje de Inscripciones y Usuarios (gestionando la lógica para registrar, confirmar y cancelar la participación de los feriantes) 
Albaro abordó el eje de Perfiles, reseñas y Visitantes, a su vez arreglando errores y sincronizando los codigos de los 3

Una decisión de diseño no obvia fue la implementación de un "soft-delete" para las inscripciones. En lugar de eliminar el registro de la base de datos (.delete()) cuando un emprendedor cancela su asistencia, el sistema simplemente actualiza el atributo estado a 'cancelada'. Esto permite mantener un historial, no rompe la trazabilidad del puesto y facilita las estadísticas.

---

## ⭐ Funcionalidades opcionales implementadas

- [ ] Vista "Mis inscripciones" para el emprendedor autenticado
- [ ] Mensajes flash con `django.contrib.messages`
- [ ] Paginación en lista de ferias
- [ ] Barra de búsqueda por nombre o ubicación
- [ ] Permisos diferenciados (Organizador vs. Emprendedor)
- [ ] Tests de integración (flujo completo)

---

## 🐛 Problemas comunes

| Problema | Solución |
|----------|----------|
| `OperationalError: no such table` | Corré `python manage.py migrate` |
| `No module named django` | Activá el entorno virtual |
| Barra de progreso muestra 0% | Verificá que `puestos_ocupados()` cuenta solo inscripciones `confirmadas` |
| Login no redirige bien | Verificá `LOGIN_REDIRECT_URL` en `settings.py` |
