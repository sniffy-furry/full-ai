import discord
from discord.ext import commands
import asyncio
import yt_dlp

voice_clients = {}
voice_queues = {}
voice_current = {}
voice_volume = {}

def setup(bot):
    @bot.command(name='join')
    async def join_voice(ctx):
        """Intră în canalul vocal al utilizatorului"""
        if not ctx.author.voice:
            await ctx.send("❌ Nu ești într-un canal vocal.")
            return
        channel = ctx.author.voice.channel
        try:
            vc = await channel.connect()
            voice_clients[ctx.guild.id] = vc
            voice_queues[ctx.guild.id] = asyncio.Queue()
            await ctx.send(f"✅ Intrat în {channel.name}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='leave')
    async def leave_voice(ctx):
        """Iese din canalul vocal"""
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_connected():
            await vc.disconnect()
            voice_clients.pop(ctx.guild.id, None)
            voice_queues.pop(ctx.guild.id, None)
            await ctx.send("👋 Ieșit din canal")
        else:
            await ctx.send("❌ Nu sunt într-un canal vocal")

    @bot.command(name='play')
    async def play_audio(ctx, *, query: str):
        """Redă audio din YouTube sau fișier local"""
        if ctx.guild.id not in voice_clients:
            await ctx.send("❌ Intră mai întâi într-un canal vocal cu !join")
            return
        vc = voice_clients[ctx.guild.id]
        try:
            await ctx.send(f"🔍 Caut: {query}...")
            source, title, duration = await get_audio_source(query, voice_volume.get(ctx.guild.id, 0.5))
            await voice_queues[ctx.guild.id].put((source, title, duration))
            await ctx.send(f"✅ Adăugat în coadă: **{title}**")
            if not vc.is_playing():
                await play_next(ctx.guild.id, bot)
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='pause')
    async def pause_audio(ctx):
        """Pauză"""
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸️ Pauză")
        else:
            await ctx.send("❌ Nu redă nimic")

    @bot.command(name='resume')
    async def resume_audio(ctx):
        """Reluare"""
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶️ Reluat")
        else:
            await ctx.send("❌ Nu este în pauză")

    @bot.command(name='stop')
    async def stop_audio(ctx):
        """Oprește și golește coada"""
        vc = voice_clients.get(ctx.guild.id)
        if vc:
            vc.stop()
            queue = voice_queues.get(ctx.guild.id)
            if queue:
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except:
                        break
                await queue.put(None)
            await ctx.send("⏹️ Oprire")
        else:
            await ctx.send("❌ Nu sunt în voice")

    @bot.command(name='skip')
    async def skip_audio(ctx):
        """Sari la următoarea melodie"""
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏭️ Skip")
        else:
            await ctx.send("❌ Nu redă nimic")

    @bot.command(name='np')
    async def now_playing(ctx):
        """Ce redă acum"""
        info = voice_current.get(ctx.guild.id)
        if info:
            elapsed = int(asyncio.get_event_loop().time() - info.get('start_time', 0))
            await ctx.send(f"🎶 **{info['title']}** - {elapsed}s / {info['duration']}s")
        else:
            await ctx.send("❌ Nu redă nimic")

    @bot.command(name='queue')
    async def show_queue(ctx):
        """Afișează coada"""
        q = voice_queues.get(ctx.guild.id)
        if not q or q.empty():
            await ctx.send("📭 Coada este goală")
        else:
            await ctx.send(f"📋 Coadă: **{q.qsize()}** melodii")

    @bot.command(name='volume')
    async def set_volume(ctx, vol: int):
        """Setează volumul (0-100)"""
        if vol < 0 or vol > 100:
            await ctx.send("❌ Volumul trebuie să fie între 0 și 100")
            return
        voice_volume[ctx.guild.id] = vol / 100.0
        await ctx.send(f"🔊 Volum setat la {vol}%")

async def play_next(guild_id, bot):
    queue = voice_queues.get(guild_id)
    vc = voice_clients.get(guild_id)
    if not queue or not vc or not vc.is_connected():
        return
    try:
        entry = await queue.get()
        if entry is None:
            return
        source, title, duration = entry
        vc.play(source, after=lambda e: asyncio.create_task(play_next(guild_id, bot)))
        voice_current[guild_id] = {"title": title, "duration": duration, "start_time": asyncio.get_event_loop().time()}
        await bot.change_presence(activity=discord.Game(name=f"🎵 {title}"))
    except:
        pass

async def get_audio_source(url_or_path, volume=0.5):
    """Obține sursa audio din URL sau fișier local"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    if url_or_path.startswith(("http://", "https://")):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_or_path, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            url = info.get('url') or info.get('webpage_url')
        source = discord.FFmpegPCMAudio(
            url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options=f'-vn -filter:a "volume={volume}"'
        )
        return source, title, duration
    else:
        title = url_or_path.split('/')[-1]
        source = discord.FFmpegPCMAudio(url_or_path, options=f'-vn -filter:a "volume={volume}"')
        return source, title, 0