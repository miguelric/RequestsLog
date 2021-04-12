# OIR DATA REQUESTS LOG PORTAL
### Development and Documentation Notes (in process)


##### Running the application using flask run
This command is OK if accessing the app from the same computer. However, from another computer in the LAN,
the access will fail. Flask will listen to 127.0.0.1, the loopback address, meaning it will only receive machine-local requests.

```
$ python -m flask run
```

To run with debugger and on localhost:3000. (Can also use a built-in server (app.run(host=...,port=...))for development, but for production, use a container.)

```
$ FLASK_DEBUG=1 python -m flask run -h localhost -p 3000
```


