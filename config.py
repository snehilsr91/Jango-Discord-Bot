from discord import app_commands
from discord.ext import commands
import discord
from database import update_server_config, get_server_config


def setup(bot):
    @bot.tree.command(name="config", description="Configure bot settings for this server. Enable or disable commands.")
    @app_commands.describe(
        option="Choose an option: disable_anime, enable_anime",
    )
    @app_commands.choices(option=[
        app_commands.Choice(name="disable_anime", value="disable_anime"),
        app_commands.Choice(name="enable_anime", value="enable_anime"),
    ])
    @app_commands.checks.has_permissions(administrator=True)  # Restrict to admins
    async def config(interaction: discord.Interaction, option: app_commands.Choice[str]):
        server_id = interaction.guild.id

        if option.value == "disable_anime":
            update_server_config(server_id, anime_enabled=0)
            await interaction.response.send_message("✅ Anime commands have been **disabled** for this server.", ephemeral=True)
        
        elif option.value == "enable_anime":
            update_server_config(server_id, anime_enabled=1)
            await interaction.response.send_message("✅ Anime commands have been **enabled** for this server.", ephemeral=True)


def anime_commands_enabled(interaction: discord.Interaction) -> bool:
    """Check if anime commands are enabled or if the user is an admin."""
    server_id = interaction.guild.id
    config = get_server_config(server_id)
    
    # If anime commands are enabled, allow the command
    if config["anime_enabled"]:
        return True
    
    # If anime commands are disabled, only allow admins to see the command
    return interaction.user.guild_permissions.administrator