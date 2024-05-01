"""
TODO:
    - create a docstring for this module
    - make sure help text exists
    - make sure the docstrings provide a simple how to
    - use a proper date picker for the assignments
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import Assignments, StudentSubmissions, User

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
        fields = ['type']
        help_texts = {
            'type':_('Select the type this user should have'),
        }

class AssignmentForm(forms.ModelForm):
    """A form to submit new assignments"""
    class Meta:
        """The model and attributes used to create a new assignment"""
        model = Assignments
        fields = "__all__"

class SubmissionForm(forms.ModelForm):
    """A form to make a submission"""
    def __init__(self, *args, user = None, **kwargs):
        super().__init__(*args,**kwargs)
        if user is not None:
            self.fields['assignment'].queryset = user.assignments.all()
        else:
            self.fields['assignment'].queryset = Assignments.objects.none()
    class Meta:
        """The model and atrributes to create a submission"""
        model = StudentSubmissions
        exclude = ['result','log']

class AddStudForm(forms.Form):
    """form to add students to an assignment"""
    students = forms.MultipleChoiceField(choices = [User.objects.filter(type = 'STU')], widget = forms.CheckboxSelectMultiple())
