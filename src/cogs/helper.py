import discord
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
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
            * discord.Colour.blue()
        > cmcdata_error_msg(solutions)
            * solutions = False

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
        > [ASYNC] add_crypto_to_user(member, cryptos)
            * member: type() == discord.Member
            * cryptos = information of cryptocurrencies being added to the user's info file; type() == dict
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

            with open(f'{self.hidden}//CMC_data.json', 'w') as f:
                json.dump(data, f, indent = 4)

        except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
            print('[CMC API] Encountered Error: ' + ERROR)
        # --

    def __repr__(self):
        pass

    def __str__(self):
        pass


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

    
    # -- File & Folder Paths --
    @property
    def cmc_filepath(self):
        return f'{self.hidden}/CMC_data.json'

    @property
    def usersinfo_dir(self):
        return f'{self.hidden}/ALL_USERS_INFO'


    # -- Discord Embed Messages --
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
        contents['crypto'] = []
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

    async def add_crypto_to_user(self, member, cryptos):
        # Finds user's info file, loads it, attaches
        # cryptocurrency info to user's info, then
        # dumps the info's contents back into file.
        filepath = self.user_filepath(member)
        info = self.json_load(filepath)
        info['crypto'] = cryptos
        self.json_dump(info, filepath)

    
# -- Cog Setup --
def setup(client):
    client.add_cog(Helper(client))