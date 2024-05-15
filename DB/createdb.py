import psycopg2

# parameters for connecting
params = {
    "host": "localhost",
    "port": 5432,
    # "dbname": "test",
    "user": "postgres",
    "password": "12345"
    # "sslmode": "verify-ca",
    # "sslcert": "/etc/ssl/server.crt",
    # "sslkey": "/etc/ssl/server.key"
}

# establish connection
conn = psycopg2.connect(**params)

cur = conn.cursor()
conn.autocommit = True


cur.execute("SELECT version()")
version = cur.fetchone()
print(f"Postgres version: {version}")

# # create user db
# user = ''' CREATE database users ''';

 
# # executing above query
# cur.execute(user)

# # create assignment db
# assgn = ''' CREATE database assingments ''';
# cur.execute(assgn)



# # create StudentSubmissions db
# submissions = ''' CREATE database submissions ''';
# cur.execute(submissions)




cur.close()
conn.close()

# connect to the User database 
params["dbname"] = 'users'
conn = psycopg2.connect(**params)
conn.autocommit = True

cur = conn.cursor()

type = ''' CREATE TYPE UserType AS ENUM ('Admin', 'Teacher', 'Student') '''

# cur.execute(type)

# create UserTable in user db
user_table = ''' 
    CREATE TABLE UserTable (
        UserID INT PRIMARY KEY NOT NULL, 
        UserName VARCHAR(30) NOT NULL, 
        Password VARCHAR(30) NOT NULL, 
        UserType UserType NOT NULL, 
        Email  VARCHAR(30)
    )
'''
# cur.execute(user_table)

# commit the changes
# conn.commit()

cur.close()
conn.close()


# # connect to the Assignments database 
params["dbname"] = 'assingments'
conn = psycopg2.connect(**params)
conn.autocommit = True
cur = conn.cursor()


time ='''SET TIME ZONE 'CET' '''
cur.execute(time)

statustype = ''' CREATE TYPE STATUSTYPE AS ENUM ('Hidden', 'active', 'paused', 'finished') '''

cur.execute(statustype)

# # create AssignmentsTable in user db
ass_table = ''' 
    CREATE TABLE AssTable(
        AssID INT PRIMARY KEY NOT NULL,
        Dockerfile VARCHAR(30) NOT NULL,
        Status STATUSTYPE NOT NULL,
        MaxMemory INT,
        MaxCPU INT,
        Starting TIMESTAMP,
        Ending TIMESTAMP,
        Timer TIME NOT NULL

    )
'''
cur.execute(ass_table)
# # commit the changes
# conn.commit()

cur.close()
conn.close()



# connect to the Submissions database 
params["dbname"] = 'submissions'
conn = psycopg2.connect(**params)
conn.autocommit = True
cur = conn.cursor()



res = ''' CREATE TYPE RES AS ENUM ('passed', 'failed', 'notRun') '''

cur.execute(res)


# create SubmissionsTable in user db
sub_table = ''' 
    CREATE TABLE SubTable(
        SubID INT PRIMARY KEY NOT NULL,
        File VARCHAR(30) NOT NULL,
        Result RES NOT NULL,
        Logfile VARCHAR(30),
        UploadTime TIMESTAMP
    ) 
'''

cur.execute(sub_table)

# # commit the changes
# conn.commit()

cur.close()
conn.close()