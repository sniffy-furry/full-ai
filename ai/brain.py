import asyncio
import logging
import ollama

from core import config
from db.database import db

logger = logging.getLogger(__name__)

class AIBrain:
    def __init__(self, bot):
        self.bot = bot
        self.conversation_memory = {}
        self.user_recent_messages = {}
        self.pending_tasks = []
        self.task_lock = asyncio.Lock()
        self.processing = False
        self.queue_event = asyncio.Event()

    async def process_message(self, message):
        content = message.content.strip()
        author_id = message.author.id
        author_name = message.author.display_name
        is_dm = message.guild is None

        if is_dm and db.is_muted(author_id):
            logger.info(f"🔇 DM ignored (muted user): {author_name}")
            return

        if await self._is_sensitive(content):
            if author_id not in config.load_trusted_users():
                logger.info(f"🔒 Sensitive blocked: {author_name}")
                await message.reply("I can't answer that.", mention_author=False, silent=True)
                return

        if is_dm and await self._is_spam(content, author_id):
            logger.info(f"📦 Spam detected: {author_name}")
            db.add_warning(author_id)
            if db.is_muted(author_id):
                logger.info(f"🔇 User muted: {author_name}")
            return

        if is_dm and await self._is_toxic(content):
            logger.info(f"🚫 Toxic detected: {author_name}")
            db.add_warning(author_id)
            if db.is_muted(author_id):
                logger.info(f"🔇 User muted: {author_name}")
            return

        if not await self._should_reply(content, is_dm, message):
            return

        response = await self._generate_response(content, author_id, author_name, is_dm, message)
        if response:
            await message.reply(response, mention_author=False, silent=True)

    async def _should_reply(self, content, is_dm, message):
        is_mentioned = self.bot.user.mentioned_in(message) or self.bot.user.name.lower() in content.lower()
        if is_dm or is_mentioned:
            return True
        prompt = (
            f"Message: \"{content}\"\n"
            "Should a user reply to this? Answer ONLY with 'yes' or 'no'."
        )
        try:
            response = ollama.chat(
                model=config.GATEKEEPER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1, "num_predict": 5}
            )
            return "yes" in response['message']['content'].strip().lower()
        except Exception:
            return False

    async def _generate_response(self, content, author_id, author_name, is_dm, message):
        history = self.conversation_memory.get(author_id, [])
        facts = db.get_user_facts(author_id)
        system_prompt = (
            f"You are {self.bot.user.display_name}, a Discord user. Respond naturally, "
            "in English, short and direct. Don't use prefixes or AI disclaimers."
        )
        user_prompt = f"Message: {content}\nReply:"
        try:
            response = ollama.chat(
                model=config.RESPONDER_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": 0.85, "num_predict": 70}
            )
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    async def _is_sensitive(self, content):
        prompt = (
            f"Question: \"{content}\"\n"
            "Does this ask about illegal drugs, violence, kidnapping, hacking, "
            "weapons, terrorism, or any illegal activity? Answer ONLY 'yes' or 'no'."
        )
        try:
            response = ollama.chat(
                model=config.FILTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1, "num_predict": 5}
            )
            return "yes" in response['message']['content'].strip().lower()
        except Exception:
            return False

    async def _is_spam(self, content, author_id):
        if len(content) < 3 or content.isupper() and len(content) > 10:
            return True
        prompt = (
            f"Message: \"{content}\"\n"
            "Is this spam or nonsense? Answer ONLY 'yes' or 'no'."
        )
        try:
            response = ollama.chat(
                model=config.FILTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1, "num_predict": 5}
            )
            return "yes" in response['message']['content'].strip().lower()
        except Exception:
            return False

    async def _is_toxic(self, content):
        if any(word in content.lower() for word in config.FORBIDDEN_WORDS):
            return True
        prompt = (
            f"Message: \"{content}\"\n"
            "Is this offensive or toxic? Answer ONLY 'yes' or 'no'."
        )
        try:
            response = ollama.chat(
                model=config.FILTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1, "num_predict": 5}
            )
            return "yes" in response['message']['content'].strip().lower()
        except Exception:
            return False
