import discord
from discord.ext import commands

def setup(bot):
    # Comanda help extinsă
    @bot.command(name='help')
    async def help_cmd(ctx, command_name: str = None):
        """Afișează ajutor pentru toate comenzile sau pentru o comandă specifică."""
        if command_name is None:
            # Afișează lista tuturor comenzilor
            cmds = sorted(bot.commands, key=lambda c: c.name)
            lines = []
            for cmd in cmds:
                if cmd.hidden:
                    continue
                # Obține descrierea (docstring)
                desc = cmd.help or "Fără descriere"
                # Argumente
                params = cmd.clean_params
                if params:
                    args_str = " ".join(f"<{p}>" for p in params.keys())
                else:
                    args_str = ""
                lines.append(f"`!{cmd.name} {args_str}` – {desc}")
            await ctx.send("📋 **Comenzi disponibile:**\n" + "\n".join(lines[:20]) + ("\n... și altele." if len(lines) > 20 else ""))
        else:
            # Caută comanda specifică
            cmd = bot.get_command(command_name)
            if cmd is None:
                await ctx.send(f"❌ Comanda `{command_name}` nu există.")
                return
            params = cmd.clean_params
            if params:
                args_str = " ".join(f"<{p}>" for p in params.keys())
            else:
                args_str = ""
            desc = cmd.help or "Fără descriere"
            await ctx.send(f"**!{cmd.name} {args_str}**\n{desc}")

    # Alte comenzi existente (ping, test, send, edit, delete, react, pin, unpin)
    @bot.command(name='ping')
    async def ping_cmd(ctx):
        await ctx.send("pong")

    @bot.command(name='test')
    async def test_cmd(ctx):
        await ctx.send("✅ Test command works!")

    # (restul comenzilor: send, edit, delete, react, pin, unpin) – le păstrezi pe cele deja existente