from django.urls import path
from . import views

urlpatterns = [
    path('', views.statistiques_globales, name='statistiques_globales'),
    path('api/global/', views.api_global_stats, name='api_global_stats'),
    path('api/em/', views.api_em_stats, name='api_em_stats'),
    path('api/charge-em/', views.get_charge_em, name='get_charge_em'),
    path('api/ems-by-year/', views.api_ems_by_year, name='api_ems_by_year'),
]
