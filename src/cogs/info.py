from re import L
import discord
from discord import user
from discord.ext import commands
import random
import json
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

    
    @commands.command(aliases = ['add-user-info', 'add-uinfo', 'adduser'])
    async def add_user_info(self, ctx, member: discord.Member):
        filepath = 'src/hidden/ALL_USERS_INFO.json'

        with open(filepath) as f:
            info = json.load(f)
            users = info['users']


        for user in users:

            if (member.display_name, member.discriminator) == (user['name'], user['discriminator']):

                response = discord.Embed(
                    title = f'@{member.name}  |  User Info:',
                    description = 'This user is already in the system.',
                    colour = (discord.Colour.blue())
                )

                return await ctx.send(embed = response)


        users.append({
            'name': member.display_name,
            'discriminator': member.discriminator,
            'id': member.id,
            'mention': member.mention,
            'nickname': member.nick,
            'colour': str(member.colour),
            'joined_at': str(member.joined_at)
        })

        with open(filepath, 'w') as outfile:
            json.dump(info, outfile, indent = 4)

        
        user_info = discord.Embed(
            title = f'{member.name}  |  User Info:',
            colour = (discord.Colour.blue())
        )

        fields = [
            ['`Name:`', member.display_name, True],
            ['`Discriminator:`', member.discriminator, True],
            ['`ID:`', f'||{member.id}||', True],
            ['Mention:', member.mention, False],
            ['Nickname:', member.nick, True],
            ['Colour:', f'{member.colour}', True],
            ['Joined At:', f'{member.joined_at}', False]
        ]

        for name, value, inline in fields:
            user_info.add_field(name = name, value = value, inline = inline)

        
        await ctx.send(embed = user_info)



def setup(client):
    client.add_cog(Information(client))