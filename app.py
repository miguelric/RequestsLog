
from flask import Flask, render_template, url_for, request       # Library Imports
import urllib
import sqlalchemy as sa
from sqlalchemy import create_engine
import pandas as pd
import pyodbc


app = Flask(__name__)                                # define our application
   

cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};""Server=BISERVDEV;""Database=IR_dataRequests;""Trusted_Connection=yes;")

cursor = cnxn.cursor()

cursor.execute("SELECT * FROM dbo.requests")

engine = sa.create_engine('mssql+pyodbc://BISERVDEV/IR_dataRequests?driver=SQL Server Native Client 11.0?Trusted_Connection=yes').connect()


dic = []
for row in cursor.fetchall():
    dic.append(row)

temp = pd.read_sql_table('requests', engine)            
temp = pd.DataFrame(temp)
#print(temp) 



uniqueNames =  temp['assignedTo'].unique()               # Find unique analyst names (currently doesnt work bc of extra analyst names in db)
uniqueNames = ['Brian Cordeau', 'Ashwin Jayagopal' , 'Fikrewold Bitew', "Jinny Case", 'Lauren Apgar', 'Mahmoud Abunawas' ,'Salma Ferdous']
numofAnalysts = len(uniqueNames)

print(numofAnalysts)

@app.route('/')                                  # url mapping
def homepage():
    df = uniqueNames
    db = dic
 
 
    return render_template("index.html", df = df, db = db)





if __name__ == "__main__":
    app.run(debug=True)