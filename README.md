# OIR DATA REQUESTS LOG PORTAL

## Development and Documentation Notes (in process)

#### Running the application using flask run
This command is OK if accessing the app from the same computer. However, from another computer in the LAN,
the access will fail. Flask will listen to 127.0.0.1, the loopback address, meaning it will only receive machine-local requests.

```
$ python -m flask run
```

To run with debugger and on localhost:3000. (Can also use a built-in server (app.run(host=...,port=...))for development, but for production, use a container.)

```
$ FLASK_DEBUG=1 python -m flask run -h localhost -p 3000
```

### Handling columns

![Columns in dbo.requests](/README-images/dbo.requests-columns.png)

When 
```
<!--For fetching rqstTitle-->
{% if x[13] != None %}
```
...may be replaced with:
```
<!--For fetching rqstTitle-->
{% if x.rqstTitle != None %}
```

Along the same lines, the following statement...
```
<label for="description"><span>Description:</span></label><textarea id="description"
class="readonly-textarea-field" readonly>{{x[11]}}</textarea>
```
..may be replaced with:
```
<label for="description"><span>Description:</span></label><textarea id="description"
class="readonly-textarea-field" readonly>{{x.rqstBy_description}}</textarea>
```
