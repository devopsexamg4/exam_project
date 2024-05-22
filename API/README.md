# api
repo containg api service

Run following command to launch api in development mode: ```fastapi dev main.py```
To run in production mode: ```fastapi run main.py```

The API is meant to use environment variables to determine the database URL, but if they are not available, or one wishes to run it locally, uncomment line 16 & 17 in database.py, whilst commenting out line 19 & 20 in database.py

For documencation go to localhost:8000/docs

Documentation is only availalbe once api is running

To test the API, run command: ```pytest```