import discord
from discord.ext import commands
from re import L
import random
import time
import json
import os
# --

# -- Load Discord API Key --
with open('src/hidden/secrets.json') as f: 
    secrets = json.load(f)
    keys = secrets['keys']
    serverinfo = secrets['server']
    prefix = serverinfo['prefix']

# -- Run Confirmations --
print('[ --- STARTUP CONFIRMATIONS: --- ]')
time.sleep(1.0)
confirm = input('Run confirmations? (y/n) [If not, the bot will startup immediately.]  |  Answer: ')
time.sleep(1.0)

if (confirm.upper() == 'Y') or (confirm.upper() == 'YES'):
    run_confs = True
    print('---')
    time.sleep(1.0)
else:
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
    time.sleep(1.0)

    if (startup_confirm.upper() == 'Y') or (startup_confirm.upper() == 'YES'):
        print('Request for startup confirmed.')
        time.sleep(1.0)
        print('---')
        time.sleep(1.0)
    else:
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
    time.sleep(1.0)

    if (prefix_confirm.upper() == 'Y') or (prefix_confirm.upper() == 'YES'):
        print(f'Request for maintaining prefix confirmed.')
        time.sleep(0.5)
        print(f'Bot Prefix: \'{prefix}\'')
        prefix_perm = False
        time.sleep(1.0)
        print('---')
    else:
        prefix = input('What would you like the command prefix to be set to?   |  Prefix: ')
        time.sleep(1.0)
        prefix_perm_confirm = input('Would you like the specified prefix to be a permanent change? (y/n)   |  Answer: ')
        if (prefix_perm_confirm.upper() == 'Y') or (prefix_perm_confirm.upper() == 'YES'):
            prefix_perm = True
        else:
            prefix_perm = False
        time.sleep(0.5)
        print(f'Bot Prefix: \'{prefix}\'')
        time.sleep(1.0)
        print('---')

    # -- CMC Data Confirmation --
    time.sleep(1.0)
    print('** Note: The following decision will be saved for future reference. **')
    time.sleep(1.0)
    data_confirm = input(f'[Confirmation] Would you like to load the CoinMarketCap data on startup? (y/n)   |  Answer: ')
    time.sleep(1.0)

    if (data_confirm.upper() == 'Y') or (data_confirm.upper() == 'YES'):
        print('Request for data load on startup confirmed.')
        data_perm = True
        time.sleep(1.0)
    else:
        print('The CoinMarketData will not be loaded on startup. Please use the \'load-cmcdata\' command to load the data manually.')
        data_perm = False
        time.sleep(1.0)

    
    # -- Dump Data --
    with open('src/hidden/secrets.json', 'w') as outfile:
        if prefix_perm:
            serverinfo['prefix'] = prefix
            serverinfo['datastartup'] = data_perm
        else:
            serverinfo['datastartup'] = data_perm

        json.dump(secrets, outfile, indent = 4)


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



# -- Load Cogs --
for filename in os.listdir('src/cogs'):

    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f'[cogs.{filename[:-3]}] has been loaded.')



# -- Run --
client.run(keys['discord'])
