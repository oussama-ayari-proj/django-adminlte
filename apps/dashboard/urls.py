from django.urls import path

from apps.dashboard import views
urlpatterns = [
    path('', views.index, name='index'),
    path('get_etb/', views.get_etb, name='get_etb'),
    path('get_pole/', views.get_pole, name='get_pole'),
    path('get_lits_fermes/', views.get_lits, name='get_lits'),
    path('get_metiers/', views.get_metiers, name='get_metiers'),
    path('get_metier_count/', views.get_metier_count, name='get_metier_count'),
]