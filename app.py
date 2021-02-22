
from flask import Flask, render_template, url_for, request       # Library Imports
import urllib
import sqlalchemy as db
from sqlalchemy import create_engine
import pandas as pd
import pyodbc


app = Flask(__name__)                                # define our application
   


SERVER = '@biservdev.utsarr.net'
DATABASE = 'IR_dataRequests'
#DRIVER = 'ODBC Driver 17 for SQL Server'
#USERNAME = 'utsarr\fts605'
#PASSWORD = 'Rico99miguel1999_' 	

cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};""Server=BISERVDEV;""Database=IR_dataRequests;""Trusted_Connection=yes;")

cursor = cnxn.cursor()








@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)
cursor.execute("SELECT * from") 
row = cursor.fetchone() 
while row: 
    print(row[0])
    row = cursor.fetchone()



@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)