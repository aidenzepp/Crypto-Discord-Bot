import discord
from discord.ext import commands
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os
#--

class Helper(commands.Cog):

    def __init__(self, client):
        self.client = client

    
# -- Cog Setup --
def setup(client):
    client.add_cog(Helper(client))