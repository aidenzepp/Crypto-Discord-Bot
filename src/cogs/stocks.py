import os
from os import error
import discord
from discord.ext import commands
from decimal import *
import json
import time

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
    async def see_crypto_info(self, ctx, *, crypto_symbols):
        await self.helper.check_and_load()

        # Making input symbols case-insensitive.
        requested_symbols = crypto_symbols.upper().split(' ')
        symbols_not_found = []

        if len(requested_symbols) == 0:
            header = [
                'Cryptocurrency Information  |  ERROR:',
                'Please call the `seecrypto` command along with the desired crytocurrencies\' symbols.'
            ]

            no_symbols_error = self.helper.create_error_msg(header, colour = discord.Colour.red())
            return await ctx.send(embed = no_symbols_error)

        i = 1
        for symbol in requested_symbols:
            # Using 'verify' to add a symbol not found in 'data'.
            # Otherwise, it would add every symbol.
            verify = False

            for currency in self.helper.data:

                if currency['symbol'] == symbol:

                    header = f'Cryptocurrency Information: [{symbol}]  |  {i} of {len(requested_symbols)}'

                    # Setting price to 2 decimal places.
                    price = round(currency['quote'][self.helper.rwc]['price'], 2)
                    dateadded_dtconv = self.helper.dtconvert(currency['date_added'], type = 'cmc')
                    lastupd_dtconv = self.helper.dtconvert(currency['last_updated'], type = 'cmc')

                    fields = [
                        ['`Name:`', currency['name'], True],
                        ['`Symbol:`', currency['symbol'], True],
                        ['`ID:`', currency['id'], True],
                        [f'`[{self.helper.rwc}] Price:`', f'${price}', True],
                        [f'`[{self.helper.rwc}] 24H Volume:`', currency['quote'][self.helper.rwc]['volume_24h'], True],
                        [f'{chr(173)}', '---', False], # Format Spacer; chr(173) is a blank character.
                        ['Date Added:', dateadded_dtconv, True],
                        ['CMC Rank:', currency['cmc_rank'], True],
                        ['Number of Market Pairs:', currency['num_market_pairs'], False],
                        ['Total Supply:', currency['total_supply'], True],
                        ['Circulating Supply:', currency['circulating_supply'], True],
                        ['Maximum Supply:', currency['max_supply'], True],
                        [f'{chr(173)}', f'{chr(173)}', False], # Format Spacer; chr(173) is a blank character.
                        ['Last Updated:', lastupd_dtconv, False]
                    ]

                    footer = self.helper.dtformat_return(True)
                    currency_info = self.helper.create_embed_msg(header, fields, footer)

                    verify = True
                    i += 1
                    time.sleep(0.5)
                    await ctx.send(embed = currency_info)
            
            if verify == False:
                symbols_not_found.append(symbol)
                continue
    
    
        # Symbols Not Found - Error Message
        if len(symbols_not_found) > 0:
            header = 'Cryptocurrency Information  |  ERROR:'
            fields = [['Symbols Not Found:', symbols_not_found, False]]
            not_found_error = self.helper.create_embed_msg(header, fields, colour = discord.Colour.red())

            time.sleep(0.5)
            await ctx.send(embed = not_found_error)

    @commands.command(aliases = ['add-crypto-self', 'add-cself', 'cryptoself'])
    async def add_crypto_to_uinfo(self, ctx, *, crypto_symbols):
        await self.helper.check_and_load()

        # Making input symbols case-insensitive.
        requested_symbols = crypto_symbols.upper().split(' ')
        symbols_not_found = []
        symbols_found = []
        symbols_found_info = {}

        # Iterate through symbols, find cryptocurrencies w/ matching symbols.
        # If such cryptocurrencies are found, add to the user's info file.
        # If not, add to 'symbols_not_found' list.
        for symbol in requested_symbols:
            verify = False

            for currency in self.helper.data:

                if currency['symbol'] == symbol:
                    name = currency['name']
                    symbols_found_info[f'{name}'] = currency

                    symbols_found.append(symbol)

                    verify = True
                    continue
            
            if verify == False:
                symbols_not_found.append(symbol)
                continue
        # --

        # If only 1 symbol is inputted and not found, a
        # faulty message is sent, which is unintentional.
        if len(symbols_found) != 0:  
            await self.helper.add_crypto_to_user(ctx.author, symbols_found_info)

            header = [
                f'Cryptocurrencies Added To {ctx.author}\'s Info:',
                f'{symbols_found}'
            ]

            added_cryptos = self.helper.create_embed_msg(header)
            await ctx.send(embed = added_cryptos)

        # Symbols Not Found - Error Message
        if len(symbols_not_found) > 0:
            header = 'Cryptocurrency Information  |  ERROR:'
            fields = [['Symbols Not Found:', symbols_not_found, False]]
            error = self.helper.create_embed_msg(header, fields, colour = discord.Colour.red())

            time.sleep(0.5)
            await ctx.send(embed = error)


# -- Cog Setup --
def setup(client):
    client.add_cog(Stocks(client))