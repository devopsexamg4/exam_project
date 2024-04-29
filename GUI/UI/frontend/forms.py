from django import forms
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

