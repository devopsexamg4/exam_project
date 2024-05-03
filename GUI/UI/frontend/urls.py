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
    path('editassignment/', views.edit_assignment, name='edit_assignment'),
    path('newassignment/', views.create_assignment, name='new_assignment'),
    path('assignment/', views.assignment, name='assignment_detail'),
    path('submission/', views.submission, name='sub_details'),
    path(r'deleteassignment/<pk>/', views.AssignmentDeleteView.as_view() ,name='delassign'),
    path(r'deleteuser/<pk>/', views.UserDeleteView.as_view() ,name='deluser'),
    path(r'deletesub/<pk>/', views.SubDeleteView.as_view() ,name='delsub'),
]
