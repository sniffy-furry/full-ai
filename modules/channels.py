import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='create_channel')
    async def create_channel(ctx, guild_id: int, name: str, type: str = "text"):
        """Creează un canal nou"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        try:
            if type.lower() == "text":
                channel = await guild.create_text_channel(name)
            elif type.lower() == "voice":
                channel = await guild.create_voice_channel(name)
            elif type.lower() == "category":
                channel = await guild.create_category(name)
            else:
                await ctx.send("❌ Tip invalid. Folosește: text, voice, category")
                return
            await ctx.send(f"✅ Canal {channel.name} creat (ID: {channel.id})")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='delete_channel')
    async def delete_channel(ctx, channel_id: int):
        """Șterge un canal"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            await channel.delete()
            await ctx.send("✅ Canal șters")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='channels')
    async def list_channels(ctx, guild_id: int):
        """Listează toate canalele dintr-un server"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        channels = []
        for channel in guild.channels:
            channels.append(f"#{channel.name} ({channel.type})")
        await ctx.send(f"📋 Canale: {', '.join(channels[:20])}")

    @bot.command(name='thread')
    async def create_thread(ctx, message_id: int, channel_id: int, name: str):
        """Creează un thread din mesaj"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            thread = await msg.create_thread(name=name)
            await ctx.send(f"✅ Thread creat: {thread.name}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")