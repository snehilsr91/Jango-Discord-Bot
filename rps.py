import discord
from discord import app_commands
import random
from database import update_rps_stats

def setup(bot):
    @bot.tree.command(name="rps", description="Play Rock Paper Scissors!")
    @app_commands.describe(choice="Choose rock, paper, or scissors")
    async def rps(interaction: discord.Interaction, choice: str):
        
        choice=choice.lower()
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        if choice not in choices:
            await interaction.response.send_message("Invalid choice! Choose rock, paper, or scissors.", ephemeral=True)
            return

        # Determine the result
        result = "It's a tie!" if choice == bot_choice else (
            "You win!" if (choice == "rock" and bot_choice == "scissors") or 
            (choice == "paper" and bot_choice == "rock") or 
            ((choice == "scissors" or choice == "scissor") and bot_choice == "paper") else "You lose!"
        )

        embed = discord.Embed(title="Rock Paper Scissors", description=f"You chose **{choice}**\n and I chose **{bot_choice}**\n\n**{result}**", color=0xD30000)
        await interaction.response.send_message(embed=embed)

        # Update the user's stats in the database
        await update_rps_stats(interaction.user.id, result, choice, interaction)