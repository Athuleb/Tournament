from django.urls import path
from . import views

app_name = 'tournament'

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration_page, name='registration_page'),
    path('teams/', views.teams, name='teams'),
    path('college-logout/', views.college_logout, name='college_logout'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('edit-student/<int:student_id>/', views.edit_student_college, name='edit_student_college'),
    
    # Custom Admin Routes
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/export/', views.export_students_pdf, name='export_students_pdf'),
    path('admin-panel/student/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('admin-panel/student/delete/<int:student_id>/', views.delete_student, name='delete_student'),
]

