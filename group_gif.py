import discord
from discord import app_commands
from discord.ext import commands
from utils import execute_group_command  # ✅ Now using the function from utils.py
from config import anime_commands_enabled

def setup(bot):
    @bot.tree.command(name="grouphug", description="Give a big hug to multiple people!")
    @app_commands.check(anime_commands_enabled)
    @app_commands.describe(
        user1="The first user you want to hug (Required)",
        user2="The second user you want to hug (Optional)",
        user3="The third user you want to hug (Optional)",
        user4="The fourth user you want to hug (Optional)"
    )
    async def grouphug(
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member = None,
        user3: discord.Member = None,
        user4: discord.Member = None
    ):
        users = [user for user in [user1, user2, user3, user4] if user]  # Remove None values

        # Prevent the interaction user from hugging themselves
        if interaction.user in users:
            await interaction.response.send_message("You can't hug yourself!", ephemeral=True)
            return

        await execute_group_command(interaction, users, "hug", "is hugging", "has hugged others")

    @bot.tree.command(name="groupdance", description="Dance with friends!")
    @app_commands.check(anime_commands_enabled)
    @app_commands.describe(
        user1="The first user you want to dance with (Required)",
        user2="The second user you want to dance with (Optional)",
        user3="The third user you want to dance with (Optional)",
        user4="The fourth user you want to dance with (Optional)"
    )
    async def grouphug(
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member = None,
        user3: discord.Member = None,
        user4: discord.Member = None
    ):
        users = [user for user in [user1, user2, user3, user4] if user]  # Remove None values

        # Prevent the interaction user from hugging themselves
        if interaction.user in users:
            await interaction.response.send_message("You can't dance with yourself! Use the solodance command instead!!", ephemeral=True)
            return

        await execute_group_command(interaction, users, "dance", "is dancing", "has danced with/without others")
