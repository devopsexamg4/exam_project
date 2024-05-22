from sqlalchemy import Table, Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship

#from .database import Base
from .database import Base

class User(Base):
    __tablename__ = "UserTable"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, index=True)
    user_type = Column(String) # "STUDENT", "TEACHER", "ADMIN"
    email = Column(String, index=True)
    password = Column(String) 
    is_active = Column(Boolean)

    submissions = relationship("StudentSubmissions", back_populates="submitter")
    assignments = relationship("Assignments", secondary="user_assignment_association", back_populates="contributors") # both teacher and student?

class Assignments(Base):
    __tablename__ = "Assignments"
    ass_id = Column(Integer, primary_key=True)
    docker_file = Column(String) # docker image, is there a concrete type for this?
    status = Column(String) # "HIDDEN", "ACTIVE", "PAUSED", "FINISHED"
    max_memory = Column(Integer)
    max_CPU = Column(Integer)
    start = Column(TIMESTAMP)
    end = Column(TIMESTAMP)
    timer = Column(TIMESTAMP)
    max_submissions = Column(Integer)

    contributors = relationship("User", secondary="user_assignment_association", back_populates="assignments") # figure out how to discern between student and teacher
    submissions = relationship("StudentSubmissions", back_populates="assignment")

class StudentSubmissions(Base):
    __tablename__ = "StudentSubmissions"
    sub_id = Column(Integer, primary_key=True)
    eval_jo = Column(String)
    file = Column(String) # path to sourcefile
    result = Column(String) # "PASSED", "FAILED", "NOTRUN"
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