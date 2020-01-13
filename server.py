# Ruchit Desai
# Ryan Anderson
# COMS W4111 - PROJECT 1 - PART 3
# ALL REFERENCES ARE NOTED AT THE BOTTOM OF THE FILE

import os
import sys
import json
import click
import datetime as dt
import pandas as pd

from sqlalchemy import *
from sqlalchemy.pool import NullPool

from flask import Flask, request, url_for, render_template, g, redirect, Response

import plotly
import plotly.graph_objs as go


'''
INITIAL EXECUTION - SET UP WORKSPACE
'''
tmpl_dir      = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app           = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI   = "postgresql://<user>:<pass>@<ip/port>/<database>"
engine        = create_engine(DATABASEURI)

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

'''
Function: index()

  Displays main website

Return Type: render_template
'''
@app.route('/')
def index():
  tickers = generate_list()

  return render_template("index.html", items=tickers) #items changed to tickers

'''
Function: generate_list()

  Pulls list of tickers from the database

Return Type: list() of str()
'''
def generate_list():
  cursor = g.conn.execute("SELECT ticker FROM Ticker")
  tickers = []
  for result in cursor:
    tickers.append(result['ticker'])  # can also be accessed using result[0]
  #print(tickers)
  cursor.close()

  return tickers

'''
Function: sub()

  Displays requested data after hitting Submit

Return Type: render_template
'''
@app.route('/sub', methods=['POST'])
def sub():
  #obtain form information from HTML
  ticker        = request.form['ticker']
  start_date    = request.form['date_start']
  end_date      = request.form['date_end']
  choice        = request.form['selection']
  
  tickers = generate_list()

  if (choice == 'options'):
    cursor        = g.conn.execute("SELECT DISTINCT * FROM options_data O WHERE O.ticker=(%s) AND O.curr_date>=(%s) AND O.curr_date <=(%s) AND O.o_volume>=9000 ORDER BY O.curr_date, O.curr_time ASC", 
                                ticker, 
                                start_date, 
                                end_date)

    results       = pd.DataFrame(list(cursor), 
                columns=['Strike', 'Options Symbol' , 'Postion' , 'Ask Price' , 'Bid Price' , 'Volume' , 'Open Interest' , 'Implied Volatility' , 'Ask Size' , 'Bid Size', 'Expiry', 'Ticker', 'Date', 'Time'])
    cursor.close()

    results       = results.drop('Ticker', 1)
    results       = results.drop('Date', 1)
    results       = results.drop('Time', 1)

    return render_template("options.html", opt_data=results, items=tickers)

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
  return render_template('index.html', plot=bar, opt_data=None, items=tickers)

#returns a list of ticker 
'''
Function: concatenate_ticker_info()

  args: Ticker Name
  
  Returns the header for Chart Pages

Return Type: str()
'''
def concate_ticker_info(request_name):
  cursor = g.conn.execute("SELECT * FROM ticker T WHERE T.ticker = (%s)", request_name)
  ticker_info = pd.DataFrame(cursor)
  ticker_list = ticker_info.values.tolist()
  header = str(ticker_list[0][0]) + " : " + str(ticker_list[0][1]) + "  " + str(ticker_list[0][2]) + "  " + str(ticker_list[0][3])
  return header

'''
Function: create_plot()
  args: pandas DataFrame
  
  Converts pandas Dataframe into Plotly JSON object

Return Type: JSON object
'''
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