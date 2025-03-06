import discord
from discord import app_commands
from utils import execute_solo_command
from config import anime_commands_enabled


def setup(bot):
    @bot.tree.command(name="sad", description="Express your sadness with a GIF")
    @app_commands.check(anime_commands_enabled)
    async def sad(interaction: discord.Interaction):
        await execute_solo_command(interaction, "sad", "is sad. ☹️", "has been sad")

    @bot.tree.command(name="die", description="Dramatically die with a GIF")
    @app_commands.check(anime_commands_enabled)
    async def die(interaction: discord.Interaction):
        await execute_solo_command(interaction, "die", "is dead. 👻", "has dramatically died")

    @bot.tree.command(name="solodance", description="Show off your solo dance moves!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "solodance", "is showing off their dance moves!!", "has danced")

    @bot.tree.command(name="smirk", description="Be smug!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "smirk", "is smirking.. SO SMUG!!", "has smirked")

    @bot.tree.command(name="cry", description="Cry your heart out!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "cry", "is crying... Someone please give a hug", "has cried")

    @bot.tree.command(name="laugh", description="Laugh your butt off!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "laugh", "is just wheezing lmao!!", "has laughed")

    @bot.tree.command(name="happy", description="No reason not to be happy, right?!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "happy", "is so happpiieeee! LOVE IT!!", "has been happy")

    @bot.tree.command(name="angry", description="No reason to be happy, right?!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "angry", "is so enraged...", "has been angry")

    @bot.tree.command(name="hmph", description="You're upset??BE MAD!!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "hmph", "is pouting... HMPH!!", "has pouted")

    @bot.tree.command(name="salute", description="Salute for your comrades!!")
    @app_commands.check(anime_commands_enabled)
    async def solodance(interaction: discord.Interaction):
        await execute_solo_command(interaction, "salute", "is saluting!!", "has saluted")
