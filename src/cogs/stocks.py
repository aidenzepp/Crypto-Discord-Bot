from inspect import indentsize
from re import L
import discord
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
#--

# -- Load API Keys --
with open('src/hidden/secrets.json') as f: 
    secrets = json.load(f)
    api_keys = secrets['keys']


class Stocks(commands.Cog):

    def __init__(self, client, secrets = secrets, keys = api_keys):
        self.client = client
        self.secrets = secrets
        self.keys = keys


        # CoinMarketCap API Documentation - Quickstart Guide's Format
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        parameters = {
            'start': '1',
            'limit': '5000',
            'convert': 'USD'
        }

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.keys['coinmarketcap']
        }


        session = Session()
        session.headers.update(headers)


        try:
            response = session.get(url, params = parameters)
            data = json.loads(response.text)

            with open('src/CMC_data.json', 'w') as f:
                json.dump(data, f, indent = 4)

        except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
            print('Encountered Error: ' + ERROR)
        # --



    # -- Events --



    # -- Commands --


def setup(client):
    client.add_cog(Stocks(client))