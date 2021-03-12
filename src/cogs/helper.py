from operator import not_
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
        # Because the code above is inserted this way,
        # the 'keys' object can be accessed using 'self.keys'.
        
    def __init__(self, client):
        self.client = client
        self.hidden = 'src/hidden' # Path for the 'hidden' folder.
        self.cogs = 'src/cogs' # Path for the 'cogs' folder.
        self.data = None
        self.rwc = 'USD' # 'rwc' = Real World Currency; the currency that the cryptocurrency will be converted to.

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

            with open(f'{self.hidden}//CMC_data.json', 'w') as f:
                json.dump(data, f, indent = 4)

        except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
            print('[CMC API] Encountered Error: ' + ERROR)
        # --

    def __repr__(self):
        pass

    def __str__(self):
        pass
        

    # -- File & Folder Paths --
    @property
    def cmc_filepath(self):
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
        # Check if the denominator is '0'.
        try:
            prcnt = (diff / denom) * 100
        except ZeroDivisionError:
            prcnt = None

        if round_output and (prcnt != None):
            prcnt_rounded = round(prcnt, round_val)
            return prcnt_rounded
        else:
            return prcnt

    async def compare_diff_val_pairs(self, values, round_output = True, calc_prcnt = False, round_val = 2):
        val_1, val_2 = values
        try:
            diff = val_2 - val_1
            diff_rounded = round(diff, round_val)
            prcnt_change = await self.prcnt_change(diff, val_1, round_output, round_val)
        except TypeError:
            diff = None
            prcnt_change = None
            return diff, prcnt_change

        if round_output and calc_prcnt:
            return diff_rounded, prcnt_change
        elif round_output:
            return diff_rounded
        elif prcnt_change:
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
        if kwargs.get('type') == 'dis':
            dt_obj = dt.datetime.strptime(input[:-7], '%Y-%m-%d %H:%M:%S')
        elif kwargs.get('type') == 'cmc':
            dt_obj = dt.datetime.strptime(input[:-5], self.dtformat_default())
        else:
            dt_obj = dt.datetime.strptime(input, self.dtformat_default())

        if kwargs.get('format') == None:
            converted = dt.datetime.strftime(dt_obj, self.dtformat_return())
        else:
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
        if (header == None) or (len(header) == 0):
            print('The header values have been left blank. Check command call.')
            return

        # Check if there's a description.
        # Format is incorrect if 'title = header' but 'type(header) == list'.
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

    def cmcdata_error_msg(self, solutions = False):
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

            if i < 2: # Highlight 1st and 2nd keys.
                name = f'`{name}`'
            elif i == 2: # Highlight 3rd key, make uppercase, and hide value.
                name = f'`{name.upper()}`'
                value = f'||{value}||'
            elif (i == 3) or (i == 6): # Give 4th and 6th keys 'inline = False'.
                inline = False
        
            fields.append([name, value, inline])
        
        msg = self.create_embed_msg(header, fields)
        return msg

    async def make_user(self, member):
        info = self.create_user_contents(member)
        filepath = self.user_filepath(member)
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

    async def find_crypto_info(self, symbols):
        symbols = [symbol.upper() for symbol in symbols]
        not_found = []
        found = []
        found_info = {}

        for symbol in symbols:
            verify = False

            for currency in self.data:
                if currency['symbol'] == symbol:
                    name = currency['name']
                    found_info[name] = currency
                    found.append([name, symbol])

                    verify = True
                    continue
            
            if verify == False:
                not_found.append(symbol)
                continue

        return found, found_info, not_found

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

    async def crypto_info_msg_simple(self, member, found, not_found):
        messages = []
        header = [
                f'Cryptocurrencies Added To {member}\'s Info:',
                f'{found}'
            ]

        found_msg = self.create_embed_msg(header)
        messages.append(found_msg)

        if len(not_found) > 0:
            error = await self.symbols_notfound_msg(not_found)
            messages.append(error)

        return messages

    async def crypto_info_msg(self, symbols):
        found, found_info, not_found = await self.find_crypto_info(symbols)
        messages = []
        i = 1

        for name, symbol in found:
            info = found_info[name]

            # Setting price to 2 decimal places.
            price = round(info['quote'][self.rwc]['price'], 2)
            dateadded_dtconv = self.dtconvert(info['date_added'], type = 'cmc')
            lastupd_dtconv = self.dtconvert(info['last_updated'], type = 'cmc')

            header = f'Cryptocurrency Information: [{symbol}]  |  {i} of {len(found)}'
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

            i += 1
            messages.append(info)
        
        if len(not_found) > 0:
            error = await self.symbols_notfound_msg(not_found)
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
        # Finds user's info file, loads it, attaches
        # cryptocurrency info to user's info, then
        # dumps the info's contents back into file.
        filepath = self.user_filepath(member)
        info = self.json_load(filepath)
        info['crypto'].update(cryptos)
        self.json_dump(info, filepath)

    async def compare_crypto(self, member, symbols):
        uinfo = await self.find_user(member)
        currencies = uinfo['crypto']
        found, found_info, not_found = await self.find_crypto_info(symbols)
        not_in_uinfo = []

        # Contains all the formatted/altered information for each currency.
        special_info_all = []

        for currency in found_info.keys():
            verify = False

            if currency in currencies:
                currency = currencies[currency]
                symbol = currency['symbol']
                name = currency['name']
                id = currency['id']
                name_finfo = found_info[name]

                sinfo = {}
                sinfo['symbol'] = symbol
                sinfo['name'] = name
                sinfo['id'] = id

                # Setting "price" to 2 decimal places. Comparing "price" total differences.
                price_uinfo = round(currency['quote'][self.rwc]['price'], 2)
                price_finfo = round(name_finfo['quote'][self.rwc]['price'], 2)
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
                special_info_all.append(sinfo)
                continue

            if verify == False:
                not_in_uinfo.append(currency)
                continue

        return special_info_all, not_in_uinfo, not_found

    async def compare_crypto_msg(self, member, symbols):
        all_sinfo, not_in_uinfo, not_found = await self.compare_crypto(member, symbols)
        messages = []
        i = 1

        for currency in all_sinfo:
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
            volume24h_uinfo, volume24h_finfo, volume24h_tdiff, volume24h_prcnt = currency['volume24h']
            # 6
            cmcrank_uinfo, cmcrank_finfo, cmcrank_tdiff = currency['cmcrank']
            # 7
            nummarkpairs_uinfo, nummarkpairs_finfo, nummarkpairs_tdiff, nummarketpairs_prcnt = currency['nummarkpairs']
            # 8
            totalsupply_uinfo, totalsupply_finfo, totalsupply_tdiff, totalsupply_prcnt = currency['totalsupply']
            # 9
            circlsupply_uinfo, circlsupply_finfo, circlsupply_tdiff, circlsupply_prcnt = currency['circlsupply']
            # 10
            maxsupply_uinfo, maxsupply_finfo, maxsupply_tdiff, maxsupply_prcnt = currency['maxsupply']
            # 11
            dateadded_dtconv, lastupd_dtconv_uinfo, lastupd_dtconv_finfo = currency['dates']



            header = f'Cryptocurrency Information: [{symbol}]  |  {i} of {len(all_sinfo)}'
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
            i += 1

        if len(not_in_uinfo) > 0:
            error_notuinfo = await self.symbols_notuinfo_msg(not_in_uinfo)
            messages.append(error_notuinfo)

        if len(not_found) > 0:
            error_notfound = await self.symbols_notfound_msg(not_found)
            messages.append(error_notfound)
            
        return messages


# -- Cog Setup --
def setup(client):
    client.add_cog(Helper(client))