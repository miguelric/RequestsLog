from flask import Flask, render_template, url_for, request           # Library Imports
import sqlalchemy as sa
from sqlalchemy import and_
from sqlalchemy import create_engine
### New imports ###
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, sessionmaker, mapper
from flask import flash, redirect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from wtforms import Form, StringField, SelectField
from flask_table import Table, Col, ButtonCol
###################
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
import numpy as np

import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime
import os
"""
startDate = '2018/10/01'
endDate = '2019/10/01'
if datetime.date.today().isoweekday() == 1:
    print("it is monday and the date is")

    startDate = datetime.date.today()
    endDate = startDate + datetime.timedelta(6)
    nextWeek = endDate + datetime.timedelta(6)

  
print(startDate)
print(endDate)
print(nextWeek)
startDate = startDate.strftime("%Y-%m-%d")
endDate = endDate.strftime("%Y-%m-%d")
nextWeek = nextWeek.strftime("%Y-%m-%d")
"""

# Define application
app = Flask(__name__) 
# Used for flash() function
app.secret_key = '123' 

# Connect to DB using pyodbc to get all data into a list
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};""Server=BISERVDEV;""Database=IR_dataRequests;""Trusted_Connection=yes;")
cursor = cnxn.cursor()
#cursor.execute("SELECT * FROM dbo.requests")



# Fetch ALL requests that are open (assignedRequests.html)
cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")



dic = []
for row in cursor.fetchall():
    dic.append(row)




#Fetch ALL requests that are open this WEEK (dueThisWeek.html)
#cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received' AND dueDate >= '"+ startDate + "' and dueDate <= '"+ endDate +"'")


thisWeekDict = []
for row in cursor.fetchall():
    thisWeekDict.append(row)

#cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Open' AND WHERE A;")



# Connect to DB using SQLAlchem in order to use Pandas
engine = sa.create_engine('mssql+pyodbc://BISERVDEV/IR_dataRequests?driver=SQL Server Native Client 11.0?Trusted_Connection=yes').connect()


temp = pd.read_sql_table('requests', engine)            
temp = pd.DataFrame(temp)
#print(temp) 



uniqueNames =  temp['assignedTo'].unique()                         # Find unique analyst names (currently doesnt work bc of extra analyst names in db)
uniqueNames = ['Ashwin Jayagopal', 'Brian Cordeau', 'Fikrewold Bitew', 'Francisco Benavides', "Jinny Case", 'Lauren Apgar', 'Mahmoud Abunawas', 'Peter Nguyen', 'Scott Lehrman', 'Shanna Sherwood']
numofAnalysts = len(uniqueNames)



#weekly = temp[temp['dueDate'].between(startDate, endDate)]                 # Use after database is updated
#weekly = temp[temp['dueDate'].between('2010-04-12', '2018-06-12')]


# Obtain how many tasks this week , next week and later on for each analyst
myDict = {}

for x in uniqueNames:
    
    tasks = []
    analyst = temp.loc[temp['assignedTo'] == x]
    total = len(analyst)

    week = analyst.loc[analyst['dueDate'].between('2010-04-12', '2018-06-12', inclusive=False)]
    tasks.append(len(week))
    nextWeek = analyst.loc[analyst['dueDate'].between('2018-06-12', '2019-06-12', inclusive=False)]
    tasks.append(len(nextWeek))
    tasks.append(total - tasks[0]- tasks[1])
    myDict[x] = tasks




"""
for x in uniqueNames:
      
    tasks = []
    analyst = temp.loc[temp['assignedTo'] == x]
    total = len(analyst)

    week = analyst.loc[analyst['dueDate'].between(startDate, endDate, inclusive=False)]
    tasks.append(len(week))
    nextWeek = analyst.loc[analyst['dueDate'].between(endDate, nextWeek, inclusive=False)]
    tasks.append(len(nextWeek))
    tasks.append(total - tasks[0]- tasks[1])
    myDict[x] = tasks

print(myDict)
"""





#print(weekly)






# Using SQLAlchemy ORM
#########################################
# create the Session class using sessionmaker.
# Alternatively, you can create a session using session = Session(bind=engine),
# but you would have to create it everytime you want to communicate with db.
# With sessionmaker (global scope), you can use session = Session() w/o arguments
# to instantiate the session as many times as you need.
# Remember: session = Session() everytime.

Session = sessionmaker(bind=engine)
Base = automap_base()

class db_table(Base): 
#    __table__ = Base.metadata.tables['requests']
    __tablename__ = 'requests'
    requestId = Column(String, primary_key=True)

Base.prepare(engine, reflect=True)
session = Session()
#######################################




