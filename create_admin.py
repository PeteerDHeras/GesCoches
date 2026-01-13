#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gescoches.settings')

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth.models import User

# Datos del admin
USERNAME = 'admin'
EMAIL = 'admin@gescoches.com'
PASSWORD = 'baleares9'

# Crear superuser si no existe
if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f'✅ Superuser "{USERNAME}" creado exitosamente')
    print(f'   Usuario: {USERNAME}')
    print(f'   Contraseña: {PASSWORD}')
else:
    print(f'⚠️ El usuario "{USERNAME}" ya existe')
