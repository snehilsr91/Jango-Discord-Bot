import discord
from discord import app_commands
import aiohttp
import random
from words import emoji_dict
from database import increment_translator_stats

# -------------------------- Fallback Dictionaries -------------------------- #
pirate_dict = {
    "hello": "ahoy", "hi": "yo-ho-ho", "my": "me", "friend": "matey",
    "is": "be", "are": "be", "you": "ye", "how are you": "how be ye doin'",
    "the": "th'", "of": "o'", "where": "whar", "there": "thar",
    "yes": "aye", "no": "nay", "stop": "avast", "yes sir": "aye aye, cap'n",
    "mate": "matey"
}

minionese_dict = {
    "hello": "bello", "apple": "bapple", "ice cream": "gelato", "thank you": "tank yu",
    "banana": "bananaaa", "i am": "me", "what": "po ka", "fire": "bee do bee do bee do",
    "stop": "tatata bala tu", "ugly": "babababa", "love": "tulaliloo ti amo"
}

uwu_faces = ["(・`ω´・)", "uwu", "(＾◡＾)", "(✿◠‿◠)", "(￣ω￣;)"]
thug_dict = {
    "hello": "yo", "friend": "homie", "money": "dolla", "cool": "dope", "car": "ride",
    "awesome": "lit", "problem": "hustle", "police": "5-0"
}

morse_dict = {
    "a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".",
    "f": "..-.", "g": "--.", "h": "....", "i": "..", "j": ".---",
    "k": "-.-", "l": ".-..", "m": "--", "n": "-.", "o": "---",
    "p": ".--.", "q": "--.-", "r": ".-.", "s": "...", "t": "-",
    "u": "..-", "v": "...-", "w": ".--", "x": "-..-", "y": "-.--",
    "z": "--..", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.", "0": "-----"
}

# -------------------------- Translation Functions -------------------------- #
async def translate_with_api(text, api_url):
    params = {"text": text}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if the data is a list
                    if isinstance(data, list) and data:
                        translation = data[0].get("translated")
                    elif isinstance(data, dict):
                        translation = data.get("translated")
                    else:
                        translation = None

                    if translation:
                        return translation

                print(f"API Error {response.status}: {await response.text()}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    return None


async def pirate_translate(text):
    api_url = "https://pirate.monkeyness.com/api/translate"
    params = {"english": text}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    translation = await response.text()
                    if translation:
                        return translation
                print(f"API Error {response.status}: {await response.text()}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    return " ".join([pirate_dict.get(word, word) for word in text.lower().split()]) or text

async def minionese_translate(text):
    return " ".join([minionese_dict.get(word, word) for word in text.lower().split()]) or text

async def uwu_translate(text):
    uwu_text = text.replace("r", "w").replace("l", "w").replace("na", "nya").replace("mo", "mowo")
    return f"{uwu_text} {random.choice(uwu_faces)}"

async def emoji_translate(text):
    return " ".join([emoji_dict.get(word, word) for word in text.lower().split()])

async def morse_translate(text):
    return " ".join([morse_dict.get(char, char) for char in text.lower()])

async def yoda_translate(text):
    words = text.split()
    mid = len(words) // 2
    return f"Hmm... {' '.join(words[mid:] + words[:mid])}, yes."

# -------------------------- Helper for Command Binding -------------------------- #
def create_translator_command(bot, name, func):
    @bot.tree.command(name=name, description=f"Translate text into {name} style.")
    @app_commands.describe(text="The text to translate")
    async def translate(interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        translated_text = await func(text)

        embed = discord.Embed(
            title=f"🌍 {name.capitalize()} Translator",
            description=f"**{translated_text}**",
            color=discord.Color.random()
        )
        embed.set_footer(text=f"Translated from: '{text}'")
        await interaction.followup.send(embed=embed)
        await increment_translator_stats(interaction.user.id, interaction)

# -------------------------- Discord Bot Setup -------------------------- #
def setup(bot):
    translators = {
        "pirate": pirate_translate,
        "minionese": minionese_translate,
        "uwu": uwu_translate,
        "emoji": emoji_translate,
        "morse": morse_translate,
        "yoda": yoda_translate
    }

    for name, func in translators.items():
        create_translator_command(bot, name, func)
