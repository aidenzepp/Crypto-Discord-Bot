from re import L
import discord
from discord.ext import commands
import random
import time
import json
import os
#--

# -- Load API Keys --
with open('src/secrets.json') as secrets_file: 
    secrets = json.load(secrets_file)
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