#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Recolectar archivos estáticos
python manage.py collectstatic --no-input

# 3. Migrar la base de datos
python manage.py migrate