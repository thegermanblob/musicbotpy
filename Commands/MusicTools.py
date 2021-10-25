import os
from posix import listdir
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
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    
play_next_song = asyncio.Event()

class MusicTools(commands.Cog):
    """ Contains all Set up commands """

    queue = {}

    def __init__(self, bot: Bot) -> None:
        """ init """
        self.bot = bot


    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(play_next_song.set)
    def NameToUrl(self, name: list):
        """ Receives name  turns it to url """
        name = name.split(" ")
        name.pop(0)
        name = "+".join(name)
        if validators.url(name):
            return name
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + name)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        return("https://www.youtube.com/watch?v=" + video_ids[0])

    async def add_queue(self, guild:guild,  song: str):
        """ Adds song to the queue"""
        if not validators.url(song):
            song = self.NameToUrl(song)
        if guild.id not in self.queue:   
            self.queue[guild.id] = asyncio.Queue()
        player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
        await self.queue[guild.id].put(player)
        print(f"Added :{song}")

    async def play_song(self, ctx:Context, vc):
        """ does the actual playing of songs """
        vc.play(self.queue[ctx.guild.id][0], after=self.toggle_next)
        play = self.queue[ctx.guild.id][0]
        await ctx.send('**Now playing:** {}'.format(play.title))



    @commands.command(name="play")
    async def play(self, ctx: Context):
        """ Plays given url from youtube """

        voice_channel = discord.utils.get(ctx.guild.voice_channels, name='smoke shack')
        await self.add_queue(ctx.guild, ctx.message.content)

        try:
            vc = await voice_channel.connect()
        except:
            vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        async with ctx.typing():
            await self.play_song(ctx, vc)
    
    @commands.command(name="playnext")
    async def playnext(self, ctx:Context):
        """ Plays the next song in the queue """

    @commands.command(name="addqueue")
    async def addqueue(self, ctx:Context):
        """ Recieves song to add to queue """
        await self.add_queue(ctx.guild, ctx.message.content)

    
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
