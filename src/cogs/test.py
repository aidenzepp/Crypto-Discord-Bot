import discord
from discord.ext import commands

class Test(commands.Cog):

    def __init__(self, client):
        self.client = client

    # -- Commands --
    @commands.command()
    async def test(self, ctx):
        await ctx.send('Command heard. Test successful.')

    
    @commands.command(aliases = ['emoji'])
    async def emoji_test(self, ctx):
        await ctx.send(':white_check_mark:')

    
    @commands.command(aliases = ['embed'])
    async def embed_test(self, ctx):
        embed = discord.Embed(
            title = 'This is a test title.',
            description = 'This is a test description.'
        )

        embed.set_author(
            name = ctx.author.display_name,
            url = 'https://github.com/',
            icon_url = ctx.author.avatar_url
        )

        embed.add_field(
            name = 'This is a test field title [#1].',
            value = 'This is a test field value. Inline is set to [False].',
            inline = False
        )

        embed.add_field(
            name = 'This is a test field title [#2].',
            value = 'This is a test field value. Inline is set to [True].',
            inline = True
        )

        embed.add_field(
            name = 'This is a test field title [#3].',
            value = 'This is a test field value. Inline is set to [True].',
            inline = True
        )

        embed.set_thumbnail(
            url = 'https://i.imgur.com/ZOKp8LH.png'
        )

        embed.set_footer(
            text = 'This is a test footer. The command was called by: @{author}.'.format(author = ctx.author)
        )

        await ctx.send(embed = embed)


def setup(client):
    client.add_cog(Test(client))
