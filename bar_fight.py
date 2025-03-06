import discord
from discord import app_commands
import random
import asyncio
from database import update_bar_fight_stat, get_bar_fight_stats, is_jailed, update_user_coins, update_bounty, get_user_coins, get_equipped_items

# GIFs for bar fights
bar_fight_gifs = [
    "https://media1.tenor.com/m/3_sc_lGWRzwAAAAd/bar-fight-brawl.gif",
    "https://media1.tenor.com/m/EgdCsAWXREQAAAAC/cowboy-bebop-spike-spiegel.gif"
]

class BarFightView(discord.ui.View):
    def __init__(self, user, opponent, user_hp, opponent_hp, user_jacket, opponent_jacket, interaction):
        super().__init__(timeout=60)  # Set timeout to 60 seconds
        self.user = user
        self.opponent = opponent
        self.user_hp = user_hp
        self.opponent_hp = opponent_hp
        self.turn = user
        self.chair_attack_uses = {self.user: 2, self.opponent: 2}  # max uses for chair attack
        self.bottle_smash_uses = {self.user: 5, self.opponent: 5}  # max uses for bottle smash
        self.embed = discord.Embed(title="Bar Fight!", color=0xD30000)
        self.embed.add_field(name="Participants", value=f"{self.user.mention} and {self.opponent.mention} are ready for the bar fight!")
        self.embed.add_field(name="HP", value=f"{self.user.mention}: {self.user_hp} HP\n{self.opponent.mention}: {self.opponent_hp} HP")
        self.embed.add_field(name="Turn", value=f"{self.turn.mention}'s turn to attack!")
        self.embed.add_field(name="Attack", value="Attack!")
        self.last_attack_time = asyncio.get_event_loop().time()
        self.first_interaction = interaction  # To store the first interaction
        self.end_game_lock = asyncio.Lock()
        self.game_over = False  # Flag to track if the game has ended
        self.attack_history = []  # List to store the last 5 attacks
        if user_jacket is None:
            self.user_factor=0
        elif user_jacket=="Dustrunner’s Hide":
            self.user_factor=1
        else:
            self.user_factor=2

        if opponent_jacket is None:
            self.opponent_factor=0
        elif opponent_jacket=="Dustrunner’s Hide":
            self.opponent_factor=1
        else:
            self.opponent_factor=2 

    async def on_timeout(self):
        if self.game_over:  # Avoid multiple end_game calls
            return
        
        winner = self.user if self.turn == self.opponent else self.opponent
        loser = self.user if self.turn == self.user else self.opponent
        # If the game had started, the player who didn't take their turn loses
        await self.end_game(self.first_interaction,f"{loser.mention} didn't respond in time, {winner.mention} won the bar fight!",winner,loser)

    async def interaction_check(self, interaction):
        # Only allow the player whose turn it is to make an attack
        self.first_interaction = interaction  # Store only the first interaction
        if interaction.user == self.turn or interaction.data["custom_id"] == "quit_button":
            return True
        else:
            if interaction.data["custom_id"] != "quit_button":
                await interaction.response.send_message(f"{interaction.user.mention}, it's not your turn to attack!", ephemeral=True)
            return False

    async def end_game(self, interaction, message, winner, loser):
        async with self.end_game_lock:
            if self.game_over:
                return  # Prevent multiple calls
            
            coins=random.randint(30,50)
            loser_coins=min(get_user_coins(loser.id),coins)
            self.game_over = True
            self.embed.add_field(name="Game Over", value=f"{message}\n {winner.mention} wins {coins}🪙 and {loser.mention} loses {loser_coins}🪙")
            self.embed.remove_field(2)
            self.embed.remove_field(0)

            # Get the streak info for the winner
            winner_stats = get_bar_fight_stats(winner.id)
            winner_current_streak = winner_stats[2]

            self.embed.set_footer(text=f"{winner.display_name} is on a HOT streak of {winner_current_streak+1}🔥")

            self.embed.set_image(url=random.choice(bar_fight_gifs))
            self.clear_items()  # Disable all buttons

            try:
                if interaction.response.is_done():
                    await interaction.followup.send(embed=self.embed, view=self)
                else:
                    await interaction.response.edit_message(embed=self.embed, view=self)
            except discord.NotFound:
                pass  # If message is deleted, don't crash


            update_user_coins(winner.id,coins)
            update_user_coins(loser.id,-loser_coins)
            update_bounty(winner.id,"bar_fight_win")

            await update_bar_fight_stat(winner, "win", interaction)  # Store win
            await update_bar_fight_stat(loser, "lose", interaction)  # Store loss

    async def attack(self, interaction, damage, attack_type):
        # Determine which player's HP to decrease
        if self.turn == self.user:
            self.opponent_hp -= damage
            attack_message = f"{self.user.mention} hits {self.opponent.mention} for {damage} damage!"
            if attack_type=="bottle" and damage>1:
                if self.opponent_factor==1 or self.opponent_factor==2:
                    jacket="Dustrunner’s Hide" if self.opponent_factor==1 else "Nightstalker’s Cloak"
                    attack_message = f"{self.user.mention} hits {self.opponent.mention} for {damage-1} damage!"
                    attack_message+=f" ({self.opponent.mention}'s Jacket Advantage: {jacket})"
                    self.opponent_hp+=1
            elif attack_type=="chair":
                if self.opponent_factor==2:
                    jacket="Nightstalker’s Cloak"
                    attack_message = f"{self.user.mention} hits {self.opponent.mention} for {damage-1} damage!"
                    attack_message+=f" ({self.opponent.mention}'s Jacket Advantage: {jacket})"
                    self.opponent_hp+=1
            self.turn = self.opponent
        else:
            self.user_hp -= damage
            attack_message = f"{self.opponent.mention} hits {self.user.mention} for {damage} damage!"
            if attack_type=="bottle" and damage>1:
                if self.user_factor==1 or self.user_factor==2:
                    jacket="Dustrunner’s Hide" if self.user_factor==1 else "Nightstalker’s Cloak"
                    attack_message = f"{self.opponent.mention} hits {self.user.mention} for {damage-1} damage!"
                    attack_message+=f" ({self.user.mention}'s Jacket Advantage: {jacket})"
                    self.user_hp+=1
            elif attack_type=="chair":
                if self.user_factor==2:
                    jacket="Nightstalker’s Cloak"
                    attack_message = f"{self.opponent.mention} hits {self.user.mention} for {damage-1} damage!"
                    attack_message+=f" ({self.user.mention}'s Jacket Advantage: {jacket})"
                    self.user_hp+=1
            self.turn = self.user

        # Add the attack message to the history
        self.attack_history.append(attack_message)

        # Keep only the last 5 attacks
        if len(self.attack_history) > 5:
            self.attack_history.pop(0)

        # Update the embed with the last 5 attacks
        self.embed.clear_fields()
        self.embed.add_field(name="Participants", value=f"{self.user.mention} and {self.opponent.mention} are ready for the bar fight!")
        self.embed.add_field(name="HP", value=f"{self.user.mention}: {self.user_hp} HP\n{self.opponent.mention}: {self.opponent_hp} HP")
        self.embed.add_field(name="Turn", value=f"{self.turn.mention}'s turn to attack!")  # Whose turn it is
        self.embed.add_field(name="Attack", value="\n".join(self.attack_history))  # Show the last 5 attacks

        # Check if someone won
        if self.user_hp <= 0 or self.opponent_hp <= 0:
            if self.user_hp <= 0 or self.opponent_hp <= 0:
                if not self.game_over:  # Ensure only one call to end_game
                    winner = self.user if self.opponent_hp <= 0 else self.opponent
                    loser= self.opponent if self.opponent_hp <=0 else self.user
                    await self.end_game(interaction, f"{winner.mention} won the bar fight!", winner, loser)
                return

        else:
            await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.select(
        placeholder="Choose your attack type",
        options=[
            discord.SelectOption(label="Drunken Punch", description="Use your damn fists!! 1-2 damage (unlimited uses)", value="punch"),
            discord.SelectOption(label="Chair Attack", description="Pick up a chair and throw it!! 4-6 damage (2 uses)", value="chair"),
            discord.SelectOption(label="Bottle Smash", description="Smash a bottle!! 1-7 damage (5 uses)", value="bottle")
        ]
    )
    async def select_callback(self, interaction, select):
        self.interaction=interaction
        attack_type = select.values[0]
        if attack_type == "punch":
            damage = random.randint(1, 2)
        elif attack_type == "chair":
            if self.chair_attack_uses[self.turn] > 0:
                damage = random.randint(4, 6)
                self.chair_attack_uses[self.turn] -= 1
            else:
                # Send an ephemeral response instead of a public message
                await interaction.response.send_message(f"{interaction.user.mention}, you are out of chair attacks, there are no chairs left!!", ephemeral=True)
                return
        elif attack_type == "bottle":
            if self.bottle_smash_uses[self.turn] > 0:
                damage = random.randint(1, 7)
                self.bottle_smash_uses[self.turn] -= 1
            else:
                # Send an ephemeral response instead of a public message
                await interaction.response.send_message(f"{interaction.user.mention}, you are out of bottle smashes, there are no bottles left!!", ephemeral=True)
                return

        await self.attack(interaction, damage, attack_type)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.danger, custom_id="quit_button")
    async def quit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_over:  # Prevent multiple calls
            return

        loser = interaction.user
        winner = self.user if interaction.user == self.opponent else self.opponent
        await self.end_game(interaction, f"{loser.mention} quit the game! {winner.mention} wins!", winner, loser)



