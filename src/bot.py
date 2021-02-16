import discord
from discord.ext import commands
from re import L
import random
import time
import os
# --


client = commands.Bot(command_prefix = '.')


# -- Events --
@client.event
async def on_ready():
    print('Bot is ready.') 


# -- Commands --


# -- Load Cogs --


# -- Run --
client.run('ODExMjg1NDY2NjQwMDIzNjUy.YCv-eA.IeA6mMJiCtSKLA2EjxR0nXaF1xQ')