import discord
import random
import asyncio, time
from discord import app_commands
from discord.ui import View, Button
from database import get_cooldown, update_cooldown, is_jailed, jail_user, update_user_coins, update_bounty, get_equipped_items, update_train_heist_stats
from cowboy import get_factor
from cowboy_shop import BOOTS

heist_gifs=[
    "https://media1.tenor.com/m/a1naSTCEBwUAAAAC/arthur-morgan-rdr2.gif",
    "https://media1.tenor.com/m/HPFobo4hdcMAAAAC/arthur-morgan-rdr2.gif",
    "https://media1.tenor.com/m/1OzOo883qD0AAAAC/rdr2-red-dead-redemption2.gif"
]

def setup(bot):
    @bot.tree.command(name="train_heist", description="Team up and rob a train!")
    async def train_heist(interaction: discord.Interaction):
        await interaction.response.defer()

        # 🏆 Join Phase (Users have 10s to join)
        participants = await join_phase(interaction)
        if not participants:
            await interaction.followup.send("🚨 No one joined the heist. Mission aborted!")
            return

        # Show confirmation message before Stage 1
        joined_users = "\n".join(f"<@{user}>" for user in participants)
        embed = discord.Embed(
            title="🚆 Train Heist Crew",
            description=f"The following players are in the heist:\n{joined_users}",
            color=0xD30000
        )
        await interaction.followup.send(embed=embed)

        # Short delay before Stage 1
        await asyncio.sleep(3)

        # 🚨 Stage 1: Fight the Guards
        if not await fight_guards(interaction, participants):
            # Participants are already jailed in the fight_guards function
            return

        # 🔐 Stage 2: Crack the Safe
        if not await crack_safe(interaction, participants):
            # Participants are already jailed in the crack_safe function
            return

        # 💰 Stage 3: Grab the Loot & Escape
        await grab_loot(interaction, participants)


