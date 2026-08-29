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
    @bot.command(name='boosts')
    async def list_boosts(ctx):
        """Listează boost-urile active"""
        boosts = bot.user.guild_boosts
        if not boosts:
            await ctx.send("📭 Niciun boost activ")
            return
        names = [f"Server {b.id} (boost: {b.boost_count})" for b in boosts]
        await ctx.send(f"📋 Boost-uri: {', '.join(names)}")

    @bot.command(name='subscriptions')
    async def list_subscriptions(ctx):
        """Listează abonamentele active"""
        subs = bot.user.subscriptions
        if not subs:
            await ctx.send("📭 Niciun abonament activ")
            return
        names = [f"{s.sku_id} - {s.entitlement_id}" for s in subs]
        await ctx.send(f"📋 Abonamente: {', '.join(names)}")
