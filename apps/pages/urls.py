from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax_uf_pagination/', views.ajax_ufs_pagination, name='ajax_uf_pagination'),
    path('ajax_sejours_pagination/', views.ajax_sejours_pagination, name='ajax_sejours_pagination'),
    path('ajax_em_pagination/', views.ajax_em_pagination, name='ajax_em_pagination'),
    path('ajax_pole_pagination/', views.ajax_poles_pagination, name='ajax_poles_pagination'),
    path('ajax_etb_pagination/', views.ajax_etbs_pagination, name='ajax_etb_pagination'),

    path('ajax_uf_unique_values/', views.ajax_uf_unique_values, name='ajax_uf_unique_values'),
    path('ajax_sejour_unique_values/', views.ajax_sejour_unique_values, name='ajax_sejour_unique_values'),
    path('ajax_em_unique_values/', views.ajax_em_unique_values, name='ajax_em_unique_values'),
    path('ajax_pole_unique_values/', views.ajax_pole_unique_values, name='ajax_pole_unique_values'),
    path('ajax_etb_unique_values/', views.ajax_etb_unique_values, name='ajax_etb_unique_values'),

    path('ajax_em_filter/', views.ajax_em_filter, name='ajax_em_filter'),
    path('ajax_uf_filter/', views.ajax_uf_filter, name='ajax_uf_filter'),
    path('ajax_sejour_filter/', views.ajax_sejour_filter, name='ajax_sejour_filter'),
    path('ajax_pole_filter/', views.ajax_pole_filter, name='ajax_pole_filter'),
    path('ajax_etb_filter/', views.ajax_etb_filter, name='ajax_etb_filter'),
]
