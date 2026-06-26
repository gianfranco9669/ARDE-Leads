from django.contrib import admin
from .models import BusquedaProspectos, Prospecto, RegistroContacto, PlantillaMensaje, Campania, ProspectoCampania
for modelo in [BusquedaProspectos, Prospecto, RegistroContacto, PlantillaMensaje, Campania, ProspectoCampania]:
    admin.site.register(modelo)
