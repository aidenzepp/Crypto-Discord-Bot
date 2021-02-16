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
for filename in os.listdir('./cogs'):

    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# -- Run --
client.run('ODExMjg1NDY2NjQwMDIzNjUy.YCv-eA.IeA6mMJiCtSKLA2EjxR0nXaF1xQ')
