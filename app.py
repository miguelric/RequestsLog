from flask import Flask, render_template, url_for, request       # Library Imports
import pandas as pd
import sqlalchemy


app = Flask(__name__)                                # define our application
   


myDB = mysql.connector.connect(                         # Connecting to SQL Server
    host="biservdev.utsarr.net",
    user="fts605",
    passwd ="",
    database = "IR_dataRequests"
)


engine = sqlalchemy.create_engine('mysql+pymysql://root:m123rico@localhost/work',)


@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")










if __name__ == "__main__":
    app.run(debug=True)