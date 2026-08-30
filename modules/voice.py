import discord
from discord.ext import commands
import asyncio
import yt_dlp

from core import config

voice_clients = {}
voice_queues = {}
voice_current = {}
voice_volume = {}

# Opțiuni yt-dlp
YDL_OPTS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',  # Caută pe YouTube dacă nu e URL
    'extract_flat': False,
}

def get_audio_source(query, volume=0.5):
    """
    Obține sursa audio din URL YouTube sau din căutare.
    Dacă query-ul nu este URL, caută pe YouTube.
    """
    import yt_dlp
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # Extrage informațiile (descarcă doar metadatele)
            info = ydl.extract_info(query, download=False)
            if info is None:
                raise Exception("Nu s-au găsit rezultate.")
            # Dacă este o playlistă sau o căutare, luăm primul rezultat
            if 'entries' in info:
                info = info['entries'][0]
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            url = info.get('url') or info.get('webpage_url')
            if not url:
                raise Exception("Nu s-a putut obține URL-ul audio.")
            # Creează sursa audio cu ffmpeg
            source = discord.FFmpegPCMAudio(
                url,
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                options=f'-vn -filter:a "volume={volume}"'
            )
            return source, title, duration
    except Exception as e:
        raise Exception(f"Eroare yt-dlp: {e}")

async def play_next(guild_id, bot):
    """Rulează următoarea melodie din coadă."""
    queue = voice_queues.get(guild_id)
    vc = voice_clients.get(guild_id)
    if not queue or not vc or not vc.is_connected():
        return
    try:
        # Verifică dacă există elemente în coadă
        if queue.empty():
            return
        entry = await queue.get()
        if entry is None:
            return
        source, title, duration = entry
        # Înregistrează callback-ul pentru după redare
        def after_play(error):
            if error:
                print(f"Eroare redare: {error}")
            # Rulează următoarea melodie în loop-ul principal
            asyncio.run_coroutine_threadsafe(play_next(guild_id, bot), bot.loop)

        vc.play(source, after=after_play)
        voice_current[guild_id] = {
            "title": title,
            "duration": duration,
            "start_time": asyncio.get_event_loop().time()
        }
        await bot.change_presence(activity=discord.Game(name=f"🎵 {title}"))
    except asyncio.QueueEmpty:
        pass
    except Exception as e:
        print(f"Eroare play_next: {e}")

def setup(bot):
    @bot.command(name='join')
    async def join_cmd(ctx):
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
    async def leave_cmd(ctx):
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_connected():
            await vc.disconnect()
            voice_clients.pop(ctx.guild.id, None)
            voice_queues.pop(ctx.guild.id, None)
            voice_current.pop(ctx.guild.id, None)
            await ctx.send("👋 Ieșit din canal")
        else:
            await ctx.send("❌ Nu sunt într-un canal vocal")

    @bot.command(name='play')
    async def play_cmd(ctx, *, query: str):
        if ctx.guild.id not in voice_clients:
            await ctx.send("❌ Intră mai întâi într-un canal vocal cu `!join`.")
            return
        vc = voice_clients[ctx.guild.id]
        try:
            await ctx.send(f"🔍 Caut: {query}...")
            # Obține sursa audio (caută pe YouTube dacă nu e URL)
            source, title, duration = await asyncio.to_thread(
                get_audio_source,
                query,
                voice_volume.get(ctx.guild.id, config.DEFAULT_VOLUME)
            )
            # Adaugă în coadă
            await voice_queues[ctx.guild.id].put((source, title, duration))
            await ctx.send(f"✅ Adăugat în coadă: **{title}**")
            # Dacă nu redă nimic, pornește redarea
            if not vc.is_playing():
                await play_next(ctx.guild.id, bot)
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='pause')
    async def pause_cmd(ctx):
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸️ Pauză")
        else:
            await ctx.send("❌ Nu redă nimic")

    @bot.command(name='resume')
    async def resume_cmd(ctx):
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶️ Reluat")
        else:
            await ctx.send("❌ Nu este în pauză")

    @bot.command(name='stop')
    async def stop_cmd(ctx):
        vc = voice_clients.get(ctx.guild.id)
        if vc:
            vc.stop()
            queue = voice_queues.get(ctx.guild.id)
            if queue:
                # Golește coada
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                # Pune un semnal de oprire pentru a nu aștepta
                await queue.put(None)
            voice_current.pop(ctx.guild.id, None)
            await ctx.send("⏹️ Oprire și coadă golită")
        else:
            await ctx.send("❌ Nu sunt în voice")

    @bot.command(name='skip')
    async def skip_cmd(ctx):
        vc = voice_clients.get(ctx.guild.id)
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("⏭️ Skip")
        else:
            await ctx.send("❌ Nu redă nimic")

    @bot.command(name='np')
    async def np_cmd(ctx):
        info = voice_current.get(ctx.guild.id)
        if info:
            elapsed = int(asyncio.get_event_loop().time() - info.get('start_time', 0))
            await ctx.send(f"🎶 **{info['title']}** - {elapsed}s / {info['duration']}s")
        else:
            await ctx.send("❌ Nu redă nimic")

    @bot.command(name='queue')
    async def queue_cmd(ctx):
        q = voice_queues.get(ctx.guild.id)
        if not q or q.empty():
            await ctx.send("📭 Coada este goală")
        else:
            await ctx.send(f"📋 Coadă: **{q.qsize()}** melodii")

    @bot.command(name='volume')
    async def volume_cmd(ctx, vol: int):
        if vol < 0 or vol > 100:
            await ctx.send("❌ Volumul trebuie să fie între 0 și 100")
            return
        voice_volume[ctx.guild.id] = vol / 100.0
        await ctx.send(f"🔊 Volum setat la {vol}% (se aplică la următoarea melodie)")
