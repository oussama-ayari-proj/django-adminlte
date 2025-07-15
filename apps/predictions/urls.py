from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/stats/', views.get_predictions_stats, name='predictions_stats'),
    path('api/predictions/', views.get_predictions, name='get_predictions'),
]
