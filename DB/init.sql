-- Description: This file contains the SQL commands to create the tables of the postgresql database

SET TIME ZONE 'CET';

-- Assignments Table
CREATE TABLE "frontend_assignments" (
    "id" bigserial NOT NULL PRIMARY KEY, 
    "status" varchar(3) NOT NULL, 
    "maxmemory" integer NOT NULL CHECK ("maxmemory" >= 0), 
    "maxcpu" integer  NOT NULL CHECK ("maxcpu" >= 0), 
    "timer" bigint NOT NULL, 
    "start" timestamp NOT NULL, 
    "endtime" timestamp NOT NULL, 
    "dockerfile" varchar(100) NOT NULL, 
    "maxsubs" integer NOT NULL CHECK ("maxsubs" >= 0), 
    "image" text NOT NULL, 
    "title" text NOT NULL
    );


-- User Table
CREATE TABLE "frontend_user" (
    "id" bigserial NOT NULL PRIMARY KEY, 
    "password" varchar(128) NOT NULL, 
    "last_login" timestamp NULL, 
    "is_superuser" boolean NOT NULL, 
    "username" varchar(150) NOT NULL UNIQUE, 
    "first_name" varchar(150) NOT NULL, 
    "last_name" varchar(150) NOT NULL, 
    "email" varchar(254) NOT NULL, 
    "is_staff" boolean NOT NULL, 
    "is_active" boolean NOT NULL, 
    "date_joined" timestamp NOT NULL, 
    "user_type" varchar(3) NULL
    );

-- Student Assignment Submission Table
CREATE TABLE "frontend_studentsubmissions" (
    "id" bigserial NOT NULL PRIMARY KEY, 
    "File" varchar(100) NOT NULL, 
    "log" varchar(100) NULL, 
    "uploadtime" timestamp NOT NULL, 
    "assignment_id" bigint NULL REFERENCES "frontend_assignments" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "student_id" bigint NOT NULL REFERENCES "frontend_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "eval_job" text NOT NULL, 
    "status" VARCHAR(3) NOT NULL, 
    "result" varchar(100) NULL
    );


-- Many to Many Relationship between Users and Assignments
CREATE TABLE "frontend_user_assignments" (
    "id" bigserial NOT NULL PRIMARY KEY, 
    "user_id" bigint NOT NULL REFERENCES "frontend_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "assignments_id" bigint NOT NULL REFERENCES "frontend_assignments" ("id") DEFERRABLE INITIALLY DEFERRED
    );
