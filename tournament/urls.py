from django.urls import path
from . import views

app_name = 'tournament'

urlpatterns = [
    path('', views.index, name='index'),
    path('download-pdf/<int:college_id>/', views.download_pdf, name='download_pdf'),
    
    # Custom Admin Routes
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/export/', views.export_students_pdf, name='export_students_pdf'),
]
