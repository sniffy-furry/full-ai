import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='create_webhook')
    async def create_webhook_cmd(ctx, channel_id: int, name: str):
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            webhook = await channel.create_webhook(name=name)
            await ctx.send(f"✅ Webhook creat: {webhook.url}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='webhook_send')
    async def webhook_send_cmd(ctx, webhook_url: str, *, content: str):
        try:
            async with discord.AsyncWebhook.from_url(webhook_url, session=bot.http.session) as webhook:
                await webhook.send(content)
            await ctx.send("✅ Mesaj trimis prin webhook")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='delete_webhook')
    async def delete_webhook_cmd(ctx, webhook_url: str):
        try:
            async with discord.AsyncWebhook.from_url(webhook_url, session=bot.http.session) as webhook:
                await webhook.delete()
            await ctx.send("✅ Webhook șters")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")
