from django.urls import path
from . import views

app_name = 'hebergement_hors_uf'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/stats/', views.get_hebergement_stats, name='hebergement_stats'),
    #path('api/ems-with-hebergements/', views.get_ems_with_hebergements, name='ems_with_hebergements'),
    path('api/ems-by-year/', views.get_ems_by_year, name='ems_by_year'),
    path('api/get_lits_fermes_filtres/', views.get_lits_fermes_filtres, name='lits_fermes_filtres'),
]
