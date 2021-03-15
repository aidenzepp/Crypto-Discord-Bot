from typing import Optional
import discord
from discord import user
from discord.member import Member
from discord.ext import commands
import json
import os

from cogs.helper import Helper
#--
'''
I. Description:
    - Stores user-callable functions that relay, store, or have some other process which is heavily related to information.

II. 'Optional[Member]':
    - Seen frequently in the functions' parameters as 'member: Optional[Member]'.
    - Allows the user calling the command to choose whether to include a target.
        * The chosen 'target' is passed throughout the command as a 'discord.Member' class.
    - If a target is specified, the command uses that target's info. If not, the command uses the author of the command call (the message).
        >>> Command Call: (w/ no target specified)  |  As would be seen if looking at a Discord server's text-channel chat.
            @ExampleUser
            .seeuser

            --> Using this format, the 'target' in the 'see_user_info' command becomes the 'ctx.author'.
            --> In this case, the 'target' would be '@ExampleUser'.
            --> '@ExampleUser' would be passed into the function as a 'discord.Member' type.
        >>> Command Call: (w/ target specified)  |  As would be seen if looking at a Discord text-channel's chat.
            @ExampleUser
            .seeuser @AnotherUser

            --> Using this format, the 'target' in the 'see_user_info' command becomes the user specified.
            --> In this case, the 'target' would be '@AnotherUser'.
            --> '@AnotherUser' would be passed into the function as a 'discord.Member' type.

III. Code Explanations:
    >>> member = target or ctx.author
        --> This section is a continuation on explanations described in the examples above.
        --> A function's 'target' parameter is optional, however, if specified it takes on the class of 'discord.Member'.
        --> This code means that:
            a.) if a 'target' is specified, the 'member' object becomes the 'target'
            b.) if a 'target' is not specified, the 'member' object becomes the 'ctx.author' (the author of the message)
    >>> ctx.author
        --> The author of a specific message. Generally, this will be the author of the command call's message.
        --> Contains a majority of identical attributes that the 'discord.Member' class has.
            * ex: Member.id, Member.name, Member.discriminator | ctx.author.id, ctx.author.name, ctx.author.discriminator
'''

class Information(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.helper = Helper(client)


    # -- Events --


    # -- Commands --
    @commands.command(aliases = ['serverinfo', 's-info', 'guild', 'guildinfo'])
    async def server_info(self, ctx):
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
    async def add_user_info(self, ctx, target: Optional[Member]):
        member = target or ctx.author
        # Sends message if the user's info file has already been created.
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
    async def see_user_info(self, ctx, target: Optional[Member]):
        member = target or ctx.author
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