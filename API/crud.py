from sqlalchemy.orm import Session
from sqlalchemy import delete, insert

import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.user_name == user_name).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    kinda_hashed_password = user.password + "hash"
    db_user = models.User(user_name=user.user_name, 
                          user_type=user.user_type, 
                          email=user.email, 
                          password=kinda_hashed_password,
                          is_active = True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, **kwargs):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    for key, value in kwargs.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.user_id == user_id).delete()
    db.commit()

def get_assignment(db: Session, ass_id: int):
    return db.query(models.Assignments).filter(models.Assignments.ass_id == ass_id).first()

def get_submission(db: Session, sub_id: int):
    return db.query(models.StudentSubmissions).filter(models.StudentSubmissions.sub_id == sub_id).first()

def create_submission(db: Session, submission: schemas.StudentSubmissionCreate, assignment_id: int, student_id: int):
    db_submission = models.StudentSubmissions(file=submission.file, 
                                              result=submission.result, 
                                              log_file=submission.log_file, 
                                              upload_time=submission.upload_time,
                                              submitter_id=student_id,
                                              assignment_id=assignment_id)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission
    

def delete_submission(db: Session, sub_id: int):
    db.query(models.StudentSubmissions).filter(models.StudentSubmissions.sub_id == sub_id).delete()
    db.commit()

def create_assignment(db: Session, assignment: schemas.AssignmentCreate):
    db_assignment = models.Assignments(docker_file=assignment.docker_file, 
                                      status=assignment.status, 
                                      max_memory=assignment.max_memory, 
                                      max_CPU=assignment.max_CPU, 
                                      start=assignment.start, 
                                      end=assignment.end)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_assignment(db: Session, ass_id: int):
    return db.query(models.Assignments).filter(models.Assignments.ass_id == ass_id).first()

def update_assignment(db: Session, ass_id: int, **kwargs):
    db_assignment = db.query(models.Assignments).filter(models.Assignments.ass_id == ass_id).first()
    for key, value in kwargs.items():
        setattr(db_assignment, key, value)
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def delete_assignment(db: Session, ass_id: int):
    db.query(models.Assignments).filter(models.Assignments.ass_id == ass_id).delete()
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

