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

    - DISCORD -
        > create_embed_message(header, fields, footer, colour)
            * header = None
            * fields = None
            * footer = None
            * colour = discord.Colour.blue()
        > cmcdata_error_msg(solutions)
            * solutions = False
        > set_server

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
        > [ASYNC] crypto_info_msg(symbols)
            * symbols: the symbols of requested cryptocurrencies; type() == tuple
        > [ASYNC] add_crypto_to_user(member, cryptos)
            * member: type() == discord.Member
            * cryptos: information of cryptocurrencies being added to the user's info file; type() == dict
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

        if round and (prcnt != None):
            prcnt_rounded = round(prcnt, round_val)
            return prcnt_rounded
        else:
            return prcnt

    async def compare_diff_val_pairs(self, values, round_output = True, calc_prcnt = False, round_val = 2):
        val_1, val_2 = values
        diff = val_2 - val_1
        diff_rounded = round(diff, round_val)
        prcnt_change = await self.prcnt_change(diff, val_1, round_output, round_val)

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
                [f'`Converted To:`', f'{self.rwc}', False],
                [f'`[{self.rwc}] Price:`', f'${price}', True],
                [f'`24H Volume:`', info['quote'][self.rwc]['volume_24h'], True],
                [f'{chr(173)}', '---', False], # Format Spacer; chr(173) is a blank character.
                ['Date Added:', dateadded_dtconv, True],
                ['CMC Rank:', info['cmc_rank'], True],
                ['Number of Market Pairs:', info['num_market_pairs'], False],
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

        return messages, not_found

    async def add_crypto_to_user(self, member, cryptos):
        # Finds user's info file, loads it, attaches
        # cryptocurrency info to user's info, then
        # dumps the info's contents back into file.
        filepath = self.user_filepath(member)
        info = self.json_load(filepath)
        info['crypto'].update(cryptos)
        self.json_dump(info, filepath)

    async def symbols_notfound_msg(self, not_found):
        header = 'Cryptocurrency Information  |  ERROR:'
        fields = [['Symbols Not Found:', not_found, False]]
        error = self.create_embed_msg(header, fields, colour = discord.Colour.red())
        return error

    async def compare_crypto_msg(self, member, symbols):
        uinfo = await self.find_user(member)
        currencies = uinfo['crypto']
        found, found_info, not_found = await self.find_crypto_info(symbols)
        messages = []
        i = 1

        for currency in currencies:
            if currency in found_info.keys():
                currency = currencies[currency]
                symbol = currency['symbol']
                name = currency['name']
                name_finfo = found_info[name]

                # Setting "price" to 2 decimal places. Comparing "price" total differences.
                price_uinfo = round(currency['quote'][self.rwc]['price'], 2)
                price_finfo = round(name_finfo['quote'][self.rwc]['price'], 2)
                price_tdiff, price_prcnt = await self.compare_diff_val_pairs(
                    [price_uinfo, price_finfo],
                    True,
                    True
                )

                # Comparing "24h volume" total differences.
                volume24h_uinfo = currency['quote'][self.rwc]['volume_24h']
                volume24h_finfo = name_finfo['quote'][self.rwc]['volume_24h']
                volume24h_tdiff, volume24h_prcnt = await self.compare_diff_val_pairs(
                    [volume24h_uinfo, volume24h_finfo],
                    True,
                    True
                )

                # Comparing "CMC rank" total differences.
                cmcrank_uinfo = currency['cmc_rank']
                cmcrank_finfo = name_finfo['cmc_rank']
                cmcrank_tdiff = await self.compare_diff_val_pairs(
                    [cmcrank_uinfo, cmcrank_finfo],
                    False,
                    False
                )

                # Comparing "number of market pairs" total differences.
                nummarkpairs_uinfo = currency['num_market_pairs']
                nummarkpairs_finfo = name_finfo['num_market_pairs']
                nummarkpairs_tdiff, nummarketpairs_prcnt = await self.compare_diff_val_pairs(
                    [nummarkpairs_uinfo, nummarkpairs_finfo],
                    True,
                    True
                )

                # Comparing "total supply" total differences.
                totalsupply_uinfo = currency['total_supply']
                totalsupply_finfo = name_finfo['total_supply']
                totalsupply_tdiff, totalsupply_prcnt = await self.compare_diff_val_pairs(
                    [totalsupply_uinfo, totalsupply_finfo],
                    True,
                    True
                )

                # Comparing "circulating supply" total differences.
                circlsupply_uinfo = currency['circulating_supply']
                circlsupply_finfo = name_finfo['circulating_supply']
                circlsupply_tdiff, circlsupply_prcnt = await self.compare_diff_val_pairs(
                    [circlsupply_uinfo, circlsupply_finfo],
                    True,
                    True
                )

                # Comparing "max supply" total differences.
                maxsupply_uinfo = currency['max_supply']
                maxsupply_finfo = name_finfo['max_supply']
                maxsupply_tdiff, maxsupply_prcnt = await self.compare_diff_val_pairs(
                    [maxsupply_uinfo, maxsupply_finfo],
                    True,
                    True
                )

                # Convert 'Date Added' and 'Last Updated' to DateTime.
                # 'Date Added' value shouldn't ever change.
                dateadded_dtconv = self.dtconvert(currency['date_added'], type = 'cmc')
                lastupd_dtconv_uinfo = self.dtconvert(currency['last_updated'], type = 'cmc')
                lastupd_dtconv_finfo = self.dtconvert(name_finfo['last_updated'], type = 'cmc')


                header = f'Cryptocurrency Information: [{symbol}]  |  {i} of {len(found_info)}'
                fields = [
                    ['`Name:`', currency['name'], True],
                    ['`Symbol:`', currency['symbol'], True],
                    ['`ID:`', currency['id'], True],
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
                    ['Maximum Supply:', f'{maxsupply_finfo} | {maxsupply_prcnt}', True],
                    [f'{chr(173)}', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                    ['[USER] Last Updated:', lastupd_dtconv_uinfo, False],
                    ['[DATA] Last Updated:', lastupd_dtconv_finfo, False]
                ]
                footer = self.dtformat_return(True)
                info = self.create_embed_msg(header, fields, footer)

                i += 1
                messages.append(info)

        return messages, not_found


# -- Cog Setup --
def setup(client):
    client.add_cog(Helper(client))