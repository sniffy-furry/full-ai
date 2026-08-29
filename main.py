#!/usr/bin/env python3

import asyncio
import logging
import sys
from datetime import datetime

from core import config
from core.client import DiscordClient
from ai.brain import AIBrain
from db.database import db
from web.dashboard import start_dashboard

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

stats = config.load_stats()
bot = None

async def main():
    global bot, stats
    token = config.load_token()
    if not token or len(token) < 20:
        logger.warning("⚠️ Token missing or invalid. Starting dashboard in SETUP mode.")
        await start_dashboard()
        return

    try:
        # 1. Creează clientul
        client = DiscordClient()
        bot = client.bot

        # 2. Încarcă modulele
        client.load_modules()

        # Elimină comanda implicită help pentru a evita conflicte
        bot.remove_command('help')

        # 3. Comenzi de test (direct pe bot)
        @bot.command(name='ping')
        async def ping_cmd(ctx):
            await ctx.send("pong")

        @bot.command(name='test')
        async def test_cmd(ctx):
            await ctx.send("✅ Test command works!")

        # 4. Inițializează AI Brain
        ai_brain = AIBrain(bot)

        # 5. Handler-ul on_message (procesare corectă)
        @bot.event
        async def on_message(message):
            if message.author.id == bot.user.id:
                return
            if message.channel.id in config.load_ignored_channels():
                return

            content = message.content.strip()
            logger.info(f"📨 Mesaj primit: '{content}' de la {message.author.name}")

            # Procesare comenzi cu prefix !
            if content.startswith('!'):
                logger.info(f"⚙️ Comanda detectată: {content}")
                # Normalizează: elimină '!' și spațiile
                cmd = content[1:].strip()
                if not cmd:
                    return

                # Obține contextul
                ctx = await bot.get_context(message)

                # Verifică dacă comanda există
                if ctx.command is not None:
                    try:
                        await bot.invoke(ctx)  # ← corect
                    except Exception as e:
                        logger.error(f"Eroare la executare: {e}")
                        await message.channel.send(f"❌ Eroare: {e}")
                else:
                    logger.warning(f"❌ Comanda '{cmd}' nu a fost găsită.")
                    await message.channel.send(f"❌ Comanda necunoscută.")
                return

            # Procesare AI pentru mesaje normale
            await ai_brain.process_message(message)

        # 6. Pornește dashboard-ul
        asyncio.create_task(start_dashboard())

        # 7. Pornește botul
        await client.start(token)

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        await start_dashboard()

if __name__ == "__main__":
    if stats.get("start_time") is None:
        stats["start_time"] = datetime.now().isoformat()
        config.save_stats(stats)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
