from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import conlist

import datetime
import io
import csv
from zipfile import ZipFile

import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Login is not finished at all
"""@app.get("/login/", response_model=schemas.User) # return to this function in the future, once OAuth2 has been looked at: https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/
def login(user_name: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=user_name)
    if not db_user:
        raise HTTPException(status_code=404, detail="User with that name not found")
    if db_user.password != password: # this line will probably need to change once hashing has been implemented
        raise HTTPException(status_code=400, detail="Incorrect password")
    return db_user"""

# student endpoints: 

@app.post("/student/create/", response_model=schemas.User)
def create_profile_student(student: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=student.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user2 = crud.get_user_by_email(db, email=student.email)
    if db_user2:
        raise HTTPException(status_code=400, detail="Email already registered")
    if student.user_type != schemas.UserType.STUDENT:
        raise HTTPException(status_code=400, detail="User type must be student")
    return crud.create_user(db=db, user=student)

@app.get("/student/{student_id}/assignments")
def get_assignments(student_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.assignments

@app.get("/student/assignments/{assignment_id}")
def get_assignment_status(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return db_assignment.status

@app.delete("/student/assignments/{student_id}/{submission_id}")
def delete_submission(student_id: int, submission_id: int, db: Session = Depends(get_db)):
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if db_submission.submitter.user_id != student_id:
        raise HTTPException(status_code=401, detail="Submission not owned by student")
    if db_submission.result != models.Result.NOTRUN:
        raise HTTPException(status_code=400, detail="Submission being processed")
    crud.delete_submission(db, sub_id=submission_id)
    return {"Deleted submission: ": submission_id}

@app.post("/student/assignments/sumbit/{assignment_id}/{student_id}")
def submit_solution(assignment_id: int, student_id: int, submission: schemas.StudentSubmissionCreate, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment")
    return crud.create_submission(db=db, submission=submission, assignment_id=assignment_id, student_id=student_id)

# teacher endpoints: 

@app.post("/teacher/assignment/")
def add_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    return crud.create_assignment(db=db, assignment=assignment)

@app.patch("/teacher/assignment/{assignment_id}")
def update_assignment(assignment_id: int, dockerfile: str | None = None, status: models.Status | None = None, max_memory: int | None = None, max_CPU: int | None = None, start: datetime.datetime | None = None, end: datetime.datetime | None = None, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return crud.update_assignment(db=db, assignment=db_assignment, dockerfile=dockerfile, status=status, max_memory=max_memory, max_CPU=max_CPU, start=start, end=end)

@app.patch("/teacher/assignment/{assignment_id}/pause")
def pause_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if db_assignment.status == models.Status.PAUSED:
        raise HTTPException(status_code=400, detail="Assignment is already paused")
    return crud.update_assignment(db=db, ass_id=assignment_id, status=models.Status.PAUSED)

@app.delete("/teacher/assignment/{assignment_id}/delete")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    crud.delete_assignment(db, ass_id=assignment_id)
    return {"Deleted assignment: ": assignment_id}

@app.patch("/teacher/assignment/{assignment_id}/remove-student/")
def remove_student_from_assignment(assignment_id: int, student_ids: conlist(int, min_length=1), db: Session = Depends(get_db)):
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
def add_student_to_assignment(assignment_id: int, student_ids: conlist(int, min_length=1), db: Session = Depends(get_db)):
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
def get_student_submissions(assignment_id: int, student_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment")
    return db.query(models.StudentSubmissions).filter(models.StudentSubmissions.submitter_id == student_id).filter(models.StudentSubmissions.assignment_id == assignment_id).all()

@app.get("/teacher/submission/{submission_id}/outcome/")
def get_submission_outcome(submission_id: int, db: Session = Depends(get_db)):
    db_submission = crud.get_submission(db, sub_id=submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    db_assignment = crud.get_assignment(db, ass_id=db_submission.assignment_id)
    return {db_assignment.status, db_submission.log_file, db_submission.result} # is the status of a submission the status of the assignment?

# here should be an endpoint for the teacher to 'trigger the re-evaluation of the submission'

# here should be an endpoint for the teacher to stop evaluation of submission

# here should be an endpoint for the teacher to stop evaluations of all submissions under an assignment

@app.get("/teacher/assignment/{assignment_id}/submission-logs/")
def get_assignment_submission_logs(assignment_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for submission in db_assignment.submissions:
            zip_file.write(submission.log_file, arcname=submission.log_file)
    zip_buffer.seek(0)
    return zip_buffer

@app.get("/teacher/assignment/{assignment_id}/student/{student_id}/submission-logs")
def get_assignment_student_submission_logs(assignment_id: int, student_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment")
    
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for submission in db_assignment.submissions:
            if submission.submitter_id == student_id:
                zip_file.write(submission.log_file, arcname=submission.log_file)
    zip_buffer.seek(0)
    return zip_buffer

@app.get("/teacher/assignment/{assignment_id}/submissions-metadata/")
def get_assignment_submissions_metadata(assignment_id: int, db: Session = Depends(get_db)):
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
        writer = csv.write(csvfile)
        writer.writerow(["Contributor Name", "Contributor Email", "Submission ID", "Upload Time", "Result"])
        for row in row_data:
            writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer

# end point that does the same as the above but for one user
@app.get("/teacher/assignment/{assignment_id}/student/{student_id}/submissions-metadata/")
def get_assignment_student_submissions_metadata(assignment_id: int, student_id: int, db: Session = Depends(get_db)):
    db_assignment = crud.get_assignment(db, ass_id=assignment_id)
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db_user = crud.get_user(db, user_id=student_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_assignment not in db_user.assignments:
        raise HTTPException(status_code=401, detail="User does not have access to this assignment")
    
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
        writer = csv.write(csvfile)
        writer.writerow(["Contributor Name", "Contributor Email", "Submission ID", "Upload Time", "Result"])
        for row in row_data:
            writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer

# administrator endpoints: 

@app.post("/admin/add-teacher", response_model=schemas.User)
def add_teacher(teacher: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=teacher.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user2 = crud.get_user_by_name(db, user_name=teacher.user_name)
    if db_user2:
        raise HTTPException(status_code=400, detail="Username already registered")
    if teacher.user_type != schemas.UserType.TEACHER:
        raise HTTPException(status_code=400, detail="User type must be teacher")
    return crud.create_user(db=db, user=teacher)

@app.patch("/admin/teacher/{teacher_id}/pause")
def pause_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=teacher_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.user_type != schemas.UserType.TEACHER:
        raise HTTPException(status_code=400, detail="User is not a teacher")
    if db_user.is_active == False:
        raise HTTPException(status_code=400, detail="User is already paused")
    return crud.update_user(db=db, user_id=teacher_id, is_active=False)

@app.delete("/admin/user/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.user_type == schemas.UserType.ADMIN:
        raise HTTPException(status_code=400, detail="Admin cannot be deleted")
    return crud.delete_user(db=db, user_id=user_id)