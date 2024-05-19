from sqlalchemy import Table, Column, Integer, String, ForeignKey, TIMESTAMP, Enum, Boolean
from sqlalchemy.orm import relationship

from enum import Enum

#from .database import Base
from database import Base

class Result(Enum):
    PASSED = 1
    FAILED = 2
    NOTRUN = 3

class Status(Enum):
    HIDDEN = 1
    ACTIVE = 2
    PAUSED = 3
    FINISHED = 4

class UserType(Enum):
    STUDENT = 1
    TEACHER = 2
    ADMIN = 3

class User(Base):
    __tablename__ = "UserTable"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, index=True)
    user_type = Column(UserType)
    email = Column(String, index=True)
    password = Column(String) 
    is_active = Column(Boolean)

    submissions = relationship("StudentSubmissions", back_populates="submitter")
    assignments = relationship("Assignments", secondary="user_assignment_association", back_populates="contributor") # both teacher and student?

class Assignments(Base):
    __tablename__ = "Assignments"
    ass_id = Column(Integer, primary_key=True)
    docker_file = Column(String) # path to docker image, is there a concrete type for this?
    status = Column(Status)
    max_memory = Column(Integer)
    max_CPU = Column(Integer)
    start = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    timer = Column(TIMESTAMP)
    max_submissions = Column(Integer)

    contributors = relationship("User", back_populates="assignments") # figure out how to discern between student and teacher
    submissions = relationship("StudentSubmissions", back_populates="assignment")

class StudentSubmissions(Base):
    __tablename__ = "StudentSubmissions"
    sub_id = Column(Integer, primary_key=True)
    eval_job: Column(String)
    file = Column(String) # path to sourcefile
    result = Column(Result)
    log_file = Column(String)
    upload_time = Column(TIMESTAMP)

    submitter_id = Column(Integer, ForeignKey("UserTable.user_id"))
    submitter = relationship("User", back_populates="submissions")

    assignment_id = Column(Integer, ForeignKey("Assignments.ass_id"))
    assignment = relationship("Assignments", back_populates="submissions")

user_assignment_association = Table(
    "user_assignment_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("UserTable.user_id")),
    Column("assignment_id", Integer, ForeignKey("Assignments.ass_id"))
)