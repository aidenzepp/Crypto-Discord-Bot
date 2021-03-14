import discord
from discord.ext import commands
from re import L
import random
import time
import json
import os
# --

prefix = '.'

# -- Run Confirmations --
print('[ --- STARTUP CONFIRMATIONS: --- ]')
time.sleep(1.0)
confirm = input('Run confirmations? (y/n) [If not, the bot will startup immediately.]  |  Answer: ')

if (confirm.upper() == 'Y') or (confirm.upper() == 'YES'):
    time.sleep(1.0)
    run_confs = True
    print('---')
    time.sleep(1.0)
else:
    time.sleep(1.0)
    run_confs = False
    print('Commencing immediate startup...')
    time.sleep(0.5)
    print(f'Bot Prefix: \'{prefix}\'')
    time.sleep(1.0)
    print('[ --- STARTUP CONFIRMATIONS: END --- ]')
    time.sleep(1.0)

if run_confs:
    # -- Startup Confirmation --
    startup_confirm = input('[Confirmation] Would you like to start the bot? (y/n)   |  Answer: ')

    if (startup_confirm.upper() == 'Y') or (startup_confirm.upper() == 'YES'):
        time.sleep(1.0)
        print('Request for startup confirmed.')
        time.sleep(1.0)
        print('---')
        time.sleep(1.0)
    else:
        time.sleep(1.0)
        print('Request for startup denied. Exiting bot\'s startup process...')
        time.sleep(1.0)
        print('[ --- STARTUP CONFIRMATIONS: END --- ]')
        time.sleep(1.0)
        print('''

        =====================
         BOT STATUS: OFFLINE
        =====================
        
        '''
        )
        time.sleep(1.0)
        print('[ --- STARTUP CANCELED --- ]')
        exit()

    # -- Prefix Confirmation --
    prefix_confirm = input(f'[Confirmation] Would you like to keep the command prefix set to \'{prefix}\'? (y/n)   |  Answer: ')

    if (prefix_confirm.upper() == 'Y') or (prefix_confirm.upper() == 'YES') and run_confs:
        time.sleep(1.0)
        print(f'Request for maintaining prefix confirmed.')
        time.sleep(0.5)
        print(f'Bot Prefix: \'{prefix}\'')
    else:
        time.sleep(1.0)
        prefix = input('What would you like the command prefix to be set to? ')
        time.sleep(0.5)
        print(f'Bot Prefix: \'{prefix}\'')

    time.sleep(1.0)
    print('[ --- STARTUP CONFIRMATIONS: END --- ]')
    time.sleep(1.0)
    


# --


intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = prefix, intents = intents)


# -- Events --
@client.event
async def on_ready():
    print('''

    =====================
      BOT STATUS: READY
    =====================
    
    '''
    )
    time.sleep(1.0)
    print('[ --- STARTUP COMPLETE --- ]')



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
    keys = secrets['keys']



# -- Load Cogs --
for filename in os.listdir('src/cogs'):

    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f'[cogs.{filename[:-3]}] has been loaded.')



# -- Run --
client.run(keys['discord'])
