"""
In this module the models (DB entries) are registered,
such that they can be accessed and modified in the built-in
django admin page
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Assignments, StudentSubmissions, User

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Assignments)
admin.site.register(StudentSubmissions)
