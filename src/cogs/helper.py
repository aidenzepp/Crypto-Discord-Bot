from operator import index, not_
from typing import Type
import discord
from discord import member
from discord import guild
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import datetime as dt
import json
import time
import os

from cogs.utility import *
#--

'''
I. Description:
    - Stores repeatedly used functions by one or multiple other cogs.
    - Stores information used by one or multiple other cogs.
    - Used to keep most of the functions, information, or other code
      in one place; this allows for keeping the other cogs more clean.


II. Using the 'Helper' Class:
    - In the body of another cog's '__init__()', insert the code below:
        >>> self.helper = Helper(client)


III. CoinMarketCap Data:
    - The CMC will be stored in the Helper Class.
        [** This keeps the error of a circular import from occurring. **]

[ ~~~ ]

Self Attributes:
    > self.client = client
    > self.hidden = 'src/hidden'
    > self.cogs = 'src/cogs'
    > self.data = data
        * data: the cryptocurrency data from CoinMarketCap; type() == dict
    > self.keys = keys
        * keys: the API keys stored in 'src/secrets.json'; type() == dict
        * keys['discord']: the Discord API key; type() == str
        * keys['coinmarketcap']: the CoinMarketCap API key; type() == str
    > self.cmc_filepath = 'src/hidden/CMC_data.json'
        * True Return Value = f'{self.hidden}/CMC_data.json'
        * Found under '-- Files & Folder Paths --' section.
    > self.usersinfo_dir = 'src/hidden/ALL_USERS_INFO'
        * True Return Value = f'{self.hidden}/ALL_USERS_INFO'
        * Found under '-- Files & Folder Paths --' section.
    > self.server = server
        * server: the 'Guild' class (discord.Guild), containing info of the server; type() == discord.guild.Guild
        * Found under '-- Discord --' section.

Functions List:
    - JSON -
        > json_load(filepath)
            * filepath = None
        > json_dump(input, filepath, indent)
            * input = None
            * filepath = None
            * indent = 4

    - MATH -
        > [ASYNC] prcnt_change(diff, denom, round_output, round_val)
            * diff: the difference used for calculating percents (e.g. '((3 - 2) / 2) * 100')
            * denom: the denominator used for calculating percents
                (Essentially the 'original' or 'base' value that the percent is calculated off of.)
            * round_output = True; whether or not to round the output
            * round_val = 2; if the output is being rounded, this is the number of decimal places it's rounded to
        > [ASYNC] compare_diff_val_pairs(values, round_output, calc_prcnt, round_val)
            * values: the values that should have their difference calculated; type() == list
            * round_output = True; whether or not to round the output
            * calc_prcnt = False; whether or not to calculate the percent change
            * round_val = 2; if the output is being rounded, this is the number of decimal places it's rounded to

    - DATETIME -
        > dtformat_default()
        > dtformat_return(description):
            * description = False; whether or not to provide the description version of the 'dtformat'
        > dtconvert(input, **kwargs):
            * input: the string that needs to be converted to a DateTime object/format; type() == str
            * **kwargs:
                1. type = 'dis': used to take the input of a Discord-formatted DateTime string
                2. type = 'cmc': used to take the input of a CMC-formatted DateTime string
                3. format = ?: specify the format the new DateTime string should take on

    - DISCORD -
        > [ASYNC] check_server()
        > create_embed_message(header, fields, footer, colour)
            * header = None
            * fields = None
            * footer = None
            * colour = discord.Colour.blue()
        > cmcdata_error_msg(solutions)
            * solutions = False
        > [ASYNC] send_embed_messages(ctx, messages, pause)
            * ctx: the 'ctx' provided by the parent command calling this command
            * messages: the embed messages that need to be sent; type() == list
            * pause = 0.0; whether or not to pause between sending messages

    - USER -
        > user_filename(member, filetype)
            * member: type() == discord.Member
            * filetype = 'json'
        > user_filepath(member)
            * member: type() == discord.Member
        > user_info(member)
            * member: type() == discord.Member
        > create_user_contents(member)
            * member: type() == discord.Member
        > [ASYNC] user_info_msg(member)
            * member: type() == discord.Member
        > [ASYNC] make_user(member)
            * member: type() == discord.Member
        > [ASYNC] find_user(member)
            * member: type() == discord.Member

    - COINMARKETCAP -
        > [ASYNC] load_cmcdata()
        > [ASYNC] check_cmcdata()
        > [ASYNC] check_and_load()
        > [ASYNC] find_crypto_info(symbols)
            * symbols: the symbols of requested cryptocurrencies; type() == tuple
        > [ASYNC] symbols_notfound_msg(not_found)
            * not_found: a list of the cryptocurrencies that couldn't be found in the data; type() == list
        > [ASYNC] symbols_notuinfo_msg(not_in_uinfo)
            * not_in_uinfo: a list of the cryptocurrencies that couldn't be found in the user's info file; type() == list
        > [ASYNC] crypto_info_msg_simple(member, found, not_found):
            * member: type() == discord.Member
            * found: a list of the cryptocurrencies that could be found in the data; type() == list
            * not_found: a list of the cryptocurrencies that couldn't be found in the data; type() == list
        > [ASYNC] crypto_info_msg(symbols)
            * symbols: the symbols of requested cryptocurrencies; type() == tuple
        > [ASYNC] crypto_top5_msg()
        > [ASYNC] add_crypto_to_user(member, cryptos)
            * member: type() == discord.Member
            * cryptos: information of cryptocurrencies being added to the user's info file; type() == dict
        > [ASYNC] compare_crypto(member, symbols)
            * member: type() == discord.Member
            * symbols: the symbols of requested cryptocurrencies; type() == tuple
        > [ASYNC] compare_crypto_msg(member, symbols)
            * member: type() == discord.Member
            * symbols: the symbols of requested cryptocurrencies; type() == tuple
'''

