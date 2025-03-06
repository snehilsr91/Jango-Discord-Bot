import discord
from discord.ext import commands
from discord import app_commands
import bot_commands
import translators, trivia, ball8
import bar_fight, rps, tic_tac_toe, coinflip
import cowboy, cowboy_shop, bottle_shooting, train_heist, jail
import user_profile, vote, leaderboard
import solo_gif, group_gif, helper, badges, config
import wanted_poster
from config import BOT_TOKEN
import asyncio
from database import cursor, free_user, time, add_xp  # Import necessary database functions

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Background task to auto-release jailed users
async def auto_release_jailed_users(bot):
    """Background task to automatically release users after 12 hours."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        cursor.execute("SELECT user_id, jailed_time FROM jailed_users")
        jailed_users = cursor.fetchall()
        current_time = time.time()

        for user_id, jailed_time in jailed_users:
            if current_time - jailed_time >= 12 * 3600:  # 12 hours in seconds
                await free_user(user_id)
                user = await bot.fetch_user(user_id)
                await user.send("🎉 You have been automatically released from jail after 12 hours!")

        await asyncio.sleep(3600)  # Check every hour

@bot.event
async def on_ready():
    activity = discord.Game(name="/help")  # Customize this
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    bot.loop.create_task(auto_release_jailed_users(bot))  # Start the background task

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Add XP whenever a user uses a slash command."""
    if interaction.type == discord.InteractionType.application_command:  # Check if it's a slash command
        user_id = interaction.user.id
        add_xp(user_id, 1)  # Add 10 XP per command

# --- Error Handling ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle errors for slash commands."""
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌This command is either admin-only, restricted to a specific channel or has been disabled in this server. Ask an admin to enable this command.", ephemeral=True)
    else:
        # Log other errors (optional)
        print(f"An error occurred: {error}")
        await interaction.response.send_message("❌ An error occurred while processing your command.", ephemeral=True)

# Load Commands
bot_commands.setup(bot)
translators.setup(bot)
bar_fight.setup(bot)
user_profile.setup(bot)
solo_gif.setup(bot)
group_gif.setup(bot)
rps.setup(bot)
tic_tac_toe.setup(bot)
trivia.setup(bot)
ball8.setup(bot)
cowboy.setup(bot)
cowboy_shop.setup(bot)
coinflip.setup(bot)
helper.setup(bot)
badges.setup(bot)
bottle_shooting.setup(bot)
wanted_poster.setup(bot)
train_heist.setup(bot)
jail.setup(bot)
config.setup(bot)
vote.setup(bot)
leaderboard.setup(bot)

bot.run(BOT_TOKEN)