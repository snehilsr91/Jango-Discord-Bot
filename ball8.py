import discord
from discord import app_commands
import random
import asyncio

ball_gifs=[
    "https://media1.tenor.com/m/sl3UIRK455QAAAAC/8ball-bart-simpson.gif",
    "https://media1.tenor.com/m/C--b2mPfzPgAAAAC/climate-change-is-real-lcvearthday.gif",
    "https://media1.tenor.com/m/7BjWvp2yPBkAAAAC/magic-8-magic-8-ball.gif"
]

def setup(bot):
    @bot.tree.command(name="8ball", description="Ask the magic 8ball a question!")
    @app_commands.describe(question="Ask the magic 8ball a question")
    async def eight_ball(interaction: discord.Interaction, question: str):
        # List of possible 8ball responses
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]

        # Create the initial embed with a shaking 8ball GIF
        initial_embed = discord.Embed(
            title="SHAKING MAGIC 8 BALL",
            color=0xD30000
        )
        initial_embed.set_image(url=random.choice(ball_gifs))  # Replace with your preferred GIF URL

        # Send the initial embed
        await interaction.response.send_message(embed=initial_embed)

        # Wait for 3 seconds
        await asyncio.sleep(3)

        # Randomly select a response
        response = random.choice(responses)

        # Create the result embed
        result_embed = discord.Embed(
            title="Magic 8ball",
            description=f"**Question:** {question}\n\n**Answer:** {response}",
            color=0xD30000
        )

        # Send the result embed as a follow-up message
        await interaction.followup.send(embed=result_embed)