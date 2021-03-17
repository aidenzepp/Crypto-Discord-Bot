import discord
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
# --

# -- CoinMarketCap --
class CMC_DATA_REQUEST(commands.Cog):
    def __init__(self, client, url = None, parameters = None, headers = None, filepath = None):
        self.client = client
        self.url = url
        self.parameters = parameters 
        self.headers = headers
        self.filepath = filepath
    
    def request_data(self):
        session = Session()
        session.headers.update(self.headers)

        try:
            response = session.get(self.url, params = self.parameters)
            all_data = json.loads(response.text)

            with open(self.filepath, 'w') as outfile:
                json.dump(all_data, outfile, indent = 4)

        except (ConnectionError, Timeout, TooManyRedirects) as ERROR:
            print('[CMC API] Encountered Error: ' + ERROR)

        return all_data['data']

class FIND_CRYPTO_RESULTS(commands.Cog):
    def __init__(self, client, found_info = {}, not_found = {}):
        self.client = client
        self.finfo = found_info
        self.fkeys = found_info.keys()
        self.nfound = not_found
        self.nfkeys = not_found.keys() 


class COMPARE_CRYPTO_RESULTS(commands.Cog):
    def __init__(self, client, not_found = {}, not_in_uinfo = {}, comparison_info_all = {}):
        self.client = client
        self.nfound = not_found
        self.nfkeys = not_found.keys()
        self.notuinfo = not_in_uinfo
        self.nuikeys = not_in_uinfo.keys()
        self.cmpinfoall = comparison_info_all
        self.ciakeys = comparison_info_all.keys()


def setup(client):
    client.add_cog(FIND_CRYPTO_RESULTS(client))
    client.add_cog(COMPARE_CRYPTO_RESULTS(client))
    client.add_cog(CMC_DATA_REQUEST(client))