import discord
from discord.ext import commands
from core import config

def setup(bot):
    @bot.command(name='shutdown')
    async def shutdown_cmd(ctx):
        """Oprește botul (doar owner)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        await ctx.send("🛑 Oprire bot...")
        await bot.close()

    @bot.command(name='stats')
    async def stats_cmd(ctx):
        """Afișează statistici (doar owner)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        s = config.load_stats()
        msg = (
            "📊 **Statistici:**\n"
            f"• Mesaje procesate: `{s.get('messages_processed', 0)}`\n"
            f"• Răspunsuri trimise: `{s.get('responses_sent', 0)}`\n"
            f"• Fapte extrase: `{s.get('facts_extracted', 0)}`\n"
            f"• Spam blocat: `{s.get('spam_blocked', 0)}`\n"
            f"• Toxic blocat: `{s.get('toxic_blocked', 0)}`\n"
            f"• Avertismente: `{s.get('warnings_issued', 0)}`\n"
            f"• Muturi: `{s.get('mutes_activated', 0)}`"
        )
        await ctx.send(msg)

    @bot.command(name='ignore')
    async def ignore_cmd(ctx, channel_id: int):
        """Ignorează un canal (doar owner)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        ignored = config.load_ignored_channels()
        ignored.add(channel_id)
        config.save_ignored_channels(ignored)
        await ctx.send(f"🔇 Canalul `{channel_id}` ignorat.")

    @bot.command(name='unignore')
    async def unignore_cmd(ctx, channel_id: int):
        """Scoate un canal din ignorate (doar owner)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        ignored = config.load_ignored_channels()
        ignored.discard(channel_id)
        config.save_ignored_channels(ignored)
        await ctx.send(f"🔊 Canalul `{channel_id}` nu mai este ignorat.")