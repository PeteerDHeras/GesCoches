#!/usr/bin/env python
import os
import django
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gescoches.settings')
django.setup()

# Datos del admin
USERNAME = 'admin'
EMAIL = 'admin@gescoches.com'
PASSWORD = 'Admin123456'

# Crear superuser si no existe
if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f'✅ Superuser "{USERNAME}" creado exitosamente')
    print(f'   Usuario: {USERNAME}')
    print(f'   Contraseña: {PASSWORD}')
else:
    print(f'⚠️ El usuario "{USERNAME}" ya existe')
