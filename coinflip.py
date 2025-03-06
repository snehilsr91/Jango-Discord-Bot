import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

async def flip_coin(interaction: discord.Interaction):
    # Initial embed with coin flipping GIF
    coin_gif = "https://media1.tenor.com/m/-wn76VhsrtUAAAAC/kanao-kanao-tsuyuri.gif"  # Replace with preferred GIF
    flip_embed = discord.Embed(
        title="🪙 **Flipping the Coin...** 🪙",
        description="Hold your breath... Let's see what it lands on!",
        color=0xD30000
    )
    flip_embed.set_image(url=coin_gif)
    
    # Send initial embed
    await interaction.response.send_message(embed=flip_embed)

    # Wait for 2-3 seconds
    await asyncio.sleep(3)

    # Determine coin flip result
    result = random.choice(["Heads", "Tails"])
    emoji = "✨🪙✨" if result == "Heads" else "🌀"
    fancy_result = f"{result.upper()}"

    # Result embed
    result_embed = discord.Embed(
        title=f"🎯 **The Verdict is In!** 🎯",
        description=f"The coin landed on ***{fancy_result}***!",
        color=0xD30000
    )
    result_embed.set_footer(text="Flip again for your luck!")
    result_embed.timestamp = discord.utils.utcnow()

    # Send the result embed
    await interaction.followup.send(embed=result_embed)

def setup(bot):
    @bot.tree.command(name="coinflip", description="Flip a coin and see if it lands on Heads or Tails!")
    async def coinflip(interaction: discord.Interaction):
        await flip_coin(interaction)
