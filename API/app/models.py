from sqlalchemy import Table, Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship

#from .database import Base
from .database import Base

class User(Base):
    __tablename__ = "frontend_user" 
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    user_type = Column(String) # "STU", "TEA", "ADM"
    email = Column(String, index=True)
    password = Column(String) 
    is_active = Column(Boolean)
    is_superuser = Column(Boolean)
    is_staff = Column(Boolean)
    date_joined = Column(TIMESTAMP)

    submissions = relationship("StudentSubmissions", back_populates="submitter")
    assignments = relationship("Assignments", secondary="user_assignment_association", back_populates="contributors") # both teacher and student?

class Assignments(Base):
    __tablename__ = "frontend_assignments"
    id = Column(Integer, primary_key=True)
    docker_file = Column(String) # path to docker image, dockerfile
    image = Column(String) # path to docker image
    status = Column(String) # "HID", "ACT", "PAU", "FIN"
    maxmemory = Column(Integer)
    maxcpu = Column(Integer)
    start = Column(TIMESTAMP)
    endtime = Column(TIMESTAMP)
    timer = Column(Integer)
    maxsubs = Column(Integer)
    title = Column(String) # title of assignment

    contributors = relationship("User", secondary="user_assignment_association", back_populates="assignments") # figure out how to discern between student and teacher
    submissions = relationship("StudentSubmissions", back_populates="assignment")

class StudentSubmissions(Base):
    __tablename__ = "frontend_submissions"
    id = Column(Integer, primary_key=True)
    eval_job = Column(String)
    file = Column(String) # path to sourcefile
    result = Column(String) # path to result file
    status = Column(String) # FIN, PEN, RUN, STP
    log = Column(String) # log
    uploadtime = Column(TIMESTAMP) # uploadtime

    student_id = Column(Integer, ForeignKey("frontend_user.id"))
    submitter = relationship("User", back_populates="submissions")

    assignment_id = Column(Integer, ForeignKey("frontend_assignments.id"))
    assignment = relationship("Assignments", back_populates="submissions")

user_assignment_association = Table(
    "user_assignment_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("frontend_user.id")),
    Column("assignment_id", Integer, ForeignKey("frontend_assignments.id"))
)