# Search functions
#######################################
# https://wtforms.readthedocs.io/en/2.3.x/fields/
class SearchForm(Form):
    search1 = StringField(label="Request Title")
    search2 = StringField(label="RequestID")
    search3 = StringField(label="Requestor")
    search4 = StringField(label="Requestor Affiliation")
    search5 = StringField(label="Assigned Analyst")

class Results(Table):
    #if rqstURL == "None" or not rqstURL:
    rqstURL = Col('Request URL (or Title)')
    #elif rqstTitle == "None" or not rqstTitle:
    rqstTitle = Col('Request Title')
    requestId = Col('Request Id')
    dateSubmitted = Col('Date Submitted')
    dueDate = Col('Due Date')
    rqstBy = Col('Requested By')
    rqstBy_title = Col('Requestor Title')
    rqstBy_affiliation = Col('Requestor Affiliation')
    rqstBy_phone = Col('Requestor Phone')
    rqstBy_email = Col('Requestor Email')
    assignedTo = Col('Assigned to')
    rqstPrioity = Col('Request Priority')
    rqstStatus = Col('Request Status')
    form = ButtonCol('Form to Update Request', 'statusUpdateForm', url_kwargs=dict(form='requestId'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    search = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('search.html', form=search)

########################################
@app.route('/results')
def search_results(search):
    results = []
    filters = []
    title_input = search.data['search1']
    requestId_input = search.data['search2']
    requestor_input = search.data['search3']
    affiliation_input = search.data['search4']
    assignedto_input = search.data['search5']
    filters.append((db_table.rqstStatus == 'Under Review') | (db_table.rqstStatus == "Received"))
    if title_input:
        filters.append(db_table.rqstURL.contains(title_input) | db_table.rqstBy_title.contains(title_input))
    if requestId_input:
        filters.append(db_table.requestId.contains(requestId_input))
    if requestor_input:
        filters.append(db_table.rqstBy.contains(requestor_input))
    if affiliation_input:
        filters.append(db_table.rqstBy_affiliation.contains(affiliation_input))
    if assignedto_input:
        filters.append(db_table.assignedTo.contains(assignedto_input))

    results = session.query(db_table).filter(and_(*filters)).all()
    
    if not results:
        flash('No results found!')
        #print('No results found!')
        return redirect('/search')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', results=results, table=table)
        #return render_template('results.html', results=results)

########################################




# Update functions
########################################
# update the assigned analyst - routed from unassignedForm.html
@app.route("/updateUnassigned", methods=["POST"])
def updateUnassigned():
    formID = request.form.get("formID")
    newAssignedAnalyst = request.form.get("newAssignedAnalyst")
    newStatus = request.form.get("newStatus")
    newPriority = request.form.get("newPriority")
    newNotes = request.form.get("newNotes")

    # Will print the raw SQL expression for querying database
    #print(session.query(db_table))
    
    # Find the record in the database matching the request ID

    # Unexpected behavior?
    #session.query(db_table).filter(db_table.requestId == 'formID').updateUnassigned({'assignedTo': newAssignedAnalyst})
    
    
    row = session.query(db_table).filter_by(requestId = formID).one()
    
    if newAssignedAnalyst == "None" or not newAssignedAnalyst:
        row.assignedTo = None
    else:
        row.assignedTo = newAssignedAnalyst
    
    if newStatus == "None" or not newStatus:
        row.rqstStatus = None
    else:
        row.rqstStatus = newStatus
    
    if newPriority == "None" or not newPriority:
        row.rqstPrioity = None
    else:
        row.rqstPrioity = newPriority
    
    if newNotes == "None" or not newNotes:
        row.notes = None
    else:
        row.notes = newNotes
    
    session.add(row)
    '''
    sql = "UPDATE requests SET assignedTo = ?, notes = ? WHERE requestID = ?"
    cursor.execute(sql, newAssignedAnalyst, newNotes, formID)
    '''
    session.commit()

    
    
    return redirect("/unassigned")

# update the status/deadline - routed from statusUpdateForm.html
@app.route("/updateStatus", methods=["POST"])
def updateStatus():
    formID = request.form.get("formID")
    newStatus = request.form.get("newStatus")
    newPriority = request.form.get("newPriority")
    newDeadline = request.form.get("newDeadline")
    newNotes = request.form.get("newNotes")
    
    row = session.query(db_table).filter_by(requestId = formID).one()
    

    if newStatus == "None" or not newStatus:
        row.rqstStatus = None
    else:
        row.rqstStatus = newStatus
    
    if newPriority == "None" or not newPriority:
        row.rqstPrioity = None
    else:
        row.rqstPrioity = newPriority
    
    if newDeadline == "None" or not newDeadline:
        row.dueDate = None
    else:
        row.dueDate = newDeadline
    
    if newNotes == "None" or not newNotes:
        row.notes = None
    else:
        row.notes = newNotes
    
    session.add(row)
    '''
    sql = "UPDATE requests SET assignedTo = ?, notes = ? WHERE requestID = ?"
    cursor.execute(sql, newAssignedAnalyst, newNotes, formID)
    '''
    session.commit()

    
    return redirect("/statusUpdate")

#########################################


'''
my_path = 'static/barGraphs/'

# Export bar graph for each analyst to barGraphs folder
for x in myDict:
    # Test Data
    names = ['This Week', 'Next Week', 'Other']
    analyst = x
    values =  myDict[analyst]

    #Creating Graph
    fig = plt.figure(figsize=(15,5))
    axis = fig.add_subplot(111)

    axis.bar(names, values, color='#ff8c00', label = 'Total Requests', width = .7, linewidth = .6, edgecolor = 'black') #orange

    axis.set_xlabel("")
    axis.set_ylabel("Amount of Requests")

    axis.spines['right'].set_visible(False)
    axis.spines['top'].set_visible(False)
    axis.tick_params(bottom=False)   
    axis.set_title('Requests for ' + analyst)
    name = analyst + ".png"
    fig.savefig(os.path.join(my_path, name))   






# Exporting main graph into barGraphs directory
uniqueNames = ['Ashwin', 'Brian', 'Fikrewold', 'Francisco', "Jinny", 'Lauren', 'Mahmoud', 'Peter', 'Scott', 'Shanna']
total =     [5, 6, 15, 22, 24, 8, 11, 1, 4, 2]
thisWeek =  [1, 2, 7, 9, 6, 2, 4, 0, 1, 0]

fig = plt.figure(figsize=(15,5))
axis = fig.add_subplot(111)

axis.bar(uniqueNames, total, color='#ff8c00', label = 'Total Requests', width = .7, linewidth = .6, edgecolor = 'black') #orange
axis.bar(uniqueNames, thisWeek, color='#002fa7', label = 'Requests this Week', width = .7, linewidth = .6, edgecolor = 'black') #navy

axis.set_xlabel("")
axis.set_ylabel("Amount of Requests")

axis.spines['right'].set_visible(False)
axis.spines['top'].set_visible(False)
axis.tick_params(bottom=False)   

axis.legend(frameon = False)

fig.savefig(os.path.join(my_path, 'mainGraph'))  












# Old way of importing graphs into website
"""
def create_figure():
    # Test Data
    uniqueNames = ['Ashwin', 'Brian', 'Fikrewold', 'Francisco', "Jinny", 'Lauren', 'Mahmoud', 'Peter', 'Scott', 'Shanna']
    total =     [5, 6, 15, 22, 24, 8, 11, 1, 4, 2]
    thisWeek =  [1, 2, 7, 9, 6, 2, 4, 0, 1, 0]

    #Creating Graph
    fig = plt.figure(figsize=(15,5))
    axis = fig.add_subplot(111)
  
    axis.bar(uniqueNames, total, color='#ff8c00', label = 'Total Requests', width = .7, linewidth = .6, edgecolor = 'black') #orange
    axis.bar(uniqueNames, thisWeek, color='#002fa7', label = 'Requests this Week', width = .7, linewidth = .6, edgecolor = 'black') #navy

    axis.set_xlabel("")
    axis.set_ylabel("Amount of Requests")

    axis.spines['right'].set_visible(False)
    axis.spines['top'].set_visible(False)
    axis.tick_params(bottom=False)   
    axis.legend(frameon = False)
    return fig

# CHANGE THIS TO CHANGE GRAPH TO SPECIFIC ANALYST
chosenAnalyst = uniqueNames[4]
def testFig(x):
    print(myDict)
    # Test Data
    names = ['This Week', 'Next Week', 'Other']
    analyst = x
    values =  myDict[analyst]

    #Creating Graph
    fig = plt.figure(figsize=(15,5))
    axis = fig.add_subplot(111)
  
    axis.bar(names, values, color='#ff8c00', label = 'Total Requests', width = .7, linewidth = .6, edgecolor = 'black') #orange

    axis.set_xlabel("")
    axis.set_ylabel("Amount of Requests")

    axis.spines['right'].set_visible(False)
    axis.spines['top'].set_visible(False)
    axis.tick_params(bottom=False)   
    axis.set_title('Requests for ' + analyst)

    return fig

@app.route('/plot.png')
def plot_png():
    #fig = create_figure()
    fig = testFig(chosenAnalyst)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
"""

'''

# URL Routes
###################################
@app.route('/')
def homepage():

    # With the database being updated from within this app, as well as any queries/updates/deletes/adds that
    # happen through SSMS or other clients, it is safer to re-fetch the database on page load.
    # fetch ALL requests that are open
    db = []
    for row in cursor.fetchall():
        db.append(row)
 
    return render_template("index.html", db = db)


@app.route('/assignedRequests')
def assignedRequests():

    # fetch ALL requests that are received (assignedRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    db = []
    for row in cursor.fetchall():
        db.append(row)

    # fetch ALL requests that are under review (assignedRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Under Review';")
    reviewdb = []
    for row in cursor.fetchall():
        reviewdb.append(row)

    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)


    return render_template("assignedRequests.html", db = db, reviewdb = reviewdb, analystList = analystList, prioritydb = prioritydb)



@app.route('/unassigned')                                                  
def unassigned():

    # fetch ALL requests that are received
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    db = []
    for row in cursor.fetchall():
        db.append(row)

    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    # fetch ALL requests that are under review AND received
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Under Review' OR rqstStatus = 'Received';")
    db_and_reviewdb = []
    for row in cursor.fetchall():
        db_and_reviewdb.append(row)

    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)

    return render_template("unassigned.html", db = db, analystList = analystList, db_and_reviewdb = db_and_reviewdb, prioritydb = prioritydb)


