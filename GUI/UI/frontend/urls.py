from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('teacher/', views.teacher, name='teacher'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('admin/', views.admin, name='admin'),
    path('student/', views.student, name='student'),
]
