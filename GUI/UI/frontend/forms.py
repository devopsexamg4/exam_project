from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User

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
