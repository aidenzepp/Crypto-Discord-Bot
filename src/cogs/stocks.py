from re import L
import discord
from discord.ext import commands
import random
import time
import os
#--

class Stocks(commands.Cog):

    def __init__(self, client):
        self.client = client

    # -- Events --


    # -- Commands --


def setup(client):
    client.add_cog(Stocks(client))