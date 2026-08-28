import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='experiments')
    async def list_experiments(ctx):
        """Listează experimentele active"""
        experiments = bot.experiments
        if not experiments:
            await ctx.send("📭 Niciun experiment activ")
            return
        names = [f"{e.id}: {e.value}" for e in list(experiments.items())[:10]]
        await ctx.send(f"📋 Experimente: {', '.join(names)}")

    @bot.command(name='set_experiment')
    async def set_experiment(ctx, experiment_id: str, value: str):
        """Setează un experiment"""
        try:
            bot.set_experiment(experiment_id, value)
            await ctx.send(f"✅ Experiment {experiment_id} setat la {value}")
        except Exception as e:
            await ctx.send(f"❌ Eroare: {e}")