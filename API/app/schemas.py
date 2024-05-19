from pydantic import BaseModel
import datetime

from .models import UserType
from .models import Status
from .models import Result

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
    result: Result
    log_file: str # path to file?
    upload_time: datetime
    submitter_id: int
    assignment_id: int

    class Config:
        orm_mode = True

class AssignmentBase(BaseModel):
    status: Status
    max_memory: int
    max_CPU: int
    start: datetime
    end: datetime
    max_submissions: int
    timer: datetime

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    docker_file: bytes # docker image
    ass_id: int
    contributors: list['User'] = []
    submissions: list[StudentSubmission] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    user_name: str
    email: str

class UserCreate(UserBase):
    password: str # hash this somehow
    is_active: bool


class User(UserBase):
    user_type: UserType
    user_id: int
    submissions: list[StudentSubmission] = []
    assignments: list[Assignment] = []

    class Config:
        orm_mode = True