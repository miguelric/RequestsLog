# OIR DATA REQUESTS LOG PORTAL

## Development and Documentation Notes


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

### Frameworks, dependencies, and helpful documentation
This is a Flask application that uses the Flask-SQLAlchemy extension (an ORM).

Flask Documentation: https://flask.palletsprojects.com/en/1.1.x/
Flask-SQLAlchemy Documentation: https://flask-sqlalchemy.palletsprojects.com/en/2.x/

This application also uses pyodbc (namely to connect Python to the SQL server).

More on pyodbc: https://code.google.com/archive/p/pyodbc/wikis/GettingStarted.wiki

More clarification: Pyodbc is a DBAPI layer to access ODBC databases, and SqlAlchemy lives on top of that and has two layers itself - core and ORM. Core (https://docs.sqlalchemy.org/en/13/core/) can be used to write SQL queries by building a Python expression instead of concatenating strings. ORM (https://docs.sqlalchemy.org/en/13/orm/) converts table data to standard Python objects.

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

When handling attributes using the 
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

---

### Site Base Layout and Jinja Template Basics
Flask uses the templating language Jinja, which allows for template inheritance: (https://flask.palletsprojects.com/en/1.1.x/patterns/templateinheritance/).

With this in mind, `site_base_layout.html` is the template that defines the base HTML skeleton for the rest of the child templates. The `render_template()` function invokes Jinja and gives the arguments for the templating engine to substitute `{{ ... }}` blocks with corresponding values. `{% ... %}` blocks are control (conditional) statements also supported by Jinja.

Child templates may inherit `site_base_layout.html` by a simple `{% extends "site_base_layout.html" %}`.
`block` statements are how Jinja knows how to combine the components of two templates.

In `site_base_layout.html`, static views take a path relative to whatever needs to be served (e.g. CSS files) using `url_for()`. With this, CSS can be propagated to the child templates.

The navigation bar will be displayed on the main pages of the application through template inheritance.

---

### Assigned Requests

This page displays all assigned requests.
From `app.py`, we render this page using 
```
return render_template("assignedRequests.html", df = df, db = db, analystList = analystList)
```
| Variables         | Description                         |
| ----------------- | ------------------------------------|
| `df`              | Set to a unique list of analyst names for using/testing graphs. No use in individual page. |
| `db`              | List of tuples representing all entries and metadata in dbo.requests |
| `analystList`     | List of tuples representing all entries and metadata in dbo.assignedTo |
| `a_fullname`      | set to value of 4th column (fullName) in dbo.assignedTo |
| `a_firstname`     | set to value of 2nd column (firstName) in dbo.assignedTo |
| `a_lastname`      | set to value of 3rd column (lastName) in dbo.assignedTo |
| `total_req`       | used to count the total number of requests for an analyst |
| `db_assignedTo`   | set to value of 17th column (assignedTo) in dbo.requests |
| `request_title`   | set to value of 14th column (rqstTitle) OR 11th column (rqstURL) in dbo.requests |


For sorting reference: https://jinja.palletsprojects.com/en/2.11.x/templates/#sort

Pseudocode structure:
```
    For each analyst in analystList, sorting by last name alphabetically, do
        Set a_fullname, a_firstname, and a_lastname to respective columns in dbo.assignedTo so that they're easier to keep track of.
    
        Set total_req to 0.

        For each entry in the table dbo.requests do
            If an analyst exists for the request (value of seventeenth column is not NULL), then set db_assignedTo to value.
        
                Split the first name and last name so we can match against firstName and lastName column in assignedTo table. 
        
                If either the full name matches the full analyst name
                OR the first name matches analyst[1] (a_firstname) AND last name matches analyst[2] (a_lastname), then count that request as being assigned to that analyst and increment their total_req by 1.
                End if
            End if
        End for

        For each entry in the table dbo.requests do 
            If an analyst exists for the request, then set db_assignedTo to value.
        
                Split the first name and last name so we can match against firstName and lastName column in assignedTo table. 
        
                If either the full name matches the full analyst name
                OR the first name matches analyst[1] (a_firstname) AND last name matches analyst[2] (a_lastname), then count that request as being assigned to that analyst and do

                    Set request_title to rqstTitle or rqstURL column. (the columns rqstTitle and rqstURL have been confused with each other in the original database, so we have to check which one to use).

                    Display all the information in accordian card.
                End if
            End if
        End for
    End for
```

---


### Unassigned Requests

---

### Due this Week

---

###  Status Update