@app.route('/unassignedForm')                                                  
def unassignedForm():

    # fetch ALL requests that are received
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    db = []
    for row in cursor.fetchall():
        db.append(row)

    formID = request.args.get('form')
 
    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)

    # fetch the status code descriptions from the statusCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[statusCode]")
    statusdb = []
    for row in cursor.fetchall():
        statusdb.append(row)

    return render_template("unassignedForm.html", db = db, formID = formID, analystList = analystList, prioritydb = prioritydb, statusdb = statusdb)



@app.route('/dueThisWeek')                                                  
def dueThisWeek():

    # fetch ALL requests that are received
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    db = []
    for row in cursor.fetchall():
        db.append(row)

    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    current_date = datetime.date.today()
    #print(current_date)

    # fetch the requests with "Received" status that are due in some range from current date/time
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received' AND DATEDIFF(DAY, dueDate, GETDATE()) >= 0 AND DATEDIFF(DAY, dueDate, GETDATE()) <= 900;")
    due_this_week_db = []
    for row in cursor.fetchall():
        due_this_week_db.append(row)
    
    # fetch the requests with "Under Review" status that are due in some range from current date/time
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Under Review' AND DATEDIFF(DAY, dueDate, GETDATE()) >= 0 AND DATEDIFF(DAY, dueDate, GETDATE()) <= 900;")
    due_this_week_reviewdb = []
    for row in cursor.fetchall():
        due_this_week_reviewdb.append(row)

    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)
 
    return render_template("dueThisWeek.html", db = db, analystList = analystList, current_date = current_date, due_this_week_db = due_this_week_db, due_this_week_reviewdb = due_this_week_reviewdb, prioritydb = prioritydb)





