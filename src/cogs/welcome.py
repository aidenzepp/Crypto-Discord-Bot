from asyncio.windows_events import NULL
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

    

    # -- Functions --
    async def create_user_info(self, member, filepath = NULL):
        info = {}

        # Storing in 'user' allows for separate entities (preferences, notifications, etc.) to be different keys.
        info['user'] = {
            'name': member.display_name,
            'discriminator': member.discriminator,
            'id': member.id,
            'mention': member.mention,
            'nickname': member.nick,
            'colour': str(member.colour),
            'joined_at': str(member.joined_at)
        }

        if filepath != NULL:
            with open(filepath, 'w') as outfile:
                json.dump(info, outfile, indent = 4)
           
            return

        return info



    # -- Events --
    @commands.Cog.listener()
    async def on_member_join(self, member):
        member_id = member.id
        filepath = f'src/hidden/ALL_USERS_INFO/{member_id}.json'

        await self.create_user_info(member, filepath)



    # -- Commands --



def setup(client):
    client.add_cog(Welcome(client))