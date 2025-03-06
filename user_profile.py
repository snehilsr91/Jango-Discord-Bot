import discord
from discord import app_commands
from discord.ui import View, Select
from database import get_bar_fight_stats, get_tic_tac_toe_stats, get_trivia_stats, get_rps_stats, get_bounty, get_equipped_items, get_user_coins
from database import get_jail_stats, get_user_level, get_shootout_stats, get_badges, get_train_heist_stats, get_bottle_shooting_stats
from items import emojis
from badges import BADGES

class ProfileView(View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=120)
        self.member = member
        
        self.add_item(ProfileSelect(member))

async def generate_main_profile_embed(member: discord.Member):
    """Generate the main profile embed for the user."""
    embed = discord.Embed(title=f"{member.display_name}'s Profile", color=0xD30000)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    # Add user info
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=True)
    
    # Add level and XP
    xp, level = get_user_level(member.id)
    required_xp = 100 * (level ** 2)  # XP required for next level
    xp_bar_length = 20
    filled = int((xp / required_xp) * xp_bar_length)
    
    # Use Unicode characters for the XP bar
    red_block = "🟥"  # Red block
    blue_block = "⬜"  # Blue block
    
    # Create the XP bar
    bar = red_block * filled + blue_block * (xp_bar_length - filled)

    # Get the badges
    badge_list=get_badges(user_id=member.id)
    if not badge_list:
        badges="No badges yet."
    else:
        badges=" ".join(badge_list)
    
    embed.add_field(name="Reputation", value=f"`Level:` {level}\n`XP:` {xp}/{required_xp}", inline=True)
    embed.add_field(name="Progress", value=bar, inline=True)
    embed.add_field(name="Badges", value=f"{badges}", inline=False)
    
    return embed

async def generate_trivia_embed(member: discord.Member):
    """Generate an embed for Trivia stats."""
    correct_count, fastest_time, total_questions, total_sessions = get_trivia_stats(member.id)
    accuracy=(correct_count/total_questions)*100 if total_questions!=0 else 0
    embed = discord.Embed(title=f"{member.display_name}'s Trivia Stats", color=0xD30000)
    embed.add_field(name="Total Questions Answered", value=total_questions, inline=True)
    embed.add_field(name="Correct Answers", value=correct_count, inline=True)
    embed.add_field(name="Accuracy", value=f"{accuracy:.2f}%", inline=True)
    embed.add_field(name="Fastest Time", value=f"{fastest_time:.2f} seconds" if fastest_time != None else "None", inline=True)
    embed.add_field(name="Sessions Participated In", value=total_sessions, inline=True)
    return embed

async def generate_badge_embed(member: discord.Member):
    """Generate an embed for Trivia stats."""
    # Get the badges
    badge_list=get_badges(user_id=member.id)
    if not badge_list:
        badges="No badges yet."
    else:
        badges=""
        for badge in badge_list:
            badges+=badge+" : "+BADGES[badge]+"\n"
    embed = discord.Embed(title=f"{member.display_name}'s Badges", color=0xD30000, description=badges)
    embed.set_footer(text="Tip: Use /badges to check how to obtain every badge.")
    return embed

async def generate_minigame_embed(member: discord.Member):
    """Generate an embed for rps stats."""
    twins, tlosses, tties = get_tic_tac_toe_stats(member.id)
    total=twins+tlosses+tties
    win_rate=0 if total==0 else twins/total

    wins, losses, ties, rock_count, paper_count, scissors_count = get_rps_stats(member.id)
    favourite_selection= "Rock"
    fav_count=rock_count
    if paper_count>rock_count:
        favourite_selection= "Paper"
        fav_count=paper_count
    elif paper_count==rock_count:
        favourite_selection= "Rock & Paper"
    if scissors_count>fav_count:
        favourite_selection= "Scissors"
    elif scissors_count==rock_count==paper_count:
        favourite_selection= "All 3 equally"
    elif scissors_count==fav_count:
        favourite_selection=f"{favourite_selection} & Scissors"

    rps_str=f"`Wins:` {wins}\n`Losses:` {losses}\n`Ties:` {ties}\n`Favourite Selection:` {favourite_selection}"
    ttt_str=f"`Wins:` {twins}\n`Losses:` {tlosses}\n`Ties:` {tties}\n`Win Rate:` {win_rate:.2f}%"
    embed = discord.Embed(title=f"{member.display_name}'s Game Stats", color=0xD30000)
    embed.add_field(name="Rock Paper Scissors", value=rps_str, inline=True)
    embed.add_field(name="Tic-Tac-Toe", value=ttt_str, inline=True)
    return embed

