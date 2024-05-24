# db
Contains the Files neccesary for the initialization of a postgresql database through a docker container. 

## Staring the DB service in development mode
1. In the DB directory
1. Build the image ```docker build -t [name of image] .```
1. run the container  
    2. ```docker run --name [name of container] -e POSTGRES_PASSWORD=[password] -p 5432:5432  -d [name of image]```
    2. Log into the database using the default values for user and database, which are both postgres
    2. ```docker exec -it [name of container] psql -U postgres -d postgres```
    2. Navigate around the database using psql commands `\d` to list databases and `\l` to show tables