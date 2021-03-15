import os
from os import error
import discord
from discord.ext import commands
from typing import Optional
from decimal import *
import json
import time

from discord.member import Member

from cogs.helper import Helper
#--


class Stocks(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.helper = Helper(client)


    # -- Events --

        
    # -- Commands --
    @commands.command(aliases = ['cmc-force', 'data-force', 'load-cmcdata'])
    async def force_load_cmc_data(self, ctx):
        # Force load the CMC data.
        await self.helper.forceload_cmcdata()

        header = [
            '[Successful] Force Load: CoinMarketCap Data',
            'The data from CoinMarketCap has been force loaded into the bot.'
        ]

        confirmation = self.helper.create_embed_msg(header)
        await ctx.send(embed = confirmation)

    @commands.command(aliases = ['crypto-top5', 'crypto-5', 'c-top5'])
    async def crypto_top_5(self, ctx):
        # Check if data is loaded, and load it if it's not.
        await self.helper.check_and_load()
        
        top5 = await self.helper.crypto_top5_msg()
        await ctx.send(embed = top5)

    @commands.command(aliases = ['see-crypto-info', 'see-cinfo', 'seecrypto'])
    async def see_crypto_info(self, ctx, *args):
        # Check if data is loaded, and load it if it's not.
        await self.helper.check_and_load()

        messages = await self.helper.crypto_info_msg(args)
        await self.helper.send_embed_messages(ctx, messages, 0.5)

    @commands.command(aliases = ['add-crypto', 'add-c', 'addcrypto'])
    async def add_crypto_to_uinfo(self, ctx, target: Optional[Member], *args):
        # Check if data is loaded, and load it if it's not.
        await self.helper.check_and_load()
        # Check if the server has been set, and set it if it's not.
        await self.helper.check_server()

        member = target or ctx.author
        cinfo = await self.helper.find_crypto_info(args)

        await self.helper.add_crypto_to_user(member, cinfo.finfo)
        messages = await self.helper.crypto_info_msg_simple(member, cinfo)
        await self.helper.send_embed_messages(ctx, messages, 0.5)

    @commands.command(aliases = ['compare-crypto', 'compare-c', 'comparecrypto', 'compcryp'])
    async def compare_crypto_to_uinfo(self, ctx, target: Optional[Member], *args):
        # Check if data is loaded, and load it if it's not.
        await self.helper.check_and_load()
        # Check if the server has been set, and set it if it's not.
        await self.helper.check_server()

        member = target or ctx.author
        messages = await self.helper.compare_crypto_msg(member, args)
        await self.helper.send_embed_messages(ctx, messages, 0.5)


# -- Cog Setup --
def setup(client):
    client.add_cog(Stocks(client))