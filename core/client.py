import discord
from discord.ext import commands

from . import config

class DiscordClient:
    def __init__(self):
        self.bot = commands.Bot(
            command_prefix='!',
            self_bot=True,
            help_command=None
        )
        self.ready = False
        self._setup_events()

    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            self.ready = True
            print(f"✅ Authenticated as: {self.bot.user} (ID: {self.bot.user.id})")
            print(f"📊 Connected to {len(self.bot.guilds)} servers")
            try:
                friends = [r for r in self.bot.relationships.values() if r.type == discord.RelationshipType.friend]
                print(f"👥 {len(friends)} friends")
            except Exception:
                print("👥 Friends: unknown")
            print("=" * 50)

    def load_modules(self):
        """Încarcă toate modulele după ce botul este disponibil."""
        from modules import (
            relationships, messages, channels, guilds, voice,
            settings, interactions, invites, webhooks, stickers,
            billing, experiments
        )
        for module in [
            relationships, messages, channels, guilds, voice,
            settings, interactions, invites, webhooks, stickers,
            billing, experiments
        ]:
            try:
                if hasattr(module, 'setup'):
                    module.setup(self.bot)
                    print(f"✅ Loaded: {module.__name__}")
                else:
                    print(f"⚠️ No setup() in {module.__name__}")
            except Exception as e:
                print(f"❌ Error loading {module.__name__}: {e}")
        print(f"✅ Total comenzi încărcate: {len(self.bot.commands)}")

    async def start(self, token):
        await self.bot.start(token)

    async def stop(self):
        await self.bot.close()
