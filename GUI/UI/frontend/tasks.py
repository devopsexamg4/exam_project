"""
Scheduled tasks are dedfined in this file
"""

import pathlib
from .img import podmanager as pm
from .models import StudentSubmissions


def eval_submissions():
    """
    get the latest 10 submissions and evaluate them using kubernetes jobs
    """
    subs = StudentSubmissions.objects.filter(status=StudentSubmissions.ResChoices.PENDING)
    subs.order_by("uploadtime").distinct("student")
    # we might as well start 10 at a time
    space = 10 - len(subs)
    if space > 0:
        add = StudentSubmissions.objects.filter(status=StudentSubmissions.ResChoices.PENDING)
        add.order_by("uploadtime").exclude(id__in=subs)
        to_start = list(subs)+list(add)[:space]
    else:
        to_start = list(subs)[:10]

    # start the evaluations
    api = pm.create_api_instance()
    for sub in to_start:
        res_dict = {
            'maxmemory':sub.assignment.maxmemory,
            'maxcpu':sub.assignment.maxcpu,
            'timer':sub.assignment.timer,
            'sub':str(pathlib.Path(sub.File.path).parent)
        }
        job,name = pm.create_job_object(sub.assignment.title,
                                        sub.assignment.image,
                                        resources=res_dict)
        pm.create_job(api, job)
        sub.eval_job = name
        sub.status = StudentSubmissions.ResChoices.RUNNING
        sub.save()
        

def read_res():
    """
    read the results of evaluations and update submissions if the job has finished
    """
    runninng = StudentSubmissions.objects.filter(status = StudentSubmissions.ResChoices.RUNNING)
    api = pm.create_api_instance()
    for sub in runninng:
        res = pm.get_job_status(api, sub.eval_job)
        if res.status.succeeded is not None or res.status.failed is not None:
            # job has fininshed read the results
            result = str(pathlib.Path(sub.File.path).parent)+"/result.txt"
            sub.result = result
            sub.status = StudentSubmissions.ResChoices.FINISHED
            sub.save()



