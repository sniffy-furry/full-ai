import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='create_invite')
    async def create_invite(ctx, channel_id: int, max_uses: int = 1, max_age: int = 86400):
        """Creează o invitație"""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            invite = await channel.create_invite(max_uses=max_uses, max_age=max_age)
            await ctx.send(f"✅ Invitație creată: {invite.url}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='delete_invite')
    async def delete_invite(ctx, invite_code: str):
        """Șterge o invitație"""
        try:
            invite = await bot.fetch_invite(f"https://discord.gg/{invite_code}")
            await invite.delete()
            await ctx.send("✅ Invitație ștearsă")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='invite_info')
    async def invite_info(ctx, invite_code: str):
        """Afișează informații despre o invitație"""
        try:
            invite = await bot.fetch_invite(f"https://discord.gg/{invite_code}")
            await ctx.send(f"📋 **Invitație:**\nServer: {invite.guild.name}\nCanal: #{invite.channel.name}\nUtilizatori: {invite.approximate_member_count}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")