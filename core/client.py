import discord
from discord.ext import commands

class DiscordClient:
    def __init__(self):
        self.bot = commands.Bot(
            command_prefix='!',
            self_bot=True,
            help_command=None,
            intents=discord.Intents.all()
        )
        self.ready = False
        self._setup_events()
        self._setup_modules()

    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            self.ready = True
            print(f"✅ Autentificat ca: {self.bot.user} (ID: {self.bot.user.id})")
            print(f"📊 Conectat la {len(self.bot.guilds)} servere")
            print(f"👥 {len(self.bot.user.friends)} prieteni")
            print("=" * 50)

        @self.bot.event
        async def on_message(message):
            if message.author.id == self.bot.user.id:
                return
            # Aici vine logica AI
            await self.bot.process_commands(message)

    def _setup_modules(self):
        # Importăm modulele și le încărcăm
        from modules import relationships, messages, channels, guilds, voice, settings, interactions, invites, webhooks, stickers, billing, experiments
        # Înregistrăm comenzile
        for module in [relationships, messages, channels, guilds, voice, settings, interactions, invites, webhooks, stickers, billing, experiments]:
            if hasattr(module, 'setup'):
                module.setup(self.bot)

    async def start(self, token):
        await self.bot.start(token)

    async def stop(self):
        await self.bot.close()