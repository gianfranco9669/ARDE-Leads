# ARDE Leads

Sistema Django para prospección comercial local.

ARDE Leads permite buscar negocios desde Google Places, normalizar teléfonos, detectar duplicados, calcular oportunidades, gestionar prospectos en un pipeline comercial y preparar contacto manual por WhatsApp.

## Stack

- Python
- Django 5
- SQLite local / PostgreSQL opcional
- HTMX
- Alpine.js
- Tailwind vía CDN
- Google Places API

## Setup local

1. Crear entorno virtual:

    python -m venv .venv

2. Activar entorno:

    .venv\Scripts\Activate.ps1

3. Instalar dependencias:

    pip install -r requirements.txt

4. Crear archivo de entorno:

    Copy-Item .env.example .env

5. Migrar base:

    python manage.py migrate

6. Cargar demo:

    python manage.py cargar_demo_prospectos

7. Levantar servidor:

    python manage.py runserver

Abrir:

    http://127.0.0.1:8000/

## Tests

    python manage.py check
    python manage.py test -v 2
    python manage.py test prospeccion -v 2

## Variables de entorno

Crear `.env` tomando como base `.env.example`.

Variables principales:

    DJANGO_SECRET_KEY=
    DJANGO_DEBUG=
    DJANGO_ALLOWED_HOSTS=
    DJANGO_CSRF_TRUSTED_ORIGINS=
    DATABASE_URL=
    GOOGLE_PLACES_API_KEY=
    GOOGLE_PLACES_FIELD_MASK=

## Comandos útiles

    python manage.py cargar_demo_prospectos
    python manage.py scan_places --help
    python manage.py rescore_leads
    python manage.py dedupe_leads
    python manage.py export_leads

## Flujo comercial

- Centro de control
- Nueva búsqueda
- Historial de búsquedas
- Explorador de prospectos
- Pipeline comercial
- Campañas
- Plantillas de mensajes manuales

ARDE Leads no envía WhatsApp automáticamente. El contacto es manual y responsable.