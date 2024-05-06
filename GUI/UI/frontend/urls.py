"""
This file maps all the urls used in this app to a function in view
additionally a name is assigned to each path to make routing a bit easier
"""
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
    path('studentdetails/', views.viewstudent, name='viewstudent'),
    path('stopeval/', views.stopeval, name='stopeval'),
    path('reeval/', views.reeval, name='reeval'),
    path('csv/', views.getcsv, name='getcsv'),
    path('zip/', views.getzip, name='getzip'),
    path(r'deleteassignment/<pk>/', views.AssignmentDeleteView.as_view() ,name='delassign'),
    path(r'deleteuser/<pk>/', views.UserDeleteView.as_view() ,name='deluser'),
    path(r'deletesub/<pk>/', views.SubDeleteView.as_view() ,name='delsub'),
]