@app.route('/statusUpdate')
def statusUpdate():

    # fetch ALL requests that are received
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    db = []
    for row in cursor.fetchall():
        db.append(row)

    # fetch ALL requests that are under review
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Under Review';")
    reviewdb = []
    for row in cursor.fetchall():
        reviewdb.append(row)


    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)


    return render_template("statusUpdate.html", db = db, reviewdb = reviewdb, analystList = analystList, prioritydb = prioritydb)



@app.route('/statusUpdateForm', methods=['GET', 'POST'])                                            
def statusUpdateForm():

    
    formID = request.args.get('form')

    # fetch ALL requests that are under review AND received
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Under Review' OR rqstStatus = 'Received';")
    db_and_reviewdb = []
    for row in cursor.fetchall():
        db_and_reviewdb.append(row)
 
    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)

    # fetch the status code descriptions from the statusCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[statusCode]")
    statusdb = []
    for row in cursor.fetchall():
        statusdb.append(row)

    return render_template("statusUpdateForm.html", db_and_reviewdb = db_and_reviewdb, formID = formID, prioritydb = prioritydb, statusdb = statusdb)



@app.route('/completedRequests')                                                  
def completedRequests():

    # fetch ALL requests that are COMPLETED
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Completed';")
    completeddb = []
    for row in cursor.fetchall():
        completeddb.append(row)

    # fetch ALL the analysts from the assignedTo table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[assignedTo]")
    analystList = []
    for row in cursor.fetchall():
        analystList.append(row)

    # fetch the priority code descriptions from the priorityCode table
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[priorityCode]")
    prioritydb = []
    for row in cursor.fetchall():
        prioritydb.append(row)


    return render_template("completedRequests.html", completeddb = completeddb, analystList = analystList, prioritydb = prioritydb)


################################


if __name__ == "__main__":
    app.run(debug=True)