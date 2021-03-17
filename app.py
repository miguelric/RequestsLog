
from flask import Flask, render_template, url_for, request           # Library Imports
import sqlalchemy as sa
from sqlalchemy import create_engine
### New imports ###
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, sessionmaker, mapper
from flask import redirect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
######
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

app = Flask(__name__)                                                # define our application
   
# Connect to DB using pyodbc to get all data into a list
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};""Server=BISERVDEV;""Database=IR_dataRequests;""Trusted_Connection=yes;")
cursor = cnxn.cursor()
#cursor.execute("SELECT * FROM dbo.requests")



# Fetch ALL requests that are open (allRequests.html)
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


# update the assigned analyst - routed from unassignedForm.html
@app.route("/update", methods=["POST"])
def update():
    newAssignedAnalyst = request.form.get("newAssignedAnalyst")
    formID = request.form.get("formID")

    # Will print the raw SQL expression for querying database
    #print(session.query(db_table))
    
    # Find the record in the database matching the request ID

    # Unexpected behavior?
    #session.query(db_table).filter(db_table.requestId == 'formID').update({'assignedTo': newAssignedAnalyst})
    

    record = session.query(db_table).filter_by(requestId = formID).one()
    record.assignedTo = newAssignedAnalyst
    session.add(record)
    session.commit()
    
    return redirect("/unassigned")

#########################################


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
    my_path = 'barGraphs/'
    fig.savefig(os.path.join(my_path, name))   





#plt.show()
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
"""





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








@app.route('/')                                                   # url mapping main page
def homepage():

    # With the database being updated from within this app, as well as any queries/updates/deletes/adds that
    # happen through SSMS or other clients, it is safer to re-fetch the database on page load.
    # Re-fetch ALL requests that are open (allRequests.html)
    dic = []
    for row in cursor.fetchall():
        dic.append(row)

    df = uniqueNames
    db = dic

    df = uniqueNames
    db = dic
 
    return render_template("index.html", df = df, db = db)


@app.route('/allRequests')                                                   # url mapping main page
def allRequests():

    # Re-fetch ALL requests that are open (allRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    dic = []
    for row in cursor.fetchall():
        dic.append(row)

    df = uniqueNames
    db = dic
 
    return render_template("allRequests.html", df = df, db = db)



@app.route('/unassigned')                                                   # url mapping main page
def unassigned():

    # Re-fetch ALL requests that are open (allRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    dic = []
    for row in cursor.fetchall():
        dic.append(row)

    df = uniqueNames
    db = dic
 
    return render_template("unassigned.html", df = df, db = db)


@app.route('/unassignedForm')                                                   # url mapping main page
def unassignedForm():

    # Re-fetch ALL requests that are open (allRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    dic = []
    for row in cursor.fetchall():
        dic.append(row)

    df = uniqueNames
    db = dic
    formID = request.args.get('form')
 
    return render_template("unassignedForm.html", df = df, db = db, formID = formID)



@app.route('/dueThisWeek')                                                   # url mapping main page
def dueThisWeek():

    # Re-fetch ALL requests that are open (allRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    dic = []
    for row in cursor.fetchall():
        dic.append(row)

    df = uniqueNames
    db = thisWeekDict
 
    return render_template("dueThisWeek.html", df = df, db = db)





@app.route('/statusUpdate')                                                   # url mapping main page
def statusUpdate():

    # Re-fetch ALL requests that are open (allRequests.html)
    cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received';")
    dic = []
    for row in cursor.fetchall():
        dic.append(row)
    
    return render_template("statusUpdate.html")







if __name__ == "__main__":                                        # Used for debugging
    app.run(debug=True)