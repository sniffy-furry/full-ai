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
        self._setup_modules()

    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            self.ready = True
            print(f"Authenticated as: {self.bot.user} (ID: {self.bot.user.id})")
            print(f"Connected to {len(self.bot.guilds)} servers")
            try:
                friends = [r for r in self.bot.relationships.values() if r.type == discord.RelationshipType.friend]
                print(f"{len(friends)} friends")
            except Exception:
                print("Friends: unknown")
            print("=" * 50)

        @self.bot.event
        async def on_message(message):
            if message.author.id == self.bot.user.id:
                return
            await self.bot.process_commands(message)

    def _setup_modules(self):
        from modules import relationships, messages, channels, guilds, voice, settings, interactions, invites, webhooks, stickers, billing, experiments
        for module in [relationships, messages, channels, guilds, voice, settings, interactions, invites, webhooks, stickers, billing, experiments]:
            if hasattr(module, 'setup'):
                module.setup(self.bot)

    async def start(self, token):
        await self.bot.start(token)

    async def stop(self):
        await self.bot.close()
