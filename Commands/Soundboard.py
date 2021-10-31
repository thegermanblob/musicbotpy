
import discord
from discord import guild
from discord.abc import User
from discord.ext import commands
from discord.ext.commands import Bot, Context

class SoundBoard(commands.Cog):
    """ Set up and test commands"""

    def __init__(self, bot: Bot):
        self.bot = bot


    @commands.command(name="soundboard")
    async def soundboard(self, ctx: Context, sound :str):
        """ Plays given url from youtube """
        voice_channel = ctx.author.voice.channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            vc = await voice_channel.connect()
            name = './sounds/' +sound +".mp3"
            vc.play(discord.FFmpegOpusAudio(name))
        except:
            voice.play(discord.FFmpegOpusAudio(name))


    @commands.command(name="mopowa")
    async def mopowa(self, ctx: Context):
        """ Plays given url from youtube """
        voice_channel = ctx.author.voice.channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegOpusAudio("./sounds/mopowa.mp3"))
        except:
            voice.play(discord.FFmpegOpusAudio("./sounds/mopowa.mp3"))

    @commands.command(name="gsucc") #!this is the template for a soundboard command for now
    async def gsucc(self, ctx: Context):
        """ Plays given url from youtube """
        voice_channel = ctx.author.voice.channel
        try:
            vc = await voice_channel.connect()
        except:
            vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            vc.play(discord.FFmpegOpusAudio("./sounds/gsucc.mp3"))
        except:
            await ctx.send("Can't while playing music, sorry")



    @commands.command(name="uwa")
    async def uwa(self, ctx: Context):
        """ Plays given url from youtube """
        voice_channel = ctx.author.voice.channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegOpusAudio("./sounds/uwa.mp3"))
        except:
            voice.play(discord.FFmpegOpusAudio("./sounds/uwa.mp3"))

def setup(bot: Bot):
    """ Adds commads to bot"""
    bot.add_cog(SoundBoard(bot))
