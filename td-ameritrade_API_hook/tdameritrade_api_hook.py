'''
REFERENCES: https://github.com/areed1192/sigma_coding_youtube/tree/master/python/python-finance/td-ameritrade

'''
import urllib                       #parse info for access token etc...
import json                         #content back
import requests                     #API component
import dateutil.parser              #Date Parser - take info from first api request and parse it
import datetime                     
from TDAuth import TDAuthentication
from config import password, account_number, client_id
import pandas as pd
import csv

def unix_time_millis(dt):
    '''
    input: dt -> unixtime (int)

    output: unixtime in milliseconds (int)
    '''
    # grab the starting point, so time '0'
    epoch = datetime.datetime.utcfromtimestamp(0)
    
    return (dt - epoch).total_seconds() * 1000.0


def main():
    #PRICE HISTORY - CHANGE PRODUCT NAME - OUTPUTS LAST MONTH OF OHLCV DATA!

    TDClient = TDAuthentication(client_id, account_number, password)
    TDClient.authenticate()

    access_token = TDClient.access_token

    product = "SPX"

    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format(product)

    payload = {'apikey': client_id,
               #'period':'2',
               #'periodType':'day',
               'frequencyType':'minute',
               'frequency':'1',
               'startDate': 1549024201000,
               'endDate': 1572916805000,
               'needExtendedHoursData':'true'
              }

    content = requests.get(url=endpoint, params  = payload)

    #convert it to dict

    data = content.json()

    with open(str(product)+(str(".csv")), "w", newline='') as writeFile:
        f = csv.writer(writeFile)
        f.writerow([ 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

        for this_data in data['candles']:
            unix_times = int(this_data['datetime']) / 1000


            actual_date = datetime.datetime.fromtimestamp(unix_times).strftime('%Y-%m-%d')
            actual_time = datetime.datetime.fromtimestamp(unix_times).strftime('%H:%M')
            f.writerow( [ actual_date, actual_time, this_data['open'], this_data['high'], this_data['low'], this_data['close'], this_data['volume'] ] )

    writeFile.close()

    print("Done 2")

def options_history(client_id):
    #OPTIONS HISTORY - CHANGE PRODUCT AND FROMDATE / TODATE

    product = "SPY"

    endpoint = "https://api.tdameritrade.com/v1/marketdata/chains"

    # get our access token
    headers = {'Authorization': "Bearer {}".format(access_token)}

    # this endpoint, requires fields which are separated by ','
    params = {'apikey': client_id,
               'symbol': product,
               'contractType':'ALL',
               'strikeCount': 5,
               'includeQuotes': 'TRUE',
               'range' : 'NTM',
               'fromDate' : '2019-11-01',
               'toDate' : '2020-02-01',
               'daysToExpiration' : 100,
               'expMonth' : 'ALL',
               'optionType': 'ALL'
              }

    # make a request
    content = requests.get(url = endpoint, params = params, headers = headers)

    #convert it to dict

    data = content.json()

if __name__ == '__main__':
    main()