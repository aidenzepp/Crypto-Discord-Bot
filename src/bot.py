import discord
from discord.ext import commands
from re import L
import random
import time
import json
import os
# --

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '.', intents = intents)


# -- Events --
@client.event
async def on_ready():

    # Creates the 'ALL_USERS_INFO.json' file if it can't be found.
    # If it is found, that means it's already been created with the format below.
    path = 'src/hidden'
    files = os.listdir(path)
    if 'ALL_USERS_INFO.json' not in files:
        info = {}
        info['users'] = []

        with open(f'{path}/ALL_USERS_INFO.json', 'w') as outfile:
            json.dump(info, outfile, indent = 4)

        print('The \'ALL_USERS_INFO.json\' has been created.')


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
        print(f'[cogs.{filename[:-3]}] has been loaded.')



# -- Run --
client.run(api_keys['discord'])
