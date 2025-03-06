import discord
from discord import app_commands
from discord.ui import Button, View, Select
import random, time
import requests
import html
from collections import defaultdict
from database import increment_correct_count, update_fastest_time, increment_total_questions, increment_total_sessions
from questions import questions

# Dictionary to track active sessions by channel ID
active_sessions = {}

# Function to fetch trivia question with fallback to 2 different APIs
def get_trivia_question(category_id, category_name):
    url = f"https://opentdb.com/api.php?amount=1&type=multiple&category={category_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        if data['response_code'] == 0:  # Valid response code from API
            return data['results'][0]
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching from primary API: {e}")
        # Fallback to secondary API (example: Trivia API by RapidAPI)
        fallback_url = f"https://api.triviaapi.com/v1/questions?category={category_id}&amount=1"
        try:
            response = requests.get(fallback_url)
            response.raise_for_status()
            data = response.json()
            if data.get('questions'):
                return data['questions'][0]
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching from secondary API: {e}")
            # Fallback to a third API or predefined questions if both fail
            return random.choice(questions[category_name])
    return None

def setup(bot):
    @bot.tree.command(name="trivia", description="Start a trivia session!")
    async def trivia(interaction: discord.Interaction, num_questions: int):
        channel_id = interaction.channel.id

        # Check if there is already an active trivia session in the channel
        if channel_id in active_sessions and active_sessions[channel_id]:
            await interaction.response.send_message("A trivia session is already in progress in this channel.", ephemeral=True)
            return

        if not (1 <= num_questions <= 20):
            await interaction.response.send_message("Please choose a number between 1 and 20.", ephemeral=True)
            return

        # Mark the channel as active when the trivia session starts
        active_sessions[channel_id] = False  # Prevents a session from starting prematurely

        categories = {
            "Any Category": "any",  # Option for any category randomly
            "General Knowledge": 9,
            "Entertainment: Film": 11,
            "Entertainment: Music": 12,
            "Science: Computers": 18,
            "Science: Gadgets": 30,
            "Science: Nature": 17,
            "Sports": 21,
            "Geography": 22
        }

        class CategorySelect(View):
            def __init__(self):
                super().__init__(timeout=30)
                options = [
                    discord.SelectOption(label=cat, value=str(cat_id))
                    for cat, cat_id in categories.items()
                ]
                self.select = Select(placeholder="Choose a trivia category...", options=options)
                self.select.callback = self.category_selected
                self.add_item(self.select)

            async def category_selected(self, interaction: discord.Interaction):
                channel_id = interaction.channel.id

                # Ensure that no trivia session has been started already
                if active_sessions.get(channel_id, False):
                    await interaction.response.send_message("A trivia session has already started. Please wait for it to finish.", ephemeral=True)
                    return

                category_id = self.select.values[0]
                if category_id == "any":
                    category_name = "Random Category"
                    category_id = random.choice([v for v in categories.values() if v != "any"])  # Randomly pick a category
                else:
                    category_name = [k for k, v in categories.items() if str(v) == category_id][0]

                # Mark the session as started after category selection
                active_sessions[channel_id] = True

                await interaction.response.defer()
                await interaction.delete_original_response()

                # Start the trivia session after the category selection
                await TriviaSession(interaction, int(category_id), category_name, num_questions, channel_id).start()

        await interaction.response.send_message("Choose a trivia category:", view=CategorySelect(), ephemeral=True)


class TriviaSession:
    def __init__(self, interaction, category_id, category_name, num_questions, channel_id=None):
        self.interaction = interaction
        self.category_id = category_id
        self.category_name = category_name
        self.num_questions = num_questions
        self.current_question = 0
        self.scores = defaultdict(int)
        self.channel = channel_id

    async def start(self):
        await self.ask_question()

    async def ask_question(self):
        if self.current_question >= self.num_questions:
            await self.show_leaderboard(self.category_name)
            active_sessions[self.channel]=False
            return

        # Fetch trivia question from the primary or fallback APIs
        question_data = get_trivia_question(self.category_id, self.category_name)
        if not question_data:
            await self.interaction.followup.send("❌ Unable to fetch trivia questions. Please try again later.", ephemeral=True)
            return

        question = html.unescape(question_data['question'])
        correct_answer = html.unescape(question_data['correct_answer'])
        incorrect_answers = [html.unescape(ans) for ans in question_data['incorrect_answers']]
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)

        answer_text = "\n".join([f"**{i+1}.** {ans}" for i, ans in enumerate(all_answers)])

        embed = discord.Embed(
            title=f"Trivia: {self.category_name} (Q{self.current_question + 1}/{self.num_questions})",
            description=f"**{question}**\n\n{answer_text}\n\n⏳ **Time limit: 20 seconds**",
            color=0x00FF00
        )

        class AnswerButtonView(View):
            def __init__(self, session, correct_answer, all_answers):
                super().__init__(timeout=20)
                self.session = session
                self.correct_answer = correct_answer
                self.all_answers = all_answers
                self.answered_users = set()
                self.start_time = time.time()  # Capture the start time of the question

                for i, answer in enumerate(all_answers):
                    button = Button(label=f"Option {i+1}", custom_id=f"answer_{i}", style=discord.ButtonStyle.primary)
                    button.callback = self.create_callback(i)
                    self.add_item(button)

            def create_callback(self, index):
                async def callback(interaction: discord.Interaction):
                    if interaction.user.id in self.answered_users:
                        await interaction.response.send_message("❌ You've already answered this question!", ephemeral=True)
                        return

                    self.answered_users.add(interaction.user.id)
                    selected_answer = self.all_answers[index]
                    increment_total_questions(interaction.user.id)

                    if selected_answer == self.correct_answer:
                        time_taken = time.time() - self.start_time
                        update_fastest_time(interaction.user.id,time_taken)
                        
                        await interaction.response.send_message(
                            f"🎉 **{interaction.user.mention} got it right!** The correct answer was: **{self.correct_answer}**", ephemeral=False
                        )
                        await increment_correct_count(interaction)
                        self.session.scores[interaction.user] += 1
                        self.disable_all_buttons()
                        self.stop()
                        await self.session.next_question()
                    else:
                        self.session.scores[interaction.user] = self.session.scores[interaction.user] if self.session.scores[interaction.user] else 0
                        await interaction.response.send_message("❌ Incorrect! Try again next time.", ephemeral=True)

                return callback

            def disable_all_buttons(self):
                for child in self.children:
                    child.disabled = True

            async def on_timeout(self):
                # If no one answered within the time limit, show the correct answer
                timeout_message = f"⏰ Time's up! The correct answer was: **{self.correct_answer}**"
                await self.session.interaction.followup.send(timeout_message)
                await self.session.next_question()

        view = AnswerButtonView(self, correct_answer, all_answers)
        await self.interaction.followup.send(embed=embed, view=view)

    async def next_question(self):
        self.current_question += 1
        await self.ask_question()

    async def show_leaderboard(self, category):
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard_text = "\n".join([f"**{user.mention}** - {score} correct" for user, score in sorted_scores])
        for user,score in sorted_scores:
            increment_total_sessions(user.id)
        embed = discord.Embed(
            title="Trivia Session Leaderboard",
            description=leaderboard_text if leaderboard_text else "Nobody participated in the session 😔",
            color=0xFFD700
        )
        embed.set_footer(text=f"Category: {category}")
        await self.interaction.followup.send(embed=embed)
