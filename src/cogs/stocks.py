from asyncio.windows_events import NULL
from inspect import indentsize
from os import error
from re import L
import discord
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from decimal import *
import json
import time
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


    async def is_data_loaded(self):
        if (self.data == NULL) or (len(self.data) == 0):
            return False
        else:
            return True

    
    async def data_status_message(self):
        error_message = discord.Embed(
            title = 'Cryptocurrency  |  ERROR:',
            description = 'The cryptocurrency data appears to be missing! Please look below for some possible solutions.',
            colour = (discord.Colour.red())
        )

        error_message.add_field(
            name = '[1] Force Load:',
            value = 'Try using the `load-cmcdata` command to force the data to load in again.',
            inline = False
        )

        error_message.add_field(
            name = '[2] Restart:',
            value = 'Try restarting the bot. This will make the bot go through the process of loading the data from CoinMarketCap\'s servers again.',
            inline = False
        )

        error_message.add_field(
            name = '[3] Reload Cog:',
            value = f'Try using the `reload (Insert Name of Cog)` command to unload the specified cog and load it back in. For this cog, the command would be `reload {self}`.',
            inline = False
        )

        return error_message



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


    @commands.command(aliases = ['crypto-top5', 'crypto-5', 'c-top5'])
    async def crypto_top_5(self, ctx):
        data = await self.load_data()
   
        if self.is_data_loaded() == False:
            error = await self.data_status_message()
            return await ctx.send(embed = error)


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


    @commands.command(aliases = ['see-crypto-info', 'see-cinfo', 'seecrypto'])
    async def see_crypto_info(self, ctx, *, crypto_symbols):
        data = await self.load_data()

        if self.is_data_loaded() == False:
            error = await self.data_status_message()
            return await ctx.send(embed = error)

        
        requested_symbols = crypto_symbols.upper().split(' ')
        symbols_not_found = []

        i = 1


        if len(requested_symbols) == 0:

            no_symbols_error = discord.Embed(
                title = 'Cryptocurrency Information  |  ERROR:',
                description = 'Please call the `seecrypto` command along with the desired crytocurrencies\' symbols.',
                colour = (discord.Colour.red())
            )

            return await ctx.send(embed = no_symbols_error)


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
                    time.sleep(0.5)
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

            time.sleep(0.5)
            await ctx.send(embed = not_found_error)

    
    @commands.command(aliases = ['add-crypto-self', 'add-cself', 'cryptoself'])
    async def add_crypto_to_uinfo(self, ctx, *, crypto_symbols):
        data = await self.load_data()

        if await self.is_data_loaded() == False:
            error = await self.data_status_message()
            return await ctx.send(embed = error)

        with open('src/hidden/ALL_USERS_INFO.json') as f:
            info = json.load(f)
            users = info['users']

        member = ctx.author

        requested_symbols = crypto_symbols.upper().split(' ')
        symbols_not_found = []
        symbols_found = []
        symbols_found_info = {}

        
        for symbol in requested_symbols:
            check = False

            for currency in data:

                if currency['symbol'] == symbol:
                    name = currency['name']
                    symbols_found_info[f'{name}'] = currency

                    symbols_found.append(symbol)

                    check = True
                    continue
            
            if check == False:
                symbols_not_found.append(symbol)
                continue

        
        for user in users:

            if (member.display_name, member.discriminator) == (user['name'], user['discriminator']):

                user['cryptocurrencies'] = symbols_found_info

        
        with open('src/hidden/ALL_USERS_INFO.json', 'w') as outfile:
            json.dump(info, outfile, indent = 4)


        success = discord.Embed(
            title = f'Cryptocurrencies Added To {member.display_name}\'s Info:',
            description = 'The following cryptocurrencies have been added.',
            colour = (discord.Color.blue())
        )

        success.add_field(
            name = 'Cryptocurrencies Added:',
            value = symbols_found
        )

        await ctx.send(embed = success)

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

            time.sleep(0.5)
            await ctx.send(embed = not_found_error)
                


def setup(client):
    client.add_cog(Stocks(client))