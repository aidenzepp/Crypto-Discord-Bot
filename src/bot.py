import discord
from discord.ext import commands
from re import L
import random
import time
import json
import os
# --


client = commands.Bot(command_prefix = '.')


# -- Events --
@client.event
async def on_ready():
    print('Bot is ready.')
    

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


# -- Load Discord API Key --
with open('src/hidden/secrets.json') as f: 
    secrets = json.load(f)
    api_keys = secrets['keys']


# -- Load Cogs --
for filename in os.listdir('src/cogs'):

    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# -- Run --
client.run(api_keys['discord'])
