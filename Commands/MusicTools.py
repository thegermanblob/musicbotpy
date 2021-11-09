import os
from posix import listdir
from typing import TYPE_CHECKING
import discord
from discord import guild
from discord.abc import User
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.core import command
import youtube_dl
import asyncio
import urllib.request
import re
import validators

ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key':'FFmpegExtractAudio',
        'preferredcodec':'mp3',
        'preferredquality':'192',
    }]
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        bob = cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        print(type(bob))
        return bob

    
play_next_song = asyncio.Event()
queue = {} 

class MusicTools(commands.Cog):
    """ Contains all Set up commands """


    def __init__(self, bot: Bot) -> None:
        """ init """
        self.bot = bot
        for guild in bot.guilds:
            print(guild.id)
            queue[guild.id] = asyncio.Queue()

    async def audio_player_task(self, id):
        while True:
            play_next_song.clear()
            current = await queue[id].get() 
            current.start() #! causes error
            await play_next_song.wait()

    def toggle_next(self, ctx=None):
        self.bot.loop.call_soon_threadsafe(play_next_song.set)
    

    async def add_queue(self, guild:guild,  song: str, vc):
        """ Adds song to the queue"""
        if not validators.url(song):
            song = self.NameToUrl(song)
        if guild.id not in queue:   
            queue[guild.id] = asyncio.Queue()
        player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
        print(type(player))
        print(f"Added :{song}")
        if not vc.is_playing():
            await queue[guild.id].put(vc.play(player))
            self.toggle_next()

        else:
            await queue[guild.id].put(player)
            self.toggle_next()

    async def play_song(self, ctx:Context, vc):
        """ does the actual playing of songs """
        player = await queue[ctx.guild.id].get()
        vc.play(player, after=self.toggle_next())
        await ctx.send('**Now playing:** {}'.format(player.title))


    def NameToUrl(self, name: list):
        """ Receives name  turns it to url """
        name = name.split(" ")
        name.pop(0)
        name = "+".join(name)
        if validators.url(name):
            return name
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + name)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        return("https://www.youtube.com/watch?v=" + video_ids[1])

    @commands.command(name="play")
    async def play(self, ctx: Context):
        """ Plays given url from youtube """
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel")
            return
        voice_channel = ctx.author.voice.channel

        try:
            vc = await voice_channel.connect()
        except:
            vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        async with ctx.typing():

            await self.add_queue(ctx.guild, ctx.message.content, vc)
            #await self.play_song(ctx, vc)
        
            self.bot.loop.create_task(self.audio_player_task(ctx.guild.id))
    
    @commands.command(name="playnext")
    async def playnext(self, ctx:Context):
        """ Plays the next song in the queue """
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        vc.stop()
        await self.play_song(ctx, vc)
        self.toggle_next()

    @commands.command(name="addqueue")
    async def addqueue(self, ctx:Context):
        """ Recieves song to add to queue """
        await self.add_queue(ctx.guild, ctx.message.content, discord.utils.get(self.bot.voice_clients, guild=ctx.guild))

    
    @commands.command(name="pause")
    async def pause(self, ctx: Context):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Currently no audio is playing.")


    @commands.command(name="resume")
    async def resume(self, ctx: Context):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Nothing is paused")
    
    @commands.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()
    

def setup(bot: Bot):
    """ Adds commads to bot"""
    bot.add_cog(MusicTools(bot))
