from django.urls import path
from . import views

urlpatterns = [
    # ទំព័រដើម
    path('', views.home, name='home'),
    
    # ការចូល និងចុះឈ្មោះ
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ការប្រឡង
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.create_exam, name='create_exam'),
    path('exams/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('attempts/<int:attempt_id>/result/', views.exam_result, name='exam_result'),
    
    # សំណួរ (សម្រាប់គ្រូ)
    path('questions/', views.question_list, name='question_list'),
    path('questions/add/', views.add_question, name='add_question'),
    
    # មើលលទ្ធផល
    path('results/my/', views.student_results, name='student_results'),
    path('results/students/', views.teacher_results, name='teacher_results'),
    
    # សម្រាប់ Import សំណួរ
    path('questions/import/', views.import_questions, name='import_questions'),
    path('questions/template/', views.download_template, name='download_template'),
    
    # ⬇️ បន្ថែមផ្លូវសម្រាប់គ្រប់គ្រងមុខវិជ្ជា (Subject Management) ⬇️
    path('subjects/', views.manage_subjects, name='manage_subjects'),
path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    # សម្រាប់ Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
]