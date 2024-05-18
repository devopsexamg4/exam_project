from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import conlist
from typing import Annotated
from jose import JWTError, jwt

import datetime
import io
import csv
from zipfile import ZipFile

import crud, models, schemas
import podmanager as pm
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "a6e9d63fce8d1f7ec31f625ea2affe18fa447beca84ac8ea9f818f4e3bf3aaec"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Token(schemas.BaseModel):
    access_token: str
    token_type: str

class TokenData(schemas.BaseModel):
    username: str | None = None

def authenticate_user(db: Session, username: str, password: str):
    db_user = crud.get_user_by_name(db, user_name=username)
    if not db_user:
        return False
    if not crud.verify_password(password, db_user.password):
        return False
    return db_user

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_name(db, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# student endpoints: 

@app.post("/login/", response_model = Token, status_code=201)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.user_name}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/student/create/", response_model=schemas.User, status_code=201)
def create_profile_student(student: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=student.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user2 = crud.get_user_by_email(db, email=student.email)
    if db_user2:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user_student(db=db, user=student)

@app.get("/student/assignments/", response_model=list[schemas.Assignment], status_code=200)
def get_assignments(current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    return current_user.assignments

@app.post("/student/assignments/{assignment_id}/sumbit/", response_model=schemas.StudentSubmission, status_code=201)
def submit_solution(assignment_id: int, submission: schemas.StudentSubmissionCreate, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if db_assignment not in current_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment", headers={"WWW-Authenticate": "Bearer"})
    for contributor in db_assignment.contributors:
        if contributor.user_type == models.UserType.TEACHER and not contributor.is_active:
            raise HTTPException(status_code=400, detail="Teacher is not active", headers={"WWW-Authenticate": "Bearer"})
    if db.query(models.StudentSubmissions).filter(models.StudentSubmissions.assignment_id == assignment_id).count() >= db_assignment.max_submissions:
        raise HTTPException(status_code=400, detail="Submission limit reached")
    # if assignment is active, run submission immediately
    return crud.create_submission(db=db, submission=submission, assignment_id=assignment_id, student_id=current_user.user_id)

@app.get("/student/assignments/{assignment_id}/submission/{submission_id}/status/", status_code=200)
def get_assignment_evaluation(assignment_id: int, submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if db_assignment not in current_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment", headers={"WWW-Authenticate": "Bearer"})
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if db_submission.submitter_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="Submission not owned by student", headers={"WWW-Authenticate": "Bearer"})
    if db_submission not in db_assignment.submissions:
        raise HTTPException(status_code=401, detail="Submission not submitted to this assignment", headers={"WWW-Authenticate": "Bearer"})
    return db_submission.result

@app.delete("/student/submissions/{submission_id}/", status_code=204)
def delete_submission(submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if db_submission.submitter_id != current_user.user_id:
        raise HTTPException(status_code=401, detail="Submission not owned by student", headers={"WWW-Authenticate": "Bearer"})
    if db_submission.result != models.Result.NOTRUN:
        raise HTTPException(status_code=400, detail="Submission being processed")
    crud.delete_submission(db, sub_id=submission_id)
    return {"Deleted submission: ": submission_id}

# teacher endpoints: 

@app.post("/teacher/assignment/")
def add_assignment(assignment: schemas.AssignmentCreate, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    return crud.create_assignment(db=db, assignment=assignment)

@app.patch("/teacher/assignment/{assignment_id}/")
def update_assignment(current_user: Annotated[schemas.User, Depends(get_current_active_user)], assignment_id: int, dockerfile: str | None = None, status: models.Status | None = None, max_memory: int | None = None, max_CPU: int | None = None, start: datetime.datetime | None = None, end: datetime.datetime | None = None, db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return crud.update_assignment(db=db, assignment=db_assignment, dockerfile=dockerfile, status=status, max_memory=max_memory, max_CPU=max_CPU, start=start, end=end)

@app.patch("/teacher/assignment/{assignment_id}/pause/")
def pause_assignment(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if db_assignment.status == models.Status.PAUSED:
        raise HTTPException(status_code=400, detail="Assignment is already paused")
    return crud.update_assignment(db=db, ass_id=assignment_id, status=models.Status.PAUSED)

@app.delete("/teacher/assignment/{assignment_id}/delete/")
def delete_assignment(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    crud.delete_assignment(db, ass_id=assignment_id)
    return {"Deleted assignment: ": assignment_id}

@app.patch("/teacher/assignment/{assignment_id}/remove-student/")
def remove_student_from_assignment(assignment_id: int, student_ids: conlist(int, min_length=1), current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found: " + assignment_id)
    for id in student_ids:
        db_user = crud.get_user(db, user_id=id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found: " + id)
        if db_assignment not in db_user.assignments:
            raise HTTPException(status_code=400, detail="User is not part of this assignment")
        crud.remove_student_from_assignment(db=db, ass_id=assignment_id, user_id=id)
    return {"Removed student(s) from assignment: ": assignment_id}

@app.patch("/teacher/assignment/{assignment_id}/add-student/")
def add_student_to_assignment(assignment_id: int, student_ids: conlist(int, min_length=1), current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found: " + assignment_id)
    for id in student_ids:
        db_user = crud.get_user(db, user_id=id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found: " + id)
        if db_assignment in db_user.assignments:
            raise HTTPException(status_code=400, detail="User is already part of this assignment")
        crud.add_student_to_assignment(db=db, ass_id=assignment_id, user_id=id)
    return {"Added student(s) to assignment: ": assignment_id}

@app.get("/teacher/assignmnet/{assignment_id}/student-submissions/{student_id}/")
def get_student_submissions(assignment_id: int, student_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment", headers={"WWW-Authenticate": "Bearer"})
    return db.query(models.StudentSubmissions).filter(models.StudentSubmissions.submitter_id == student_id).filter(models.StudentSubmissions.assignment_id == assignment_id).all()

@app.get("/teacher/submission/{submission_id}/outcome/")
def get_submission_outcome(submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db_assignment = crud.get_assignment(db, ass_id=db_submission.assignment_id)
    return {db_assignment.status, db_submission.log_file, db_submission.result}

# here should be an endpoint for the teacher to 'trigger the re-evaluation of the submission'

# here should be an endpoint for the teacher to stop evaluation of submission

# here should be an endpoint for the teacher to stop evaluations of all submissions under an assignment

@app.get("/teacher/assignment/{assignment_id}/submission-logs/")
def get_assignment_submission_logs(assignment_id: int,  current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for submission in db_assignment.submissions:
            zip_file.write(submission.log_file, arcname=str(submission.sub_id) + submission.log_file)
    zip_buffer.seek(0)
    return zip_buffer

@app.get("/teacher/assignment/{assignment_id}/student/{student_id}/submission-logs/")
def get_assignment_student_submission_logs(assignment_id: int, student_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Student not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="Student does not have access to this assignment", headers={"WWW-Authenticate": "Bearer"})
    
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for submission in db_assignment.submissions:
            if submission.submitter_id == student_id:
                zip_file.write(submission.log_file, arcname=submission.log_file)
    zip_buffer.seek(0)
    return zip_buffer

@app.get("/teacher/assignment/{assignment_id}/submissions-metadata/")
def get_assignment_submissions_metadata(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    row_data = [[], [], [], [], []]
    for contributor in db_assignment.contributors:
        for submission in contributor.submissions:
            if submission.assignment_id == assignment_id:
                row_data[0].append(contributor.user_name)
                row_data[1].append(contributor.email)
                row_data[2].append(submission.sub_id)
                row_data[3].append(submission.upload_time)
                row_data[4].append(submission.result)
    
    csv_buffer = io.StringIO()
    with csv_buffer as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Contributor Name", "Contributor Email", "Submission ID", "Upload Time", "Result"])
        for row in row_data:
            writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer

@app.get("/teacher/assignment/{assignment_id}/student/{student_id}/submissions-metadata/")
def get_assignment_student_submissions_metadata(assignment_id: int, student_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type == models.UserType.STUDENT:
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment", headers={"WWW-Authenticate": "Bearer"})
    
    row_data = [[], [], [], [], []]
    for submission in db_user.submissions:
        if submission.assignment_id == assignment_id:
            row_data[0].append(db_user.user_name)
            row_data[1].append(db_user.email)
            row_data[2].append(submission.sub_id)
            row_data[3].append(submission.upload_time)
            row_data[4].append(submission.result)
    
    csv_buffer = io.StringIO()
    with csv_buffer as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Contributor Name", "Contributor Email", "Submission ID", "Upload Time", "Result"])
        for row in row_data:
            writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer

# administrator endpoints: 

@app.post("/admin/add-teacher/", response_model=schemas.User)
def add_teacher(teacher: schemas.UserCreate, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=401, detail="User is not an admin", headers={"WWW-Authenticate": "Bearer"})
    db_user = crud.get_user_by_email(db, email=teacher.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user2 = crud.get_user_by_name(db, user_name=teacher.user_name)
    if db_user2:
        raise HTTPException(status_code=400, detail="Username already registered")
    if teacher.user_type != models.UserType.TEACHER:
        raise HTTPException(status_code=400, detail="User type must be teacher")
    return crud.create_user_teacher(db=db, user=teacher)

@app.patch("/admin/teacher/{teacher_id}/pause/")
def pause_teacher(teacher_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=401, detail="User is not an admin", headers={"WWW-Authenticate": "Bearer"})
    db_user = crud.get_user(db, user_id=teacher_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.user_type != models.UserType.TEACHER:
        raise HTTPException(status_code=400, detail="User is not a teacher")
    if db_user.is_active == False:
        raise HTTPException(status_code=400, detail="User is already paused")
    # pause / cancel all submissions to a teachers assignments?
    return crud.update_user(db=db, user_id=teacher_id, is_active=False)

@app.delete("/admin/user/{user_id}/delete/")
def delete_user(user_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(status_code=401, detail="User is not an admin", headers={"WWW-Authenticate": "Bearer"})
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.user_type == models.UserType.ADMIN:
        raise HTTPException(status_code=400, detail="Admin cannot be deleted")
    # delete all assignments this teacher is responsible for
    crud.delete_user(db=db, user_id=user_id)
    return {"Deleted user: ": user_id}