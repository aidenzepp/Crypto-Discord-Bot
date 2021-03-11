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

    
# -- Cog Setup --
def setup(client):
    client.add_cog(Helper(client))