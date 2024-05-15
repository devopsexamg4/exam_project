"""
functions that perform tasks used multiple times
"""
from .models import StudentSubmissions

def stopsub(usr):
    """
    Stop submission evaluation when a teacher is set to inactive or deleted
    """
    assigns = usr.assignments_set.all()
    subs = []
    for ass in assigns:
        subs += list(ass.studentsubmissions_set
                        .filter(result = StudentSubmissions.ResChoices.PENDING))
    for s in subs:
        s.result = StudentSubmissions.ResChoices.STOP
        s.save()