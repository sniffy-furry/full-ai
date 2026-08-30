import discord
from discord.ext import commands
import importlib
import sys
import asyncio

from core import config
from db.database import db

def setup(bot):
    """Înregistrează comenzile admin pe bot."""

    @bot.command(name='shutdown')
    async def shutdown_cmd(ctx):
        """Oprește botul (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        await ctx.send("🛑 Oprește botul...")
        await bot.close()

    @bot.command(name='stats')
    async def stats_cmd(ctx):
        """Afișează statistici (Owner only)."""
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
            f"• Sensitive blocate: `{s.get('sensitive_blocked', 0)}`\n"
            f"• Avertismente: `{s.get('warnings_issued', 0)}`\n"
            f"• Muturi: `{s.get('mutes_activated', 0)}`\n"
            f"• Pornit de la: `{s.get('start_time', 'necunoscut')}`"
        )
        await ctx.send(msg)

    @bot.command(name='trust')
    async def trust_cmd(ctx, action: str, user_id: int = None):
        """Adaugă/elimină utilizatori în lista de încredere (AI nerestricționat)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        trusted = config.load_trusted_users()
        if action == "add" and user_id:
            trusted.add(user_id)
            config.save_trusted_users(trusted)
            await ctx.send(f"✅ User `{user_id}` adăugat în lista de încredere.")
        elif action == "remove" and user_id:
            trusted.discard(user_id)
            config.save_trusted_users(trusted)
            await ctx.send(f"❌ User `{user_id}` eliminat din lista de încredere.")
        elif action == "list":
            if trusted:
                await ctx.send(f"📋 Utilizatori de încredere: {', '.join(map(str, trusted))}")
            else:
                await ctx.send("📭 Niciun utilizator de încredere.")
        else:
            await ctx.send("❌ Folosește: `!trust add <id>` | `!trust remove <id>` | `!trust list`")

    @bot.command(name='ignore')
    async def ignore_cmd(ctx, user_id: int):
        """Adaugă un utilizator în lista de ignorați (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        ignored = config.load_ignored_channels()
        ignored.add(user_id)
        config.save_ignored_channels(ignored)
        await ctx.send(f"🔇 User `{user_id}` adăugat în lista de ignorați.")

    @bot.command(name='unignore')
    async def unignore_cmd(ctx, user_id: int):
        """Elimină un utilizator din lista de ignorați (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        ignored = config.load_ignored_channels()
        ignored.discard(user_id)
        config.save_ignored_channels(ignored)
        await ctx.send(f"🔊 User `{user_id}` eliminat din lista de ignorați.")

    @bot.command(name='list_ignored')
    async def list_ignored_cmd(ctx):
        """Afișează utilizatorii ignorați (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        ignored = config.load_ignored_channels()
        if ignored:
            await ctx.send(f"🚫 Utilizatori ignorați: {', '.join(map(str, ignored))}")
        else:
            await ctx.send("📭 Niciun utilizator ignorat.")

    @bot.command(name='say')
    async def say_cmd(ctx, channel_id: int, *, message: str):
        """Trimite un mesaj într-un canal specific (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent.")
            return
        await channel.send(message)
        await ctx.send(f"✅ Mesaj trimis în #{channel.name}")

    @bot.command(name='broadcast')
    async def broadcast_cmd(ctx, *, message: str):
        """Trimite un mesaj în toate serverele (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        count = 0
        for guild in bot.guilds:
            for channel in guild.text_channels:
                try:
                    await channel.send(f"📢 {message}")
                    count += 1
                    await asyncio.sleep(0.5)
                    break  # Trimite doar într-un canal per server
                except:
                    continue
        await ctx.send(f"✅ Mesaj trimis în {count} servere.")

    @bot.command(name='reload_modules')
    async def reload_modules_cmd(ctx):
        """Reîncarcă modulele fără repornire (Owner only)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        try:
            # Reîncarcă toate modulele din modules/
            import modules
            importlib.reload(modules)
            # Reîncarcă fiecare modul individual
            module_names = ['relationships', 'messages', 'channels', 'guilds', 'voice',
                           'settings', 'interactions', 'invites', 'webhooks', 'stickers',
                           'billing', 'experiments', 'admin']
            for name in module_names:
                try:
                    module = importlib.import_module(f'modules.{name}')
                    importlib.reload(module)
                    if hasattr(module, 'setup'):
                        module.setup(bot)
                except Exception as e:
                    print(f"❌ Error reloading {name}: {e}")
            await ctx.send("✅ Module reîncărcate cu succes.")
        except Exception as e:
            await ctx.send(f"❌ Eroare la reîncărcare: {e}")

    @bot.command(name='eval')
    async def eval_cmd(ctx, *, code: str):
        """Execută cod Python (Owner only, periculos!)."""
        if ctx.author.id != config.OWNER_ID:
            await ctx.send("❌ Nu ai permisiunea.")
            return
        try:
            result = eval(code)
            await ctx.send(f"✅ Rezultat: ```{result}```")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")
