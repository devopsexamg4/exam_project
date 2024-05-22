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
    id: int
    result: str # path to result file
    status: str # FIN, PEN, RUN, STP
    log: str # path to file?
    uploadtime: datetime
    student_id: int
    assignment_id: int

    class Config:
        from_attributes = True

class AssignmentBase(BaseModel):
    status: str # HID, ACT, PAU, FIN
    maxmemory: int
    maxcpu: int
    start: datetime
    endtime: datetime
    maxsubs: int
    timer: int # minutes
    title: str # title of assignment

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    docker_file: bytes # docker image
    id: int
    contributors: list['User'] = []
    submissions: list[StudentSubmission] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str # hash this somehow

class User(UserBase):
    is_active: bool
    user_type: str # STU, TEA, ADM
    id: int
    submissions: list[StudentSubmission] = []
    assignments: list[Assignment] = []

    class Config:
        from_attributes = True