from re import L
import discord
from discord.ext import commands
import random
import time
import os
#--

class Information(commands.Cog):

    def __init__(self, client):
        self.client = client



    # -- Events --



    # -- Commands --
    @commands.command(aliases = ['serverinfo', 's-info', 'guild', 'guildinfo'])
    async def server(self, ctx):
        server_name = ctx.guild.name
        description = ctx.guild.description
        owner = ctx.guild.owner
        id = ctx.guild.id
        region = ctx.guild.region
        member_count = ctx.guild.member_count
        icon = ctx.guild.icon_url

        # Deleting the command message.
        await ctx.channel.purge(limit = 1)


        server_info = discord.Embed(
            title = server_name + ' | Server Information:',
            description = description,
            colour = (discord.Colour.blue())
        )

        server_info.set_thumbnail(url = icon)
        
        server_info.set_footer(text = f'Command called by: @{ctx.author}.')

        fields = [
            ['Owner:', owner, False],
            ['ID:', f'||{id}||', False],
            ['Region:', region, True],
            ['Member Count:', member_count, True]
        ]

        # Adding multiple fields.
        for name, value, inline in fields:
            server_info.add_field(name = name, value = value, inline = inline)


        await ctx.send(embed = server_info)



def setup(client):
    client.add_cog(Information(client))