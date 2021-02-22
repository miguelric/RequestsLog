
from flask import Flask, render_template, url_for, request           # Library Imports
import sqlalchemy as sa
from sqlalchemy import create_engine
import pandas as pd
import pyodbc


app = Flask(__name__)                                                # define our application
   
# Connect to DB using pyodbc to get all data into a list
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};""Server=BISERVDEV;""Database=IR_dataRequests;""Trusted_Connection=yes;")
cursor = cnxn.cursor()
cursor.execute("SELECT * FROM dbo.requests")

dic = []
for row in cursor.fetchall():
    dic.append(row)



# Connect to DB using SQLAlchem in order to use Pandas
engine = sa.create_engine('mssql+pyodbc://BISERVDEV/IR_dataRequests?driver=SQL Server Native Client 11.0?Trusted_Connection=yes').connect()


temp = pd.read_sql_table('requests', engine)            
temp = pd.DataFrame(temp)
#print(temp) 



uniqueNames =  temp['assignedTo'].unique()                         # Find unique analyst names (currently doesnt work bc of extra analyst names in db)
uniqueNames = ['Brian Cordeau', 'Ashwin Jayagopal' , 'Fikrewold Bitew', "Jinny Case", 'Lauren Apgar', 'Mahmoud Abunawas' ,'Salma Ferdous']
numofAnalysts = len(uniqueNames)

print(numofAnalysts)



@app.route('/')                                                   # url mapping main page
def homepage():

    df = uniqueNames
    db = dic
 
    return render_template("index.html", df = df, db = db)



@app.route('/factbook')                                           # url mapping factbook
def factbook():
 
    return render_template("factbook_dashboard_ref.html")







if __name__ == "__main__":                                        # Used for debugging
    app.run(debug=True)