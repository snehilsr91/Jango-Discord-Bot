import discord
from discord import app_commands
import random
import asyncio
from database import update_tic_tac_toe_stat

# GIFs for tic_tac_toe challenges
tic_tac_toe_gifs = [
    "https://media1.tenor.com/m/Gctw4yiRBuwAAAAC/aharen-san-wa-hakarenai-aharen-ren.gif",
    "https://media1.tenor.com/m/i1PdFwjx0bUAAAAC/meme-movie.gif",
    "https://media1.tenor.com/m/alpCHGwZChgAAAAd/haikyu-haikyuu.gif"
]

class TicTacToeButton(discord.ui.Button):
    def __init__(self, row, column, game):
        super().__init__(label="⬜", style=discord.ButtonStyle.secondary, custom_id=f"{row}{column}")
        self.row = row
        self.column = column
        self.game = game
        

    async def callback(self, interaction: discord.Interaction):
        await self.game.make_move(interaction, self.row, self.column)

class TicTacToeGame(discord.ui.View):
    def __init__(self, player1, player2, interaction):
        super().__init__(timeout=60)
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.player1 = player1
        self.player2 = player2
        self.current_turn = player1
        self.buttons = [[TicTacToeButton(i, j, self) for j in range(3)] for i in range(3)]
        self.embed = discord.Embed(title="Tic-Tac-Toe!", color=0xD30000)
        self.embed.add_field(name="Participants", value=f"{self.player1.mention} and {self.player2.mention} are ready!")
        self.embed.add_field(name="Turn", value=f"{self.current_turn.mention}'s turn!")
        self.last_attack_time = asyncio.get_event_loop().time()
        self.first_interaction = interaction # To store the first interaction
        self.end_game_lock = asyncio.Lock()
        self.game_over = False  # Flag to track if the game has ended
        
        # ✅ Proper 3x3 grid layout
        for row in self.buttons:
            for button in row:
                self.add_item(button)

        # ✅ Add the "Quit" button at the bottom after the grid
        quit_button = discord.ui.Button(label="Quit", style=discord.ButtonStyle.danger, custom_id="unique_quit_button_id")
        quit_button.callback = self.quit_button_callback  # Assign callback for quit button
        self.add_item(quit_button)
        

    async def on_timeout(self):
        if self.game_over:  # Avoid multiple end_game calls
            return

        winner = self.player2 if self.current_turn == self.player1 else self.player2
        loser = self.player1 if self.current_turn == self.player1 else self.player2
        await self.end_game(self.first_interaction, f"{loser.mention} didn't respond in time, {winner.mention} wins!", winner, loser)

    async def make_move(self, interaction: discord.Interaction, row, col):
        if interaction.user != self.current_turn:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        if self.board[row][col] != " ":
            await interaction.response.send_message("That spot is already taken!", ephemeral=True)
            return

        symbol = "❌" if self.current_turn == self.player1 else "⭕"
        self.board[row][col] = symbol
        self.buttons[row][col].label = symbol
        self.buttons[row][col].style = discord.ButtonStyle.success if symbol == "❌" else discord.ButtonStyle.danger
        self.buttons[row][col].disabled = True
        # Check for a winner
        winner = self.check_winner()
        loser= self.player1 if winner==self.player2 else self.player2
        if winner:
            await self.end_game(interaction, f"{winner.mention} wins!", winner, loser)
            return

        # Check for a tie
        if all(self.board[i][j] != " " for i in range(3) for j in range(3)):
            await self.end_game(interaction, "It's a tie!", self.player1, self.player2)
            return

        self.current_turn = self.player1 if self.current_turn == self.player2 else self.player2
        self.embed.clear_fields()
        self.embed.add_field(name="Participants", value=f"{self.player1.mention} and {self.player2.mention} are ready!")
        self.embed.add_field(name="Turn", value=f"{self.current_turn.mention}'s turn!")
        await interaction.response.edit_message(embed=self.embed, view=self)

    def check_winner(self):
        """Check for a winning condition."""
        for row in self.board:
            if row[0] == row[1] == row[2] != " ":
                return self.player1 if row[0] == "❌" else self.player2

        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                return self.player1 if self.board[0][col] == "❌" else self.player2

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return self.player1 if self.board[0][0] == "❌" else self.player2

        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return self.player1 if self.board[0][2] == "❌" else self.player2

        return None

    async def interaction_check(self, interaction):
        # Only allow the player whose turn it is to make an attack
        self.first_interaction = interaction  # Store only the first interaction
        if interaction.user == self.current_turn or interaction.data["custom_id"] == "unique_quit_button_id":
            return True
        else:
            if interaction.data["custom_id"] != "quit_button":
                await interaction.response.send_message(f"{interaction.user.mention}, it's not your turn to attack!", ephemeral=True)
            return False
    
    async def end_game(self, interaction, message, winner, loser):
        """End the game and disable all buttons."""
        async with self.end_game_lock:
            if self.game_over:
                return  # Prevent multiple calls
            
            for row in self.buttons:
                for button in row:
                    button.disabled = True

            self.game_over=True
            self.embed.add_field(name="Game Over", value=message)
            self.embed.set_image(url=random.choice(tic_tac_toe_gifs))
            self.embed.remove_field(1)
            self.clear_items()  # Disable all buttons


            try:
                if interaction.response.is_done():
                    await interaction.followup.send(embed=self.embed, view=self)
                else:
                    await interaction.response.edit_message(embed=self.embed, view=self)
            except discord.NotFound:
                pass  # If message is deleted, don't crash

            if "tie" in message:
                await update_tic_tac_toe_stat(winner.id, "tie", interaction)  # Store win
                await update_tic_tac_toe_stat(loser.id, "tie", interaction)
            else:
                await update_tic_tac_toe_stat(winner.id, "win", interaction)  # Store win
                await update_tic_tac_toe_stat(loser.id, "lose", interaction)  # Store loss

    # Callback for quit button
    async def quit_button_callback(self, interaction: discord.Interaction):
        if self.game_over:  # Prevent multiple calls
            return

        loser = interaction.user
        winner = self.player1 if interaction.user == self.player2 else self.player2
        await self.end_game(interaction, f"{loser.mention} quit the game! {winner.mention} wins!", winner, loser)


