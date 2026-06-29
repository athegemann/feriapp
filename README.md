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

Describir aquí:
- Por qué eligieron este dominio
- Cómo modelaron la disponibilidad de puestos (método vs. anotación ORM)
- Qué validaciones pusieron en el modelo vs. en el formulario
- Cómo dividieron el trabajo entre los integrantes
- Cualquier decisión no obvia (ej: por qué el constraint de puesto único, cómo manejaron lista de espera, etc.)

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
