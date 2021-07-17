from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('student/', views.student_dashboard, name='studentdashboard'),
    path('lecturer/', views.lecturer_dashboard, name='lecturerdashboard'),
    path('hod/', views.hod_dashboard, name='hoddashboard'),
    path('senate/', views.senate_dashboard, name='senatedashboard'),
    path('csis/', views.csis_dashboard, name='csisdashboard'),
    path('json/', views.json, name='json'),
    path('hod_json/', views.hod_json, name='hod_json'),
    path('json_lecturer/', views.json_lecturer, name='json_lecturer'),
    path('lecturer_single/', views.lecturer_single, name='lecturer_single'),
    path('lecturer_message/', views.lecturer_message, name='lecturer_message'),
    path('forward_HOD/', views.forward_HOD, name='forward_HOD'),
    path('forward_SENATE/', views.forward_SENATE, name='forward_SENATE'),
    path('senate_json/', views.senate_json, name='senate_json'),
    path('forward_CSIS/', views.forward_CSIS, name='forward_CSIS'),
    path('csis_json/', views.csis_json, name='csis_json'),
    path('markasC/', views.markasC, name='markasC'),
    path('logout/', views.logout, name='logout'),
]
