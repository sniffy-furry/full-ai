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
    @bot.command(name='status')
    async def set_status(ctx, *, status_text: str):
        """Setează statusul personalizat"""
        await bot.change_presence(activity=discord.CustomActivity(name=status_text))
        await ctx.send(f"✅ Status setat: {status_text}")

    @bot.command(name='avatar')
    async def set_avatar(ctx):
        """Schimbă avatarul (atașează o imagine)"""
        if not ctx.message.attachments:
            await ctx.send("❌ Atașează o imagine cu mesajul")
            return
        attachment = ctx.message.attachments[0]
        image_bytes = await attachment.read()
        await bot.user.edit(avatar=image_bytes)
        await ctx.send("✅ Avatar actualizat")

    @bot.command(name='nickname')
    async def set_nickname(ctx, guild_id: int, *, nickname: str):
        """Schimbă nickname-ul pe un server"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        try:
            await guild.me.edit(nick=nickname)
            await ctx.send(f"✅ Nickname setat: {nickname}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='username')
    async def set_username(ctx, *, username: str):
        """Schimbă numele de utilizator"""
        try:
            await bot.user.edit(username=username)
            await ctx.send(f"✅ Nume schimbat în: {username}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='online')
    async def set_online(ctx):
        """Setează statusul online"""
        await bot.change_presence(status=discord.Status.online)
        await ctx.send("✅ Status setat: Online")

    @bot.command(name='idle')
    async def set_idle(ctx):
        """Setează statusul idle"""
        await bot.change_presence(status=discord.Status.idle)
        await ctx.send("✅ Status setat: Idle")

    @bot.command(name='dnd')
    async def set_dnd(ctx):
        """Setează statusul Do Not Disturb"""
        await bot.change_presence(status=discord.Status.dnd)
        await ctx.send("✅ Status setat: Do Not Disturb")

    @bot.command(name='invisible')
    async def set_invisible(ctx):
        """Setează statusul invizibil"""
        await bot.change_presence(status=discord.Status.invisible)
        await ctx.send("✅ Status setat: Invizibil")
