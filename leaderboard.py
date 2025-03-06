import discord
from discord import app_commands
from discord.ext import commands
from database import get_top_bounty_users, get_top_xp_users

def setup(bot):
    @bot.tree.command(name="leaderboard", description="Show the top 10 users by bounty or XP")
    async def leaderboard(interaction: discord.Interaction):
        # Create a select menu with options for bounty and XP leaderboards
        select_menu = discord.ui.Select(
            placeholder="Choose a leaderboard",
            options=[
                discord.SelectOption(label="Bounty Leaderboard", value="bounty", description="Top 10 users by bounty"),
                discord.SelectOption(label="XP Leaderboard", value="xp", description="Top 10 users by XP")
            ]
        )

        # Define the callback for the select menu
        async def select_callback(interaction: discord.Interaction):
            selected_value = select_menu.values[0]
            if selected_value == "bounty":
                top_users = get_top_bounty_users()
                title = "🏆 **Top 10 Users by Bounty** 🏆"
                description = "\n".join([f"{i+1}. <@{user[0]}> - {user[1]} bounty" for i, user in enumerate(top_users)])
            else:
                top_users = get_top_xp_users()
                title = "🏆 **Top 10 Users by XP** 🏆"
                description = "\n".join([f"{i+1}. <@{user[0]}> - {user[1]} XP" for i, user in enumerate(top_users)])

            embed = discord.Embed(title=title, description=description, color=discord.Color.gold())
            await interaction.response.edit_message(embed=embed)

        # Attach the callback to the select menu
        select_menu.callback = select_callback

        # Create a view and add the select menu to it
        view = discord.ui.View()
        view.add_item(select_menu)

        # Fetch the initial leaderboard (bounty by default)
        top_users = get_top_bounty_users()
        title = "🏆 **Top 10 Users by Bounty** 🏆"
        description = "\n".join([f"{i+1}. <@{user[0]}> - {user[1]} bounty" for i, user in enumerate(top_users)])

        embed = discord.Embed(title=title, description=description, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed, view=view)