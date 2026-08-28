"""
Funcțiile disponibile pentru AI.
Fiecare funcție poate fi apelată de AI pentru a interacționa cu Discord.
"""

import discord
import asyncio

# Cache pentru utilizatori și canale
user_cache = {}
channel_cache = {}

async def get_user(bot, user_id):
    if user_id not in user_cache:
        user_cache[user_id] = await bot.fetch_user(user_id)
    return user_cache[user_id]

async def get_channel(bot, channel_id):
    if channel_id not in channel_cache:
        channel_cache[channel_id] = bot.get_channel(channel_id)
    return channel_cache[channel_id]

# ===== FUNCȚII PENTRU MESAJE =====

async def send_message(bot, channel_id, content):
    channel = await get_channel(bot, channel_id)
    if channel:
        await channel.send(content)
        return f"✅ Mesaj trimis în #{channel.name}"
    return "❌ Canal inexistent"

async def send_dm(bot, user_id, content):
    user = await get_user(bot, user_id)
    if user:
        await user.send(content)
        return f"✅ Mesaj trimis lui {user.name}"
    return "❌ Utilizator inexistent"

async def edit_message(bot, channel_id, message_id, content):
    channel = await get_channel(bot, channel_id)
    if channel:
        msg = await channel.fetch_message(message_id)
        await msg.edit(content=content)
        return f"✅ Mesaj editat"
    return "❌ Canal inexistent"

async def delete_message(bot, channel_id, message_id):
    channel = await get_channel(bot, channel_id)
    if channel:
        msg = await channel.fetch_message(message_id)
        await msg.delete()
        return f"✅ Mesaj șters"
    return "❌ Canal inexistent"

async def add_reaction(bot, channel_id, message_id, emoji):
    channel = await get_channel(bot, channel_id)
    if channel:
        msg = await channel.fetch_message(message_id)
        await msg.add_reaction(emoji)
        return f"✅ Reacție {emoji} adăugată"
    return "❌ Canal inexistent"

async def pin_message(bot, channel_id, message_id):
    channel = await get_channel(bot, channel_id)
    if channel:
        msg = await channel.fetch_message(message_id)
        await msg.pin()
        return f"✅ Mesaj fixat"
    return "❌ Canal inexistent"

# ===== FUNCȚII PENTRU RELAȚII =====

async def add_friend(bot, user_id):
    user = await get_user(bot, user_id)
    if user:
        await bot.send_friend_request(user)
        return f"✅ Cerere trimisă lui {user.name}"
    return "❌ Utilizator inexistent"

async def remove_friend(bot, user_id):
    user = await get_user(bot, user_id)
    if user:
        await bot.remove_friend(user)
        return f"✅ {user.name} eliminat din prieteni"
    return "❌ Utilizator inexistent"

async def block_user(bot, user_id):
    user = await get_user(bot, user_id)
    if user:
        await bot.block_user(user)
        return f"✅ {user.name} blocat"
    return "❌ Utilizator inexistent"

async def unblock_user(bot, user_id):
    user = await get_user(bot, user_id)
    if user:
        await bot.unblock_user(user)
        return f"✅ {user.name} deblocat"
    return "❌ Utilizator inexistent"

# ===== FUNCȚII PENTRU VOICE =====

async def join_voice(bot, guild_id, channel_id):
    guild = bot.get_guild(guild_id)
    if not guild:
        return "❌ Server inexistent"
    channel = guild.get_channel(channel_id)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        return "❌ Canal vocal inexistent"
    try:
        vc = await channel.connect()
        return f"✅ Intrat în {channel.name}"
    except Exception as e:
        return f"❌ Eroare: {e}"

async def leave_voice(bot, guild_id):
    # Voice client management
    from modules.voice import voice_clients
    vc = voice_clients.get(guild_id)
    if vc and vc.is_connected():
        await vc.disconnect()
        del voice_clients[guild_id]
        return "✅ Ieșit din canal"
    return "❌ Nu sunt într-un canal vocal"

# ===== FUNCȚII PENTRU SERVER =====

async def list_guilds(bot):
    guilds = bot.guilds
    if not guilds:
        return "📭 Nu ești în niciun server"
    names = [f"{g.name} (ID: {g.id})" for g in guilds[:10]]
    return f"📋 Servere: {', '.join(names)}"

async def leave_guild(bot, guild_id):
    guild = bot.get_guild(guild_id)
    if guild:
        await guild.leave()
        return f"✅ Serverul {guild.name} părăsit"
    return "❌ Server inexistent"

# ===== FUNCȚII PENTRU SETĂRI =====

async def set_status(bot, status_text):
    await bot.change_presence(activity=discord.CustomActivity(name=status_text))
    return f"✅ Status setat: {status_text}"

async def set_username(bot, username):
    await bot.user.edit(username=username)
    return f"✅ Nume schimbat în: {username}"

async def set_avatar(bot, image_bytes):
    await bot.user.edit(avatar=image_bytes)
    return f"✅ Avatar actualizat"

# ===== FUNCȚII PENTRU INVITAȚII =====

async def create_invite(bot, channel_id, max_uses=1, max_age=86400):
    channel = bot.get_channel(channel_id)
    if channel:
        invite = await channel.create_invite(max_uses=max_uses, max_age=max_age)
        return f"✅ Invitație: {invite.url}"
    return "❌ Canal inexistent"

# Dicționar cu toate funcțiile disponibile pentru AI
TOOLS = {
    "send_message": send_message,
    "send_dm": send_dm,
    "edit_message": edit_message,
    "delete_message": delete_message,
    "add_reaction": add_reaction,
    "pin_message": pin_message,
    "add_friend": add_friend,
    "remove_friend": remove_friend,
    "block_user": block_user,
    "unblock_user": unblock_user,
    "join_voice": join_voice,
    "leave_voice": leave_voice,
    "list_guilds": list_guilds,
    "leave_guild": leave_guild,
    "set_status": set_status,
    "set_username": set_username,
    "set_avatar": set_avatar,
    "create_invite": create_invite,
}