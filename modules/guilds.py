import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='guilds')
    async def list_guilds(ctx):
        """Listează toate serverele"""
        guilds = bot.guilds
        if not guilds:
            await ctx.send("📭 Nu ești în niciun server.")
            return
        names = [f"{g.name} (ID: {g.id})" for g in guilds[:10]]
        await ctx.send(f"📋 Servere ({len(guilds)}): {', '.join(names)}")

    @bot.command(name='leave_guild')
    async def leave_guild(ctx, guild_id: int):
        """Părăsește un server"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        try:
            await guild.leave()
            await ctx.send(f"✅ Părăsit serverul {guild.name}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='members')
    async def list_members(ctx, guild_id: int):
        """Listează membrii unui server"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        members = []
        async for member in guild.fetch_members(limit=50):
            members.append(f"{member.display_name} ({member.id})")
        await ctx.send(f"👥 Membri: {', '.join(members[:20])}")

    @bot.command(name='create_role')
    async def create_role(ctx, guild_id: int, name: str):
        """Creează un rol nou"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        try:
            role = await guild.create_role(name=name)
            await ctx.send(f"✅ Rol {role.name} creat (ID: {role.id})")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='add_role')
    async def add_role(ctx, guild_id: int, user_id: int, role_id: int):
        """Adaugă un rol unui membru"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        try:
            member = await guild.fetch_member(user_id)
            role = guild.get_role(role_id)
            if not role:
                await ctx.send("❌ Rol inexistent")
                return
            await member.add_roles(role)
            await ctx.send(f"✅ Rol {role.name} adăugat lui {member.display_name}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")

    @bot.command(name='remove_role')
    async def remove_role(ctx, guild_id: int, user_id: int, role_id: int):
        """Elimină un rol de la un membru"""
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send("❌ Server inexistent")
            return
        try:
            member = await guild.fetch_member(user_id)
            role = guild.get_role(role_id)
            if not role:
                await ctx.send("❌ Rol inexistent")
                return
            await member.remove_roles(role)
            await ctx.send(f"✅ Rol {role.name} eliminat de la {member.display_name}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")