#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Convertir archivos estáticos (CSS/Imágenes del sistema)
python manage.py collectstatic --no-input

# Crear las tablas en la base de datos de la nube
python manage.py migrate

# El "|| true" es un truco para que si el usuario ya existe, no falle la instalación.
python manage.py createsuperuser --noinput || true