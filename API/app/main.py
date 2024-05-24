from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import conlist
from typing import Annotated
from jose import JWTError, jwt
from contextlib import asynccontextmanager
from kubernetes.client.rest import ApiException
import re

import datetime
import io
import csv
import os
from zipfile import ZipFile

from . import crud, models, schemas, database
from . import podmanager as pm
from .database import SessionLocal, engine

ADMIN_USERNAME=os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
pvc_file_path = "/var/www/api" # append name of file to look for, path as well if needed

database.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):    
    admin_user = schemas.UserCreate(username=ADMIN_USERNAME, email="admin@localhost.com", password=ADMIN_PASSWORD)
    db_admin = crud.create_user_admin(db=next(get_db()), user=admin_user)
    yield
    crud.delete_user(db=next(get_db()), user_id=db_admin.id)

app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class Token(schemas.BaseModel):
    access_token: str
    token_type: str

class TokenData(schemas.BaseModel):
    username: str | None = None

def verify_email(email: str):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

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
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/student/create/", response_model=schemas.User, status_code=201)
def create_profile_student(student: schemas.UserCreate, db: Session = Depends(get_db)):
    if not verify_email(student.email):
        raise HTTPException(status_code=400, detail="Invalid email")
    db_user = crud.get_user_by_name(db, user_name=student.username)
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
    if db_assignment.status == "PAU":
        raise HTTPException(status_code=400, detail="Assignment is paused", headers={"WWW-Authenticate": "Bearer"})
    if db.query(models.StudentSubmissions).filter(models.StudentSubmissions.assignment_id == assignment_id).count() >= db_assignment.maxsubs:
        raise HTTPException(status_code=400, detail="Submission limit reached")
    name: str
    if db_assignment.status == "ACT":
        manifest = pm.build_kaniko(submission.file, submission.eval_job)
        docker_image = manifest["spec"]["containers"][0]["args"][2]
        resource_dict = {
            "maxmemory": str(db_assignment.maxmemory),
            "maxcpu": str(db_assignment.maxcpu),
            "timer": str(db_assignment.timer),
            "sub": "./"}
        api = pm.create_api_instance()
        job, name = pm.create_job_object(submission.eval_job, docker_image, resource_dict)
        try:
            api_response = pm.create_job(api, job)
        except ApiException as e:
            raise HTTPException(status_code=500, detail="Error: " + str(e))
    with open(pvc_file_path+name, 'w') as file:
        file.write(submission.file)
    db_submission = crud.create_submission(db=db, submission=submission, file=pvc_file_path+submission.file, assignment_id=assignment_id, student_id=current_user.id, eval_job=name)
    return db_submission

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
    if db_submission.id != current_user.id:
        raise HTTPException(status_code=401, detail="Submission not owned by student", headers={"WWW-Authenticate": "Bearer"})
    if db_submission not in db_assignment.submissions:
        raise HTTPException(status_code=401, detail="Submission not submitted to this assignment", headers={"WWW-Authenticate": "Bearer"})
    api = pm.create_api_instance()
    api_response = pm.get_job_status(api, db_submission.eval_job)
    return {"Status": api_response}

