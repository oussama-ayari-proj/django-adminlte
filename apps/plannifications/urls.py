from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sans_contraintes/', views.index_sans_contraintes, name='index_sans_contraintes')
]