class TicTacToeInviteView(discord.ui.View):
    def __init__(self, user, opponent):
        super().__init__()
        self.user = user
        self.opponent = opponent

    async def interaction_check(self, interaction):
        return interaction.user == self.opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = True
        self.stop()
        await interaction.response.send_message(f"{self.opponent.mention} accepted the challenge! Let's go! {self.user.mention}")

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.accepted = False
        self.stop()
        await interaction.response.send_message(f"{self.opponent.mention} declined the challenge.")

async def invite_for_tic_tac_toe(interaction: discord.Interaction, opponent: discord.Member):
    # Check if the user is challenging themselves
    if interaction.user == opponent:
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge yourself!", ephemeral=True)
        return
    
    # Check if the user or opponent is a bot
    if opponent.bot:
        await interaction.response.send_message(f"{interaction.user.mention}, you can't challenge a bot!", ephemeral=True)
        return

    
    view = TicTacToeInviteView(interaction.user, opponent)
    await interaction.response.send_message(f"{interaction.user.mention} challenged {opponent.mention} to tic-tac-toe!", view=view)
    await view.wait()
    if not view.accepted:
        # Challenge was declined or timed out
        await interaction.followup.send(f"{opponent.mention} didn't respond. Challenge canceled.")
        return
    
    fight_view = TicTacToeGame(interaction.user, opponent, interaction)

    await interaction.followup.send(embed=fight_view.embed,view=fight_view)


def setup(bot):
    @bot.tree.command(name="tic_tac_toe", description="Challenge someone to a Tic-Tac-Toe game!")
    @app_commands.describe(opponent="The person you want to play against")
    async def tic_tac_toe(interaction: discord.Interaction, opponent: discord.Member):
        await invite_for_tic_tac_toe(interaction, opponent)