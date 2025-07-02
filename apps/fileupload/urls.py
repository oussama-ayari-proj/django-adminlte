from django.urls import path
from . import views

app_name = 'fileupload'

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('success-multiple/<str:session_key>/', views.upload_success_multiple, name='upload_success_multiple'),
]
