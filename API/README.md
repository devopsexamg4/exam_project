# API
## Production mode
To run in production mode: ```fastapi run main.py```

## Development mode
Uncomment line 16 & 17 in database.py, whilst commenting out line 19 & 20 in database.py </br>
Run following command to launch api in development mode: ```fastapi dev main.py```

## Documentation
For documencation go to localhost:8000/docs </br>
Documentation is only availalbe once api is running

## Testing
It is a good idea to run the API test locally, to ensure that it runs correctly. To do so, refer to development mode. </br>
To test the API, run command: ```pytest ; rm sql_app.db```

The last part of the command isn't strictly needed, but it will clean up the local database created by running the test. </br>
This is also necessary if one wishes to run the test multiple times, as most of the tests will fail if there is a pre-existing local database. 