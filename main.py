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
        client = DiscordClient()
        bot = client.bot
        ai_brain = AIBrain(bot)
        
        @bot.event
        async def on_message(message):
            if message.author.id == bot.user.id:
                return
            if message.channel.id in config.load_ignored_channels():
                return
            if message.content.startswith('!'):
                await bot.process_commands(message)
                return
            await ai_brain.process_message(message)
        
        asyncio.create_task(start_dashboard())
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
