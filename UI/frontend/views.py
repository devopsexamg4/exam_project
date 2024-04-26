"""
In This file all the rendering of the pages is defined
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import SignupForm, LoginForm

STRING_403 = "You do not have permissions to view this page"

"""
home and about are info pages, viewable by all
"""
def home(request):
    """Collect the data to show on the frontpage"""
    print([u.type for u in User.objects.filter(type=request.user.type)])
    context = {
        'title':'Home',
    }
    return render(request,'home.html',context)

def about(request):
    """collect data to show on the about page"""
    context = {
        'title':'About',
    }
    return render(request, 'about.html', context)

"""
admin, student and teacher presents the views of those types of users
"""
@login_required(login_url='/login/')
def admin(request):
    """collect data to show on the admin page"""
    if request.user not in [User.objects.filter(type = 'ADM' )]:
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    context = {
        'title':'Admin',
    }
    return render(request, 'admin.html', context)


@login_required(login_url='/login/')
def student(request):
    """collect data to show on the student page"""
    if request.user not in [User.objects.filter(type = 'STU')]:
        # the logged in user is not a student but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    context = {
        'title':'Student',
    }
    return render(request, 'student.html', context)

@login_required(login_url='/login/')
def teacher(request):
    """collect data to show on the teacher page"""
    if request.user not in [User.objects.filter(type = 'TEA')]:
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    context = {
        'title':'Teacher',
    }
    return render(request, 'teacher.html', context)

"""
user_login, signup and user_logout are used as their names suggest to login, create a user and logout
"""
def user_login(request):
    """the login page"""
    context = {
        'title':'Login',
    }
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f"Welcome {username}")
                return redirect('index')
    else:
        form = LoginForm()

    context['form'] = form
    return render(request, 'login.html', context )

def signup(request):
    """ to create a new user """
    context = {
        'title':'Signup',
    }
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, f"user {form.cleaned_data['username']} has been created\nPlease login")
            return redirect('login')
    else:
        form = SignupForm()

    context['form'] = form

    return render(request, 'signup.html', context)

def user_logout(request):
    """ 
    logout page
    """
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('index')
