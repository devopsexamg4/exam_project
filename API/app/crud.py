from sqlalchemy.orm import Session
from sqlalchemy import delete, insert
from passlib.context import CryptContext

import datetime

from . import models, schemas

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.username == user_name).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user_student(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, 
                          user_type="STU",
                          first_name=user.first_name,
                          last_name=user.last_name,
                          email=user.email, 
                          password=hashed_password,
                          is_active=True,
                          is_superuser = False,
                          is_staff = False,
                          date_joined = datetime.datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_teacher(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, 
                          user_type="TEA", 
                          first_name=user.first_name,
                          last_name=user.last_name,
                          email=user.email, 
                          password=hashed_password,
                          is_active = True,
                          is_superuser = False,
                          is_staff = True,
                          date_join = datetime.datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_admin(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, 
                          user_type="ADM", 
                          first_name=user.first_name,
                          last_name=user.last_name,
                          email=user.email, 
                          password=hashed_password,
                          is_active = True,
                          is_superuser = True,
                          is_staff = True,
                          date_join = datetime.datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, **kwargs):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for key, value in kwargs.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()

def get_submission(db: Session, sub_id: int):
    return db.query(models.StudentSubmissions).filter(models.StudentSubmissions.id == sub_id).first()

def create_submission(db: Session, submission: schemas.StudentSubmissionCreate, assignment_id: int, student_id: int):
    db_submission = models.StudentSubmissions(file=submission.file, 
                                              status="PEN", # set to RUN if can be run right away?
                                              result="",
                                              log="",
                                              uploadtime=datetime.datetime.now(),
                                              student_id=student_id,
                                              assignment_id=assignment_id,
                                              eval_job=submission.eval_job)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission
    

def delete_submission(db: Session, sub_id: int):
    db.query(models.StudentSubmissions).filter(models.StudentSubmissions.id == sub_id).delete()
    db.commit()

def create_assignment(db: Session, assignment: schemas.AssignmentCreate, docker_image: bytes):
    db_assignment = models.Assignments(docker_file=docker_image, 
                                      status=assignment.status, 
                                      maxmemory=assignment.maxmemory, 
                                      maxcpu=assignment.maxcpu, 
                                      start=assignment.start, 
                                      endtime=assignment.endtime,
                                      maxsubs=assignment.maxsubs,
                                      timer=assignment.timer,
                                      title=assignment.title)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_assignment(db: Session, ass_id: int):
    return db.query(models.Assignments).filter(models.Assignments.id == ass_id).first()

def update_assignment(db: Session, ass_id: int, **kwargs):
    db_assignment = db.query(models.Assignments).filter(models.Assignments.id == ass_id).first()
    for key, value in kwargs.items():
        setattr(db_assignment, key, value)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def delete_assignment(db: Session, ass_id: int):
    db.query(models.Assignments).filter(models.Assignments.id == ass_id).delete()
    db.commit()

def remove_student_from_assignment(db: Session, ass_id: int, user_id: int):
    statement = (delete(models.user_assignment_association)
                 .where(models.user_assignment_association.c.user_id == user_id)
                 .where(models.user_assignment_association.c.assignment_id == ass_id))
    db.execute(statement)
    db.commit()

def add_student_to_assignment(db: Session, ass_id: int, user_id: int):
    statement = (insert(models.user_assignment_association)
                 .values(user_id=user_id, assignment_id=ass_id))
    db.execute(statement)
    db.commit()

