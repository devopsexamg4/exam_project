# Tasks
In this document all the tasks regarding the project is listed and marked done or not.</br>
## API
### Endpoints
#### Student
- [x] Create profile
- [x] Log into the system
- [x] Get list of own assignments
- [ ] Submit a solution to an assignment
- [x] Check evaluation of assignment
- [x] Cancel submission if not processed
- [x] See results of assignment

#### Teacher
- [x] Add an assignment
- [x] Update configuration information of assignment
- [x] Pause an assignment
- [x] Delete an assignment
- [x] Add or remove student(s) from assignment
- [x] Get list of submissions from given student & assignment
- [x] Get metadata about a submission
- [ ] Trigger re-evaluation of assignment
- [ ] Stop evaluation of assignment
- [ ] Stop evaluation of all submissions to an assignment
- [x] Get all logs of all submissions to an assignment
- [x] Extract metadata about all submissions to an assignment
- [x] Extract all submission logs for a single student from an assignment in a zip file
- [x] Extract metadata about all submissions from a given student to an assignment

#### Admin
- [x] Add a teacher
- [ ] Pause a teacher
    - Teacher can be paused, but currently it does not pause their assignments
- [x] Delete a student or teacher

### Testing
#### Student
- [x] Create profile
- [x] Log into the system
- [x] Get list of own assignments
- [ ] Submit a solution to an assignment
- [ ] Check evaluation of assignment
- [ ] Cancel submission if not processed
- [ ] See results of assignment

#### Teacher
- [ ] Add an assignment
- [ ] Update configuration information of assignment
- [ ] Pause an assignment
- [ ] Delete an assignment
- [ ] Add or remove student(s) from assignment
- [ ] Get list of submissions from given student & assignment
- [ ] Get metadata about a submission
- [ ] Trigger re-evaluation of assignment
- [ ] Stop evaluation of assignment
- [ ] Stop evaluation of all submissions to an assignment
- [ ] Get all logs of all submissions to an assignment
- [ ] Extract metadata about all submissions to an assignment
- [ ] Extract all submission logs for a single student from an assignment in a zip file
- [ ] Extract metadata about all submissions from a given student to an assignment

#### Admin
- [ ] Add a teacher
- [ ] Pause a teacher
- [ ] Delete a student or teacher

### 

## Database
- [x] Design entities and relations
- [x] decide on a DBMS
- [x] Implement DBMS in a way that allows deployment on a generic kubernetes cluster

## GUI
- [x] sketch features of individual pages
- [x] decide on a framework
- [x] make login/user creation
- [x] make admin page
    - [x] allow admin the change type of user
    - [x] allow admin to delete user
    - [x] allow admin to set user inactive
    - [ ] create dashborad for admin to view status of system
- [x] make teacher page
    - [x] add assignment
    - [x] stop and or remove assignment
    - [x] pause assignment
    - [x] edit assignment
    - [x] add/remove students from an assignment
    - [x] list student assignments (all and individual students)
    - [x] stop/restart evaluation of assignment
    - [x] extract logs of submissions
    - [x] extract results of submissions
- [x] make student page
    - [x] list submissions
    - [x] submit submission(?)
    - [x] cancel submission if unprocessed/not started
    - [x] view results of evaluation
- [x] integrate imagebuilder
    - [x] schedule tasks to start evaluations
    - [x] schedule tasks to stop evaluations and read results
- [ ] connect to production db
- [ ] unittests for database queries
- [ ] beautify pages

## Deployment
- [ ] containerize API
- [x] containerize GUI
- [x] containerize DB
- [x] configure persistent storage
- [x] configure reverse proxy
    - [x] (optional) get domain
        - [x] get certificate
    - [x] install reverse proxy
- [ ] store secrets in a safe manner

## Pipeline
- [ ] set up automatic deployment
- [ ] set up automatic unittests
- [ ] set up automatic integration tests
- [ ] set up automatic code analysis

## Cluster