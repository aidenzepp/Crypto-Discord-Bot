import discord
from discord.ext import commands

class Test(commands.Cog):

    def __init__(self, client):
        self.client = client

    # -- Commands --
    @commands.command()
    async def test(self, ctx):
        await ctx.send('Command heard. Test successful.')

    
    @commands.command(aliases = ['emoji'])
    async def emoji_test(self, ctx):
        await ctx.send(':white_check_mark:')


def setup(client):
    client.add_cog(Test(client))
