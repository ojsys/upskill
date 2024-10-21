from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
]