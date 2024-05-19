"""
In This file all the rendering of the pages is defined

home and about are info pages, viewable by all
admin, student and teacher presents the views of those types of users
user_login, signup and user_logout are used as their names suggest
    to login, create a user and logout
"""
import csv
import zipfile
import io
import pathlib

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.utils.datastructures import MultiValueDictKeyError
from django.urls import reverse_lazy
from django_tables2 import RequestConfig
from django.conf import settings


from .img import podmanager as pm
from . import tables as t
from . import forms as f
from .models import User, Assignments, StudentSubmissions, stopsub


STRING_403 = "You do not have permissions to view this page"

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

@login_required(login_url='/login/')
def admin(request):
    """collect data to show on the admin page"""
    if (User.objects.filter(username = request.user).first()
        not in User.objects.filter(type = 'ADM')) and (not request.user.is_staff):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    if request.method == 'POST':
        # a user has had its type updated
        usr = User.objects.get(pk = request.POST['pk'])
        form = f.UserTypeForm(request.POST, instance=usr)
        if form.is_valid():
            form.save()
            # if the update was setting a teacher as inactive stop or cancel all submissions
            if usr.type == User.TypeChoices.TEACHER and not usr.is_active:
                stopsub(usr)
            messages.info(request, f"{usr.username} has been updated")
        else:
            messages.error(request, form.errors)

    # populate the user table
    filt = t.UserFilter(request.GET, queryset = User.objects.all())
    table = t.UserTable(data = filt.qs)
    table.exclude = 'teacher'
    RequestConfig(request).configure(table)

    form = f.UserTypeForm()

    context = {
        'title':'Admin',
        'table':table,
        'form':form,
        'filter':filt
    }
    return render(request, 'admin.html', context)


@login_required(login_url='/login/')
def student(request):
    """collect data to show on the student page"""
    if (User.objects.filter(username = request.user).first()
        not in User.objects.filter(type = 'STU')):
        # the logged in user is not a student but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    if request.method == "POST":
        form = f.SubmissionForm(request.POST, request.FILES, user = request.user)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.student = request.user
            sub.save()
            messages.info(request, "submission received")
        else:
            messages.error(request, form.errors)
    form = f.SubmissionForm(user=request.user)

    filt = t.SubmissionFilter(request.GET,
                              queryset = StudentSubmissions.objects.filter(student = request.user))
    table = t.SubmissionTable(data=filt.qs)
    table.exclude = 'teacher_actions'
    RequestConfig(request).configure(table)

    context = {
        'title':'Student',
        'form':form,
        'filter':filt,
        'table':table
    }
    return render(request, 'student.html', context)

@login_required(login_url='/login')
def viewstudent(request):
    """Presents a detailed view of a student"""
    try:
        stud = User.objects.get(pk = request.POST['student-pk'])
    except MultiValueDictKeyError:
        stud = User.objects.get(pk = request.session['student-pk'])
    try:
        assign = Assignments.objects.get(pk = request.POST['assignment-pk'])
    except MultiValueDictKeyError:
        assign = Assignments.objects.get(pk = request.session['pk'])

    table = t.SubmissionTable(
        data = StudentSubmissions.objects.filter(student = stud).filter(assignment = assign)
                            )
    table.exclude = 'delete'

    context = {
        'title':stud.username,
        'table':table
    }

    return render(request, 'student.html', context)


@login_required(login_url='/login/')
def teacher(request):
    """collect data to show on the teacher page"""
    if (User.objects.filter(username = request.user).first()
        not in User.objects.filter(type = 'TEA')):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')
    usr = request.user
    filt = t.AssFilter(request.GET, queryset = usr.assignments.all())
    bobby = t.AssTable(data=filt.qs)
    RequestConfig(request).configure(bobby)

    context = {
        'title':'Teacher',
        'filter':filt,
        'table':bobby
    }
    return render(request, 'teacher.html', context)

def user_login(request):
    """the login page"""
    context = {
        'title':'Login',
    }
    if request.method == 'POST':
        form = f.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.info(request, f"Welcome {username}")
                return redirect('index')
    else:
        form = f.LoginForm()

    context['form'] = form
    return render(request, 'login.html', context )

