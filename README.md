# GesCoches - Sistema de Gestión de Vehículos de Sustitución

Sistema profesional para la gestión interna de vehículos de sustitución, desarrollado con Django y PostgreSQL.

## 🚗 Características

- **Gestión de Vehículos**: Control total del inventario de vehículos
- **Estados de Vehículos**: 
  - Disponible
  - En Uso
  - Mantenimiento/Reparación
  - Dado de Baja
- **Asignaciones**: Registro completo de asignaciones a clientes
- **Mantenimientos**: Seguimiento de revisiones y reparaciones
- **Dashboard**: Vista general con estadísticas en tiempo real
- **Panel de Administración**: Interface personalizada de Django Admin
- **Validación de Matrículas**: Formato español automático

## 📋 Requisitos Previos

- Python 3.9 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar el repositorio o descargar el código

```bash
cd c:\Users\pedro\Desktop\Pedro\Proyectos\GesCoches\GesCoches
```

### 2. Crear y activar entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL

Crear la base de datos en PostgreSQL:

```sql
CREATE DATABASE gescoches_db;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'Europe/Madrid';
GRANT ALL PRIVILEGES ON DATABASE gescoches_db TO postgres;
```

Si necesitas cambiar las credenciales, edita el archivo `gescoches/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gescoches_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Aplicar migraciones

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario

```powershell
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador.

### 7. Recopilar archivos estáticos

```powershell
python manage.py collectstatic --noinput
```

### 8. Iniciar el servidor

```powershell
python manage.py runserver
```

La aplicación estará disponible en: `http://127.0.0.1:8000/`

## 🎯 Uso

### Acceso al Sistema

- **Dashboard**: http://127.0.0.1:8000/
- **Panel de Administración**: http://127.0.0.1:8000/admin/

### Funcionalidades Principales

#### Dashboard
- Visualización de estadísticas de vehículos por estado
- Listado de asignaciones activas
- Mantenimientos pendientes

#### Gestión de Vehículos
- Alta/baja de vehículos
- Cambio de estados
- Registro de kilometraje
- Historial completo

#### Asignaciones
- Crear nuevas asignaciones
- Finalizar asignaciones activas
- Registro de kilometraje de entrada/salida
- Historial por vehículo

#### Mantenimientos
- Programar mantenimientos
- Tipos: Revisión, Reparación, ITV, Neumáticos, Otros
- Control de costes
- Registro de talleres

## 📊 Estructura del Proyecto

```
GesCoches/
├── gescoches/              # Configuración del proyecto
│   ├── settings.py         # Configuración principal
│   ├── urls.py             # URLs principales
│   └── wsgi.py            # Configuración WSGI
├── vehiculos/              # Aplicación principal
│   ├── models.py          # Modelos de datos
│   ├── admin.py           # Configuración del admin
│   ├── views.py           # Vistas
│   └── urls.py            # URLs de la app
├── templates/              # Plantillas HTML
│   ├── base.html          # Plantilla base
│   └── vehiculos/         # Plantillas de vehículos
├── static/                 # Archivos estáticos
│   └── css/               # Hojas de estilo
├── manage.py              # Script de gestión Django
└── requirements.txt       # Dependencias Python
```

## 🔐 Seguridad

**IMPORTANTE**: Antes de poner en producción:

1. Cambiar `SECRET_KEY` en `settings.py`
2. Establecer `DEBUG = False`
3. Configurar `ALLOWED_HOSTS` apropiadamente
4. Usar variables de entorno para credenciales
5. Configurar HTTPS
6. Activar protección CSRF

## 🚀 Despliegue en Producción

Para producción se recomienda:

- Usar gunicorn como servidor WSGI
- Configurar nginx como proxy inverso
- Usar PostgreSQL en servidor dedicado
- Configurar backups automáticos
- Implementar logging apropiado

## 📝 Notas para Desarrollo

- El formato de matrícula sigue el estándar español: 1234ABC
- La zona horaria está configurada para Europe/Madrid
- El idioma de la aplicación está en español
- Los archivos estáticos se sirven desde `/static/`

## 🐛 Resolución de Problemas

### Error de conexión a PostgreSQL
- Verificar que PostgreSQL está ejecutándose
- Comprobar credenciales en `settings.py`
- Verificar que la base de datos existe

### Error de migraciones
```powershell
python manage.py migrate --run-syncdb
```

### Problemas con archivos estáticos
```powershell
python manage.py collectstatic --clear --noinput
```

## 📞 Soporte

Para soporte interno, contacta al administrador del sistema.

## 📄 Licencia

Sistema de uso interno de la empresa.

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2026  
**Desarrollador**: Pedro
