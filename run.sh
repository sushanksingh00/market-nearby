#!/bin/bash
set -a
source .env
set +a
source .venv/bin/activate
python manage.py runserver
