from re import L
import discord
from discord.ext import commands
import random
import json
import time
import os
#--

class Welcome(commands.Cog):

    def __init__(self, client):
        self.client = client



    # -- Events --
    @commands.Cog.listener()
    async def on_member_join(self, member):
        filepath = 'src/hidden/ALL_USERS_INFO.json'

        with open(filepath) as f:
            info = json.load(f)

        info['users'].append({
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
        



    # -- Commands --



def setup(client):
    client.add_cog(Welcome(client))