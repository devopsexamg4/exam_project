"""
All models used througout the application is defined in this file
TODO:
    - add help text to all fields
    - add docstring to studentsubmission
    - add docstring to User
    - validate the uploaded files
"""
from datetime import datetime,timedelta
from tkinter import CASCADE
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator


def dockerdir(instance, _):
    """generate a path to save the uploaded dockerfile"""
    return f"assignments/{str(uuid4())}/{instance.dockerfile}"

def subdir(instance, _):
    """Generate a path to save the uploaded submission"""
    return f"submissions/{str(uuid4())}/{instance.File}"

class Assignments(models.Model):
    """
    This model is used to configure a new assignment
    the attributes stored here will be used to generate a yml file
    that yml file is how kubernetes is configered to run the assignment
    """
    class StatusChoices(models.TextChoices):
        """
        An assignment can be in one of four states as defined in this class
        """
        HIDDEN = "HID",_("Hidden")
        ACTIVE = "ACT",_("Active")
        PAUSED = "PAU",_("Paused")
        FINISHED = "FIN",_("Finished")

    status = models.CharField(
        max_length = 3,
        choices = StatusChoices,
        default = StatusChoices.HIDDEN
    )

    maxmemory = models.PositiveIntegerField(
        default = 100,
        validators = [ MaxValueValidator(1000) ]
    )

    maxcpu = models.PositiveIntegerField(
        default = 1,
        validators = [ MaxValueValidator(4) ]
    )

    timer = models.DurationField(
        default = timedelta(seconds = 120),
        validators = [ MaxValueValidator(timedelta(minutes = 10)) ]
    )

    start = models.DateTimeField(
        default = datetime.now()
    )

    end = models.DateTimeField(
        default = datetime.now() + timedelta(days = 14)
    )

    dockerfile = models.FileField(
        upload_to = dockerdir
    )

    maxsubs = models.PositiveIntegerField(
        default = 5,
        validators = [ MaxValueValidator(15) ]
    )


class StudentSubmissions(models.Model):
    class ResChoices(models.TextChoices):
        PASSED = "PAS", _("Passed")
        FAILED = "FAI", _("Failed")
        PENDING = "PEN", _("Pending")

    result = models.CharField(
        max_length = 3,
        choices = ResChoices,
        default = ResChoices.PENDING
    )

    File = models.FileField(
        upload_to = subdir
    )

    log = models.FileField(
        blank = True,
        null = True
    )

    uploadtime = models.DateTimeField(
        auto_now_add = True
    )

    assignment = models.ForeignKey(
        Assignments,
        on_delete = models.CASCADE
    )

class User(AbstractUser):
    class TypeChoices(models.TextChoices):
        ADMIN = "ADM", _("Admin")
        TEACHER = "TEA", _("Teacher")
        STUDENT = "STU", _("Student")

    type = models.CharField(
        max_length = 3,
        choices = TypeChoices,
        null = True,
        default = TypeChoices.STUDENT,
        )

    submission = models.ForeignKey(
        StudentSubmissions,
        on_delete = models.CASCADE,
        blank = True,
        null = True
    )

    assignments = models.ManyToManyField(
        Assignments
    )
