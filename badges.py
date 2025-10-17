import discord
from discord import app_commands

BADGES = {
    #Trivia Badges
    "🔰": "Trivia Novic",  # Badge for 1 correct answer
    "🥉": "Trivia Expert",  # Badge for 10 correct answers
    "🥈": "Trivia Master",  # Badge for 50 correct answers
    "🥇": "Trivia Legend",  # Badge for 200 correct answers
    
    #Bar Fight Badges
    "🩸": "First Blood",  # Badge for 1 bar fight win
    "💥": "Haymaker",  # Badge for 20 bar fight wins
    "<:sf_beer:1341493938267226222>": "The Unstoppable Drunk",  # Badge for 100 bar fight wins

    #Bottle Shooting Badges
    "<:bottle:1341494505752232087>": "Bottle Blaster",  # Badge for shooting 100 bottles
    "🎯": "Sharpshooter Supreme",  # Badge for 25 bottle shooting contest wins

    #Cowboy Duel Badges
    "<:blobCowboy:1341492890274369678>": "Quick-Draw Rookie",  # Badge for 1 cowboy duel win
    "<:cat_cowboy:1341495301839519806>": "Dueling Daredevil",  # Badge for 10 cowboy duel wins
    "⏳": "The Quick and the Dead",  # Badge for 25 cowboy duel wins
    "🌵": "High Noon Hero",  # Badge for 50 cowboy duel wins
    "🏜️": "Legend of the West",  # Badge for 100 cowboy duel wins

    #Train Heist Badges
    "🚆": "Boxcar Bandit",  # Badge for 1 successful train heist
    "🚂": "Conductor’s Nightmare",  # Badge for 20 successful train heists
    "🚧": "Master of the Rails",  # Badge for 50 successful train heists
    "🔓": "Lock Breaker",  # Badge for cracking 20 lock codes
    "💀": "Guard Slayer",  # Badge for killing 500 guards
    "💰": "Loot Master", # Badge for looting 5000 coins from train heists

    #Jail Badges
    "👮": "Jail-Bound",  # Badge for going to jail 1 time
    "🏴‍☠️": "The Ghost of Alcatraz",  # Badge for 20 times
    "🏃‍♂️": "Breakout Rookie",  # Badge for escaping from jail 1 time
    "⛓️": "Chain Breaker",  # Badge for escaping from jail 15 times
    "🪂": "Escape Ace",  # Badge for escaping from jail 50 times

    #Vote Badges
    "👍": "Bot Believer",  # Badge for 200 correct answers
    "💖": "Loyal Supporter",  # Badge for 200 correct answers
    "🛡️": "Vote Vanguard",  # Badge for 200 correct answers

    #Misc Badges
    "🤓": "Polyglot Prodigy",  # Badge for using translation commands 100 times
    "❌": "Grid Genius",  # Badge for winning tic-tic-toe 20 times
    "✂️": "RPS Royalty",  # Badge for winning at rock paper scissors 100 times
    "<:vip:1341794893592268841>": "VIP" # Badge for being a VIP
}

# Dictionary for badge descriptions
BADGE_DESCRIPTIONS = {
    "🔰": "Correctly answer 1 trivia questions",
    "🥉": "Correctly answer 10 trivia questions",
    "🥈": "Correctly answer 50 trivia questions",
    "🥇": "Correctly answer 200 trivia questions\n",
    "🩸": "Win 1 bar fight",
    "💥": "Win 20 bar fights",
    "<:sf_beer:1341493938267226222>": "Win 100 bar fights\n",
    "<:bottle:1341494505752232087>": "Badge for shooting 100 bottles",
    "🎯": "Win 25 bottle shooting contests\n",
    "<:blobCowboy:1341492890274369678>": "Win 1 cowboy duel",
    "<:cat_cowboy:1341495301839519806>": "Win 10 cowboy duels",
    "⏳": "Win 25 cowboy duels",
    "🌵": "Win 50 cowboy duels",
    "🏜️": "Win 100 cowboy duels\n",
    "🚆": "Badge for 1 successful train heist",
    "🚂": "Badge for 20 successful train heists",
    "🚧": "Badge for 50 successful train heists",
    "🔓": "Crack 20 lock codes",
    "💀": "Kill 500 guards",
    "💰": "Badge for looting 5000 coins from train heists\n",
    "👮": "Go to jail 1 time",
    "🏴‍☠️": "Go to jail 20 times",
    "🏃‍♂️": "Escape from jail 1 time",
    "⛓️": "Escape from jail 15 times",
    "🪂": "Escape from jail 50 times\n",
    "👍": "Vote for the bot on top.gg 1 time",
    "💖": "Vote for the bot on top.gg 10 times",
    "🛡️": "Vote for the bot on top.gg 50 times\n",
    "🤓": "Use translation commands 100 times",
    "❌": "Win 20 tic-tac-toe games",
    "✂️": "Win against the bot at rock paper scissors 100 times\n",
    "<:vip:1341794893592268841>": "Badge for being a VIP",
}

def setup(bot):
    @bot.tree.command(name="badges", description="Display all badges and their descriptions")
    async def badges(interaction: discord.Interaction):
        # Create a single string with all badges and their descriptions
        description = ""
        for emoji, name in BADGES.items():
            # Get the description from the BADGE_DESCRIPTIONS dictionary
            badge_description = BADGE_DESCRIPTIONS.get(emoji, "No description available.")
            description += f"{emoji} **{name}**: {badge_description}\n"

        # Create an embed with the description
        embed = discord.Embed(
            title="🏅 Badges 🏅",
            description=description,
            color=0xD30000,
        )
        embed.set_footer(text="Tip: Go to your profile to check your badges won.")

        # Send the embed as a response
        await interaction.response.send_message(embed=embed)
