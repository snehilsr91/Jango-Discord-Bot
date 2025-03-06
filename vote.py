import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from aiohttp import web, ClientConnectorError  # Import ClientConnectorError
import json
import time
from database import conn, update_cooldown
from config import TOPGG_TOKEN, BOT_ID

def setup(bot):
    # Webhook handler for automatic vote detection
    async def handle_webhook(request):
        # Verify the authorization header
        auth = request.headers.get("Authorization")
        if auth != TOPGG_TOKEN:
            return web.Response(status=401, text="Unauthorized")

        # Parse the JSON payload
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")

        # Extract user ID and bot ID from the payload
        user_id = data.get("user")
        bot_id = data.get("bot")

        if bot_id != BOT_ID:
            return web.Response(status=400, text="Invalid bot ID")

        # Update the database and send a thank-you DM
        cursor = conn.cursor()
        current_time = time.time()

        # Check if the user has already voted recently
        cursor.execute("SELECT last_vote_time FROM user_votes WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            last_vote_time = result[0]
            cooldown = 12 * 60 * 60  # 12 hours cooldown in seconds
            if current_time - last_vote_time < cooldown:
                # User has already voted recently
                return web.Response(status=200, text="User has already voted recently")

        # Update the user's vote count in the database
        cursor.execute("""
            INSERT INTO user_votes (user_id, vote_count, last_vote_time) 
            VALUES (?, 1, ?)
            ON CONFLICT(user_id) DO UPDATE 
            SET vote_count = vote_count + 1, last_vote_time = ?
        """, (user_id, current_time, current_time))
        conn.commit()

        # Release the train_heist cooldown
        update_cooldown(user_id, cooldown_time=True)

        # Get the updated vote count
        cursor.execute("SELECT vote_count FROM user_votes WHERE user_id = ?", (user_id,))
        vote_count = cursor.fetchone()[0]

        # Send a thank-you DM to the user
        user = bot.get_user(int(user_id))
        if user:
            try:
                await user.send(
                    embed=discord.Embed(
                        title="🎉 Thanks for Voting! 🎉",
                        description=f"You've voted **{vote_count}** times!\nYour **train_heist** cooldown has been reset!",
                        color=0x00FF00
                    )
                )
            except discord.Forbidden:
                # If the user has DMs disabled, log the error
                print(f"Could not send DM to user {user_id}")

        return web.Response(status=200, text="Vote recorded")

    # Start the web server for top.gg webhook
    async def start_web_server():
        web_server = web.Application()
        web_server.router.add_post("/webhook", handle_webhook)
        runner = web.AppRunner(web_server)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)  # Change port if needed
        await site.start()
        print("Webhook server started on port 8080")

    # Use the setup_hook to start the web server
    bot.setup_hook = start_web_server

    # /vote command for manual vote checking
    @bot.tree.command(name="vote", description="Check your vote status or release the train_heist cooldown.")
    async def vote(interaction: discord.Interaction):
        user_id = interaction.user.id
        cursor = conn.cursor()

        # Assign current_time at the beginning to avoid UnboundLocalError
        current_time = interaction.created_at.timestamp()

        # Check if the user has voted on top.gg
        async def has_user_voted(user_id: int, bot_id: int, topgg_token: str) -> bool:  
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": topgg_token}
                async with session.get(f"https://top.gg/api/bots/{bot_id}/check?userId={user_id}", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("voted", False)
                    return False
                    
        has_voted = await has_user_voted(user_id, BOT_ID, TOPGG_TOKEN)

        if has_voted:
            # Check the last vote time from the database
            cursor.execute("SELECT last_vote_time FROM user_votes WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                last_vote_time = result[0]
                cooldown = 12 * 60 * 60  # 12 hours cooldown in seconds
                if current_time - last_vote_time < cooldown:
                    # User has already voted recently
                    remaining_time = cooldown - (current_time - last_vote_time)
                    hours, remainder = divmod(remaining_time, 3600)
                    minutes, _ = divmod(remainder, 60)

                    embed = discord.Embed(
                        title="⏳ You've Already Voted!",
                        description=f"Please wait **{int(hours)} hours and {int(minutes)} minutes** to vote again.",
                        color=0xFFA500
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

            # Update the user's vote count in the database
            cursor.execute("""
                INSERT INTO user_votes (user_id, vote_count, last_vote_time) 
                VALUES (?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE 
                SET vote_count = vote_count + 1, last_vote_time = ?
            """, (user_id, current_time, current_time))
            conn.commit()

            # Release the train_heist cooldown
            update_cooldown(user_id, cooldown_time=True)

            # Get the updated vote count
            cursor.execute("SELECT vote_count FROM user_votes WHERE user_id = ?", (user_id,))
            vote_count = cursor.fetchone()[0]

            # Send a response to the user
            embed = discord.Embed(
                title="🎉 Thanks for Voting! 🎉",
                description=f"You've voted **{vote_count}** times!\nYour **train_heist** cooldown has been reset!",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # If the user hasn't voted, prompt them to vote
            embed = discord.Embed(
                title="Vote to Unlock Rewards!",
                description="You haven't voted yet! [Vote on top.gg](https://top.gg/bot/1122526375157448714) to release your **train_heist** cooldown and earn rewards!",
                color=0xFF0000
            )
            embed.set_footer(text="After voting, use the /vote command again to reset your train_heist cooldown.")
            await interaction.response.send_message(embed=embed)