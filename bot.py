import asyncio
import discord
import youtube_dl
from discord.ext import commands

client = commands.Bot(command_prefix= '.')

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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

@client.event
async def on_ready():
    print('Bot is ready')

@client.event
async def on_message(message):
    lowermsg = message.content.lower()
    if (message.author.bot == False and ("among us" in lowermsg or "amogus" in lowermsg)):
        if "stop" not in lowermsg:
            await message.channel.send("When the imposter is SUS!!!")
            await message.channel.send(file=discord.File('amongus.png'))
        if(message.author.voice):
            channel = message.author.voice.channel
            guild = message.guild
            connected = False
            for voice_client in client.voice_clients:
                if(voice_client.guild == guild):
                    connected = True
                    if "stop amogus" in lowermsg or "stop among gus" in lowermsg:
                        await voice_client.disconnect()
                        break
            if(connected == False):
                voice_client = await channel.connect()
                player = await YTDLSource.from_url("https://www.youtube.com/watch?v=RHtlLxm9wNI")
                voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
                while True:
                    await asyncio.sleep(5)
                    if voice_client.is_playing() == False: 
                        await voice_client.disconnect()
                        break


#client.run('PUT BOT TOKEN IN HERE')