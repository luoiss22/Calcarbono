# CalCarb - Calculadora de Huella de Carbono

Aplicación web para calcular, monitorear y reducir la huella de carbono personal, con énfasis en el reciclaje y su impacto económico y ambiental.

## Características Principales

- Cálculo detallado de la huella de carbono personal por categorías (consumo, transporte, energía, residuos)
- Seguimiento del reciclaje y su valor económico
- Visualización de estadísticas y tendencias
- Recomendaciones personalizadas para reducir el impacto ambiental
- Sistema de usuarios con perfiles personalizados

## Requisitos Técnicos

- Python 3.10+
- Django 5.1+
- Node.js 18+ (para el frontend con Next.js)

## Configuración del Entorno de Desarrollo Backend

### 1. Clonar el Repositorio

```bash
git clone <repo-url>
cd CalCarb
```

### 2. Crear y Activar Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos

El proyecto utiliza SQLite como base de datos por defecto, lo que simplifica la configuración inicial.

No se requiere ninguna configuración adicional para la base de datos, ya que SQLite crea un archivo local automáticamente cuando se ejecutan las migraciones.

### 5. Aplicar Migraciones

```bash
cd CalculadoraCarbono
python manage.py makemigrations
python manage.py migrate
```

### 6. Cargar Datos Iniciales

```bash
python manage.py loaddata miapp/fixtures/initial_data.json
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el Servidor Django

```bash
python manage.py runserver
```

La API estará disponible en http://localhost:8000/api/

La documentación de la API se puede acceder en:
- http://localhost:8000/swagger/ (interfaz Swagger)
- http://localhost:8000/redoc/ (interfaz ReDoc)

## Configuración del Frontend (Next.js)

La configuración del frontend se encuentra en desarrollo y se agregará en futuras actualizaciones.

## Estructura del Proyecto

```
CalCarb/
├── CalculadoraCarbono/    # Proyecto Django
│   ├── miapp/             # Aplicación principal
│   │   ├── fixtures/      # Datos iniciales
│   │   ├── migrations/    # Migraciones de la BD
│   │   ├── models.py      # Modelos de datos
│   │   ├── serializers.py # Serializadores para API
│   │   ├── views.py       # Vistas y endpoints
│   │   ├── urls.py        # Rutas de la API
│   │   └── admin.py       # Configuración de admin
│   └── CalculadoraCarbono/ # Configuración del proyecto
├── frontend/              # (Pendiente) Frontend con Next.js
└── requirements.txt       # Dependencias del proyecto
```

## Arquitectura del Sistema

La aplicación está construida con una arquitectura cliente-servidor:

- **Backend:** API REST con Django y Django REST Framework
- **Base de Datos:** PostgreSQL
- **Frontend:** (Pendiente) SPA con Next.js y Tailwind CSS

## API Endpoints

### Autenticación
- `POST /api/token/` - Obtener token de acceso
- `POST /api/token/refresh/` - Refrescar token

### Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/usuarios/` - Crear usuario
- `GET /api/usuarios/me/` - Ver perfil propio
- `GET /api/usuarios/dashboard/` - Dashboard del usuario

### Huella de Carbono
- `GET /api/huella-carbono/` - Listar registros de huella
- `POST /api/huella-carbono/` - Crear registro de huella
- `GET /api/huella-carbono/{id}/` - Ver detalle de registro
- `GET /api/huella-carbono/historico/` - Datos históricos

### Reciclaje
- `GET /api/reciclaje/` - Listar registros de reciclaje
- `POST /api/reciclaje/` - Crear registro de reciclaje
- `GET /api/reciclaje/estadisticas/` - Estadísticas de reciclaje

### Materiales
- `GET /api/materiales/` - Listar materiales reciclables
- `GET /api/materiales/por_tipo/` - Materiales organizados por tipo

### Recomendaciones
- `GET /api/recomendaciones/` - Listar recomendaciones
- `GET /api/recomendaciones/personalizadas/` - Recomendaciones personalizadas

## Licencia

Este proyecto se encuentra bajo la licencia MIT.

## Contacto

Para más información o soporte, contactar a ejemplo@ejemplo.com
