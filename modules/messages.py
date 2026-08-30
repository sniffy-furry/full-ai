import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='ping')
    async def ping_cmd(ctx):
        """Verifică latența botului."""
        await ctx.send("pong")

    @bot.command(name='test')
    async def test_cmd(ctx):
        """Comandă de test."""
        await ctx.send("✅ Test command works!")

    @bot.command(name='help')
    async def help_cmd(ctx, command_name: str = None):
        """Afișează lista de comenzi sau detalii despre o comandă specifică."""
        if command_name is None:
            cmds = [c.name for c in bot.commands]
            # Grupează comenzile după modul (aproximativ)
            await ctx.send(
                f"📋 **Comenzi disponibile:**\n{', '.join(sorted(cmds))}\n\n"
                f"Folosește `!help <comandă>` pentru detalii."
            )
        else:
            cmd = bot.get_command(command_name)
            if cmd is None:
                await ctx.send(f"❌ Comanda `{command_name}` nu există.")
                return
            params = cmd.params
            if params:
                sig = " " + " ".join([f"<{p}>" for p in params if p not in ('ctx', 'self')])
            else:
                sig = ""
            await ctx.send(
                f"**!{cmd.name}{sig}**\n"
                f"{cmd.help or 'Fără descriere.'}"
            )

    @bot.command(name='send')
    async def send_cmd(ctx, channel_id: int, *, content: str):
        """Trimite un mesaj într-un canal specific."""
        channel = bot.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ Canal inexistent")
            return
        await channel.send(content)
        await ctx.send(f"✅ Mesaj trimis în #{channel.name}")

    @bot.command(name='edit')
    async def edit_cmd(ctx, message_id: int, channel_id: int, *, content: str):
        """Editează un mesaj existent."""
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
        """Șterge un mesaj."""
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
    async def react_cmd(ctx, message_id: int, channel_id: int, emoji: str):
        """Adaugă o reacție la un mesaj."""
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
    async def pin_cmd(ctx, message_id: int, channel_id: int):
        """Fixează un mesaj."""
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
        """Defixează un mesaj."""
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
