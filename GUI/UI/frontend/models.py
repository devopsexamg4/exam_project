"""
All models used througout the application is defined in this file
TODO:
    - validate the uploaded files
"""
from datetime import datetime,timedelta
from django.utils import timezone
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError

def get_deadline():
    """get the default deadline for an assignment"""
    return timezone.now() + timedelta(days = 14)

def dockerdir(instance, _):
    """generate a path to save the uploaded dockerfile"""
    return f"assignments/{str(uuid4())[0:5]}{instance.dockerfile}"

def subdir(instance, _):
    """Generate a path to save the uploaded submission"""
    return f"submissions/{str(uuid4())[0:5]}{instance.File}"

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

    title = models.TextField(
        default = f"Assignment-{str(uuid4())[:5]}",
        help_text = "The name of this assignment to easily distinguish it from other assignments"
    )

    status = models.CharField(
        max_length = 3,
        choices = StatusChoices,
        default = StatusChoices.HIDDEN,
        help_text = """The status of this assignment,
                        only assignments with 'Active' status can receive submissions""",
    )

    maxmemory = models.PositiveIntegerField(
        default = 100,
        validators = [ MaxValueValidator(1000) ],
        help_text = """Amount of memory allocated to this assignment in MiB,
                        Must be within [1, 1000], default is 100"""
    )

    maxcpu = models.PositiveIntegerField(
        default = 1,
        validators = [ MaxValueValidator(4) ],
        help_text = """The amount of vCPU's allocated to this assignment,
                         must be within [1,4], default is 1"""
    )

    timer = models.DurationField(
        default = timedelta(seconds = 120),
        validators = [ MaxValueValidator(timedelta(minutes = 10)) ],
        help_text = """The maximum time submission can be tested in seconds,
                        must be within [1, 600], default is 120"""
    )

    start = models.DateTimeField(
        default = timezone.now,
        help_text = """The starting time of this assignment, must be a vaild date and time"""
    )

    end = models.DateTimeField(
        default = get_deadline,
        help_text = """The deadline of the assignment must be a valid date and time,
                    must be after the start time, default is 14 days after the start"""
    )

    dockerfile = models.FileField(
        upload_to = dockerdir,
        help_text = """The dockerfile defining the image which runs the tests
                         on the uploaded submissions"""

    )

    maxsubs = models.PositiveIntegerField(
        default = 5,
        validators = [ MaxValueValidator(15) ],
        help_text = """The maximum amount of pending submissions per student,
                        must be within [1,15], default is 5"""
    )

    def _validinterval(self):
        end = self.end
        start = self.start
        if end <= start:
            raise ValidationError("Deadline must be later than starting time")

    def save(self, *args, **kwargs):
        """Validate that the assignment has a valid interval before saving"""
        self._validinterval()
        super().save(*args, **kwargs)

    def __str__(self):
        """returns a textual representation of the assignment"""
        return str(self.title)

    def delete(self):
        """
        reomve the associated file before deleting the object,
        how cool would it be if this was the default behaviour
        pylint please read this:
        https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.fields.files.FieldFile.delete
        """
        self.dockerfile.delete()
        super().delete()

class User(AbstractUser):
    """
    An extension of the django user class
    to include the attributes we need
    """
    class TypeChoices(models.TextChoices):
        """
        The choices for the type field
        """
        ADMIN = "ADM", _("Admin")
        TEACHER = "TEA", _("Teacher")
        STUDENT = "STU", _("Student")

    type = models.CharField(
        max_length = 3,
        choices = TypeChoices,
        null = True,
        default = TypeChoices.STUDENT,
        help_text = """The type of a user, default is student"""
        )

    assignments = models.ManyToManyField(
        Assignments,
        help_text = """The assignment(s) a user can interact with"""
    )

    def __str__(self):
        """A textual representation of a user"""
        return str(self.username)

class StudentSubmissions(models.Model):
    """
    This class models a submission by a student to an assignment
    an individual assignment is removed if the assignment is removed
    or the user (student) is removed
    """
    class ResChoices(models.TextChoices):
        """The choices for the result field"""
        PASSED = "PAS", _("Passed")
        FAILED = "FAI", _("Failed")
        PENDING = "PEN", _("Pending")
        STOP = "STP",_("Stopped")

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text = """The student who made this submission"""
    )

    result = models.CharField(
        max_length = 3,
        choices = ResChoices,
        default = ResChoices.PENDING,
        help_text = """The status of this submission"""
    )

    File = models.FileField(
        upload_to = subdir,
        help_text = """The file to be tested, must be a zip archive"""
    )

    log = models.FileField(
        blank = True,
        null = True,
        help_text = """The log showing the evaluation process of this assignment"""
    )

    uploadtime = models.DateTimeField(
        auto_now_add = True,
        help_text = """The time this assignment was uploaded"""
    )


    assignment = models.ForeignKey(
        Assignments,
        on_delete = models.CASCADE,
        help_text = """The assignment for which this is a submission"""
    )

    def _validtime(self):
        """validate that the upload time is after assignment start
        and before assignment end
        """
        end = self.assignment.end
        start = self.assignment.start
        upl = self.uploadtime
        if (upl < start) or (end < upl):
            raise ValidationError("Submission uploaded outside of assignment time window")

    def _validpending(self):
        maxsub = self.assignment.maxsubs
        current = len(self.student.studentsubmissions_set.filter(assignment = self.assignment))
        if maxsub <= current:
            raise ValidationError("You already have the maximum amount of pending submissions")

    def __str__(self):
        """textual representation of a submission
        user who uploaded and time of upload
        """
        return f"{self.student} - {self.uploadtime.strftime('%d/%m/%y, %H:%M')}"

    def save(self, *args, **kwargs):
        """custom save function in order to validate:
         - upload time is within assignment interval
         - the student does not have too many pending submissions
         """
        self._validtime()
        self._validpending()
        super().save(*args, **kwargs)

    def delete(self):
        """custom delete function to remove the associated file
        """
        self.File.delete()
        super().delete()
