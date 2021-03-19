import discord
from discord.ext import commands
from re import L
import random
import time
import json
import os

from startup.startup import *
# --

# -- Load Secrets --
with open('src/hidden/secrets.json') as f: 
    secrets = json.load(f)
    keys = secrets['keys']
    serverinfo = secrets['server']
    prefix = serverinfo['prefix']
    datastartup = str(serverinfo['datastartup']).upper()


# Runs Terminal Startup (w/ option for confirmations); 'confs' = whether to run confirmations or not.
confs = startup(prefix, datastartup)

# Runs Terminal Confirmations (if requested)
if confs:
    confirmations(prefix)

# --

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = prefix, intents = intents)


# -- Events --
@client.event
async def on_ready():
    onready()



# -- Commands --
@client.command()
async def load(ctx, extension): 
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')



# -- Load Cogs --
loadcogs(client)


# -- Run --
client.run(keys['discord'])
