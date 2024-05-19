# Tasks
In this document all the tasks regarding the project is listed and marked done or not.</br>
## API
- [ ] sketch features
- [ ] decide on a framework
- [ ] make login/user creation
- [ ] make admin endpoint
    - [ ] allow admin the change type of user
    - [ ] allow admin to delete user
    - [ ] allow admin to set user inactive
- [ ] make teacher endpoint
    - [ ] add assignment
    - [ ] stop and or remove assignment
    - [ ] pause assignment
    - [ ] edit assignment
    - [ ] add/remove students from an assignment
    - [ ] list student assignments (all and individual students)
    - [ ] stop/restart evaluation of assignment
    - [ ] extract logs of submissions
    - [ ] extract results of submissions
- [ ] make student endpoint
    - [ ] list submissions
    - [ ] submit submission
    - [ ] cancel submission if unprocessed/not started
    - [ ] view results of evaluation
- [ ] integrate imagebuilder
    - [ ] schedule tasks to start evaluations
    - [ ] schedule tasks to stop evaluations and read results
- [ ] connect to production db
- [ ] unittests for database queries

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
