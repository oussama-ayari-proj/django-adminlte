from django.urls import path

from apps.correlation import views
urlpatterns = [
    path('', views.index, name='index'),
    path('get_ufs/', views.get_ufs, name='get_ufs'),
    path('get_data/', views.get_data, name='get_data'),
    path('get_metiers/', views.get_metiers, name='get_metiers'),
    path('get_data_metiers/', views.get_data_metiers, name='get_data_metiers'),
]