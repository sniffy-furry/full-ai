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
    @bot.command(name='send')
    async def send_message(ctx, channel_id: int, *, content: str):
        """Trimite un mesaj într-un canal"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        await channel.send(content)
        await ctx.send(f"✅ Mesaj trimis în #{channel.name}")

    @bot.command(name='edit')
    async def edit_message(ctx, message_id: int, channel_id: int, *, content: str):
        """Editează un mesaj"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(content=content)
            await ctx.send("✅ Mesaj editat")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='delete')
    async def delete_message(ctx, message_id: int, channel_id: int):
        """Șterge un mesaj"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.delete()
            await ctx.send("✅ Mesaj șters")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='react')
    async def add_reaction(ctx, message_id: int, channel_id: int, emoji: str):
        """Adaugă o reacție la un mesaj"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.add_reaction(emoji)
            await ctx.send(f"✅ Reacție {emoji} adăugată")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='pin')
    async def pin_message(ctx, message_id: int, channel_id: int):
        """Fixează un mesaj"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.pin()
            await ctx.send("✅ Mesaj fixat")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='unpin')
    async def unpin_message(ctx, message_id: int, channel_id: int):
        """Defixează un mesaj"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.unpin()
            await ctx.send("✅ Mesaj defixat")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")
