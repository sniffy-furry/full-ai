import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='friends')
    async def list_friends(ctx):
        """Listează toți prietenii"""
        friends = bot.user.friends
        if not friends:
            await ctx.send("📭 Nu ai prieteni.")
            return
        names = [f"{f.name}#{f.discriminator}" for f in friends[:10]]
        await ctx.send(f"👥 Prieteni ({len(friends)}): {', '.join(names)}")

    @bot.command(name='add_friend')
    async def add_friend(ctx, user_id: int):
        """Trimite cerere de prietenie"""
        user = await bot.fetch_user(user_id)
        await bot.send_friend_request(user)
        await ctx.send(f"✅ Cerere trimisă către {user.name}")

    @bot.command(name='remove_friend')
    async def remove_friend(ctx, user_id: int):
        """Șterge un prieten"""
        user = await bot.fetch_user(user_id)
        await bot.remove_friend(user)
        await ctx.send(f"❌ {user.name} a fost eliminat din prieteni")

    @bot.command(name='block')
    async def block_user(ctx, user_id: int):
        """Blochează un utilizator"""
        user = await bot.fetch_user(user_id)
        await bot.block_user(user)
        await ctx.send(f"🔇 {user.name} blocat")

    @bot.command(name='unblock')
    async def unblock_user(ctx, user_id: int):
        """Deblochează un utilizator"""
        user = await bot.fetch_user(user_id)
        await bot.unblock_user(user)
        await ctx.send(f"🔊 {user.name} deblocat")

    @bot.command(name='blocked')
    async def list_blocked(ctx):
        """Listează utilizatorii blocați"""
        blocked = bot.user.blocked_users
        if not blocked:
            await ctx.send("📭 Niciun utilizator blocat.")
            return
        names = [f"{b.name}#{b.discriminator}" for b in blocked[:10]]
        await ctx.send(f"🚫 Blocați ({len(blocked)}): {', '.join(names)}")