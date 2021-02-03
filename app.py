from flask import Flask, render_template, url_for, request       # Library Imports
import pyodbc 
#import pandas as pd
#import sqlalchemy

app = Flask(__name__)                                # define our application
   


"""
conn = pyodbc.connect(
    "Driver = {};"
    "Server = biservdev.utsarr.net;"
    "Database = IR_dataRequests;"
    "UID = fts605;"
    "PWD = ;"
    "Trusted_Connection = yes;"

)

"""




@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")










if __name__ == "__main__":
    app.run(debug=True)