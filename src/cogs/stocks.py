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
    async def force_load__cmc_data(self, ctx):
        with open(self.helper.cmc_filepath) as CMC_data:
            all_data = json.load(CMC_data)
            self.data = all_data['data']

        header = [
            '[Successful] Force Load: CoinMarketCap Data',
            'The data from CoinMarketCap has been force loaded into the bot.'
        ]

        confirmation = self.helper.create_embed_msg(header)
        await ctx.send(embed = confirmation)
        return self.data

    @commands.command(aliases = ['crypto-top5', 'crypto-5', 'c-top5'])
    async def crypto_top_5(self, ctx):
        await self.helper.check_and_load()

        header = [
            'Cryptocurrency  |  Top 5 Ranked Currencies:',
            'The following is information on the top 5 ranked cryptocurriences.'
        ]
        fields = []

        for currency in self.helper.data:

            # Stops after reaching CMC Rank of 6.
            if currency['cmc_rank'] == 6:
                break

            name = currency['name']
            symbol = currency['symbol']
            rank = currency['cmc_rank']
            last_updated = currency['last_updated']

            # Setting price to 2 decimal places.
            price = round(currency['quote'][self.helper.rwc]['price'], 2)
            lastupd_dtconv = self.helper.dtconvert(last_updated, type = 'cmc')

            fields.append([
                f'Rank {rank}:',
                '''
                `Name:` **{name}**
                `Symbol:` {symbol}
                `[{rwc}] Price:` ${price}
                `Last Updated:` {lastupd_dtconv}'''
                .format(name = name, symbol = symbol, rwc = self.helper.rwc, price = price, lastupd_dtconv = lastupd_dtconv),
                False
            ])
        
        footer = self.helper.dtformat_return(True)
        top_5 = self.helper.create_embed_msg(header, fields, footer)
        await ctx.send(embed = top_5)

    @commands.command(aliases = ['see-crypto-info', 'see-cinfo', 'seecrypto'])
    async def see_crypto_info(self, ctx, *args):
        await self.helper.check_and_load()

        messages, not_found = await self.helper.crypto_info_msg(args)

        for message in messages:
            time.sleep(0.5)
            await ctx.send(embed = message)
    
        # Symbols Not Found - Error Message
        if len(not_found) > 0:
            header = 'Cryptocurrency Information  |  ERROR:'
            fields = [['Symbols Not Found:', not_found, False]]
            not_found_error = self.helper.create_embed_msg(header, fields, colour = discord.Colour.red())

            time.sleep(0.5)
            await ctx.send(embed = not_found_error)

    @commands.command(aliases = ['add-crypto', 'add-c', 'addcrypto'])
    async def add_crypto_to_uinfo(self, ctx, target: Optional[Member], *args):
        await self.helper.check_and_load()
        await self.helper.check_server()

        member = target or ctx.author
        found, found_info, not_found = await self.helper.find_crypto_info(args)

        # Error occurs w/ 1 crypto-symbol input and it not being found.
        if len(found) != 0:  
            await self.helper.add_crypto_to_user(member, found_info)

            header = [
                f'Cryptocurrencies Added To {member}\'s Info:',
                f'{found}'
            ]

            added_cryptos = self.helper.create_embed_msg(header)
            await ctx.send(embed = added_cryptos)

        # Symbols Not Found - Error Message
        if len(not_found) > 0:
            error = self.helper.symbols_notfound_msg(not_found)
            time.sleep(0.5)
            await ctx.send(embed = error)

    @commands.command(aliases = ['compare-crypto', 'compare-c', 'comparecrypto', 'compcryp'])
    async def compare_crypto_to_uinfo(self, ctx, target: Optional[Member], *args):
        await self.helper.check_and_load()
        await self.helper.check_server()

        member = target or ctx.author
        messages = await self.helper.compare_crypto_msg(member, args)

        for message in messages:
            time.sleep(0.5)
            await ctx.send(embed = message)


# -- Cog Setup --
def setup(client):
    client.add_cog(Stocks(client))