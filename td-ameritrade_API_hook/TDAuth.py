# References in attached Jupyter Notebook titled "tdameritrade_api_hook_for_historica_data.ipynb"

import time
import requests
import os
import urllib
from splinter import Browser

class TDAuthentication():
    def __init__ (self, client_id, account_number, password):
        self.client_id          = client_id
        self.account_number     = account_number
        self.password           = password
        self.access_code        = None
        self.access_token       = None

    def authenticate(self):
        try:
            self.access_token = os.environ['td_token']
        except KeyError:
            self.get_access_code()
            self.get_access_token()

    def get_access_code(self):
        executable_path = {'executable_path': r'C:\Users\xitra\ChromeDriver\chromedriver.exe'}

        # Create a new instance of the browser, make sure we can see it (Headless = False)
        browser = Browser('chrome', **executable_path, headless=False)

        # define the components to build a URL
        method = 'GET'
        url = 'https://auth.tdameritrade.com/auth?'
        client_code = self.client_id + '@AMER.OAUTHAP'
        payload = {'response_type':'code', 'redirect_uri':'http://localhost/', 'client_id':client_code}

        # build the URL and store it in a new variable
        p = requests.Request(method, url, params=payload).prepare()
        myurl = p.url

        # go to the URL
        browser.visit(myurl)

        # define items to fillout form
        payload = {'username': self.account_number,
                   'password': self.password}

        # fill out each part of the form and click submit
        username = browser.find_by_id("username").first.fill(payload['username'])
        password = browser.find_by_id("password").first.fill(payload['password'])
        submit   = browser.find_by_id("accept").first.click()

        # click the Accept terms button
        browser.find_by_id("accept").first.click() 

        # give it a second, then grab the url
        time.sleep(1)
        new_url = browser.url

        # grab the part we need, and decode it.
        access_code = urllib.parse.unquote(new_url.split('code=')[1])

        # close the browser
        browser.quit()
        self.access_code = access_code

        return access_code

    def get_access_token(self):
        # define the endpoint
        url = r"https://api.tdameritrade.com/v1/oauth2/token"

        # define the headers
        headers = {"Content-Type":"application/x-www-form-urlencoded"}

        # define the payload
        payload = {'grant_type': 'authorization_code', 
                   'access_type': 'offline', 
                   'code': self.access_code, 
                   'client_id': self.client_id, 
                   'redirect_uri':'http://localhost/'}

        # post the data to get the token
        authReply = requests.post(r'https://api.tdameritrade.com/v1/oauth2/token', headers = headers, data=payload)

        print(authReply)

        # convert it to a dictionary
        decoded_content = authReply.json()        

        # grab the access_token
        access_token2 = decoded_content['access_token']
        self.access_token = access_token2

        return access_token2