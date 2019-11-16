#Ruchit Desai
#Ryan Anderson
#Raw database connection filtering; no "Magic" used

from sqlalchemy import *
import pandas as pd
from flask import Flask, request, render_template, g, redirect, Response

class cs4111db():
    self.g.conn = None

    def __init__(self, databaseuri):
        self.engine = create_engine(databaseuri)

    def pull_ticker_from_DB(self, ticker, date_start, date_end):
        """
            Pull custom request from DB, return pandas dataframe with data
        """
        pass

    #
    def pull_tickers(self):
        """
            Pull list of tickers
        """
        pass

    def before_req(self):
        """
            This function is run at the beginning of every web request 
            (every time you enter an address in the web browser).
            We use it to setup a database connection that can be used throughout the request.

            The variable g is globally accessible.
        """
        try:
            g.conn = self.engine.connect()
        except:
            print("uh oh, problem connecting to database")
            import traceback; traceback.print_exc()
            g.conn = None

    def teardown_req(self, exception):
        """
            At the end of the web request, this makes sure to close the database connection.
            If you don't, the database could run out of memory!
        """
        try:
            self.g.conn.close()
        except Exception as e:
            pass