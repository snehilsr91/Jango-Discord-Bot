import discord
from discord import app_commands
from discord.ui import Button, View
import asyncio
import time, random
from database import get_user_coins, update_user_coins, get_equipped_items, update_shootout_stats, is_jailed, update_bounty
from cowboy_shop import HOLSTERS, GUNS, BOOTS, HATS


cowboy_gifs=[
    "https://media1.tenor.com/m/pW7JMd5q9LcAAAAC/cowboy-bebop-spike-spiegel.gif",
    "https://media1.tenor.com/m/db3jduFnXPIAAAAC/rdr2-john-marston.gif",
    "https://media1.tenor.com/m/YsP5ODHvty0AAAAC/john-marston-rdr.gif",
    "https://media1.tenor.com/m/HExoastQwvcAAAAC/red-dead-redemption-rdr2.gif"
]

def get_factor(dict_name,item_name):
    if item_name is None:
        return None
    for item in dict_name:
        if item["name"] == item_name:
            return item["factor"]
    return None  # Return None if the holster name is not found

class Shootout:
    def __init__(self, user, holster_factor, gun_factor, hat_factor):
        self.user = user
        self.start_time = None
        self.shoot_time = None
        self.final_time = None
        self.holster_factor=holster_factor
        self.gun_factor=gun_factor
        self.hat_factor=hat_factor
        self.target=""

    async def send_draw_button(self, interaction, opponent):
        """Send the Draw button to the user and manage the interaction"""
        draw_view = View()
        draw_button = Button(label="Draw", style=discord.ButtonStyle.primary)

        async def draw_callback(inter):
            if inter.user != self.user:
                await inter.response.send_message("This ain't your duel, partner!", ephemeral=True)
                return

            if self.start_time is not None:
                await inter.response.send_message("You've already drawn, cowboy!", ephemeral=True)
                return

            self.start_time = time.time()
            await inter.response.send_message(f"{inter.user.mention} has drawn their gun!", ephemeral=True)

            # Wait for both players to draw and then show the shoot button after a 5-second delay
            await asyncio.sleep(5-self.holster_factor)
            await self.show_shoot_button(interaction, opponent)

        draw_button.callback = draw_callback
        draw_view.add_item(draw_button)

        await interaction.followup.send(f"{self.user.mention}, click **Draw** to prepare your gun!", view=draw_view)

    async def show_shoot_button(self, interaction, opponent):
        """Show the Shoot button after both users have drawn their guns"""
        shoot_view = View()
        shoot_button = Button(label="Shoot", style=discord.ButtonStyle.danger)

        async def shoot_callback(inter):
            if inter.user != self.user:
                await inter.response.send_message("This ain't your duel, partner!", ephemeral=True)
                return

            if self.shoot_time is not None:
                await inter.response.send_message("The duel is already over, partner!", ephemeral=True)
                return

            self.shoot_time = time.time()
            self.final_time = self.shoot_time - self.start_time
            shoot_view.clear_items()
            roll = random.randint(1, 100)
            if roll < 30-self.gun_factor+self.hat_factor:
                self.target="miss"
            else:
                self.target="hit"
            await inter.response.send_message(f"{inter.user.mention} shot!!", ephemeral=True)

        shoot_button.callback = shoot_callback
        shoot_view.add_item(shoot_button)

        await interaction.followup.send(f"{self.user.mention}, **SHOOT NOW!**", view=shoot_view)

async def invite_for_shootout(interaction, opponent):
    """Handle the initial invitation and challenge acceptance"""
    if opponent == interaction.user:
        await interaction.response.send_message("You can't challenge yourself, cowboy!", ephemeral=True)
        return

    if opponent.bot:
        await interaction.response.send_message("You can't challenge a bot, partner!", ephemeral=True)
        return
    
    # Check if the user is jailed
    if is_jailed(interaction.user.id):
        await interaction.response.send_message(f"{interaction.user.mention}, you can't enter a bar fight! You're in jail!! Use `jailbreak` to escape.", ephemeral=True)
        return
    
    # Check if the opponent is jailed
    if is_jailed(opponent.id):
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge a user who is in jail!!", ephemeral=True)
        return

    invite_view = View()
    accept_button = Button(label="Accept", style=discord.ButtonStyle.success)
    reject_button = Button(label="Reject", style=discord.ButtonStyle.danger)

    async def accept_callback(inter):
        if inter.user != opponent:
            await inter.response.send_message("This ain't your challenge to accept, partner!", ephemeral=True)
            return
        invite_view.clear_items()
        await inter.response.edit_message(content=f"{opponent.mention} accepted the duel! 🤠", view=None)
        await start_duel(interaction, interaction.user, opponent)

    async def reject_callback(inter):
        if inter.user != opponent:
            await inter.response.send_message("This ain't your challenge to reject, partner!", ephemeral=True)
            return
        invite_view.clear_items()
        await inter.response.edit_message(content=f"{opponent.mention} rejected the duel. Duel canceled. 🤠", view=None)

    accept_button.callback = accept_callback
    reject_button.callback = reject_callback
    invite_view.add_item(accept_button)
    invite_view.add_item(reject_button)

    await interaction.response.send_message(f"{opponent.mention}, {interaction.user.mention} has challenged you to a cowboy duel! Do you accept?", view=invite_view)

