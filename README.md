# OIR DATA REQUESTS LOG PORTAL

## Development and Documentation Notes
<details open>
<summary>Table of Contents</summary>

- [Running the application using flask run](#s1)
- [Frameworks, dependencies, any clarifications on semantics, and helpful documentation](#s2)
- [About getting an existing database table and sessions](#s3)
- [How tables in the database are "read-in" and parsed](#s4)
- [Handling columns](#s5)
- [Site Base Layout and Jinja Template Basics](#s6)
- [Assigned Requests](#s7)
- [Unassigned Requests](#s8)
- [Form for an Unassigned Request](#s9)
- [Due this Week](#s10)
- [Status Update](#s11)
</details>

---

### Running the application using flask run <a name="s1"/>
This command is OK if accessing the app from the same computer. However, from another computer in the LAN, the access will fail. Flask will listen to 127.0.0.1, the loopback address, meaning it will only receive machine-local requests.

```
$ python -m flask run
```

To run with debugger and on localhost:3000. (Can also use a built-in server (app.run(host=...,port=...))for development, but for production, use a container.)

```
$ FLASK_DEBUG=1 python -m flask run -h localhost -p 3000
```

---

### Frameworks, dependencies, any clarifications on semantics, and helpful documentation <a name="s2"/>
This is a Flask application that uses the Flask-SQLAlchemy extension (an ORM).

Flask Documentation: https://flask.palletsprojects.com/en/1.1.x/
Flask-SQLAlchemy Documentation: https://flask-sqlalchemy.palletsprojects.com/en/2.x/

This application also uses pyodbc (namely to connect Python to the SQL server).

More on pyodbc: https://code.google.com/archive/p/pyodbc/wikis/GettingStarted.wiki

More clarification: Pyodbc is a DBAPI layer to access ODBC databases, and SqlAlchemy lives on top of that and has two layers itself - core and ORM. Core (https://docs.sqlalchemy.org/en/13/core/) can be used to write SQL queries by building a Python expression instead of concatenating strings. ORM (https://docs.sqlalchemy.org/en/13/orm/) converts table data to standard Python objects.

Now, technically, a row is not a record, a distinction not made well in some documentations. For this application, I might have included comments/code that seem to suggest that they're fully interchangeable here and there, but when an INSERT is performed, a *row* is inserted, and when a SELECT is performed, a *row* is retrieved. But the differences between row and record matter very little in practice.

Also helpful: CRUD using SQLAlchemy ORM: https://overiq.com/sqlalchemy-101/crud-using-sqlalchemy-orm/

---
### About getting an existing database table and sessions <a name="s3"/>
As the starting point for this Flask-SQLAlchemy application, the engine is configured in `app.py` (more about it here: https://docs.sqlalchemy.org/en/14/core/engines.html):
```
engine = sa.create_engine('mssql+pyodbc://BISERVDEV/IR_dataRequests?driver=SQL Server Native Client 11.0?Trusted_Connection=yes').connect()
```

Using SQLAlchemy ORM, we create the Session class using sessionmaker. Alternatively, you can create a session using... 
```
session = Session(bind=engine)
```
...but you would have to create it everytime you want to communicate with db. With sessionmaker (global scope), you can use... 
```
session = Session() 
```
...w/o arguments to instantiate the session as many times as you need. Remember: session = Session() everytime.

To reflect a database schema into ORM-style classes, we produce a declarative automap base. In `class db_table(Base):`, db_table is pre-declared for the 'requests' table, and I've set the primary key to requestId. If we don't set the primary key, this error will come up: "sqlalchemy.exc.ArgumentError: Mapper mapped class db_table->requests could not assemble any primary key columns for mapped table 'requests'"

Then the tables are reflected with `AutomapBase.prepare()`.
```
Base = automap_base()

class db_table(Base): 
    __tablename__ = 'requests'
    requestId = Column(String, primary_key=True)

Base.prepare(engine, reflect=True)
```

### How tables in the database are "read-in" and parsed <a name="s4"/>

In the most common scenario (may be all scenerios, actually), the entries from a specific table in the database will be stored as a list of tuples. Read more on Python list of tuples here: https://www.askpython.com/python/list/python-list-of-tuples

To show how it looks so you get the feel, the *first* row of the dbo.requests table is stored and would print to console as this:
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

### Handling columns <a name="s5"/>

![Columns in dbo.requests](/README-images/dbo.requests-columns.JPG)

Since the entries and their metadata of a specified database table are stored is list of tuples (i.e. `{% for x in db %}` is so that `x` represents a tuple), we can use the index operator `[]` to access an item in the tuple i.e. whatever column value of the row you want to access.

It's relevant to note that an alternative to indexing using `[]` is to do an attribute access (dot notation). It occasionally has its limitations (e.g. special column names, creating a new column won't be consistent with column in the case the column name is changed, won't work if you have spaces in the column name/if it's an integer etc), so indexing using `[]` seems to be preferable. If the original database table is edited so that the *order* of columns change, then it will pose a problem (so don't change the order of columns! - column *names* can be edited). If dot notation is desired as a better substitute (under the assumption that the column names in the database won't be changed, *and* you know what you're doing), then it's your discretion.

Also! I did use the dot notation in the update() function in `app.py`... this might be changed, but maybe not hah.

For example:
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

### Site Base Layout and Jinja Template Basics <a name="s6"/>
Flask uses the templating language Jinja, which allows for template inheritance: (https://flask.palletsprojects.com/en/1.1.x/patterns/templateinheritance/).

With this in mind, `site_base_layout.html` is the template that defines the base HTML skeleton for the rest of the child templates. The `render_template()` function invokes Jinja and gives the arguments for the templating engine to substitute `{{ ... }}` blocks with corresponding values. `{% ... %}` blocks are control (conditional) statements also supported by Jinja.

Child templates may inherit `site_base_layout.html` by a simple `{% extends "site_base_layout.html" %}`.
`block` statements are how Jinja knows how to combine the components of two templates.

In `site_base_layout.html`, static views take a path relative to whatever needs to be served (e.g. CSS files) using `url_for()`. With this, CSS can be propagated to the child templates.

The navigation bar will be displayed on the main pages of the application through template inheritance.

---

### Assigned Requests <a name="s7"/>

This page displays all assigned requests.
From `app.py`, we render this page using 
```
return render_template("assignedRequests.html", df = df, db = db, analystList = analystList)
```

**Variables**
| Variable         | Description                         |
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

**Pseudocode structure:**
```
    For each analyst in analystList, sorting by last name alphabetically, do
        Set a_fullname, a_firstname, and a_lastname to respective columns in dbo.assignedTo so that they're easier to keep track of.
    
        Set total_req to 0.

        For each request in the table dbo.requests do
            If an analyst exists for the request (value of seventeenth column is not NULL) do
                Set db_assignedTo to value of seventeeth column.
        
                Split the first name and last name so we can match against firstName and lastName column in assignedTo table. 
        
                If either the full name matches the full analyst name
                OR the first name matches analyst[1] (a_firstname) AND last name matches analyst[2] (a_lastname), then count that request as being assigned to that analyst and increment their total_req by 1.
                End if
            End if
        End for

        For each request in the table dbo.requests do 
            If an analyst exists for the request, do 
                Set db_assignedTo to value of seventeeth column.
        
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

### Unassigned Requests <a name="s8"/>

This page displays all unassigned requests.
From `app.py`, we render this page using 
```
return render_template("unassignedForm.html", df = df, db = db, formID = formID, analystList = analystList)
```

**Variables**

| Variable         | Description                         |
| ----------------- | ------------------------------------|
| `df`              | Set to a unique list of analyst names for using/testing graphs. No use in individual page. |
| `db`              | List of tuples representing all entries and metadata in dbo.requests |
| `analystList`     | List of tuples representing all entries and metadata in dbo.assignedTo |
| `unassignedID`    | Set to value of 2nd column (requestId) in dbo.assignedTo; used in `showForm()` function |


**Functions**

The `showForm()` function uses the `window.location` object to get the current page address (URL) and redirect the browser to a new page, specifically the respective form to a request. It uses `unassignedID`, which is the requestID, as the value to pass to the `form` parameter to associate the form and the request.

```
<script type="text/javascript">
	function showForm(unassignedID) {
		window.location = 'unassignedForm?form=' + unassignedID;
	}
</script>

<input type="button" name="theBvalue="Edit Form and Assign Analyst"
	onclick="showForm('{{x[1]}}');">
```

**Pseudocode structure:**
```
    For each request in the table dbo.requests do
        If an analyst DOES NOT exist for the request (value of seventeenth column is NULL) do
            Set request_title to rqstTitle or rqstURL column. (the columns rqstTitle and rqstURL have been confused with each other in the original database, so we have to check which one to use).

            Create the accordian card that displays information about the request.

            Create the button that redirects to the unassigned request form page (unassignedForm.html), passing the unassignedID of a respective request.
        End if
    End for

```
---

### Form for an Unassigned Request <a name="s9"/>
This page displays the form for a specific unassigned request, with editable fields to update the row in the database. It is redirected to from `unassigned.html`.

From `app.py`, we render this page using: 
```
return render_template("unassignedForm.html", df = df, db = db, formID = formID, analystList = analystList)
```

**Variables**
| Variable            | Description                         |
| ------------------- | ------------------------------------|
| `df`                | Set to a unique list of analyst names for using/testing graphs. No use in individual page. |
| `db`                | List of tuples representing all entries and metadata in dbo.requests |
| `analystList`       | List of tuples representing all entries and metadata in dbo.assignedTo |
| `formID`            | passed to parameter `form` in URL to associate a unique form to a specific request |
| `newAssignedAnalyst`| set to value of selected analyst in form |
| `newNotes`          | set to value of notes field in form |
| `request_title`     | set to value of 14th column (rqstTitle) OR 11th column (rqstURL) in dbo.requests |
| `db_table`          | name of model pre-declared for the 'requests' table - reference **About getting an existing database table and sessions** section |


**Functions**

In `app.py`, before rendering the page, the formID is retrived from the `form` parameter. This will associate a unique form to a specific requestId i.e. a request.
```
formID = request.args.get('form')
```

In `app.py`, the update() function, routed from clicking a "Submit" button on the form in `unassignedForm.html` will perform the actual inserting/updating of a row in the dbo.requests table.

In `unassignedForm.html`...
```
<form method="POST" action="./update">
```
...sends us to the function in `app.py`:
```
@app.route("/update", methods=["POST"])
def update():
    formID = request.form.get("formID")
    newAssignedAnalyst = request.form.get("newAssignedAnalyst")
    newNotes = request.form.get("newNotes")
    row = session.query(db_table).filter_by(requestId = formID).one()
    
    if newAssignedAnalyst == "None" or not newAssignedAnalyst:
        row.assignedTo = None
    else:
        row.assignedTo = newAssignedAnalyst
    
    if newNotes == "None" or not newNotes:
        row.notes = None
    else:
        row.notes = newNotes
    
    session.add(row)
    session.commit()    
    return redirect("/unassigned")
```
The various `request.form.get()` methods will retrieve form data, using them as new values for the columns, if they exist. The updated Python object will be added to the session and committed to session.

**Pseudocode structure:**
```
    For each request in the table dbo.requests do
        If the second column (requestId) matches formID (the id of the request that was clicked on from unassigned.html)
            Set request_title to rqstTitle or rqstURL column. (the columns rqstTitle and rqstURL have been confused with each other in the original database, so we have to check which one to use).

            Create the form, displaying information about the request along with editable field(s).

            Create a "submit" button that sends us to update() function, which handles the actual insert/update of a row in database - it will redirect back to unassigned.html
        End if
    End for
```

### Due this Week <a name="s10"/>

---

###  Status Update <a name="s11"/>
