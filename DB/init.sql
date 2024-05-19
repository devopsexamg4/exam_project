CREATE TYPE UserType AS ENUM ('Admin', 'Teacher', 'Student');

SET TIME ZONE 'CET';

CREATE TABLE Users (
        id serial PRIMARY KEY NOT NULL, 
        username VARCHAR(30) NOT NULL,
        usertype UserType NOT NULL,
        first_name VARCHAR(30) NOT NULL, 
        last_name VARCHAR(30) NOT NULL,
        password VARCHAR(30) NOT NULL, 
        email  VARCHAR(30),
        date_joined TIMESTAMP NOT NULL,
        is_active BOOLEAN NOT NULL,
        is_staff BOOLEAN NOT NULL,
        is_superuser BOOLEAN NOT NULL,
        last_login TIMESTAMP
    );

-- hidden or HID? 
CREATE TYPE STATUSTYPE AS ENUM ('Hidden', 'Active', 'Paused', 'Finished');

CREATE TABLE Assignments(
        id serial PRIMARY KEY NOT NULL,
        title VARCHAR(30) NOT NULL,
        status STATUSTYPE NOT NULL,
        maxmemory INT CHECK (maxmemory > 0),
        maxcpu INT  CHECK (maxcpu > 0),
        timer TIME NOT NULL,
        start TIMESTAMP,
        endtime TIMESTAMP,
        dockerfile VARCHAR(255) NOT NULL,
        maxsubs INT NOT NULL CHECK (maxsubs > 0),
        image VARCHAR(255) NOT NULL
    );

-- many to many relationship between users and assignments
CREATE TABLE UserAssignments (
    userID int REFERENCES Users(id),
    assID int REFERENCES Assignments(id),
    PRIMARY KEY (userID, AssID)
);


CREATE TYPE resstatus AS ENUM ('Finished', 'Pending', 'Running', 'Stopped');


CREATE TABLE StudentSubmissions(
        id serial PRIMARY KEY NOT NULL,
        student int REFERENCES Users(id),
        result VARCHAR(255) NOT NULL,
        File VARCHAR(255) NOT NULL,
        status resstatus NOT NULL,
        log VARCHAR(255),
        uploadtime TIMESTAMP,
        assignment int REFERENCES Assignments(id),
        eval_job VARCHAR(30)
    );