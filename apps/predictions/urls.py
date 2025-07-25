from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/stats/', views.get_predictions_stats, name='predictions_stats'),
    path('api/predictions/', views.get_predictions, name='get_predictions'),
    path('api/filter-ufs-mae/', views.filter_ufs_with_mae_above_zero, name='filter_ufs_mae')]
