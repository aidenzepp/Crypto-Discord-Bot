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



    # -- Events --



    # -- Commands --    


def setup(client):
    client.add_cog(Stocks(client))