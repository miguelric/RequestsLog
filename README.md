# OIR DATA REQUESTS LOG PORTAL

## Development and Documentation Notes (in process)

---

### Running the application using flask run
This command is OK if accessing the app from the same computer. However, from another computer in the LAN,
the access will fail. Flask will listen to 127.0.0.1, the loopback address, meaning it will only receive machine-local requests.

```
$ python -m flask run
```

To run with debugger and on localhost:3000. (Can also use a built-in server (app.run(host=...,port=...))for development, but for production, use a container.)

```
$ FLASK_DEBUG=1 python -m flask run -h localhost -p 3000
```

---

### How tables in the database are "read-in" and parsed

In the most common scenario (may be all scenerios, actually), the entries from a specific table in the database will be stored as a list of tuples. Read more on Python list of tuples here: https://www.askpython.com/python/list/python-list-of-tuples

To show how it looks so you get the feel, the *first* entry of the dbo.requests table is stored and would print to console as this:
![First entries of dbo.requests table](/README-images/print(db[0]).JPG)

...and *all* entries of the dbo.assignedTo table are stored as this:
![All entries of dbo.assignedTo table](/README-images/print(analystList).JPG)

By default, the entries will be sorted so that the highest id will be at the top, but you can sort the entries however using Python's `sorted()`; this is done in the individual html pages. Reference on sorting: https://jinja.palletsprojects.com/en/2.11.x/templates/#sort

The following code shows how the function will pass the entries of two tables to `assignedRequests.html` template (well, and a third list `df`, which at this time was used for working with graphs). It will then return the rendered version. 

Specifically, the two tables are dbo.requests and dbo.assignedTo. `SELECT *` will select all columns (though this may produce some unnecessary network load/query performance problems - it may be replaced by an explicit column list, but we need not worry about it now).

The `fetchall()` method will fetch all (or all remaining) rows of the query result set and returns a list of tuples.

```
@app.route('/assignedRequests')                                                   
def assignedRequests():

    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    dic = []
    for row in cursor.fetchall():
        dic.append(row)

    df = uniqueNames
    db = dic

    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    return render_template("assignedRequests.html", df = df, db = db, analystList = analystList)
```

---

### Handling columns

![Columns in dbo.requests](/README-images/dbo.requests-columns.JPG)

When handling attributes using the () 
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
