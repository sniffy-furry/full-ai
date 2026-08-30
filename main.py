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

        # 2. Încarcă modulele (include comanda help)
        logger.info("🔄 Încărcare module...")
        client.load_modules()

        # NU elimina comanda help! Este definită în modules/messages.py
        # bot.remove_command('help')

        # 4. Afișează comenzile încărcate
        cmd_names = [c.name for c in bot.commands]
        logger.info(f"📋 Total comenzi încărcate: {len(cmd_names)}")
        logger.info(f"📋 Comenzi: {', '.join(cmd_names[:20])}...")

        # 5. Inițializează AI Brain
        ai_brain = AIBrain(bot)

        # 6. Handler-ul on_message (cu procesare manuală)
        @bot.event
        async def on_message(message):
            if message.author.id == bot.user.id:
                return
            if message.channel.id in config.load_ignored_channels():
                return

            content = message.content.strip()
            logger.info(f"📨 Mesaj primit: '{content}' de la {message.author.name}")

            if content.startswith('!'):
                logger.info(f"⚙️ Comanda detectată: {content}")
                parts = content[1:].strip().split()
                if not parts:
                    return
                cmd_name = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # Caută comanda manual
                command = bot.get_command(cmd_name)
                if command is None:
                    logger.warning(f"❌ Comanda '{cmd_name}' nu a fost găsită.")
                    await message.channel.send(f"❌ Comanda necunoscută.")
                    return

                # Construiește contextul
                ctx = await bot.get_context(message)
                ctx.command = command
                if args:
                    ctx.args = [ctx] + args
                else:
                    ctx.args = [ctx]

                try:
                    await bot.invoke(ctx)
                except Exception as e:
                    logger.error(f"Eroare la executare: {e}")
                    await message.channel.send(f"❌ Eroare: {e}")
                return

            # Procesare AI pentru mesaje normale
            await ai_brain.process_message(message)

        # 7. Pornește dashboard-ul
        asyncio.create_task(start_dashboard())

        # 8. Pornește botul
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
