import youtube_dl
import discord
from discord.ext import commands, tasks
import asyncio

folder = 'music_files'

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'music_files/%(id)s.mp3',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
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




@commands.command(name='play', help='This command plays music')
async def play(self, ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return

    else:
        channel = ctx.message.author.voice.channel

    try:
        await channel.connect()
    except:
        pass

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))