def signup(request):
    """ to create a new user """
    context = {
        'title':'Signup',
    }
    if request.method == 'POST':
        form = f.SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request,
                          f"user {form.cleaned_data['username']} has been created\nPlease login")
            return redirect('login')
    else:
        form = f.SignupForm()

    context['form'] = form

    return render(request, 'signup.html', context)

def user_logout(request):
    """ 
    logout page
    """
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('index')

@login_required(login_url='/login/')
def assignment(request):
    """Provides a detailed view of an assignment"""
    if request.method == 'POST':
        request.session['pk'] = request.POST['pk']

    # get the assignment
    assign = Assignments.objects.get(pk=request.session['pk'])
    # make sure the user is a teacher who is associated with the assignment
    if (User.objects.filter(username = request.user).first() not in
        User.objects.filter(type = 'TEA').filter(assignments__pk = assign.pk)):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')
    studs = assign.user_set.filter(type = 'STU')
    filter = t.UserFilter(request.GET, queryset = studs)
    table = t.UserTable(data = filter.qs)
    table.exclude = ('type','is_active','action')
    table._orderable = False

    subfilter = t.SubmissionFilter(request.GET, queryset =
                StudentSubmissions.objects.filter(student__in=studs).filter(assignment = assign))

    subtable = t.SubmissionTable(data = subfilter.qs)
    subtable.exclude = ('assignment','delete')
    subtable._orderable = False

    RequestConfig(request).configure(table)
    RequestConfig(request).configure(subtable)


    context = {
        'title':f"{assign}",
        'assignment':assign,
        'students':table,
        'studfilter':filter,
        'submissions':subtable,
        'subfilter':subfilter,
    }
    return render(request, 'assignment.html', context)

@login_required(login_url='/login/')
def edit_assignment(request):
    """Presents the form to edit an existing assignment"""
    assign = Assignments.objects.get(pk = request.POST['pk'])

    if (User.objects.filter(username = request.user).first() not in
        User.objects.filter(type = 'TEA').filter(assignments__pk = assign.pk)):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    studs_old = User.objects.filter(assignments__pk = assign.pk)
    if 'save' in request.POST.keys():
        # we want to save our edit
        form = f.AssignmentForm(request.POST, request.FILES, instance = assign)
        studform = f.AddStudForm(request.POST)

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
                messages.info(request, "Assignment has been updated")
                return redirect('teacher')
            # studform was faulty
            messages.error(request, studform.errors)
        # form was faulty
        messages.error(request, form.errors)

    # we intent to edit an existing assignment
    # get the assignment
    form = f.AssignmentForm(instance = assign)
    studform = f.AddStudForm(initial = {'students':[u.id for u in studs_old]})
    context = {
        'title':f"edit {assign.title}",
        'form':form,
        'studform':studform,
        'pk':assign.pk
    }
    return render(request, 'edit_assignment.html', context)

@login_required(login_url='/login/')
def create_assignment(request):
    """view presents the form to create a new assignment"""
    if (User.objects.filter(username = request.user).first() not in
        User.objects.filter(type = 'TEA')):
        # the logged in user is not a teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    if request.method == "POST":
        form = f.AssignmentForm(request.POST, request.FILES)
        users = f.AddStudForm(request.POST)
        if form.is_valid():
            if users.is_valid():
                # save the assignment
                assign = form.save()
                # get the students and add them to the assignment
                users = users.cleaned_data['students']
                studs_new = User.objects.filter(pk__in = users)
                # very important
                request.user.assignments.add(assign)
                for studs in studs_new:
                    studs.assignments.add(assign)
                messages.info(request, "Assignment has been created")
                return redirect('teacher')
            # users was faulty
            messages.error(request, users.errors)
        # form was faulty
        messages.error(request, form.errors)

    form = f.AssignmentForm()
    studform = f.AddStudForm()
    context = {
        'title':'Teacher',
        'form':form,
        'studform':studform,
    }
    return render(request, 'edit_assignment.html', context)

@login_required(login_url='/login/')
def submission(request):
    """View presenting the details of a submission"""
    sub = StudentSubmissions.objects.get(pk = request.POST['pk'])
    if (User.objects.filter(username = request.user).first()
        not in (User.objects.filter(type = User.TypeChoices.STUDENT).filter(studentsubmissions = sub)
        or User.objects.filter(type = User.TypeChoices.TEACHER))):
        # the logged in user is not a student or teacher but is trying to access the page
        messages.error(request, STRING_403)
        return redirect('index')

    context = {
        'title':f'Details {sub}',
        'submission':sub
    }
    return render(request, 'submission.html', context)

