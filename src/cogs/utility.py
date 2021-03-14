import discord
from discord.ext import commands
# --

class FIND_CRYPTO_RESULTS(commands.Cog):
    def __init__(self, client, found_info = {}, not_found = {}):
        self.client = client
        self.finfo = found_info
        self.fkeys = found_info.keys()
        self.nfound = not_found
        self.nfkeys = not_found.keys() 


class COMPARE_CRYPTO_RESULTS(commands.Cog):
    def __init__(self, client, not_found = {}, not_in_uinfo = {}, comparison_info_all = {}):
        self.client = client
        self.nfound = not_found
        self.nfkeys = not_found.keys()
        self.notuinfo = not_in_uinfo
        self.nuikeys = not_in_uinfo.keys()
        self.cmpinfoall = comparison_info_all
        self.ciakeys = comparison_info_all.keys()


def setup(client):
    client.add_cog(FIND_CRYPTO_RESULTS(client))
    client.add_cog(COMPARE_CRYPTO_RESULTS(client))