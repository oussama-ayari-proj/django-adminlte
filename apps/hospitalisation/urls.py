from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='hospitalisation_index'),
    path('analyse-sejours/', views.analyse_sejours, name='analyse_sejours'),
    path('api/stats/', views.get_hospitalisation_stats, name='hospitalisation_stats'),
    path('api/sejours-analysis/', views.get_sejours_analysis, name='sejours_analysis'),
    path('api/date-ranges/', views.get_date_ranges, name='hospitalisation_date_ranges'),
    path('lits-fermes/', views.index_lits_fermes, name='index_lits_fermes'),
    path('api/stats/lits-fermes/', views.get_lits_fermes_stats, name='lits_fermes_stats'),
]
