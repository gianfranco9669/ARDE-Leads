from django.urls import path
from . import views
app_name='leadfinder'
urlpatterns=[path('',views.dashboard,name='dashboard'),path('searches/',views.searches,name='searches'),path('searches/new/',views.search_new,name='search_new'),path('searches/<int:pk>/cancel/',views.search_cancel,name='search_cancel'),path('explorer/',views.explorer,name='explorer'),path('lead/<int:pk>/drawer/',views.lead_drawer,name='lead_drawer'),path('lead/<int:pk>/status/<slug:status>/',views.lead_status,name='lead_status'),path('lead/<int:pk>/whatsapp/',views.whatsapp_action,name='whatsapp_action'),path('pipeline/',views.pipeline,name='pipeline'),path('campaigns/',views.campaigns,name='campaigns'),path('templates/',views.templates,name='templates')]
