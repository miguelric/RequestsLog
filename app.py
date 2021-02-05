
from flask import Flask, render_template, url_for, request       # Library Importsclear

import pypyodbc  
#import pandas as pd
#import sqlalchemy

app = Flask(__name__)                                # define our application
   


conn = pypyodbc.connect(server='biservdev.utsarr.net',
                            user='fts605', 
                            password='yourpassword', 
                            database='IR_dataRequests')






@app.route('/')                                  # url mapping
def homepage():
 
 
    return render_template("index.html")





if __name__ == "__main__":
    app.run(debug=True)