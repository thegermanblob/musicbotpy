import re
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot, Context, context
from discord.ext.commands.core import command

class ModTools(commands.Cog):
    """ Class containing all mod tools """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.last_msg = None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel('721904939730993224')

        if not channel:
            return

        await channel.send(f"Le Mod Bot welcomes you to the shack, {member}!")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """ Grabs last deleted message """
        self.last_msg = message

    @commands.command(name="snipe")
    async def snipe(self, ctx: Context):
        """ Command to send the last deleted message"""
        if not self.last_msg:
            await ctx.send("There's  no tea to spill!")
            return 

        author = self.last_msg.author
        content = self.last_msg.content

        embed = discord.Embed(title=f"Author of the tea {author}", description=content)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """ Command to run the user joined your channel"""
        if member.name == 'Le Mod Bot':
            return
        
        voice = discord.utils.get(self.bot.voice_clients, guild=member.guild)
        if voice.is_playing():
            return
        await asyncio.sleep(1)
        user = member
        if after != None:
            voice_channel = after.channel
            try:
                vc = await voice_channel.connect()
                vc.play(discord.FFmpegOpusAudio('sounds/userjoin.mp3'))
                await asyncio.sleep(3)
                await vc.disconnect()
            except:
                voice.play(discord.FFmpegOpusAudio('sounds/userjoin.mp3'))
        else:
            voice_channel = before.channel
            voice = discord.utils.get(self.bot.voice_clients, guild=member.guild)
            try:
                vc = await voice_channel.connect()
                vc = await voice_channel.connect()
                vc.play(discord.FFmpegOpusAudio('sounds/userleft.mp3'))
                await asyncio.sleep(3)
                await vc.disconnect()
            except:
                voice.play(discord.FFmpegOpusAudio('sounds/userleft.mp3'))
    

    def name_check(name):
        """ Checks naming convention """
        if not (re.match(r"[A-Z]\w* \w*", name)):
            return False
        
        

            


def setup(bot : Bot):
    """ Adds commands to bot """
    bot.add_cog(ModTools(bot))