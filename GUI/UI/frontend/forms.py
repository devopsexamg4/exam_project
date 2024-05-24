"""
This module contains all the forms used throughout the frontend 'app'
These forms are used to create and modify database entries
"""
from bootstrap_datepicker_plus.widgets import DateTimePickerInput, TimePickerInput
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import Assignments, User, StudentSubmissions

class SignupForm(UserCreationForm):
    """form to create a new user"""
    class Meta:
        """define model and attributes to include in the form"""
        model = User
        fields = ['username','password1','password2']


class LoginForm(forms.Form):
    """form to login"""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserTypeForm(forms.ModelForm):
    """
    This form is used to allow admins to change the user type of a user
    choices are {Student, Teacher, Admin}
    """
    class Meta:
        """The model and attributes needed to perform the action"""
        model = User
        fields = ['user_type','is_active']
        help_texts = {
            'user_type':_('Select the type this user should have'),
        }

class AssignmentForm(forms.ModelForm):
    """A form to submit new assignments"""
    class Meta:
        """The model and attributes used to create a new assignment"""
        model = Assignments
        fields = ['title',
                  'status',
                  'maxmemory',
                  'maxcpu',
                  'timer',
                  'start',
                  'endtime',
                  'dockerfile',
                  'maxsubs',]
        widgets = {
            'start':DateTimePickerInput(),
            'endtime':DateTimePickerInput(),
            'timer':TimePickerInput(),
            'title':forms.Textarea(attrs={'rows':2})
        }

class SubmissionForm(forms.ModelForm):
    """
    A form to make a submission
    When initializing this form a user should be provided in order to
    correctly list the assignments for which a student can upload a submission
    """
    def __init__(self, *args, user = None, **kwargs):
        super().__init__(*args,**kwargs)
        if user is not None:
            self.fields['assignment'].queryset = user.assignments.all()
        else:
            self.fields['assignment'].queryset = Assignments.objects.none()
    class Meta:
        """The model and atrributes to create a submission"""
        model = StudentSubmissions
        fields = ['file','assignment']


class AddStudForm(forms.Form):
    """form to add students to an assignment"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['students'].choices = [ (u.id,u.username) 
                                           for u in User.objects.filter(user_type = User.TypeChoices.STUDENT)]

    students = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple(), required=False)
