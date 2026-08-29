import discord
from discord.ext import commands
import asyncio
import yt_dlp

from core import config

voice_clients = {}
voice_queues = {}
voice_current = {}
voice_volume = {}

# ... restul codului rămâne neschimbat ...

def setup(bot):
    @bot.command(name='stickers')
    async def list_stickers(ctx, guild_id: int):
        """Listează sticker-ele dintr-un server"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        stickers = guild.stickers
        if not stickers:
            await ctx.send("📭 Niciun sticker")
            return
        names = [f"{s.name} ({s.id})" for s in stickers[:10]]
        await ctx.send(f"📋 Stickers: {', '.join(names)}")

    @bot.command(name='emoji')
    async def list_emojis(ctx, guild_id: int):
        """Listează emoji-urile dintr-un server"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        emojis = guild.emojis
        if not emojis:
            await ctx.send("📭 Niciun emoji")
            return
        names = [f"{e.name} ({e.id})" for e in emojis[:10]]
        await ctx.send(f"📋 Emoji-uri: {', '.join(names)}")
