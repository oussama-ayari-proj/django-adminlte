from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='hospitalisation_index'),
    path('analyse-sejours/', views.analyse_sejours, name='analyse_sejours'),
    path('api/stats/', views.get_hospitalisation_stats, name='hospitalisation_stats'),
    path('api/sejours-analysis/', views.get_sejours_analysis, name='sejours_analysis'),
    path('api/date-ranges/', views.get_date_ranges, name='hospitalisation_date_ranges'),
]