async def start_duel(interaction, player1, player2):
    """Start the duel between two players"""
    items1=get_equipped_items(player1.id)
    items2=get_equipped_items(player2.id)
    gun1=items1["gun"]
    gun2=items2["gun"]
    hat1=items1["hat"]
    hat2=items2["hat"]
    holster1=items1["holster"]
    holster2=items2["holster"]
    player1_shootout = Shootout(player1,get_factor(HOLSTERS,holster1),get_factor(GUNS,gun1),get_factor(HATS,hat2) if get_factor(HATS,hat2) is not None else 0)
    player2_shootout = Shootout(player2,get_factor(HOLSTERS,holster2),get_factor(GUNS,gun2),get_factor(HATS,hat1) if get_factor(HATS,hat1) is not None else 0)

    # Send draw buttons for both players, handled by their respective classes
    await player1_shootout.send_draw_button(interaction, player2)
    await player2_shootout.send_draw_button(interaction, player1)

    # Wait for both players to complete the duel
    await asyncio.sleep(25)  # Wait for both players to finish their shoot actions

    # Declare the result based on the times taken for each player to shoot
    await declare_result(interaction, player1, player1_shootout.final_time, player1_shootout.target, player2, player2_shootout.final_time, player2_shootout.target)

async def declare_result(interaction, player1, player1_time, target1, player2, player2_time, target2):
    BASE_WIN_REWARD = 50
    BASE_DRAW_REWARD = 25

    # Coin Transfer Logic
    async def transfer_coins(winner, loser):
        loser_coins = get_user_coins(loser.id)
        COIN_STEAL_AMOUNT = random.randint(0, min(40, loser_coins))
        coins_stolen = min(COIN_STEAL_AMOUNT, loser_coins)
        update_bounty(winner.id,"cowboy_duel")
        if coins_stolen > 0:
            update_user_coins(winner.id, coins_stolen)
            update_user_coins(loser.id, -coins_stolen)
        return coins_stolen

    # Embed Generator
    def create_result_embed(title, description, winner=None, loser=None, coins_stolen=None, base_reward=0):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color(0xD30000) if winner else discord.Color(0x808080)
        )

        if winner and loser:
            total_reward = base_reward + coins_stolen
            embed.add_field(name="🏆 Winner", value=f"{winner.mention}", inline=True)
            embed.add_field(name="💀 Loser", value=f"{loser.mention}", inline=True)
            embed.add_field(name="💰 Coins Earned", value=f"**{base_reward}**🪙 (Base) + **{coins_stolen}**🪙 (Stolen) = **{total_reward}**🪙", inline=False)
        else:
            embed.add_field(name="⚔️ Outcome", value="**Draw**", inline=True)
            embed.add_field(name="💰 Participation Reward", value=f"Each player earns **{base_reward}**🪙.", inline=False)
            embed.set_footer(text="Good duel, cowboys!")
        
        embed.set_image(url=random.choice(cowboy_gifs))
        return embed

    # Result Logic
    if player1_time is None and player2_time is None:
        embed = create_result_embed(
            title="🤠 Cowboy Duel Result 🤠",
            description="Both players didn't shoot in time. Duel canceled."
        )
        await interaction.followup.send(embed=embed)
        return

    elif player2_time is None or player1_time is None:
        winner, loser = (player2, player1) if player1_time is None else (player1, player2)
        coins_stolen = await transfer_coins(winner, loser)
        update_user_coins(winner.id, BASE_WIN_REWARD)
        await update_shootout_stats(winner,"win", interaction)
        await update_shootout_stats(loser,"lose",interaction)

        embed = create_result_embed(
            title="🤠 Cowboy Duel Result 🤠",
            description=f"**{loser.mention} didn't shoot in time, {winner.mention} wins by default!**",
            winner=winner, loser=loser, coins_stolen=coins_stolen, base_reward=BASE_WIN_REWARD
        )
        await interaction.followup.send(embed=embed)
        return

    # Both Shot
    if player1_time < player2_time and target1 == "hit":
        coins_stolen = await transfer_coins(player1, player2)
        update_user_coins(player1.id, BASE_WIN_REWARD)
        await update_shootout_stats(player1,"win", interaction)
        await update_shootout_stats(player2,"lose",interaction)

        embed = create_result_embed(
            title="🤠 Cowboy Duel Result 🤠",
            description=f"**{player1.mention} was quicker on the draw and didn't miss!**",
            winner=player1, loser=player2, coins_stolen=coins_stolen, base_reward=BASE_WIN_REWARD
        )
        await interaction.followup.send(embed=embed)

    elif player2_time < player1_time and target2 == "hit":
        coins_stolen = await transfer_coins(player2, player1)
        update_user_coins(player2.id, BASE_WIN_REWARD)
        await update_shootout_stats(player2,"win", interaction)
        await update_shootout_stats(player1,"lose",interaction)

        embed = create_result_embed(
            title="🤠 Cowboy Duel Result 🤠",
            description=f"**{player2.mention} outgunned the competition, {player1.mention} was faster but missed!**",
            winner=player2, loser=player1, coins_stolen=coins_stolen, base_reward=BASE_WIN_REWARD
        )
        await interaction.followup.send(embed=embed)

    elif player1_time == player2_time:
        if target1 == "hit" and target2 == "miss":
            coins_stolen = await transfer_coins(player1, player2)
            update_user_coins(player1.id, BASE_WIN_REWARD)
            await update_shootout_stats(player1,"win", interaction)
            await update_shootout_stats(player2,"lose",interaction)

            embed = create_result_embed(
                title="🤠 Cowboy Duel Result 🤠",
                description=f"**{player1.mention} wins with a sharp shot! {player2.mention} missed their shot!**",
                winner=player1, loser=player2, coins_stolen=coins_stolen, base_reward=BASE_WIN_REWARD
            )
            await interaction.followup.send(embed=embed)

        elif target2 == "hit" and target1 == "miss":
            coins_stolen = await transfer_coins(player2, player1)
            update_user_coins(player2.id, BASE_WIN_REWARD)
            await update_shootout_stats(player2,"win", interaction)
            await update_shootout_stats(player1,"lose",interaction)

            embed = create_result_embed(
                title="🤠 Cowboy Duel Result 🤠",
                description=f"**{player2.mention} hits the mark and wins! {player1.mention} missed their shot!**",
                winner=player2, loser=player1, coins_stolen=coins_stolen, base_reward=BASE_WIN_REWARD
            )
            await interaction.followup.send(embed=embed)

        else:
            update_user_coins(player1.id, BASE_DRAW_REWARD)
            update_user_coins(player2.id, BASE_DRAW_REWARD)
            await update_shootout_stats(player2,"tie",interaction)
            await update_shootout_stats(player1,"tie",interaction)

            embed = create_result_embed(
                title="🤠 Cowboy Duel Result 🤠",
                description="It's a tie! Both players either missed or shot at the same time.",
                base_reward=BASE_DRAW_REWARD
            )
            await interaction.followup.send(embed=embed)
    else:
        update_user_coins(player1.id, BASE_DRAW_REWARD)
        update_user_coins(player2.id, BASE_DRAW_REWARD)
        await update_shootout_stats(player2,"tie",interaction)
        await update_shootout_stats(player1,"tie",interaction)

        embed = create_result_embed(
            title="🤠 Cowboy Duel Result 🤠",
            description="It's a tie! Both players missed their shots.",
            base_reward=BASE_DRAW_REWARD
        )
        await interaction.followup.send(embed=embed)

        
def setup(bot):
    @bot.tree.command(name="cowboy_duel", description="Challenge someone to a cowboy shootout")
    @app_commands.describe(opponent="The person you want to challenge")
    async def shootout(interaction: discord.Interaction, opponent: discord.Member):
        await invite_for_shootout(interaction, opponent)