async def join_phase(interaction: discord.Interaction):
    participants = set()
    view = View(timeout=10)

    async def join_callback(interaction: discord.Interaction):
        user_id = interaction.user.id

        # Check if the user is jailed
        if is_jailed(user_id):
            await interaction.response.send_message(
                f"🚨 {interaction.user.mention}, you're in jail! Use `/jailbreak` to escape.", 
                ephemeral=True
            )
            return

        # Check if the user is on cooldown
        last_join_time = get_cooldown(user_id)
        if last_join_time:
            cooldown_remaining = (last_join_time + 2 * 3600) - time.time()  # 5 hours in seconds
            if cooldown_remaining > 0:
                # User is on cooldown
                hours = int(cooldown_remaining // 3600)
                minutes = int((cooldown_remaining % 3600) // 60)
                await interaction.response.send_message(
                    f"⏳ You can join another heist in **{hours}h {minutes}m**.", 
                    ephemeral=True
                )
                return

        # If the user is not jailed or on cooldown, add them to the participants
        if user_id not in participants:
            participants.add(user_id)
            update_cooldown(user_id)  # Update the last join time
            await interaction.response.send_message(f"🤠 {interaction.user.mention} joined the heist!", ephemeral=True)

    button = Button(label="Join Heist", style=discord.ButtonStyle.success)
    button.callback = join_callback
    view.add_item(button)

    # Send the initial message with the timer
    message = await interaction.followup.send("🤠 **Train Heist is starting!** Click below to join! (10s)", view=view)

    # Timer logic
    start_time = time.time()
    while time.time() - start_time < 10:  # 10-second timer
        remaining_time = int(10 - (time.time() - start_time))
        await message.edit(content=f"🤠 **Train Heist is starting!** Click below to join! Time left: **{remaining_time}s**", view=view)
        await asyncio.sleep(1)

    # Disable the button after the timer ends
    for item in view.children:
        item.disabled = True
    await message.edit(view=view)

    return list(participants)  # Return list of joined user IDs


# 🚨 Stage 1: Fight the Guards (4x5 Grid with Guard Emojis)
async def fight_guards(interaction: discord.Interaction, participants):
    # Determine the number of guards based on the number of participants
    num_participants = len(participants)
    if num_participants == 1:
        num_guards = random.randint(4, 6)  # 4-6 guards for 1 member
    elif num_participants == 2:
        num_guards = random.randint(6, 9)  # 6-9 guards for 2 members
    elif num_participants == 3:
        num_guards = random.randint(9, 12)  # 9-12 guards for 3 members
    elif num_participants == 4:
        num_guards = random.randint(12, 15)  # 12-15 guards for 4 members
    else:
        num_guards = random.randint(16, 20)  # 16-20 guards for 4+ members

    guard_positions = random.sample(range(20), num_guards)  # Randomly place guards
    clicked_positions = set()
    view = View(timeout=10)  # 10 seconds to shoot all guards

    async def button_callback(interaction: discord.Interaction, index: int):
        if interaction.user.id in participants:
            if index in guard_positions:
                clicked_positions.add(index)
                await interaction.response.edit_message(view=view)

            if clicked_positions == set(guard_positions):  # All guards shot
                view.stop()

    for i in range(20):
        button = Button(label="👤" if i in guard_positions else "🔲", style=discord.ButtonStyle.red if i in guard_positions else discord.ButtonStyle.gray)
        button.callback = lambda inter, i=i: asyncio.create_task(button_callback(inter, i))
        view.add_item(button)

    # Send the initial message with the timer
    message = await interaction.followup.send("🔫 **Stage 1: Fight the Guards** - Click the guards before time runs out!", view=view)

    # Timer logic
    start_time = time.time()
    while time.time() - start_time < 10:  # 10-second timer
        remaining_time = int(10 - (time.time() - start_time))
        await message.edit(content=f"🔫 **Stage 1: Fight the Guards** - Click the guards before time runs out! Time left: **{remaining_time}s**", view=view)
        await asyncio.sleep(1)

    # Disable all buttons after the timer ends
    for item in view.children:
        item.disabled = True
    await message.edit(content="🔫 **Stage 1: Fight the Guards** - Time's up!", view=view)

    # Check if all guards were killed
    if clicked_positions != set(guard_positions):
        # Send all participants to jail
        for user_id in participants:
            await jail_user(user_id, interaction)  # Mark user as jailed
        await interaction.followup.send("🚨 The heist failed! The guards stopped you! All participants have been sent to jail. Use `/jailbreak` to escape.")
        return False  # End the game

    # Update the number of guards killed for each participant
    for user_id in participants:
        await update_train_heist_stats(user_id, guards_killed=num_guards, interaction=interaction)

    return True  # Proceed to the next stage


# 🔐 Stage 2: Crack the Safe (5-button code guessing game)
async def crack_safe(interaction: discord.Interaction, participants):
    safe_code = [random.randint(1, 5) for _ in range(5)]  # Generate a random 5-digit code
    attempts = 6
    success = False

    embed = discord.Embed(title="🔐 Stage 2: Crack the Safe", description="Guess the 5-digit code!\n\n", color=0xD30000)
    embed.add_field(name="Your Guess:", value="⬜⬜⬜⬜⬜", inline=False)

    message = await interaction.followup.send(embed=embed, wait=True)

    async def update_embed(guess):
        """ Updates the embed with the current guess and hint feedback """
        if len(guess) < 5:
            guess_display = "".join(str(num) for num in guess) + "⬜" * (5 - len(guess))  
            embed.set_field_at(0, name="Your Guess:", value=guess_display, inline=False)
        else:
            hints = ["🟩" if guess[i] == safe_code[i] else "🟨" if guess[i] in safe_code else "🟥" for i in range(5)]
            embed.set_field_at(0, name="Your Guess:", value=" ".join(str(num) for num in guess), inline=False)
            embed.add_field(name="Hint:", value=" ".join(hints), inline=False)

        await message.edit(embed=embed, view=view)

    for _ in range(attempts):
        guess = []
        view = View(timeout=15)
        current_player = random.choice(participants)

        await interaction.followup.send(f"<@{current_player}>'s turn!")

        async def button_click(inter: discord.Interaction, number: int):
            """ Handles button clicks to input numbers """
            if inter.user.id not in participants:
                await inter.response.send_message("❌ You have not participated in this heist!", ephemeral=True)
                return

            if inter.user.id != current_player:
                await inter.response.send_message("❌ It's not your turn!", ephemeral=True)
                return

            guess.append(number)
            await inter.response.defer()
            await update_embed(guess)

            if len(guess) == 5:  # When 5 numbers are entered, check it
                if guess == safe_code:
                    nonlocal success
                    success = True
                view.stop()  # Instantly stop waiting for more input

        # Create buttons 1-5
        for i in range(1, 6):
            button = Button(label=str(i), style=discord.ButtonStyle.primary)
            button.callback = lambda inter, num=i: asyncio.create_task(button_click(inter, num))
            view.add_item(button)

        await message.edit(embed=embed, view=view)
        await view.wait()  # Only waits for the current input

        if success:
            # Update the number of safes cracked for each participant
            for user_id in participants:
                await update_train_heist_stats(user_id, safes_cracked=1, interaction=interaction)
            return True  # Safe cracked successfully

    # If all attempts fail, send all participants to jail
    for user_id in participants:
        await jail_user(user_id, interaction)  # Mark user as jailed
    await interaction.followup.send("💥 The safe was too tough to crack! All participants have been sent to jail. Use `/jailbreak` to escape.")
    return False  # Failed to crack safe


# 🪙 Stage 3: Grab the Loot & Escape
async def grab_loot(interaction: discord.Interaction, participants):
    loot = {user: 0 for user in participants}
    view = View(timeout=10)
    start_time = time.time()
    total_time = 15  # Game lasts 15 seconds

    async def loot_callback(interaction: discord.Interaction):
        if time.time() - start_time > total_time:  # Stop if time limit is reached
            return

        if interaction.user.id in loot:
            loot_collected = random.randint(10, 15)  # Random amount of loot per click
            loot[interaction.user.id] += loot_collected
            if random.random() < 0.2:  # 20% chance for an obstacle
                await interaction.response.send_message(f"🚆 The train is speeding up, {interaction.user.mention}! Click faster!", ephemeral=True)
            else:
                await interaction.response.defer()

    button = Button(label="💰 Grab Loot", style=discord.ButtonStyle.success)
    button.callback = loot_callback
    view.add_item(button)

    # Send the initial message with the timer
    message = await interaction.followup.send("💰 **Stage 3: Grab the Loot & Escape!** - Click as fast as you can!", view=view)

    # Timer logic
    while time.time() - start_time < total_time:
        remaining_time = int(total_time - (time.time() - start_time))
        await message.edit(content=f"💰 **Stage 3: Grab the Loot & Escape!** - Click as fast as you can! Time left: **{remaining_time}s**", view=view)
        await asyncio.sleep(1)

    view.stop()
    await message.edit(view=None)  # Disable button after time ends

    # Update the database with the collected loot
    for user_id, coins_collected in loot.items():
        update_user_coins(user_id, coins_collected)  # Add coins to the user's total
        await update_train_heist_stats(user_id, total_loot_collected=coins_collected, interaction=interaction)
        update_bounty(user_id, "train_heist")

    # Update the number of successful heists for each participant
    for user_id in participants:
        await update_train_heist_stats(user_id, successful_heists=1, interaction=interaction)

    # Create an embed to show the results
    embed = discord.Embed(
        title="🏆 Train Heist Results",
        description="Here's how much loot each participant collected:",
        color=0xD30000
    )
    # Create a description string that lists each member's loot
    description = ""
    for user_id, coins_collected in loot.items():
        items = get_equipped_items(user_id)
        boots = items["boots"]
        factor = get_factor(BOOTS, boots)
        coins = coins_collected + int((factor * coins_collected) / 100)
        description += f"<@{user_id}>: **{coins}🪙**\n"

    # Add the description to the embed
    embed.description = description
    embed.set_image(url=random.choice(heist_gifs))
    total_loot = sum(loot.values())
    embed.set_footer(text=f"Total loot collected: {total_loot}🪙")

    await interaction.followup.send(embed=embed)