@app.delete("/student/submissions/{submission_id}/", status_code=204)
def delete_submission(submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if db_submission.id != current_user.id:
        raise HTTPException(status_code=401, detail="Submission not owned by student", headers={"WWW-Authenticate": "Bearer"})
    if db_submission.result != "PEN":
        raise HTTPException(status_code=400, detail="Submission being, or already has been processed")
    job_status = pm.get_job_status(pm.create_api_instance(), db_submission.eval_job)
    if job_status.status.active > 0 or job_status.succeeded > 0:
        raise HTTPException(status_code=400, detail="Submission being, or already has been processed")
    crud.delete_submission(db, sub_id=submission_id)
    return {"Deleted submission: ": submission_id}

# teacher endpoints: 

@app.post("/teacher/assignment/", response_model=schemas.Assignment, status_code=201)
def add_assignment(current_user: Annotated[schemas.User, Depends(get_current_active_user)], assignment: schemas.AssignmentCreate, docker_image: UploadFile, db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    with open(pvc_file_path+assignment.title, 'w') as file:
        file.write(assignment.docker_file)
    return crud.create_assignment(db=db, assignment=assignment, docker_image=docker_image.read())

@app.patch("/teacher/assignment/{assignment_id}/", response_model=schemas.Assignment, status_code=200)
def update_assignment(current_user: Annotated[schemas.User, Depends(get_current_active_user)], assignment_id: int, docker_image: UploadFile | None = None, status: str | None = None, max_memory: int | None = None, max_CPU: int | None = None, start: datetime.datetime | None = None, end: datetime.datetime | None = None, db: Session = Depends(get_db)):
    if current_user.user_type == "STU" :
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if docker_image:
        if os.path.exists(pvc_file_path+db_assignment.title):
            os.remove(pvc_file_path+db_assignment.title)
        with open(pvc_file_path+db_assignment.title, 'w') as file:
            file.write(docker_image)
    return crud.update_assignment(db=db, assignment=db_assignment, dockerfile=docker_image, status=status, max_memory=max_memory, max_CPU=max_CPU, start=start, end=end)

@app.patch("/teacher/assignment/{assignment_id}/pause/", response_model=schemas.Assignment, status_code=200)
def pause_assignment(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if db_assignment.status == "PAU":
        raise HTTPException(status_code=400, detail="Assignment is already paused")
    return crud.update_assignment(db=db, ass_id=assignment_id, status="PAUSED")

@app.delete("/teacher/assignment/{assignment_id}/delete/", status_code=204)
def delete_assignment(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if os.path.exists(pvc_file_path+db_assignment.title):
        os.remove(pvc_file_path+db_assignment.title)
    crud.delete_assignment(db, ass_id=assignment_id)
    return {"Deleted assignment: ": assignment_id}

@app.patch("/teacher/assignment/{assignment_id}/remove-student/", status_code=204)
def remove_student_from_assignment(assignment_id: int, student_ids: conlist(int, min_length=1), current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
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

@app.patch("/teacher/assignment/{assignment_id}/add-student/", status_code=204)
def add_student_to_assignment(assignment_id: int, student_ids: conlist(int, min_length=1), current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
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

@app.get("/teacher/assignmnet/{assignment_id}/student-submissions/{student_id}/", response_model=list[schemas.StudentSubmission], status_code=200)
def get_student_submissions(assignment_id: int, student_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment", headers={"WWW-Authenticate": "Bearer"})
    return db.query(models.StudentSubmissions).filter(models.StudentSubmissions.id == student_id).filter(models.StudentSubmissions.id == assignment_id).all()

@app.get("/teacher/submission/{submission_id}/outcome/", status_code=200)
def get_submission_outcome(submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db_assignment = crud.get_assignment(db, ass_id=db_submission.assignment_id)
    return {"status": db_assignment.status, "log_file": db_submission.log, "result": db_submission.result}

@app.patch("/teacher/submission/{submission_id}/re-evaluate/", status_code=204)
def re_evaluate_submission(submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db_assignment = crud.get_assignment(db, ass_id=db_submission.assignment_id)
    resource_dict: dict = {
        "maxmemory": db_assignment.maxmemory,
        "maxcpu": db_assignment.maxcpu,
        "timer": db_assignment.timer,
        "sub": "./"}
    api = pm.create_api_instance()
    job, name = pm.create_job_object(db_submission.eval_job, db_submission.file, resource_dict)
    api_response = pm.create_job(api, job)
    return {"Job name: ": name}

# This is working under the assumption that 'name' returned from create_job_object is equal to the name given to the function
@app.patch("/teacher/submission/{submission_id}/stop-evaluation/", status_code=204)
def stop_submission_evaluation(submission_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    api = pm.create_api_instance()
    api_response = pm.delete_job(api, db_submission.eval_job)
    return {"Stopped evaluation of submission: ": submission_id, "api_response": api_response}

# Same comment as above
@app.patch("/teacher/assignment/{assignment_id}/stop-evaluation/", status_code=204)
def stop_assignment_submissions_evaluations(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    for submission in db_assignment.submissions:
        api = pm.create_api_instance()
        api_response = pm.delete_job(api, submission.eval_job)
    return {"Stopped evaluation of all submissions under assignment: ": assignment_id}

@app.get("/teacher/assignment/{assignment_id}/submission-logs/", status_code=200)
def get_assignment_submission_logs(assignment_id: int,  current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for submission in db_assignment.submissions:
            zip_file.write(submission.log, arcname=submission.eval_job + submission.log)
    zip_buffer.seek(0)
    return zip_buffer

@app.get("/teacher/assignment/{assignment_id}/student/{student_id}/submission-logs/", status_code=200)
def get_assignment_student_submission_logs(assignment_id: int, student_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
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
            if submission.id == student_id:
                zip_file.write(submission.log, arcname=submission.log)
    zip_buffer.seek(0)
    return zip_buffer

@app.get("/teacher/assignment/{assignment_id}/submissions-metadata/", status_code=200)
def get_assignment_submissions_metadata(assignment_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)],  db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
        raise HTTPException(status_code=401, detail="User is not a teacher", headers={"WWW-Authenticate": "Bearer"})
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    row_data = [[], [], [], [], []]
    for contributor in db_assignment.contributors:
        for submission in contributor.submissions:
            if submission.id == assignment_id:
                row_data[0].append(contributor.username)
                row_data[1].append(contributor.email)
                row_data[2].append(submission.id)
                row_data[3].append(submission.uploadtime)
                row_data[4].append(submission.status)
    
    csv_buffer = io.StringIO()
    with csv_buffer as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Contributor Name", "Contributor Email", "Submission ID", "Upload Time", "Result"])
        for row in row_data:
            writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer

@app.get("/teacher/assignment/{assignment_id}/student/{student_id}/submissions-metadata/", status_code=200)
def get_assignment_student_submissions_metadata(assignment_id: int, student_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type == "STU":
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
            row_data[0].append(db_user.username)
            row_data[1].append(db_user.email)
            row_data[2].append(submission.id)
            row_data[3].append(submission.uploadtime)
            row_data[4].append(submission.status)
    
    csv_buffer = io.StringIO()
    with csv_buffer as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Contributor Name", "Contributor Email", "Submission ID", "Upload Time", "Result"])
        for row in row_data:
            writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer

# administrator endpoints: 

@app.post("/admin/add-teacher/", response_model=schemas.User, status_code=201)
def add_teacher(teacher: schemas.UserCreate, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if not verify_email(teacher.email):
        raise HTTPException(status_code=400, detail="Invalid email")
    if current_user.user_type != "ADM":
        raise HTTPException(status_code=401, detail="User is not an admin", headers={"WWW-Authenticate": "Bearer"})
    db_user = crud.get_user_by_email(db, email=teacher.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user2 = crud.get_user_by_name(db, user_name=teacher.username)
    if db_user2:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user_teacher(db=db, user=teacher)

@app.patch("/admin/teacher/{teacher_id}/pause/", response_model=schemas.User, status_code=200)
def pause_teacher(teacher_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type != "ADM":
        raise HTTPException(status_code=401, detail="User is not an admin", headers={"WWW-Authenticate": "Bearer"})
    db_user = crud.get_user(db, user_id=teacher_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.user_type != "TEA":
        raise HTTPException(status_code=400, detail="User is not a teacher")
    if db_user.is_active == False:
        raise HTTPException(status_code=400, detail="User is already paused")
    for assignment in db_user.assignments:
        crud.update_assignment(db=db, ass_id=assignment.id, status="PAU")
    return crud.update_user(db=db, user_id=teacher_id, is_active=False)

@app.delete("/admin/user/{user_id}/delete/", status_code=204)
def delete_user(user_id: int, current_user: Annotated[schemas.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    if current_user.user_type != "ADM":
        raise HTTPException(status_code=401, detail="User is not an admin", headers={"WWW-Authenticate": "Bearer"})
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.user_type == "ADM":
        raise HTTPException(status_code=400, detail="Admin cannot be deleted")
    for assignment in db_user.assignments:
        crud.delete_assignment(db=db, ass_id=assignment.id)
    crud.delete_user(db=db, user_id=user_id)
    return {"Deleted user: ": user_id}