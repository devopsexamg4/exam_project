from pydantic import BaseModel
import datetime

from .models import UserType
from .models import Status
from .models import Result

# base classes contain data common to creating and reading
# create classes contain data unique to creating
# the third type, the 'actual' class, contains data that can only be returned by reading from database

class StudentSubmissionBase(BaseModel):
    file: str # path to file? Return here with answer

class StudentSubmissionCreate(StudentSubmissionBase):
    pass

class StudentSubmission(StudentSubmissionBase):
    sub_id: int
    result: Result
    log_file: str # perhaps name of file? Return here with answer
    upload_time: datetime
    submitter_id: int
    assignment_id: int

    class Config:
        orm_mode = True

class AssignmentBase(BaseModel):
    docker_file: str # path to file? Return here with answer
    status: Status
    max_memory: int
    max_CPU: int
    start: datetime
    end: datetime
    max_submissions: int

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    ass_id: int
    timer: datetime
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