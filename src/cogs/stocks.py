from inspect import indentsize
from re import L
import discord
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from decimal import *
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
            'limit': '100',
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
    @commands.command(aliases = ['c-info', 'crypto-5ranks', 'crypto'])
    async def crypto_info(self, ctx):
        with open('src/CMC_data.json') as CMC_data:
            all_data = json.load(CMC_data)
            data = all_data['data']

        response = discord.Embed(
            title = 'Cryptocurrency  |  Top 5 Ranked Currencies:',
            description = 'The following is information on the top 5 ranked cryptocurriences.',
            colour = (discord.Colour.blue())
        )

        for currency in data:

            if currency['cmc_rank'] <= 5:

                currency_name = currency['name']
                symbol = currency['symbol']
                rank = currency['cmc_rank']
                last_updated = currency['last_updated']

                # Setting price to 2 decimal places.
                price_USD = round(currency['quote']['USD']['price'], 2)


                response.add_field(
                    name = f'Rank {rank}:',
                    value = '''\
                        `Name:` **{name}**
                        `Symbol:` {symbol}
                        `Price [USD]`: ${price_USD}
                        `Last Updated:` {last_updated}'''\
                        .format(name = currency_name, symbol = symbol, price_USD = price_USD, last_updated = last_updated),
                    inline = False
                )

        response.set_footer(
            text = 'The above data is provided by CoinMarketCap\'s API.'
        )

        await ctx.send(embed = response)



def setup(client):
    client.add_cog(Stocks(client))