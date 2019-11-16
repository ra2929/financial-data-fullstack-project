#Ruchit Desai
#Ryan Anderson
#COMS W4111 - PROJECT 1 - PART 3
# ALL REFERENCES ARE NOTED AT THE BOTTOM OF THE FILE

import os
import sys
import datetime as dt
import pandas as pd
import numpy as np
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import plotly
import plotly.graph_objs as go
import json


'''
INITIAL EXECUTION - SET UP WORKSPACE
'''
tmpl_dir      = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app           = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI   = "postgresql://rbd2127:group69db@35.243.220.243/proj1part2"
engine        = create_engine(DATABASEURI)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
#
# This line creates a database engine that knows how to connect to the URI above.
#
#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  # DEBUG: this is debugging code to see what request looks like
  print("Request Args: " + str(request.args))


  #
  # example of a database query
  #
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  """

  tickers = generate_list()
  #context = None #= dict(data = names)

  return render_template("index.html", items=tickers) #items changed to tickers

def generate_list():
  cursor = g.conn.execute("SELECT ticker FROM Ticker")
  tickers = []
  for result in cursor:
    tickers.append(result['ticker'])  # can also be accessed using result[0]
  print(tickers)
  cursor.close()

  return tickers
#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/sub', methods=['POST'])
def sub():
  #obtain form information from HTML
  ticker        = request.form['ticker']
  start_date    = request.form['date_start']
  end_date      = request.form['date_end']

  #pull from database
  cursor        = g.conn.execute("SELECT * FROM price P WHERE P.ticker=(%s) AND P.curr_date>=(%s) AND P.curr_date <=(%s) ORDER BY P.curr_date, P.curr_time ASC", 
                                  ticker, 
                                  start_date, 
                                  end_date)
  
  #convert cursor items into a pandas DataFrame
  results       = pd.DataFrame(list(cursor), 
                  columns=['Close', 'High' , 'Low' , 'Volume' , 'p_implied_volatility' , 'p_ask_size' , 'p_bid_size' , 'Ticker' , 'Date' , 'Time'])
  cursor.close()
  #print(results[:10])
  #merge date and time columns into datetime format for plotly
  results_dt    = results.apply(lambda r : pd.datetime.combine(r['Date'],r['Time']),1)
  results       = results.drop('Date', 1)
  results       = results.drop('Time', 1)
  results['datetime'] = results_dt
  
  #Generate plotly Chart
  bar = create_plot(results)

  tickers = generate_list()
  return render_template('index.html', plot=bar, items=tickers)

#returns a list of ticker 
def concate_ticker_info(request_name):
  cursor = g.conn.execute("SELECT * FROM ticker T WHERE T.ticker = (%s)", request_name)
  ticker_info = pd.DataFrame(cursor)
  ticker_list = ticker_info.values.tolist()
  header = str(ticker_list[0][0]) + " : " + str(ticker_list[0][1]) + "  " + str(ticker_list[0][2]) + "  " + str(ticker_list[0][3])
  return header

def create_plot(df):
  #generate list for hover text from pulled market data
  hovertxt = []

  for x in range(len(df['datetime'])):
    hovertxt.append('Date Time: '+str(df['datetime'][x])+
                    '<br>Close: '+str(df['Close'][x])+
                    '<br>High: '+str(df['High'][x])+
                    '<br>Low: '+str(df['Low'][x])+
                    '<br>Volume: '+str(df['Volume'][x])+
                    '<br>Implied Volatility: '+str(df['p_implied_volatility'][x])+
                    '<br>Ask Size: '+str(df['p_ask_size'][x])+
                    '<br>Bid Size: '+str(df['p_bid_size'][x]))
  
  #Create Plotly Figure
  fig = go.Figure(data=[go.Candlestick(x=df['datetime'],
                  open=df['Close'],
                  high=df['High'],
                  low=df['Low'],
                  close=df['Close'],
                  text=hovertxt,
                  hoverinfo='text')])
                  
  header = concate_ticker_info(df['Ticker'][0])
  fig.update_layout(autosize=True,height=1000, title=header)

  cs_color = fig.data[0]

  # Set line and fill colors
  cs_color.increasing.fillcolor = '#00BFFF'
  cs_color.increasing.line.color = '#00BFFF'
  cs_color.decreasing.fillcolor = '#737373'
  cs_color.decreasing.line.color = '#737373'
  
  #fig = go.Figure([go.Scatter(x=df['datetime'], y=df['High'])])
  
  #Convert all data to Plotly-specific-JSON using Plotly's JSONEncoder.
  
  graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

  return graphJSON

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()

'''
REFERENCES:

1. https://blog.heptanalytics.com/2018/08/07/flask-plotly-dashboard/
    FLASK + PLOTLY INTEGRATION TUTORIAL
2. https://plot.ly/python/ohlc-charts/
    PLOTLY OHLC Charts
3. https://plot.ly/python/reference/#ohlc
    PLOTLY Reference guide for figure settings
4. https://stackoverflow.com/questions/17978092/combine-date-and-time-columns-using-python-pandas
    Convert Date and Time to datetime format.
'''