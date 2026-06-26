import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-only-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','leadfinder']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'arde_leads.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'arde_leads.wsgi.application'
if os.getenv('DATABASE_URL'):
    import urllib.parse as up
    u=up.urlparse(os.environ['DATABASE_URL'])
    DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':u.path[1:],'USER':u.username,'PASSWORD':u.password,'HOST':u.hostname,'PORT':u.port or 5432}}
else:
    DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
LANGUAGE_CODE='es-ar'; TIME_ZONE='UTC'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'; STATICFILES_DIRS=[BASE_DIR/'static'] if (BASE_DIR/'static').exists() else []
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
GOOGLE_PLACES_API_KEY=os.getenv('GOOGLE_PLACES_API_KEY','')
GOOGLE_PLACES_DEFAULT_FIELD_MASK=os.getenv('GOOGLE_PLACES_FIELD_MASK','places.id,places.displayName,places.formattedAddress,places.shortFormattedAddress,places.location,places.nationalPhoneNumber,places.internationalPhoneNumber,places.websiteUri,places.googleMapsUri,places.rating,places.userRatingCount,places.primaryType,places.types,places.businessStatus')
