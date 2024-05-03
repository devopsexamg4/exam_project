"""
In This file all the rendering of the pages is defined
TODO:
    - do some nice formatting and stuff for the html pages
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django_tables2 import RequestConfig
from django.views.generic.edit import DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy


from .tables import *
from .models import User
from .forms import AddStudForm, SignupForm, LoginForm, SubmissionForm, UserTypeForm, AssignmentForm

STRING_403 = "You do not have permissions to view this page"

"""
home and about are info pages, viewable by all
"""
def home(request):
    """Collect the data to show on the frontpage"""
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
    if (User.objects.filter(username = request.user).first() not in User.objects.filter(type = 'ADM')) and (not request.user.is_staff):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')
    
    if request.method == 'POST':
        usr = User.objects.get(pk = request.POST['pk'])
        form = UserTypeForm(request.POST, instance=usr)
        if form.is_valid():
            form.save()
            messages.info(request, f"{usr.username} has been updated")
        else:
            messages.error(request, form.errors)

    filt = UserFilter(request.GET, queryset = User.objects.all())
    table = UserTable(data=filt.qs)
    RequestConfig(request).configure(table)

    form = UserTypeForm()
    context = {
        'title':'Admin',
        'form':form,
        'table':table,
        'filter':filt
    }
    return render(request, 'admin.html', context)


@login_required(login_url='/login/')
def student(request):
    """collect data to show on the student page"""
    if User.objects.filter(username = request.user).first() not in User.objects.filter(type = 'STU'):
        # the logged in user is not a student but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, user = request.user)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.student = request.user
            sub.save()
            messages.info(request, f"submission received")
        else:
            messages.error(request, form.errors)
    form = SubmissionForm(user=request.user)

    filt = SubmissionFilter(request.GET, queryset = StudentSubmissions.objects.filter(student = request.user))
    table = SubmissionTable(data=filt.qs)
    RequestConfig(request).configure(table)

    context = {
        'title':'Student',
        'form':form,
        'filter':filt,
        'table':table
    }
    return render(request, 'student.html', context)

@login_required(login_url='/login/')
def teacher(request):
    """collect data to show on the teacher page"""
    if User.objects.filter(username = request.user).first() not in User.objects.filter(type = 'TEA'):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')
    usr = request.user
    filt = AssFilter(request.GET, queryset = usr.assignments.all())
    bobby = AssTable(data=filt.qs)
    RequestConfig(request).configure(bobby)

    context = {
        'title':'Teacher',
        'filter':filt,
        'table':bobby
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

@require_http_methods(["POST"])
@login_required(login_url='/login/')
def assignment(request):
    # get the assignment
    assign = Assignments.objects.get(pk=request.POST['pk'])
    # make sure the user is a teacher who is associated with the assignment
    if (User.objects.filter(username = request.user).first() not in
        User.objects.filter(type = 'TEA').filter(assignments__pk = assign.pk)):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')
    studs = assign.user_set.filter(type = 'STU')
    context = {
        'title':f"{assign.title}",
        'assignment':assign,
        'students':studs,
        'submissions':StudentSubmissions.objects.filter(student__in=studs).filter(assignment = assign)
    }
    return render(request, 'assignment.html', context)

@login_required(login_url='/login/')
def edit_assignment(request):
    assign = Assignments.objects.get(pk = request.POST['pk'])

    if (User.objects.filter(username = request.user).first() not in 
            User.objects.filter(type = 'TEA').filter(assignments__pk = assign.pk)):
            # the logged in user is not a teacher but is trying to access the page
            messages.error(request, STRING_403)
            return redirect('index')    
    
    studs_old = User.objects.filter(assignments__pk = assign.pk)
    print(studs_old)
    if 'save' in request.POST.keys():
        # we want to save our edit
        form = AssignmentForm(request.POST, request.FILES, instance = assign)
        studform = AddStudForm(request.POST)
        
        if form.is_valid():
            if studform.is_valid():
                assign = form.save()
                studs_new = User.objects.filter(pk__in = studform.cleaned_data['students'])
                remove = [ u for u in studs_old if u not in list(studs_new)+[request.user] ]
                add = [ u for u in studs_new if u not in studs_old ]

                for user in remove:
                    user.assignments.remove(assign)
                for user in add:
                    user.assignments.add(assign)
                messages.info(request, f"Assignment has been updated")
                return redirect('teacher')
            else:
                messages.error(request, form.errors)
        else:
            messages.error(request, form.errors)

    # we intent to edit an existing assignment
    # get the assignment
    form = AssignmentForm(instance = assign)
    studform = AddStudForm(initial = {'students':[u.id for u in studs_old]})
    context = {
        'title':f"edit {assign.title}",
        'form':form,
        'studform':studform,
        'pk':assign.pk
    }
    return render(request, 'edit_assignment.html', context)

@login_required(login_url='/login/')
def create_assignment(request):
    if (User.objects.filter(username = request.user).first() not in
        User.objects.filter(type = 'TEA')):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)
        users = AddStudForm(request.POST)
        if form.is_valid():
            if users.is_valid():
                # save the assignment
                assignment = form.save()
                # get the students and add them to the assignment
                users = users.cleaned_data['students']
                studs_new = User.objects.filter(pk__in = users)
                # very important
                request.user.assignments.add(assignment)
                for studs in studs_new:
                    studs.assignments.add(assignment)
                messages.info(request, f"Assignment has been created")
                return redirect('teacher')
            else:
                messages.error(request, form.errors)
        else:
            messages.error(request, form.errors)

    form = AssignmentForm()
    studform = AddStudForm()
    context = {
        'title':'Teacher',
        'form':form,
        'studform':studform,
    }
    return render(request, 'edit_assignment.html', context)

@login_required(login_url='/login/')
def submission(request):
    sub = StudentSubmissions.objects.get(pk = request.POST['pk'])
    if (User.objects.filter(username = request.user).first()
        not in User.objects.filter(type = 'STU').filter(studentsubmissions = sub)):
        # the logged in user is not a student but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')
    
    context = {
        'title':f'Details {sub}',
        'submission':sub
    }
    return render(request, 'submission.html', context)

# @login_required(login_url='/login/')
class AssignmentDeleteView(DeleteView, SingleObjectMixin):
    model = Assignments
    success_url = reverse_lazy('teacher')
    
class UserDeleteView(DeleteView, SingleObjectMixin):
    model = User
    success_url = reverse_lazy('admin')

class SubDeleteView(DeleteView, SingleObjectMixin):
    model = StudentSubmissions
    success_url = reverse_lazy('student')
