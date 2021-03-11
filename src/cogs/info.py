import discord
from discord import user
from discord.ext import commands
import json
import os

from cogs.helper import Helper
#--

class Information(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.helper = Helper(client)


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

        header = [
            f'{server_name}  |  Server Information:',
            description
        ]

        fields = [
            ['Owner:', owner, False],
            ['ID:', f'||{id}||', False],
            ['Region:', region, True],
            ['Member Count:', member_count, True]
        ]

        footer = f'Command called by: @{ctx.author}.'

        server_info = self.helper.create_embed_msg(header, fields, footer)
        server_info.set_thumbnail(url = icon)
        await ctx.send(embed = server_info)
    
    @commands.command(aliases = ['add-user-info', 'add-uinfo', 'adduser'])
    async def add_user_info(self, ctx, member: discord.Member):
        # Check if the user's info file has already been created.
        verify = await self.helper.find_user(member)
        if verify != None:
            header = [
                f'{member}  |  User Info:',
                'This user is already in the system.'
            ]
            response = self.helper.create_embed_msg(header)
            return await ctx.send(embed = response)

        await self.helper.make_user(member)

        # Sends a message w/ user's info.
        user_info = await self.helper.user_info_msg(member)
        await ctx.send(embed = user_info)

    @commands.command(aliases = ['see-user-info', 'see-uinfo', 'seeuser'])
    async def see_user_info(self, ctx, member: discord.Member):
        # Sends error message if the user's info file can not be found.
        verify = await self.helper.find_user(member)
        if verify == None:
            header = [
                f'{member}  |  User Info:',
                'The above user could not be found in the system. Please use the `adduser` command to add this user to the system.'
            ]
            error = self.helper.create_embed_msg(header, colour = discord.Colour.red())
            return await ctx.send(embed = error)

        # Sends a message w/ user's info.
        user_info = await self.helper.user_info_msg(member)
        await ctx.send(embed = user_info)


# -- Cog Setup --
def setup(client):
    client.add_cog(Information(client))