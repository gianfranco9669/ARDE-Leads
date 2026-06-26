from django.urls import path
from . import views
app_name='prospeccion'
urlpatterns=[
    path('',views.dashboard,name='dashboard'),
    path('searches/',views.busquedas,name='busquedas'),
    path('searches/new/',views.nueva_busqueda,name='nueva_busqueda'),
    path('searches/<int:pk>/cancel/',views.cancelar_busqueda,name='cancelar_busqueda'),
    path('explorer/',views.explorador,name='explorador'),
    path('prospecto/<int:pk>/drawer/',views.drawer_prospecto,name='drawer_prospecto'),
    path('prospecto/<int:pk>/estado/<slug:estado>/',views.cambiar_estado,name='cambiar_estado'),
    path('prospecto/<int:pk>/whatsapp/',views.accion_whatsapp,name='accion_whatsapp'),
    path('pipeline/',views.pipeline,name='pipeline'),
    path('campaigns/',views.campanias,name='campanias'),
    path('templates/',views.plantillas,name='plantillas'),
]
