from re import L
import discord
from discord.ext import commands
import random
import time
import os
#--

api_keys = {
    'Public': 'WJdQbnsubNK5kn9oQWLFAlBy4zjEXkJe7SSoTEpdMySh+XRQsKKs2aSG',
    'Private': 'eg7TpG6fyhWqHdGU/AHMHSRH3lZPZx6og3ahbYUj234NxRS6sMznp2eJsafzo3J12ulmXlf3iOOIUrMVP0GI4w=='
}

class Stocks(commands.Cog):

    def __init__(self, client, keys = api_keys):
        self.client = client
        self.keys = keys

    # -- Events --


    # -- Commands --


def setup(client):
    client.add_cog(Stocks(client))