async def generate_cowboy_embed(member: discord.Member):
    """Generate an embed for cowboy profile."""
    items=get_equipped_items(member.id)
    gun_emoji=emojis[items["gun"]]
    holster_emoji=emojis[items["holster"]]
    boots_emoji=emojis[items["boots"]]
    hat_emoji=None
    if items["hat"] is not None:
        hat_emoji=emojis[items["hat"]]
    jacket_emoji=None
    if items["jacket"] is not None:
        hat_emoji=emojis[items["jacket"]]
    bounty=get_bounty(member.id)
    item_emojis=gun_emoji+" "+holster_emoji+" "+boots_emoji
    if hat_emoji is not None:
        item_emojis+" "+hat_emoji
    if jacket_emoji is not None:
        item_emojis+" "+jacket_emoji

    jail_stats=get_jail_stats(member.id)
    coins=get_user_coins(member.id)
    wins,losses,ties=get_shootout_stats(member.id)
    embed = discord.Embed(title=f"{member.display_name}'s Cowboy Records", color=0xD30000)
    embed.add_field(name="Wealth & Infamy", value=f"`Coins:` {coins}🪙\n`Bounty:` {bounty}")
    embed.add_field(name="Cowboy Duel Stats", value=f"`Wins:` {wins}\n`Losses:` {losses}\n`Ties:` {ties}", inline=True)
    embed.add_field(name="Rap Sheet", value=f"`Times Jailed:` {jail_stats[0]}\n`Times Escaped:` {jail_stats[1]}")
    wins, losses, curstreak, maxstreak = get_bar_fight_stats(member.id)
    heists,guards,safes,loot=get_train_heist_stats(member.id)
    bottles,contests=get_bottle_shooting_stats(member.id)
    embed.add_field(name="Bar Fights", value=f"`Wins:` {wins}\n`Losses:` {losses}\n`Current Streak:` {curstreak}\n`Max Streak:` {maxstreak}", inline=True)
    embed.add_field(name="Bottle Shooting Stats", value=f"`Bottles Shot:` {bottles}\n`Contests won:` {contests}", inline=True)
    embed.add_field(name="Train Heist Stats", value=f"`Successful Heists:` {heists}\n`Guards Killed:` {guards}\n`Safes Cracked:` {safes}\n`Total Loot:` {loot}", inline=True)
    embed.add_field(name="Equipped Items", value=item_emojis, inline=False)
    return embed

class ProfileSelect(Select):
    def __init__(self, member: discord.Member):
        options = [
            discord.SelectOption(label="Cowboy Records", description="View your Cowboy Profile/Stats", value="cowboy"),
            discord.SelectOption(label="Main Profile", description="View your Main Profile", value="main_profile"),
            discord.SelectOption(label="Mini Game Stats", description="View your Mini Game stats", value="game"),
            discord.SelectOption(label="Trivia Stats", description="View your Trivia stats", value="trivia"),
            discord.SelectOption(label="Your Badges", description="View the badges you have won", value="badge"),
        ]
        super().__init__(placeholder="Select a category", options=options)
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "main_profile":
            embed = await generate_main_profile_embed(self.member)
        elif self.values[0] == "game":
            embed = await generate_minigame_embed(self.member)
        elif self.values[0] == "trivia":
            embed = await generate_trivia_embed(self.member)
        elif self.values[0] == "cowboy":
            embed = await generate_cowboy_embed(self.member)
        elif self.values[0] == "badge":
            embed = await generate_badge_embed(self.member)     
        else:
            embed = discord.Embed(title="Error", description="Invalid selection", color=0xD30000)
        
        await interaction.response.edit_message(embed=embed, view=self.view)

def setup(bot):
    @bot.tree.command(name="profile", description="Check your profile stats")
    @app_commands.describe(member="The user whose profile you want to check (leave blank for yourself)")
    async def profile(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user  # Default to the command sender if no user is mentioned
        embed = await generate_main_profile_embed(member)
        view = ProfileView(member)
        await interaction.response.send_message(embed=embed, view=view)
