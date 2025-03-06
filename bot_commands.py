import discord
from discord import app_commands
from utils import interaction_command  # Importing the helper function
from config import anime_commands_enabled

def setup(bot):
    @bot.tree.command(name="hug", description="Give someone a warm hug!")
    @app_commands.describe(target="The user you want to hug")
    @app_commands.check(anime_commands_enabled)
    async def hug(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "hug", "is hugging", "SO WARM!!", "has been hugged", "has hugged others")

    # Slash Command: /uppercut
    @bot.tree.command(name="uppercut", description="Uppercut someone!")
    @app_commands.describe(target="The user you want to uppercut")
    @app_commands.check(anime_commands_enabled)
    async def uppercut(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "uppercut", "just gave a nasty uppercut to", "That must have hurt!!", "has got uppercutted", "has given uppercuts to others")

    # Slash Command: /dropkick
    @bot.tree.command(name="dropkick", description="Dropkick someone!")
    @app_commands.describe(target="The user you want to dropkick")
    @app_commands.check(anime_commands_enabled)
    async def dropkick(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "dropkick", "just gave a crazy dropkick to", "", "has got dropkicked", "has dropkicked others")

    # Slash Command: /punch
    @bot.tree.command(name="punch", description="Punch someone!")
    @app_commands.describe(target="The user you want to punch")
    @app_commands.check(anime_commands_enabled)
    async def punch(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "punch", "just punched", "SMACKED!!", "has been punched", "has punched others")

    # Slash Command: /highfive
    @bot.tree.command(name="highfive", description="Give someone a high-five!")
    @app_commands.describe(target="The user you want to high-five")
    @app_commands.check(anime_commands_enabled)
    async def highfive(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "highfive", "gave a high-five to", "", "has received high-fives", "has given high-fives")

    @bot.tree.command(name="fistbump", description="Give someone a fistbump!")
    @app_commands.describe(target="The user you want to fistbump")
    @app_commands.check(anime_commands_enabled)
    async def fistbump(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "fistbump", "is bumping fists with", "", "has received fistbumps", "has given fistbumps")

    @bot.tree.command(name="slap", description="Slap someone!")
    @app_commands.describe(target="The user you want to slap")
    @app_commands.check(anime_commands_enabled)
    async def slap(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "slap", "just slapped", "", "has been slapped", "has slapped others")

    @bot.tree.command(name="handshake", description="Shake hands with someone!")
    @app_commands.describe(target="The user you want to shake hands with")
    @app_commands.check(anime_commands_enabled)
    async def kiss(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "handshake", "is shaking hands with", "", "has received handshakes", "has shook hands with others")

    @bot.tree.command(name="wave", description="Wave at someone!")
    @app_commands.describe(target="The user you want to wave at")
    @app_commands.check(anime_commands_enabled)
    async def wave(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "wave", "is waving at", "", "has been waved at", "has waved at others")

    @bot.tree.command(name="stab", description="Stab someone!")
    @app_commands.describe(target="The user you want to stab")
    @app_commands.check(anime_commands_enabled)
    async def stab(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "stab", "stabbed", "STABBY-STAB-STAB!!", "has been stabbed", "has stabbed others")

    @bot.tree.command(name="flirt", description="Flirt with someone!")
    @app_commands.describe(target="The user you want to flirt with")
    @app_commands.check(anime_commands_enabled)
    async def flirt(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "flirt", "is flirting with", "", "has been flirted with", "has flirted with others")

    @bot.tree.command(name="throw", description="Throw an object at someone!")
    @app_commands.describe(target="The user you want to throw something at")
    @app_commands.check(anime_commands_enabled)
    async def throw(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "throw", "is throwing objects at", "WATCH OUT!!", "has been hit with something", "has thrown objects at others")

    @bot.tree.command(name="feed", description="Feed someone!")
    @app_commands.describe(target="The user you want to feed")
    @app_commands.check(anime_commands_enabled)
    async def feed(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "feed", "is feeding", "", "has been fed", "has fed others")

    @bot.tree.command(name="headpat", description="Pat someone on the head!")
    @app_commands.describe(target="The user you want to headpat")
    @app_commands.check(anime_commands_enabled)
    async def headpat(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "headpat", "gives a headpat to", "ADORABLE!!", "has been patted on the head", "has given headpats")

    @bot.tree.command(name="suplex", description="Suplex someone with style!")
    @app_commands.describe(target="The user you want to suplex")
    @app_commands.check(anime_commands_enabled)
    async def suplex(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "suplex", "gives a suplex to", "WHAT A MOVE!", "has been suplexed", "has suplexed others")

    @bot.tree.command(name="yeet", description="Yeet someone away!")
    @app_commands.describe(target="The user you want to yeet")
    @app_commands.check(anime_commands_enabled)
    async def yeet(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "yeet", "just yeeted", "FLYING HIGH!", "has been yeeted", "has yeeted others")

    @bot.tree.command(name="bite", description="Bite someone playfully!")
    @app_commands.describe(target="The user you want to bite")
    @app_commands.check(anime_commands_enabled)
    async def bite(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "bite", "is biting", "NOM NOM!", "has been bitten", "has bitten others")

    @bot.tree.command(name="poke", description="Poke someone gently!")
    @app_commands.describe(target="The user you want to poke")
    @app_commands.check(anime_commands_enabled)
    async def poke(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "poke", "pokes", "", "has been poked", "has poked others")

    @bot.tree.command(name="boop", description="Boop someone’s nose!")
    @app_commands.describe(target="The user you want to boop")
    @app_commands.check(anime_commands_enabled)
    async def boop(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "boop", "boops", "BOOP!", "has been booped", "has booped others")

    @bot.tree.command(name="cuddle", description="Give someone a warm cuddle!")
    @app_commands.describe(target="The user you want to cuddle")
    @app_commands.check(anime_commands_enabled)
    async def cuddle(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "cuddle", "is cuddling with", "SO COZY!", "has been cuddled with", "has cuddled with others")

    @bot.tree.command(name="glomp", description="Glomp someone affectionately!")
    @app_commands.describe(target="The user you want to glomp")
    @app_commands.check(anime_commands_enabled)
    async def glomp(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "glomp", "is running and jumping around hugging", "", "has been glomped", "has glomped others")

    @bot.tree.command(name="flyingkiss", description="Send someone a flying kiss!")
    @app_commands.describe(target="The user you want to send a flying kiss")
    @app_commands.check(anime_commands_enabled)
    async def flyingkiss(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "flyingkiss", "blows a flying kiss to", "SO SWEET!", "has received a flying kiss", "has given flying kisses")

    @bot.tree.command(name="foreheadkiss", description="Give someone a gentle forehead kiss!")
    @app_commands.describe(target="The user you want to give a forehead kiss")
    @app_commands.check(anime_commands_enabled)
    async def foreheadkiss(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "foreheadkiss", "kisses", "on the forehead", "has received a forehead kiss", "has given forehead kisses")

    @bot.tree.command(name="pullcheek", description="Pull someone's cheek playfully!")
    @app_commands.describe(target="The user you want to pull cheek")
    @app_commands.check(anime_commands_enabled)
    async def pullcheek(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "pullcheek", "pulls the cheek of", "SO SQUISHY!", "has had their cheek pulled", "has pulled others' cheeks")

    @bot.tree.command(name="shoot", description="Shoot someone with a gun, playfully hehe!")
    @app_commands.describe(target="The user you want to shoot")
    @app_commands.check(anime_commands_enabled)
    async def pullcheek(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "shoot", "shot", "GAME OVER!!", "has got shot", "has shot others")

    @bot.tree.command(name="cheer", description="Cheer for someone!")
    @app_commands.describe(target="The user you want to cheer for")
    @app_commands.check(anime_commands_enabled)
    async def pullcheek(interaction: discord.Interaction, target: discord.Member):
        await interaction_command(interaction, target, "cheer", "is cheering for", "", "has got cheered for", "has cheered for others")