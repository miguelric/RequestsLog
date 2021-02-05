
from flask import Flask, render_template, url_for, request       # Library Imports
import sqlalchemy as db
from sqlalchemy import create_engine
import pandas as pd



app = Flask(__name__)                                # define our application
   
SERVER = '@biservdev.utsarr.net'
DATABASE = 'IR_dataRequests'
DRIVER = 'SQL Server Native Client 11.0'
USERNAME = 'utsarr/fts605'
PASSWORD = 'utsarr/rico99miguel1999_'
DATABASE_CONNECTION = 'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'

engine = db.create_engine(DATABASE_CONNECTION)
connection = engine.connect()


engine = create_engine('mssql+pyodbc://fts605:{Password}@biservdev.utsarr.net')






@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)