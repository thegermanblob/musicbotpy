from datetime import datetime
from time import time
import discord
from discord.ext import commands
from discord.ext.commands import Bot


class TestCommands(commands.Cog):
    """ Set up and test commands"""

    def __init__(self, bot: Bot):
        self.bot = bot


    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """ Tests latency """
        start_time = time()
        message  = await ctx.send("Testing Ping...")
        end_time = time()
        await message.edit(content=f"Pong! {round(self.bot.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")

    @commands.command(name="embed")
    async def embed(self, ctx: commands.Context):
        """ Commmand sends and embed message test """
        embed  = discord.Embed(title="Embed test", description="This is a test", colour= 0x7747B6, timestamp=datetime.utcnow())
        embed.set_author(name="Mr.T")
        embed.add_field(name="Field 1, fool", value="Not an inline field, fool", inline=False)
        embed.add_field(name="Field 2, fool", value="This is an inline, fool", inline=True)
        embed.add_field(name="Field 3, fool", value="This is an inline too, fool", inline=True)
        await ctx.send(embed=embed)

def setup(bot : Bot):
    """ Adds commads to bot"""
    bot.add_cog(TestCommands(bot))