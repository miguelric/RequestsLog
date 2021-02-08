
from flask import Flask, render_template, url_for, request       # Library Imports
import urllib
import sqlalchemy as db
from sqlalchemy import create_engine
import pandas as pd
import pyodbc


app = Flask(__name__)                                # define our application
   


SERVER = '@biservdev.utsarr.net'
DATABASE = 'IR_dataRequests'
DRIVER = 'SQL Server Native Client 11.0'
USERNAME = 'utsarr\fts605'
PASSWORD = 'Rico99miguel1999_' 	

#engine = create_engine(f'mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}')
#connection = engine.connect()

cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER='+SERVER+';DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
cursor = cnxn.cursor()








@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)