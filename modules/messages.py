import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='ping')
    async def ping_cmd(ctx):
        """Verifica latența botului."""
        await ctx.send("pong")

    @bot.command(name='test')
    async def test_cmd(ctx):
        """Comanda de test."""
        await ctx.send("✅ Test command works!")

    @bot.command(name='help')
    async def help_cmd(ctx, command_name: str = None):
        """
        Afiseaza lista de comenzi sau detalii despre o comanda specifica.
        Ex: !help ping
        """
        if command_name is None:
            # Lista toate comenzile
            cmds = sorted([c.name for c in bot.commands])
            await ctx.send(
                f"📋 **Comenzi disponibile ({len(cmds)}):**\n"
                f"`{', '.join(cmds)}`\n\n"
                f"Foloseste `!help <comanda>` pentru detalii."
            )
        else:
            cmd = bot.get_command(command_name)
            if cmd is None:
                await ctx.send(f"❌ Comanda `{command_name}` nu exista.")
                return
            
            # Construieste semnatura comenzii
            params = cmd.params
            if params:
                sig = " " + " ".join([f"<{p}>" for p in params if p not in ('ctx', 'self')])
            else:
                sig = ""
            
            # Descrierea comenzii (docstring)
            help_text = cmd.help or "Fara descriere."
            
            await ctx.send(
                f"**!{cmd.name}{sig}**\n"
                f"📝 {help_text}"
            )

    @bot.command(name='send')
    async def send_cmd(ctx, channel_id: int, *, content: str):
        """Trimite un mesaj intr-un canal specific."""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        await channel.send(content)
        await ctx.send(f"✅ Mesaj trimis in #{channel.name}")

    @bot.command(name='edit')
    async def edit_cmd(ctx, message_id: int, channel_id: int, *, content: str):
        """Editeaza un mesaj existent."""
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
    async def delete_cmd(ctx, message_id: int, channel_id: int):
        """Sterge un mesaj."""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.delete()
            await ctx.send("✅ Mesaj sters")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='react')
    async def react_cmd(ctx, message_id: int, channel_id: int, emoji: str):
        """Adauga o reactie la un mesaj."""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        try:
            msg = await channel.fetch_message(message_id)
            await msg.add_reaction(emoji)
            await ctx.send(f"✅ Reactie {emoji} adaugata")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='pin')
    async def pin_cmd(ctx, message_id: int, channel_id: int):
        """Fixeaza un mesaj."""
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
    async def unpin_cmd(ctx, message_id: int, channel_id: int):
        """Defixeaza un mesaj."""
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
