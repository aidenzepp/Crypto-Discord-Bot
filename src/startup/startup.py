import json
import time
import os
# --


with open('src/startup/startup.json') as f1:
    startlog = json.load(f1)
    secretsfile = startlog['filepath']
    responses = startlog['responses']
    rconfirm = responses['confirm']
    rdecline = responses['decline']

with open(secretsfile) as f2:
    secrets = json.load(f2)
    serverinfo = secrets['server']

botprefix = (lambda x: f'Bot Prefix: \'{x}\'')

# -- Initial Startup --
def startup(prefix, datastartup):
    # I. Startup Header
    print(startlog['startup_start'])
    time.sleep(0.5)

    # II. Settings
    for index, line in enumerate(startlog['settings']):
        if index == 2:
            print(f'1. {botprefix(prefix)}')
        elif index == 3:
            print(f'2. Load Data on Startup: {datastartup}')
        else:
            print(line)
    time.sleep(1.0)

    # III. Startup Process Option
    confirm = (input(startlog['run']['input'])).upper()
    time.sleep(1.0)

    # III.I Check 'Startup Process' Input
    if confirm in rconfirm:
        run_confs = True
        print('---')
        time.sleep(1.0)
    else:
        run_confs = False
        print('Commencing immediate startup...')
        time.sleep(0.5)
        print('\n[ --- STARTUP CONFIRMATIONS: END --- ]\n')
        time.sleep(1.0)
    
    # Return decision.
    return run_confs

# -- Confirmations --
def confirmations(prefix):
    # I. Startup
    startup = (input('[Confirmation] Would you like to start the bot? (y/n)   |  Answer: ')).upper()
    time.sleep(1.0)

    # I.I Check 'Startup' Input
    if_startup = startlog['startup']['if_startup']

    if startup in rconfirm:
        for line in if_startup['true']:
            print(line)
            time.sleep(1.0)
    else:
        for index, line in enumerate(if_startup['false']):
            if index != (3, 4):
                print(line)
                time.sleep(1.0)
            else:
                print(line)

        # Exit the program (i.e. 'bot.py').
        exit()

    # II. Prefix
    keep_prefix = (input(f'[Confirmation] Would you like to keep the command prefix set to \'{prefix}\'? (y/n)   |  Answer: ')).upper()
    time.sleep(1.0)

    # II.I Check 'Maintain Prefix' Input
    if_prefix = startlog['prefix']['if_prefix']
    if keep_prefix in rconfirm:
        prefix_perm = False
        for index, line in enumerate(if_prefix['true']):
            if index == 1:
                print(botprefix(prefix))
            else:
                print(line)
            time.sleep(1.0)
    
    # II.II Set New Prefix
    else:
        prefix = (input('What would you like the command prefix to be set to?   |  Prefix: ')).upper()
        time.sleep(1.0)

        # II.III Set Prefix Permanence
        permanent = (input('Would you like the specified prefix to be a permanent change? (y/n)   |  Answer: ')).upper()
        time.sleep(1.0)

        # II.IV Check 'Permanence' Input
        if_permanent = if_prefix['false']['permanent']['if_permanent']
        if permanent in rconfirm:
            prefix_perm = True
            print(if_permanent['true'])
            time.sleep(0.5)
        else:
            prefix_perm = False
            print(if_permanent['false'])
            time.sleep(0.5)
        
        # II.V Display Bot Prefix
        print(botprefix(prefix))
        time.sleep(1.0)
        print('---')
        time.sleep(1.0)

    # III. CMC Data
    print('** Note: The following decision will be saved for future reference. **')
    time.sleep(1.0)
    data = (input('[Confirmation] Would you like to load the CoinMarketCap data on startup? (y/n)   |  Answer: ')).upper()
    time.sleep(1.0)

    # III.I Check 'Data' Input
    if_data = startlog['data']['if_data']
    if data in rconfirm:
        data_startup = True
        print('Request for data load on startup confirmed.')
        time.sleep(1.0)
    else:
        data_startup = False
        for line in if_data['false']:
            print(line)
            time.sleep(1.0)

    # IV. Dump Data
    with open(secretsfile, 'w') as outfile:
        # IV.I Check Prefix Permanence
        if prefix_perm:
            serverinfo['prefix'] = prefix
            serverinfo['datastartup'] = data_startup
        else:
            serverinfo['datastartup'] = data_startup

        # IV.II Dump Contents Back To File
        json.dump(secrets, outfile, indent = 4)
        print(startlog['preferences'])
        time.sleep(1.0)

    # V. Startup Footer
    print(startlog['startup_end'])
    time.sleep(1.0)

# -- On Ready --
def onready():
    for index, line in enumerate(startlog['onready']):
        if index < 2:
            print(line)
        else:
            print(line)
            time.sleep(1.0)

# -- Load Cogs --
def loadcogs(client, directory = 'src/cogs'):
    # Terminal Print-Out: Start
    for line in startlog['cogs'][:2]:
        print(line)
        time.sleep(0.75)

    # Process for loading cogs.
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            cog = f'cogs.{filename[:-3]}'
            client.load_extension(cog)
            print(f'--> [{cog}] has been loaded.')

    # Terminal Print-Out: End
    for line in startlog['cogs'][-2:]:
        print(line)
        time.sleep(0.75)
