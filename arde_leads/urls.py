from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('leads/', include('prospeccion.urls')),
    path('', lambda request: redirect('/leads/', permanent=False), name='inicio'),
]
