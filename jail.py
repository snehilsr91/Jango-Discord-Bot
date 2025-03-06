import discord
from discord import app_commands, ui
from discord.ext import commands
import random
import asyncio, time
from database import is_jailed, free_user, update_user_coins, get_user_coins, get_cooldowns, update_bounty, update_daily_cooldown

def setup(bot):
    @bot.tree.command(name="jailbreak", description="Attempt to escape from jail.")
    async def jailbreak(interaction: discord.Interaction):
        user_id = interaction.user.id

        # Check if the user is in jail
        if not is_jailed(user_id):
            await interaction.response.send_message("🚨 You are not in jail!", ephemeral=True)
            return

        # Create an embed with the options
        embed = discord.Embed(
            title="🚨 Jailbreak",
            description="Choose how you want to escape from jail:",
            color=0xD30000
        )
        embed.add_field(name="Pay Out", value="Pay a fee of **500 coins** to be freed.", inline=False)
        embed.add_field(name="Escape Out", value="Solve 4 random math questions to escape.", inline=False)

        # Create a view with buttons
        view = discord.ui.View(timeout=None)

        # Pay Out Button
        async def pay_out_callback(interaction: discord.Interaction):
            user_id = interaction.user.id

            # Check if the user has enough coins
            if get_user_coins(user_id) < 500:
                await interaction.response.send_message("❌ You don't have enough coins to pay the fee!", ephemeral=True)
                return

            # Deduct 500 coins and free the user
            update_user_coins(user_id, -500)
            await free_user(user_id)

            # Disable buttons
            for item in view.children:
                item.disabled = True

            await interaction.response.edit_message(view=view)
            await interaction.followup.send("🎉 You have paid the fee and been freed from jail!", ephemeral=False)

        # Escape Out Button
        async def escape_out_callback(interaction: discord.Interaction):
            user_id = interaction.user.id

            # Generate 4 random math questions
            questions = []
            answers = []
            for _ in range(4):
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                op = random.choice(["+", "-", "*"])
                question = f"{a} {op} {b}"
                answer = str(eval(question))  # Calculate the correct answer
                questions.append(question)
                answers.append(answer)

            # Send the questions in an embed
            embed = discord.Embed(
                title="🔢 Solve the Math Questions",
                description="You have 5 seconds to memorize the answers!",
                color=0xD30000
            )
            for i, question in enumerate(questions):
                embed.add_field(name=f"Question {i+1}", value=question, inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # Delete the embed after 5 seconds
            await asyncio.sleep(5)
            try:
                await interaction.delete_original_response()
            except discord.errors.NotFound:
                # If the message is already deleted, ignore the error
                pass

            # Ask the user to enter the answers
            embed = discord.Embed(
                title="🔐 Enter the Answers",
                description="Enter the 4 answers separated by spaces (e.g., `3 5 7 2`).",
                color=0xD30000
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            # Wait for the user's response
            def check(m):
                return m.author.id == user_id and m.channel.id == interaction.channel_id

            try:
                response = await bot.wait_for("message", timeout=30, check=check)
                user_answers = response.content.split()

                # Check if the answers are correct
                if user_answers == answers:
                    await free_user(user_id, escaped=True, interaction=interaction)  # Pass escaped=True when the user escapes
                    update_bounty(user_id, "jail_escape")
                    await interaction.followup.send("🎉 You solved the questions and escaped from jail!", ephemeral=False)
                else:
                    await interaction.followup.send("❌ Incorrect answers! You remain in jail.", ephemeral=False)
            except asyncio.TimeoutError:
                await interaction.followup.send("⏰ Time's up! You remain in jail.", ephemeral=False)

            # Disable buttons
            for item in view.children:
                item.disabled = True

            # Edit the original message to disable buttons
            try:
                await interaction.edit_original_response(view=view)
            except discord.errors.NotFound:
                # If the original message is already deleted, ignore the error
                pass

            
        # Add buttons to the view
        pay_out_button = discord.ui.Button(label="Pay Out", style=discord.ButtonStyle.green)
        pay_out_button.callback = pay_out_callback
        view.add_item(pay_out_button)

        escape_out_button = discord.ui.Button(label="Escape Out", style=discord.ButtonStyle.red)
        escape_out_button.callback = escape_out_callback
        view.add_item(escape_out_button)

        # Send the embed with buttons
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


    @bot.tree.command(name="cooldown", description="Check your or another user's cooldowns.")
    @app_commands.describe(user="The user to check cooldowns for (leave blank to check yourself).")
    async def cooldown(interaction: discord.Interaction, user: discord.User = None):
        # If no user is provided, default to the command user
        target_user = user or interaction.user
        user_id = target_user.id

        # Get cooldowns from the database
        cooldowns = get_cooldowns(user_id)

        # Calculate remaining time for each cooldown
        current_time = time.time()
        train_heist_remaining = None
        jail_remaining = None
        daily_remaining = None
        vote_remaining = None

        if cooldowns["train_heist"]:
            train_heist_remaining = max(0, (cooldowns["train_heist"] + 2 * 3600) - current_time)  # 5-hour cooldown

        if cooldowns["jail"]:
            jail_remaining = max(0, (cooldowns["jail"] + 12 * 3600) - current_time)  # 12-hour cooldown

        if cooldowns["daily"]:
            daily_remaining = max(0, (cooldowns["daily"] + 24 * 3600) - current_time)  # 24-hour cooldown

        if cooldowns["vote"]:
            vote_remaining = max(0, (cooldowns["vote"] + 12 * 3600) - current_time)  # 24-hour cooldown

        # Create an embed to display the cooldowns
        embed = discord.Embed(
            title=f"⏳ Cooldowns for {target_user.display_name}",
            color=0xD30000
        )

        # Add train heist cooldown
        if train_heist_remaining is not None and train_heist_remaining > 0:
            hours = int(train_heist_remaining // 3600)
            minutes = int((train_heist_remaining % 3600) // 60)
            embed.add_field(
                name="🚆 Train Heist Cooldown",
                value=f"**{hours}h {minutes}m** remaining.",
                inline=False
            )
        else:
            embed.add_field(
                name="🚆 Train Heist Cooldown",
                value="No active cooldown.",
                inline=False
            )

        # Add jail cooldown
        if jail_remaining is not None and jail_remaining > 0:
            hours = int(jail_remaining // 3600)
            minutes = int((jail_remaining % 3600) // 60)
            embed.add_field(
                name="🚨 Jail Cooldown",
                value=f"**{hours}h {minutes}m** remaining.",
                inline=False
            )
        else:
            embed.add_field(
                name="🚨 Jail Cooldown",
                value="Not in jail.",
                inline=False
            )

        # Add daily cooldown
        if daily_remaining is not None and daily_remaining > 0:
            hours = int(daily_remaining // 3600)
            minutes = int((daily_remaining % 3600) // 60)
            embed.add_field(
                name="🎁 Daily Cooldown",
                value=f"**{hours}h {minutes}m** remaining.",
                inline=False
            )
        else:
            embed.add_field(
                name="🎁 Daily Cooldown",
                value="No active cooldown.",
                inline=False
            )

        # Add daily cooldown
        if vote_remaining is not None and vote_remaining > 0:
            hours = int(vote_remaining // 3600)
            minutes = int((vote_remaining % 3600) // 60)
            embed.add_field(
                name="✅ Vote Cooldown",
                value=f"**{hours}h {minutes}m** remaining.",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Vote Cooldown",
                value="No active cooldown.",
                inline=False
            )

        embed.set_footer(text="Vote for bot on top.gg to reset your Train Heist cooldown.")

        # Send the embed
        await interaction.response.send_message(embed=embed, ephemeral=False)

    
    @bot.tree.command(name="daily", description="Claim your daily coins.")
    async def daily(interaction: discord.Interaction):
        user_id = interaction.user.id

        # Get the user's cooldowns from the database
        cooldowns = get_cooldowns(user_id)

        # Check if the user has already claimed their daily coins today
        current_time = time.time()
        if cooldowns["daily"] and (current_time - cooldowns["daily"]) < 24 * 3600:
            # Calculate remaining time
            remaining_time = 24 * 3600 - (current_time - cooldowns["daily"])
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)

            await interaction.response.send_message(
                f"⏳ You have already claimed your daily 🪙! Please wait **{hours}h {minutes}m**.",
                ephemeral=True
            )
            return

        # Update the user's daily cooldown in the database
        update_daily_cooldown(user_id)

        # Give the user their daily coins (e.g., 1000 coins)
        daily_coins = 50
        update_user_coins(user_id, daily_coins)

        await interaction.response.send_message(
            f"🎉 You claimed your daily **{daily_coins}🪙**! Come back in 24 hours to claim again.",
            ephemeral=False
        )