import discord
from discord import app_commands
import asyncio
import random, time
from database import is_jailed, update_user_coins, update_bottle_shooting_stats

# Constants
BOTTLE_EMOJI = "🍾"
BUTTON_LABELS = ['🅰️', '🅱️', '🆎', '🆑']

# Button View Class
class BottleView(discord.ui.View):
    def __init__(self, players, scores, round_num):
        super().__init__(timeout=15)  # Set timeout to 15 seconds
        self.players = players
        self.scores = scores
        self.round_num = round_num
        self.current_bottle_button = None
        self.clicked = False

        # Add buttons
        for label in BUTTON_LABELS:
            self.add_item(BottleButton(label, self))

    async def start_shuffling(self, message):
        for _ in range(10):  # Shuffle 10 times
            # Clear the bottle emoji from all buttons
            for button in self.children:
                button.label = button.label.replace(BOTTLE_EMOJI, '')

            # Randomly choose a button to place the bottle
            self.current_bottle_button = random.choice(self.children)
            self.current_bottle_button.label += BOTTLE_EMOJI

            # Edit the message to reflect the new button labels
            await message.edit(view=self)
            await asyncio.sleep(0.5)  # Shuffle speed

    async def on_timeout(self):
        self.clicked = True
        self.stop()

    async def register_click(self, interaction: discord.Interaction, button):
        if self.clicked:
            await interaction.response.send_message("⚠️ Someone already shot the bottle!", ephemeral=True)
            return

        if button == self.current_bottle_button:
            self.scores[interaction.user] += 10
            self.clicked = True
            await interaction.response.send_message(f"🎯 **{interaction.user.display_name} hit the bottle!** (+10 points)", ephemeral=True)
            await interaction.followup.send(f"**Round {self.round_num} Winner:** {interaction.user.mention} 🎯 (+10 points)")
            self.stop()
        else:
            await interaction.response.send_message("❌ Missed! Try faster next time.", ephemeral=True)

# Button Logic
class BottleButton(discord.ui.Button):
    def __init__(self, label, custom_view):  # Renamed parameter to avoid conflict
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.custom_view = custom_view  # Store the view separately

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.custom_view.scores:
            await interaction.response.send_message("🚫 You're not part of this game!", ephemeral=True)
            return

        await self.custom_view.register_click(interaction, self)


# Challenge Handler
async def invite_for_bottle_shoot(interaction: discord.Interaction, opponent: discord.Member):
    if opponent.bot or opponent == interaction.user:
        await interaction.response.send_message("❌ You can't challenge yourself or a bot!", ephemeral=True)
        return
    
    # Check if the user is jailed
    if is_jailed(interaction.user.id):
        await interaction.response.send_message(f"{interaction.user.mention}, you can't enter a bar fight! You're in jail!! Use `jailbreak` to escape.", ephemeral=True)
        return
    
    # Check if the opponent is jailed
    if is_jailed(opponent.id):
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge a user who is in jail!!", ephemeral=True)
        return

    await interaction.response.send_message(
        f"🎯 {opponent.mention}, do you accept the **Bottle Shooting Contest** challenge from {interaction.user.mention}?",
        view=ChallengeView(interaction, opponent)
    )

# Challenge Accept/Decline View
class ChallengeView(discord.ui.View):
    def __init__(self, interaction, opponent):
        super().__init__(timeout=15)
        self.interaction = interaction
        self.opponent = opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("This challenge isn’t for you!", ephemeral=True)
            return

        await interaction.response.edit_message(content="✅ Challenge Accepted! Starting the game...", view=None)
        await start_bottle_game(self.interaction, [self.interaction.user, self.opponent])

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("This challenge isn’t for you!", ephemeral=True)
            return

        await interaction.response.edit_message(content="❌ Challenge Declined!", view=None)

# Start the Game
async def start_bottle_game(interaction, players):
    scores = {player: 0 for player in players}
    await interaction.followup.send("🎯 **Bottle Shooting Contest Begins!** Get ready...")

    for round_num in range(1, 6):
        await asyncio.sleep(random.randint(2, 4))  # Random delay before each round
        await interaction.followup.send(f"**Round {round_num}:** Get ready to shoot the moving bottle! 🍾")

        view = BottleView(players, scores, round_num)
        message = await interaction.followup.send("🔫 **Shoot the bottle when you see it!**", view=view)
        await view.start_shuffling(message)
        await view.wait()

    coins=random.randint(10,30)
    result_message=""
    # Display Final Scores
    for player, score in scores.items():
        await update_bottle_shooting_stats(player, bottles_shot=(score/10), interaction=interaction)
        result_message += f"**{player.display_name}**: {score} points\n"

    winner = max(scores, key=scores.get)
    embed = discord.Embed(
            title="🏆 Final Scores:",
            description=result_message if result_message else "Nobody got a single shot on a bottle!!",
            color=0xD30000
    )
    if result_message:
        if len(set(scores.values())) == 1:  # Check if all scores are the same (tie)
            embed.add_field(name="🏳️ Tie!", value="The scores were tied!")
        else:
            embed.add_field(name="🥇 Winner: ", value=f" {winner.mention}!")
            embed.set_footer(text=f"{winner.display_name} wins {coins}🪙")
            update_user_coins(winner.id,coins)
            await update_bottle_shooting_stats(winner, contests_won=1, interaction=interaction)

    await interaction.followup.send(embed=embed)

# Setup Function
def setup(bot):
    @bot.tree.command(name="bottle_shoot", description="Challenge someone to a bottle shooting contest")
    @app_commands.describe(opponent="The person you want to challenge")
    async def bottle_shoot(interaction: discord.Interaction, opponent: discord.Member):
        await invite_for_bottle_shoot(interaction, opponent)