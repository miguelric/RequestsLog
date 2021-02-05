
from flask import Flask, render_template, url_for, request       # Library Imports
import sqlalchemy
from sqlalchemy import create_engine
#import pandas as pd



app = Flask(__name__)                                # define our application
   
SERVER = '@biservdev.utsarr.net'
DATABASE = 'IR_dataRequests'
DRIVER = 'SQL Server Native Client 11.0'
USERNAME = 'fts605'
PASSWORD = '123'
DATABASE_CONNECTION = f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'




engine = create_engine('mssql+pyodbc://fts605:{Password}@biservdev.utsarr.net')


"""
conn = pypyodbc.connect(server='biservdev.utsarr.net',
                            user='fts605', 
                            password='yourpassword', 
                            database='IR_dataRequests')

"""




@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)