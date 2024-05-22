from pydantic import BaseModel
from datetime import datetime

# from .models import UserType
# from .models import Status
# from .models import Result
from . import models

# base classes contain data common to creating and reading
# create classes contain data unique to creating
# the third type, the 'actual' class, contains data that can only be returned by reading from database

class StudentSubmissionBase(BaseModel):
    file: str # docker file
    eval_job: str

class StudentSubmissionCreate(StudentSubmissionBase):
    pass

class StudentSubmission(StudentSubmissionBase):
    sub_id: int
    result: str
    log_file: str # path to file?
    upload_time: datetime
    submitter_id: int
    assignment_id: int

    class Config:
        from_attributes = True

class AssignmentBase(BaseModel):
    status: str
    max_memory: int
    max_CPU: int
    start: datetime
    end: datetime
    max_submissions: int
    timer: int # minutes

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    docker_file: bytes # docker image
    ass_id: int
    contributors: list['User'] = []
    submissions: list[StudentSubmission] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    user_name: str
    email: str

class UserCreate(UserBase):
    password: str # hash this somehow
    is_active: bool


class User(UserBase):
    user_type: str
    user_id: int
    submissions: list[StudentSubmission] = []
    assignments: list[Assignment] = []

    class Config:
        from_attributes = True