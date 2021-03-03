from asyncio.windows_events import NULL
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
        self.data = NULL
        self.CMC_filepath = 'src/hidden/CMC_data.json'


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

            with open(self.CMC_filepath, 'w') as f:
                json.dump(data, f, indent = 4)

        except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
            print('[CMC API] Encountered Error: ' + ERROR)
        # --



    # -- Functions --
    async def load_data(self):
        if self.data == NULL:
            with open(self.CMC_filepath) as CMC_data:
                all_data = json.load(CMC_data)
                self.data = all_data['data']
        
        return self.data



    # -- Events --

        

    # -- Commands --
    @commands.command(aliases = ['cmc-force', 'data-force', 'load-cmcdata'])
    async def force_load__cmc_data(self, ctx):
        with open(self.CMC_filepath) as CMC_data:
            all_data = json.load(CMC_data)
            self.data = all_data['data']
        
        confirmation = discord.Embed(
            title = '[Successful] Force Load: CoinMarketCap Data',
            description = 'The data from CoinMarketCap has been force loaded into the bot.',
            colour = (discord.Colour.blue())
        )
        
        await ctx.send(embed = confirmation)
        return self.data


    @commands.command(aliases = ['c-info', 'crypto-5ranks', 'crypto'])
    async def crypto_info(self, ctx):
        data = await self.load_data()

        if len(data) == 0:
            error = discord.Embed(
                title = 'Cryptocurrency  |  ERROR:',
                description = 'The cryptocurrency data appears to be missing!',
                colour = (discord.Colour.red())
            )

            await ctx.send(embed = error)
            return


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
                        `Price [USD]:` ${price_USD}
                        `Last Updated:` {last_updated}'''\
                        .format(name = currency_name, symbol = symbol, price_USD = price_USD, last_updated = last_updated),
                    inline = False
                )

        response.set_footer(
            text = 'The above data is provided by CoinMarketCap\'s API.'
        )

        await ctx.send(embed = response)

    
    @commands.command()
    async def checkout(self, ctx, symbol = 'BTC'):
        data = await self.load_data()
        upper_symbol = symbol.upper()

        # Currency Info - Message
        currency_info = discord.Embed(
            title = f'Cryptocurrency Information: [{upper_symbol}]',
            colour = (discord.Colour.blue())
        )

        # Currency Not Found - Error Message
        not_found_error = discord.Embed(
            title = 'Cryptocurrency Information  |  ERROR:',
            description = f'The cryptocurrency, {upper_symbol}, requested cannot be found in the list of cryptocurrencies.',
            colour = (discord.Colour.red())
        )


        for currency in data:

            if currency['symbol'] == upper_symbol:

                # Setting price to 2 decimal places.
                price_USD = round(currency['quote']['USD']['price'], 2)

                fields = [
                    ['`Name:`', currency['name'], True],
                    ['`Symbol:`', currency['symbol'], True],
                    ['`ID:`', currency['id'], True],
                    ['`Price [USD]:`', f'${price_USD}', True],
                    ['`[USD] 24H Volume:`', currency['quote']['USD']['volume_24h'], True],
                    ['[---]', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                    ['Date Added:', currency['date_added'], True],
                    ['CMC Rank:', currency['cmc_rank'], True],
                    ['Number of Market Pairs:', currency['num_market_pairs'], False],
                    ['Total Supply:', currency['total_supply'], True],
                    ['Circulating Supply:', currency['circulating_supply'], True],
                    ['Maximum Supply:', currency['max_supply'], True],
                    [f'{chr(173)}', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                    ['Last Updated:', currency['last_updated'], False]
                ]

                for name, value, inline in fields:
                    currency_info.add_field(name = name, value = value, inline = inline)

                return await ctx.send(embed = currency_info)
        
        return await ctx.send(embed = not_found_error)


    @commands.command(aliases = ['check-many', 'multicheck', 'mcheck', 'checkm'])
    async def checkout_many(self, ctx, *, crypt_symbols):
        data = await self.load_data()
        
        requested_symbols = crypt_symbols.upper().split(' ')
        symbols_not_found = []

        i = 1


        for symbol in requested_symbols:
            # Using 'check' to add a symbol not found in 'data'.
            # Otherwise it would add every symbol.
            check = False

            for currency in data:

                if currency['symbol'] == symbol:

                    currency_info = discord.Embed(
                        title = f'Cryptocurrency Information: [{symbol}]  |  {i} of {len(requested_symbols)}',
                        colour = (discord.Colour.blue())
                    )

                    # Setting price to 2 decimal places.
                    price_USD = round(currency['quote']['USD']['price'], 2)

                    fields = [
                        ['`Name:`', currency['name'], True],
                        ['`Symbol:`', currency['symbol'], True],
                        ['`ID:`', currency['id'], True],
                        ['`Price [USD]:`', f'${price_USD}', True],
                        ['`[USD] 24H Volume:`', currency['quote']['USD']['volume_24h'], True],
                        [f'{chr(173)}', '---', False], # Format Spacer; chr(173) is a blank character.
                        ['Date Added:', currency['date_added'], True],
                        ['CMC Rank:', currency['cmc_rank'], True],
                        ['Number of Market Pairs:', currency['num_market_pairs'], False],
                        ['Total Supply:', currency['total_supply'], True],
                        ['Circulating Supply:', currency['circulating_supply'], True],
                        ['Maximum Supply:', currency['max_supply'], True],
                        [f'{chr(173)}', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                        ['Last Updated:', currency['last_updated'], False]
                    ]

                    for name, value, inline in fields:
                        currency_info.add_field(name = name, value = value, inline = inline)

                    check = True
                    i += 1
                    await ctx.send(embed = currency_info)
            
            if check == False:
                symbols_not_found.append(symbol)
                continue
    
    
        # Symbols Not Found - Error Message
        if len(symbols_not_found) > 0:

            not_found_error = discord.Embed(
                title = 'Cryptocurrency Information  |  ERROR:',
                colour = (discord.Colour.red())
            )

            not_found_error.add_field(
                name = 'Symbols Not Found:',
                value = f'{symbols_not_found}'
            )

            await ctx.send(embed = not_found_error)



def setup(client):
    client.add_cog(Stocks(client))