import plotly.graph_objects as go 
import pandas as pd
from datetime import datetime
import sqlalchemy as db 
import glob
from flask import Flask, render_template

#connect to database
#DATABASEURI = "postgresql://rbd2127:group69db@35.243.220.243/proj1part2"
#engine = create_engine(DATABASEURI)
#metadata = db.MetaData()
#ticker =  db.Table('ticker', metadata, autoload = True, autoload_width = engine)

#get dat file names
df = pd.read_csv('https://github.com/ra2929/w4111-proj1/tree/master/csv_data_for_db/AAPL.csv')

#implement function to iterate through CSV files and select the ticker to display graphically

#create candlestick chart (Using AAPL as the first example)

graph = go.Figure(data = [go.Candlestick(x=df['Date'], open = df['AAPL.Open'], high=df['AAPL.High'],
                        low = df['AAPL.Low'], close = df['AAPL.Close']
                        )])

graph.show()

#render webpage
@app.route('/')
def index():
    return render_template("index.html", ticker = ticker, startDate = startDate, endDate = endDate, size = size)



