from django.urls import path
from . import views

app_name = 'fileupload'

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('success/<str:file_name>/', views.upload_success, name='upload_success'),
    path('success-multiple/<str:session_key>/', views.upload_success_multiple, name='upload_success_multiple'),
]
