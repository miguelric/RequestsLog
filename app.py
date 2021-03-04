
from flask import Flask, render_template, url_for, request           # Library Imports
import sqlalchemy as sa
from sqlalchemy import create_engine
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

startDate = '2018/10/01'
endDate = '2019/10/01'
if datetime.date.today().isoweekday() == 1:
    print("it is monday and the date is")

    startDate = datetime.date.today()
    endDate = startDate + datetime.timedelta(6)
  
print(startDate)
print(endDate)


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
cursor.execute("SELECT * FROM [IR_dataRequests].[dbo].[requests] WHERE rqstStatus = 'Received' AND dueDate >= '"+ startDate + "' and dueDate <= '"+ endDate +"'")


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
uniqueNames = ['Brian Cordeau', 'Ashwin Jayagopal' , 'Fikrewold Bitew', "Jinny Case", 'Lauren Apgar', 'Mahmoud Abunawas' ,'Salma Ferdous']
numofAnalysts = len(uniqueNames)

print(numofAnalysts)










#plt.show()

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

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')




@app.route('/')                                                   # url mapping main page
def homepage():

    df = uniqueNames
    db = dic
 
    return render_template("index.html", df = df, db = db)


@app.route('/allRequests')                                                   # url mapping main page
def allRequests():

    df = uniqueNames
    db = dic
 
    return render_template("allRequests.html", df = df, db = db)



@app.route('/unassigned')                                                   # url mapping main page
def unassigned():

    df = uniqueNames
    db = dic
 
    return render_template("unassigned.html", df = df, db = db)




@app.route('/dueThisWeek')                                                   # url mapping main page
def dueThisWeek():

    df = uniqueNames
    db = thisWeekDict
 
    return render_template("dueThisWeek.html", df = df, db = db)





@app.route('/statusUpdate')                                                   # url mapping main page
def statusUpdate():

    
    return render_template("statusUpdate.html")







if __name__ == "__main__":                                        # Used for debugging
    app.run(debug=True)