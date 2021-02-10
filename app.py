
from flask import Flask, render_template, url_for, request       # Library Imports
import urllib
import sqlalchemy as db
from sqlalchemy import create_engine
import pandas as pd
import pyodbc


app = Flask(__name__)                                # define our application
   


SERVER = '@biservdev.utsarr.net'
DATABASE = 'IR_dataRequests'
DRIVER = 'ODBC Driver 17 for SQL Server'
USERNAME = 'utsarr\fts605'
PASSWORD = 'Rico99miguel1999_' 	

pyodbc.drivers()

engine = create_engine(f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}')
connection = engine.connect()

#cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER= '+SERVER+' ;DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)

#cnxn = pyodbc.connect('DRIVER={SQL Native Client};SERVER='+SERVER+';DATABASE='+ DATABASE+'; TRUSTED_CONNECTION = yes')


#cursor = cnxn.cursor()








@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)