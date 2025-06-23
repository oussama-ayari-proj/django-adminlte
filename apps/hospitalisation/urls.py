from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='hospitalisation_index'),
    path('api/stats/', views.get_hospitalisation_stats, name='hospitalisation_stats'),
    path('api/date-ranges/', views.get_date_ranges, name='hospitalisation_date_ranges'),
]