class BarFightInviteView(discord.ui.View):
    def __init__(self, user, opponent, user_hp):
        super().__init__()
        self.user = user
        self.opponent = opponent
        self.user_hp = user_hp
        self.accepted = False

    async def interaction_check(self, interaction):
        return interaction.user == self.opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = True
        self.stop()
        await interaction.response.send_message(f"{self.opponent.mention} accepted!! THE BAR FIGHT IS ON!!! Let's go! {self.user.mention}")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = False
        self.stop()
        await interaction.response.send_message(f"{self.opponent.mention} declined the challenge.")

async def invite_for_bar_fight(interaction: discord.Interaction, opponent: discord.Member, hp: int):
    # Check if the user is jailed
    if is_jailed(interaction.user.id):
        await interaction.response.send_message(f"{interaction.user.mention}, you can't enter a bar fight! You're in jail!! Use `jailbreak` to escape.", ephemeral=True)
        return
    
    # Check if the user is challenging themselves
    if interaction.user == opponent:
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge yourself to a bar fight!", ephemeral=True)
        return
    
    # Check if the opponent is jailed
    if is_jailed(opponent.id):
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge a user who is in jail!!", ephemeral=True)
        return
    
    # Check if the user or opponent is a bot
    if opponent.bot:
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge a bot to a bar fight!", ephemeral=True)
        return

    
    if hp < 20 or hp > 50:
        # Send an ephemeral error message to the user who initiated the challenge
        await interaction.response.send_message(f"{interaction.user.mention}, please provide a valid HP value between 20 and 50.", ephemeral=True)
        return
    
    view = BarFightInviteView(interaction.user, opponent, hp)
    await interaction.response.send_message(f"{interaction.user.mention} challenged {opponent.mention} to a bar fight with {hp} HP!", view=view)
    await view.wait()
    if not view.accepted:
        await interaction.followup.send(f"{opponent.mention} didn't respond. Challenge canceled.")
        return

    items1=get_equipped_items(interaction.user.id)
    items2=get_equipped_items(opponent.id)
    jacket1=items1["jacket"]
    jacket2=items2["jacket"]
    fight_view = BarFightView(interaction.user, opponent, hp, hp, jacket1, jacket2, interaction)  # Set both players' HP
    await interaction.followup.send(embed=fight_view.embed, view=fight_view)

def setup(bot):
    @bot.tree.command(name="bar_fight", description="Get involved in a bar fight with someone!!")
    @app_commands.describe(opponent="The user you want to invite", hp="The maximum HP for both players")
    async def bar_fight(interaction: discord.Interaction, opponent: discord.Member, hp: int):
        await invite_for_bar_fight(interaction, opponent, hp)