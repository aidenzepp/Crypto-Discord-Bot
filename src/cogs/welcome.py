import discord
from discord.ext import commands
import json

from cogs.helper import Helper
#--

class Welcome(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.helper = Helper(client)


    # -- Events --
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.helper.make_user(member)


    # -- Commands --


# -- Cog Setup --
def setup(client):
    client.add_cog(Welcome(client))