@login_required(login_url='/login/')
def reeval(request):
    """trigger the re-evaluation of assignment(s)"""
    mode = request.POST['mode']
    request.session['student-pk'] = request.POST['student-pk']
    assign = Assignments.objects.get(pk = request.session['pk'])
    if mode == 'single':
        subs = StudentSubmissions.objects.filter(pk = request.POST['subpk'])
    else:
        subs = assign.studentsubmissions_set.exclude(
            status = StudentSubmissions.ResChoices.PENDING
            )

    for sub in subs:
        sub.status = StudentSubmissions.ResChoices.PENDING
        # test are run with the debug set to false
        # podmanager has to run in a cluster
        if not settings.DEBUG:
            api = pm.create_api_instance()
            path = pathlib.Path(sub.File.path)
            job,name = pm.create_job_object(assign.title,
                                            assign.image,
                                            resources={
                                                'maxmemory':assign.maxmemory,
                                                'maxcpu':assign.maxcpu,
                                                'timer':assign.timer,
                                                'sub':str(path.parent)
                                                })
            sub.eval_job = name
            pm.create_job(api, job)
        sub.save()
        

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/login/')
def stopeval(request):
    """stop the evaluation of assignment(s)"""
    mode = request.POST['mode']
    request.session['student-pk'] = request.POST['student-pk']
    assign = Assignments.objects.get(pk = request.session['pk'])
    if mode == 'single':
        subs = StudentSubmissions.objects.filter(pk = request.POST['subpk'])
    else:
        subs = assign.studentsubmissions_set.filter(status = StudentSubmissions.ResChoices.RUNNING )

    for sub in subs:
        sub.status = StudentSubmissions.ResChoices.STOP
        # test are run with the debug set to false
        # podmanager has to run in a cluster
        if settings.DEBUG:
            name = sub.eval_job
            sub.eval_job = ""
            sub.save()
            api = pm.create_api_instance()
            pm.delete_job(api, name)

    return redirect(request.META.get('HTTP_REFERER', '/'))

def getcsv(request):
    """extract the results of the given submissions as a csv file"""
    mode = request.POST['mode']

    assign = Assignments.objects.get(pk = request.session['pk'])
    if mode == 'single':
        stud = User.objects.get(pk = request.POST['student-pk'])
        subs = stud.studentsubmissions_set.filter(assignment = assign)
    else:
        subs = assign.studentsubmissions_set.all()

    response = HttpResponse(
        content_type = "text/csv",
        headers = {"Content-Disposition": 'attachment; filename="metadata.csv"'},
    )
    fields = ["student", "submission id", "submission time", "submission result"]

    writer = csv.writer(response)
    writer.writerow(fields)
    for sub in subs:
        writer.writerow([sub.student.username,
                         str(sub.pk),
                         sub.uploadtime.strftime("%d/%m/%y, %H:%M:%S"),
                         sub.result.open('r').read() ])

    return response

def getzip(request):
    """extract the logs of the given submissions as a zip file"""
    mode = request.POST['mode']

    assign = Assignments.objects.get(pk = request.session['pk'])
    if mode == 'single':
        stud = User.objects.get(pk = request.POST['student-pk'])
        subs = stud.studentsubmissions_set.filter(assignment = assign)
    else:
        subs = assign.studentsubmissions_set.all()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode='w') as zip_file:
        for sub in subs:
            zip_file.writestr(sub.log.name, sub.log.open('r').read())

    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = "application/x-zip-compressed"
    response['Content-Disposition'] = 'attachment; filename="logs.zip"'

    return response
class AssignmentDeleteView(DeleteView, SingleObjectMixin):
    """delete an assignment"""
    model = Assignments
    success_url = reverse_lazy('teacher')

class UserDeleteView(DeleteView, SingleObjectMixin):
    """delete a user"""
    model = User
    success_url = reverse_lazy('admin')

class SubDeleteView(DeleteView, SingleObjectMixin):
    """delete a submission"""
    model = StudentSubmissions
    success_url = reverse_lazy('student')
