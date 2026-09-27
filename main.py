import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True) #app:"app.app:app" is used to run the API from the app.py file | Host is specifying the domain on which this server will run (0.0.0.0-Localhost) | port is the port number on which the server is hosted

# This main.py is a server runner file