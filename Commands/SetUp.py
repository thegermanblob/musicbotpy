import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context

class SetUp(commands.Cog):
    """ Contains all Set up commands """

    def __init__(self, bot: Bot) -> None:
        """ init """
        self.bot = bot

    @commands.command(name="setstatus") 
    @commands.cooldown(rate=1, per=30)
    async def setstatus(self ,ctx: Context, *, text: str):
       """ Set Status """
       await self.bot.change_presence(activity=discord.Game(name=text))

def setup(bot : Bot):
    """ Adds commads to bot"""
    bot.add_cog(SetUp(bot))