class Helper(commands.Cog):

    # -- Load API Keys --
    with open('src/hidden/secrets.json') as f: 
        secrets = json.load(f)
        keys = secrets['keys']
        serverinfo = secrets['server']
        datastartup = serverinfo['datastartup']
        # Because the code above is inserted this way,
        # the 'keys' object can be accessed using 'self.keys'.
        
    def __init__(self, client):
        self.client = client
        self.hidden = 'src/hidden' # Path for the 'hidden' folder.
        self.cogs = 'src/cogs' # Path for the 'cogs' folder.
        self.data = None
        self.rwc = 'USD' # 'rwc' = Real World Currency; the currency that the cryptocurrency will be converted to.

        
        if self.datastartup:
            # CoinMarketCap API Documentation - Quickstart Guide's Format
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

            parameters = {
                'start': '1',
                'limit': '100',
                'convert': self.rwc
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

                with open(f'{self.hidden}/CMC_data.json', 'w') as f:
                    json.dump(data, f, indent = 4)

            except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
                print('[CMC API] Encountered Error: ' + ERROR)
            # --

            self.data = data

        else:
            # If the file can be found, and its contents present, then
            # load into an unused variable.
            # If the file can't be found (and throws the error below), then
            # create the file by loading an empty dict. into the file.
            try:
                with open(f'{self.hidden}/CMC_data.json', 'r') as f:
                    _ = json.load(f)
            except FileNotFoundError:
                with open(f'{self.hidden}/CMC_data.json', 'w') as outfile:
                    empty = {}
                    json.dump(empty, outfile)

    def __repr__(self):
        pass

    def __str__(self):
        pass
        

    # -- File & Folder Paths --
    @property
    def cmc_filepath(self):
        try:
            return f'{self.hidden}/CMC_data.json'
        except FileNotFoundError:
            with open(f'{self.hidden}/CMC_data.json', 'w') as f:
                _ = json.load(f)
            return f'{self.hidden}/CMC_data.json'

    @property
    def usersinfo_dir(self):
        return f'{self.hidden}/ALL_USERS_INFO'


    # -- JSON --
    @staticmethod
    def json_load(filepath = None):
        if filepath != None:
            with open(filepath, 'r') as f:
                contents = json.load(f)
            print('File\'s contents loaded.')
            return contents
        else:
            print('Missing contents. Check command call.')
            return None
        
    @staticmethod
    def json_dump(input = None, filepath = None, indent = 4):
        if (input, filepath) != None:
            with open(filepath, 'w') as outfile:
                json.dump(input, outfile, indent = indent)
            print('Input dumped to filepath.')
        else:
            print('Input could not be dumped to filepath. Check command call.')


    # -- Math --
    @staticmethod
    async def prcnt_change(diff, denom, round_output = True, round_val = 2):
        # Check if the denominator is zero.
        try:
            prcnt = (diff / denom) * 100
        except ZeroDivisionError:
            prcnt = None

        # If it needs to round and 'prcnt' didn't have a 'ZeroDivisionError' issue, round 'prcnt'.
        if round_output and (prcnt != None):
            prcnt_rounded = round(prcnt, round_val)
            return prcnt_rounded
        else:
            return prcnt

    async def compare_diff_val_pairs(self, values, round_output = True, calc_prcnt = False, round_val = 2):
        val_1, val_2 = values

        # Check if 'val_2' is 'None'.
        try:
            diff = val_2 - val_1
            diff_rounded = round(diff, round_val)
            prcnt_change = await self.prcnt_change(diff, val_1, round_output, round_val)
        except TypeError:
            # Return 'diff' as 'None'. If 'calc_prcnt == True', return 'prcnt_change' as None along w/ 'diff'.
            diff = None
            if calc_prcnt:
                prcnt_change = None
                return diff, prcnt_change
            return diff

        if round_output and calc_prcnt: # If it needs to round and calculate the percent.
            return diff_rounded, prcnt_change
        elif round_output: # If it only needs to round.
            return diff_rounded
        elif prcnt_change: # If it needs 'diff' w/o rounding and to calculate the percent.
            return diff, prcnt_change
        else:
            return diff

    
    # -- DateTime --
    @staticmethod
    def dtformat_default():
        return '%Y-%m-%dT%H:%M:%S'

    @staticmethod
    def dtformat_return(description = False):
        if description:
            return 'Time Format: DD MMMM, YYYY - [HH:MM:SS]'
        else:
            return '%d %b, %Y - [%H:%M:%S]'

    def dtconvert(self, input, **kwargs):
        if kwargs.get('type') == 'dis': # If the input's format is from Discord.
            dt_obj = dt.datetime.strptime(input[:-7], '%Y-%m-%d %H:%M:%S')
        elif kwargs.get('type') == 'cmc': # If the input's format is from CoinMarketCap.
            dt_obj = dt.datetime.strptime(input[:-5], self.dtformat_default())
        else:
            dt_obj = dt.datetime.strptime(input, self.dtformat_default())

        if kwargs.get('format') == None: # If there is no specific format needed.
            converted = dt.datetime.strftime(dt_obj, self.dtformat_return())
        else: # If there needs to be a specific format.
            converted = dt.datetime.strftime(dt_obj, kwargs.get('format'))
        
        return converted


    # -- Discord --
    @property
    def server(self):
        server = discord.Guild
        return server

    async def check_server(self):
        if self.server == None:
            print('Server wasn\'t loaded. Loading now...')
            self.server = discord.Guild
        return self.server

    @staticmethod
    def create_embed_msg(header = None, fields = None, footer = None, colour = discord.Colour.blue()):
        # Check if a 'header' was provided.
        if (header == None) or (len(header) == 0):
            print('The header values have been left blank. Check command call.')
            return

        # Check if there's a description.
        # Resulting format is incorrect if 'title = header' but 'type(header) == list'.
        if (type(header) == list) and (len(header) > 1):
            title = header[0]
            description = header[1]

            msg = discord.Embed(
                title = title,
                description = description,
                colour = colour
            )
        elif (type(header) == list) and (len(header) == 1):
            title = header[0]

            msg = discord.Embed(
                title = title,
                colour = colour
            )
        else:
            title = header

            msg = discord.Embed(
                title = title,
                colour = colour
            )
        # --

        # Check if there are fields.
        if fields != None:
            for field in fields:
                name, value, inline = field
                msg.add_field(name = name, value = value, inline = inline)

        # Check if there's a footer.
        if footer != None:
            msg.set_footer(text = footer)

        return msg

    @staticmethod
    async def send_embed_messages(ctx, messages, pause = 0.0):
        for message in messages:
            time.sleep(pause)
            await ctx.send(embed = message)
        

    # -- User --
    @staticmethod
    def user_filename(member, filetype = 'json'):
        return f'{member.id}.{filetype}'

    def user_filepath(self, member):
        return '{users_folder}/{filename}'.format(users_folder = self.usersinfo_dir, filename = self.user_filename(member))

    @staticmethod
    def user_info(member):
        info = {
            'name': member.display_name,
            'discriminator': member.discriminator,
            'id': member.id,
            'mention': member.mention,
            'nickname': member.nick,
            'colour': str(member.colour),
            'joined_at': str(member.joined_at)
        }
        return info

    def create_user_contents(self, member):
        contents = {}
        contents['user'] = self.user_info(member)
        contents['crypto'] = {}
        return contents

    async def user_info_msg(self, member):
        info = self.user_info(member)
        header = f'{member}  |  User Information:'
        fields = []

        keys = [key for key in info.keys()]
        for i in range(len(keys)):
            name = f'{keys[i]}:'.title()
            value = info.get(keys[i])
            inline = True

            if i < 2: # Highlight 1st and 2nd keys ('name', 'discriminator').
                name = f'`{name}`'
            elif i == 2: # Highlight 3rd key ('id'), make uppercase, and hide value.
                name = f'`{name.upper()}`'
                value = f'||{value}||'
            elif i == 3: # Give 4th key ('mention') 'inline = False'.
                inline = False
            elif i == 6: # Give 6th key ('joined_at') a proper title and 'inline = False'.
                name = 'Joined At:' 
                inline = False
        
            fields.append([name, value, inline])
        
        msg = self.create_embed_msg(header, fields)
        return msg

    async def make_user(self, member):
        # 1. Create the user-info contents for the user's file.
        info = self.create_user_contents(member)
        # 2. Get the string for the user's file path.
        filepath = self.user_filepath(member)
        # 3. Dump 'info' in a new JSON file. 
        self.json_dump(info, filepath)
        return info

    async def find_user(self, member):
        files = os.listdir(self.usersinfo_dir)
        user_filename = self.user_filename(member)
        user_filepath = self.user_filepath(member)

        if user_filename in files:
            info = self.json_load(user_filepath)
            print(f'{member}\'s file found. Returning info...')
            return info
        else:
            return None

    
    # -- CoinMarketCap --
    async def forceload_cmcdata(self):
        # CoinMarketCap API Documentation - Quickstart Guide's Format
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        parameters = {
            'start': '1',
            'limit': '100',
            'convert': self.rwc
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

            with open(f'{self.hidden}/CMC_data.json', 'w') as f:
                json.dump(data, f, indent = 4)

        except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
            print('[CMC API] Encountered Error: ' + ERROR)
        # --

        self.data = data
        return self.data


    async def load_cmcdata(self):
        if self.data == None:
            all_data = self.json_load(self.cmc_filepath)
            self.data = all_data['data']
        return self.data

    async def check_cmcdata(self):
        if (self.data == None) or (len(self.data) == 0):
            return False
        else:
            return True

    async def check_and_load(self):
        if await self.check_cmcdata() == False:
            print('Data wasn\'t loaded. Loading data now...')
            return await self.load_cmcdata()

    async def cmcdata_error_msg(self, solutions = False):
        # Check if the error message should contain possible solutions.
        if solutions:
            header = [
                'Cryptocurrency  |  ERROR:',
                'The cryptocurrency data appears to be missing!'
            ]

            fields = [
                ['[1] Force Load:', 'Try using the `load-cmcdata` command to force the data to load in again.', False],
                ['[2] Restart:', 'Try restarting the bot. This will make the bot go through the process of loading the data from CoinMarketCap\'s servers again.', False],
                ['[3] Reload Cog:', 'Try using the `reload {Insert Name of Cog}` command to unload the specified cog and load it back in. For this cog, the command would be `reload stocks`.', False]
            ]
        else:
            header = [
                'Cryptocurrency  |  ERROR:',
                'The cryptocurrency data appears to be missing!'
            ]

        msg = self.create_embed_msg(header, fields, colour = discord.Colour.red())
        return msg


    async def find_crypto_info(self, symbols):
        symbols = [symbol.upper() for symbol in symbols]
        found_info = {}
        not_found = {}

        # For each crypto-symbol in the user's requested crypto-symbols...
        for symbol in symbols:
            # Guarantees a symbol not in 'self.data' doesn't pass through.
            verify = False

            for currency in self.data:
                # If the currency matches a user's requested symbol...
                if currency['symbol'] == symbol:
                    # Set a key in 'found_info' to the currency's name.
                    # Set the key's value to the info of the currency. 
                    name = currency['name']
                    found_info[name] = currency

                    verify = True
                    continue
            
            # Verify if none of the currencies' symbols matched the requested symbol.
            if verify == False:
                not_found[symbol] = None
                continue

        return FIND_CRYPTO_RESULTS(self.client, found_info, not_found)

    async def symbols_notfound_msg(self, not_found):
        header = [
            'Cryptocurrency Information  |  ERROR - NOT FOUND:',
            'The symbols shown below could not be found in the cryptocurrency data. Please make sure the correct cryptocurrency symbol was used.'
        ]
        fields = [['Symbols Not Found:', not_found, False]]
        error = self.create_embed_msg(header, fields, colour = discord.Colour.red())
        return error

    async def symbols_notuinfo_msg(self, not_in_uinfo):
        header = [
            'Cryptocurrency Information  |  ERROR - NOT STORED:',
            'The symbols shown below could not be found in the user\'s info file. Please use `addcrypto` to add a cryptocurrency to a user\'s info file.'
        ]
        fields = [['Symbols Not Found:', not_in_uinfo, False]]
        error = self.create_embed_msg(header, fields, colour = discord.Colour.red())
        return error

    async def crypto_info_msg_simple(self, member, cinfo):
        messages = []
        fkeys = [{key: cinfo.finfo[key]['symbol']} for key in cinfo.fkeys]
        header = [
                f'Cryptocurrencies Added To {member}\'s Info:',
                f'{fkeys}'
            ]

        found_msg = self.create_embed_msg(header)
        messages.append(found_msg)

        # Creates an 'error' message if 'not_found' contains any
        # symbols that couldn't be found in 'self.data'.
        if len(cinfo.nfound) > 0:
            error = await self.symbols_notfound_msg(cinfo.nfound)
            messages.append(error)

        return messages

    async def crypto_info_msg(self, symbols):
        cinfo = await self.find_crypto_info(symbols)
        messages = []

        # For each pair (name, symbol) in 'found'...
        for index, name in enumerate(cinfo.fkeys):
            # 'info' equals the value of the key in 'found_info' that matches 'name'.
            info = cinfo.finfo[name]
            symbol = info['symbol']

            # Setting price to 2 decimal places.
            price = round(info['quote'][self.rwc]['price'], 2)

            # Convert date/time strings from the cryptocurrencies' info
            # into newly-formatted 'DateTime' strings.
            dateadded_dtconv = self.dtconvert(info['date_added'], type = 'cmc')
            lastupd_dtconv = self.dtconvert(info['last_updated'], type = 'cmc')

            header = f'Cryptocurrency Information: [{symbol}]  |  {index + 1} of {len(cinfo.finfo)}'
            fields = [
                ['`Name:`', info['name'], True],
                ['`Symbol:`', info['symbol'], True],
                ['`ID:`', info['id'], True],
                [f'`Converted To:`', f'{self.rwc}', True],
                [f'`Price:`', f'${price}', True],
                [f'`24H Volume:`', info['quote'][self.rwc]['volume_24h'], True],
                [f'{chr(173)}', '---', False], # Format Spacer; chr(173) is a blank character.
                ['Date Added:', dateadded_dtconv, True],
                ['CMC Rank:', info['cmc_rank'], True],
                ['Number of Market Pairs:', info['num_market_pairs'], True],
                ['Total Supply:', info['total_supply'], True],
                ['Circulating Supply:', info['circulating_supply'], True],
                ['Maximum Supply:', info['max_supply'], True],
                [f'{chr(173)}', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                ['Last Updated:', lastupd_dtconv, False]
            ]
            footer = self.dtformat_return(True)

            info = self.create_embed_msg(header, fields, footer)
            messages.append(info)
        
        # Creates an 'error' message if 'not_found' contains any
        # symbols that couldn't be found in 'self.data'.
        if len(cinfo.nfound) > 0:
            error = await self.symbols_notfound_msg(cinfo.nfound)
            messages.append(error)

        return messages

    async def crypto_top5_msg(self):
        header = [
            'Cryptocurrency  |  Top 5 Ranked Currencies:',
            'The following is information on the top 5 ranked cryptocurriences.'
        ]
        fields = []

        for currency in self.data:

            # Stops after reaching CMC Rank of 6.
            if currency['cmc_rank'] == 6:
                break

            rank = currency['cmc_rank']
            last_updated = currency['last_updated']

            # Setting price to 2 decimal places.
            price = round(currency['quote'][self.rwc]['price'], 2)
            lastupdt_dtconv = self.dtconvert(last_updated, type = 'cmc')
            
            value = '''
                `Name:` **{name}**
                `Symbol:` {symbol}
                `[{rwc}] Price:` ${price}
                `Last Updated:` {lastupdt}'''.format(
                    name = currency['name'],
                    symbol = currency['symbol'],
                    rwc = self.rwc,
                    price = price,
                    lastupdt = lastupdt_dtconv
                )

            fields.append([f'Rank {rank}:', value, False])
        
        footer = self.dtformat_return(True)
        top5 = self.create_embed_msg(header, fields, footer)
        return top5

    async def add_crypto_to_user(self, member, cryptos):
        # 1. Find the specified member's info file path.
        filepath = self.user_filepath(member)
        # 2. Load the member's info.
        info = self.json_load(filepath)
        # 3. Update the 'crypto' key's value to include 'cryptos'.
        info['crypto'].update(cryptos)
        # 4. Dump 'info' back into the member's info file.
        self.json_dump(info, filepath)

    async def compare_crypto(self, member, symbols):
        # Find the user's info.
        uinfo = await self.find_user(member)
        # Store the 'crypto' key's value (cryptocurrencies' info) in 'currencies'.
        currencies = uinfo['crypto']
        # Gather the info of the currencies found and the name and symbol of ones not found in 'self.data'.
        cinfo = await self.find_crypto_info(symbols)
        fkeys = cinfo.fkeys
        # Stores the currencies not in the user's info file.
        not_in_uinfo = {}
        # Contains all the formatted/altered information for each currency.
        comparison_info_all = {}

        # For each currency's name in 'cinfo.finfo's keys (e.g. 'Bitcoin')...
        for currency_name in fkeys:
            # Guarantees a symbol not in 'self.data' doesn't pass through.
            verify = False

            if currency_name in currencies:
                # Cryptocurrency Information
                currency = currencies[currency_name]
                symbol = currency['symbol']
                name = currency['name']
                id = currency['id']
                name_finfo = cinfo.finfo[name]
                # --

                # Cryptocurrency information being stored in 'sinfo' dict.,
                # which is stored in 'comparison_info_all'.
                sinfo = {}
                sinfo['symbol'] = symbol
                sinfo['name'] = name
                sinfo['id'] = id
                # --

                # Comparing "price" total differences.
                price_uinfo = currency['quote'][self.rwc]['price']
                price_finfo = name_finfo['quote'][self.rwc]['price']
                price_tdiff, price_prcnt = await self.compare_diff_val_pairs(
                    [price_uinfo, price_finfo],
                    True,
                    True
                )
                sinfo['price'] = [price_uinfo, price_finfo, price_tdiff, price_prcnt]

                # Comparing "24h volume" total differences.
                volume24h_uinfo = currency['quote'][self.rwc]['volume_24h']
                volume24h_finfo = name_finfo['quote'][self.rwc]['volume_24h']
                volume24h_tdiff, volume24h_prcnt = await self.compare_diff_val_pairs(
                    [volume24h_uinfo, volume24h_finfo],
                    True,
                    True
                )
                sinfo['volume24h'] = [volume24h_uinfo, volume24h_finfo, volume24h_tdiff, volume24h_prcnt]

                # Comparing "CMC rank" total differences.
                cmcrank_uinfo = currency['cmc_rank']
                cmcrank_finfo = name_finfo['cmc_rank']
                cmcrank_tdiff = await self.compare_diff_val_pairs(
                    [cmcrank_uinfo, cmcrank_finfo],
                    False,
                    False
                )
                sinfo['cmcrank'] = [cmcrank_uinfo, cmcrank_finfo, cmcrank_tdiff]

                # Comparing "number of market pairs" total differences.
                nummarkpairs_uinfo = currency['num_market_pairs']
                nummarkpairs_finfo = name_finfo['num_market_pairs']
                nummarkpairs_tdiff, nummarketpairs_prcnt = await self.compare_diff_val_pairs(
                    [nummarkpairs_uinfo, nummarkpairs_finfo],
                    True,
                    True
                )
                sinfo['nummarkpairs'] = [nummarkpairs_uinfo, nummarkpairs_finfo, nummarkpairs_tdiff, nummarketpairs_prcnt]

                # Comparing "total supply" total differences.
                totalsupply_uinfo = currency['total_supply']
                totalsupply_finfo = name_finfo['total_supply']
                totalsupply_tdiff, totalsupply_prcnt = await self.compare_diff_val_pairs(
                    [totalsupply_uinfo, totalsupply_finfo],
                    True,
                    True
                )
                sinfo['totalsupply'] = [totalsupply_uinfo, totalsupply_finfo, totalsupply_tdiff, totalsupply_prcnt]

                # Comparing "circulating supply" total differences.
                circlsupply_uinfo = currency['circulating_supply']
                circlsupply_finfo = name_finfo['circulating_supply']
                circlsupply_tdiff, circlsupply_prcnt = await self.compare_diff_val_pairs(
                    [circlsupply_uinfo, circlsupply_finfo],
                    True,
                    True
                )
                sinfo['circlsupply'] = [circlsupply_uinfo, circlsupply_finfo, circlsupply_tdiff, circlsupply_prcnt]

                # Comparing "max supply" total differences.
                maxsupply_uinfo = currency['max_supply']
                maxsupply_finfo = name_finfo['max_supply']
                maxsupply_tdiff, maxsupply_prcnt = await self.compare_diff_val_pairs(
                    [maxsupply_uinfo, maxsupply_finfo],
                    True,
                    True
                )
                sinfo['maxsupply'] = [maxsupply_uinfo, maxsupply_finfo, maxsupply_tdiff, maxsupply_prcnt]

                # Convert 'Date Added' and 'Last Updated' to DateTime.
                # 'Date Added' value shouldn't ever change.
                dateadded_dtconv = self.dtconvert(currency['date_added'], type = 'cmc')
                lastupd_dtconv_uinfo = self.dtconvert(currency['last_updated'], type = 'cmc')
                lastupd_dtconv_finfo = self.dtconvert(name_finfo['last_updated'], type = 'cmc')
                sinfo['dates'] = [dateadded_dtconv, lastupd_dtconv_uinfo, lastupd_dtconv_finfo]

                verify = True
                comparison_info_all[currency_name] = sinfo
                continue

            # Verify if the currency's info couldn't be found in the user's info file.
            if verify == False:
                not_in_uinfo[currency_name] = cinfo.finfo[currency_name]['symbol']
                continue

        return COMPARE_CRYPTO_RESULTS(self.client, cinfo.nfound, not_in_uinfo, comparison_info_all)

    async def compare_crypto_msg(self, member, symbols):
        sinfo = await self.compare_crypto(member, symbols)
        messages = []

        for index, currency_name in enumerate(sinfo.cmpinfoall):
            currency = sinfo.cmpinfoall[currency_name]
            count = index + 1

            '''
            1. Symbol
            2. Name
            3. ID
            4. Price
            5. 24H Volume
            6. CMC Rank
            7. Number of Market Pairs
            8. Total Supply
            9. Circulating Supply
            10. Max Supply
            11. Dates
            '''
            # 1
            symbol = currency['symbol']
            # 2
            name = currency['name']
            # 3
            id = currency['id']
            # 4
            price_uinfo, price_finfo, price_tdiff, price_prcnt = currency['price']
            # 5
            _, volume24h_finfo, _, volume24h_prcnt = currency['volume24h']
            # 6
            cmcrank_uinfo, cmcrank_finfo, _ = currency['cmcrank']
            # 7
            _, nummarkpairs_finfo, _, nummarketpairs_prcnt = currency['nummarkpairs']
            # 8
            _, totalsupply_finfo, _, totalsupply_prcnt = currency['totalsupply']
            # 9
            _, circlsupply_finfo, _, circlsupply_prcnt = currency['circlsupply']
            # 10
            _, maxsupply_finfo, _, maxsupply_prcnt = currency['maxsupply']
            # 11
            dateadded_dtconv, lastupd_dtconv_uinfo, lastupd_dtconv_finfo = currency['dates']



            header = f'Cryptocurrency Information: [{symbol}]  |  {count} of {len(sinfo.cmpinfoall)}'
            fields = [
                ['`Name:`', name, True],
                ['`Symbol:`', symbol, True],
                ['`ID:`', id, True],
                [f'{chr(173)}', '---', False], # Format Spacer; chr(173) is a blank character.
                [f'`Converted To:`', f'{self.rwc}', True],
                [f'`Current Price:`', f'${price_finfo}', True],
                [f'`Old Price:`', f'${price_uinfo}', True],
                [f'`Total Difference:`', f'${price_tdiff}', True],                    
                [f'`Percent Change:`', f'{price_prcnt}%', True],
                ['`24H Volume:`', f'{volume24h_finfo} | {volume24h_prcnt}%', True],
                [f'{chr(173)}', '---', False], # Format Spacer; chr(173) is a blank character.
                ['Date Added:', dateadded_dtconv, True],
                ['CMC Rank:', f'{cmcrank_uinfo} *>>>* {cmcrank_finfo}', True],
                ['Number of Market Pairs:', f'{nummarkpairs_finfo} | {nummarketpairs_prcnt}%', True],
                ['Total Supply:', f'{totalsupply_finfo} | {totalsupply_prcnt}%', True],
                ['Circulating Supply:', f'{circlsupply_finfo} | {circlsupply_prcnt}%', True],
                ['Maximum Supply:', f'{maxsupply_finfo} | {maxsupply_prcnt}%', True],
                [f'{chr(173)}', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                ['[USER] Last Updated:', lastupd_dtconv_uinfo, False],
                ['[DATA] Last Updated:', lastupd_dtconv_finfo, False]
            ]
            footer = self.dtformat_return(True)

            info = self.create_embed_msg(header, fields, footer)
            messages.append(info)

        # Verify if the currency's info couldn't be found in the user's info file.
        if len(sinfo.nuikeys) > 0:
            error_notuinfo = await self.symbols_notuinfo_msg(sinfo.notuinfo)
            messages.append(error_notuinfo)

        # Verify if none of the currencies' symbols matched the requested symbol.
        if len(sinfo.nfkeys) > 0:
            error_notfound = await self.symbols_notfound_msg(sinfo.nfound)
            messages.append(error_notfound)

        return messages


# -- Cog Setup --
def setup(client):
    client.add_cog(Helper(client))