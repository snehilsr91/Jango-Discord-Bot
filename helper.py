import discord
from discord import app_commands
from discord.ui import View, Select, Button

description="**Jango** is the ultimate Discord bot packed with fun mini-games, interactive commands, and customization options.\nChallenge friends to cowboy duels 🤠🔫, hustle up in a bar fight 👊🍻, team up for train heists 🚂💰, or test your reflexes in a bottle shooting contest 🎯 while earning coins 💰 to upgrade your cowboy gear in the shop..\nPlay classic games like Rock-Paper-Scissors, Tic-Tac-Toe, and Trivia.\nExpress yourself with anime GIF reactions 🎭, translate text into pirate speech 🏴‍☠️, morse code 🆘, minionese spech 🍌 and many other translations, and track your stats 📊.\nWith regular updates and easy-to-use commands, Jango is the perfect addition to any server. Invite it now and start the adventure! 🚀🔥"

def setup(bot):
    @bot.tree.command(name="help", description="Get a list of commands or info about a specific command")
    @app_commands.describe(command="The specific command you want info about")
    async def help_command(interaction: discord.Interaction, command: str = None):
        if command:
            cmd = bot.tree.get_command(command)
            if cmd:
                await interaction.response.send_message(f"**/{cmd.name}**: {cmd.description}")
            else:
                await interaction.response.send_message("❌ Command not found.")
        else:
            categories = {
                "GIF Commands": ["angry","bite","boop","cheer","cry","cuddle","die","dropkick","feed","flirt","flyingkiss","foreheadkiss",
                                 "glomp","groupdance","grouphug","handshake","happy","happy","headpat","highfive","hmph","hug","laugh","poke",
                                 "pullcheek","punch","sad","salute","shoot","slap","smirk","solodance","stab","suplex","throw","uppercut","wave","yeet"],

                "Cowboy": ["bar_fight", "bottle_shoot", "cooldown", "cowboy_duel", "cowboy_shop", "cowboy_equipped", "cowboy_inventory", "daily",
                            "jailbreak", "train_heist", "wanted_poster"],

                "Utilities": ["about", "badges", "config", "commands", "help", "suggest"],
                "Fun": ["emoji", "minionese", "morse", "pirate", "uwu", "yoda"],
                "Minigames": ["8ball", "coinflip", "rps", "tic_tac_toe"]
            }

            embed = discord.Embed(title="📜 Available Commands", color=0xD30000)
            for category, cmds in categories.items():
                cmd_list = [f"{cmd}" for cmd in cmds]
                embed.add_field(name=f"📂 {category}", value=", ".join(cmd_list), inline=False)

            embed.set_footer(text="Tip: Use /help command:<command_name> to see more about a specific command")
            await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="suggest", description="Send a suggestion to the bot creator")
    async def suggest(interaction: discord.Interaction, suggestion: str):
        # Get the user who sent the suggestion
        user = interaction.user
        user_id = user.id
        username = user.name

        # Send the suggestion to the bot creator's DMs
        creator = await bot.fetch_user(691739332511531088)
        embed_to_creator = discord.Embed(
            title="New Suggestion",
            description=suggestion,
            color=discord.Color.blue()
        )
        embed_to_creator.add_field(name="User", value=f"{username} (ID: {user_id})", inline=False)
        await creator.send(embed=embed_to_creator)

        # Send a confirmation embed to the channel
        embed_to_user = discord.Embed(
            title="Suggestion Received",
            description="Your suggestion has been successfully sent to the bot creator!",
            color=0xD30000
        )
        await interaction.response.send_message(embed=embed_to_user, ephemeral=True)


    @bot.tree.command(name="commands", description="Sends a list of all commands to your DMs.")
    async def commands(interaction: discord.Interaction):
        # Fetch all commands from the bot's command tree
        command_list = bot.tree.get_commands()

        # Create a formatted string for the embed description
        description = ""
        for command in command_list:
            description += f"**/{command.name}** : {command.description or 'No description provided.'}\n"

        # Create an embed for the DM
        embed = discord.Embed(
            title="Command List",
            description=description,
            color=discord.Color.blue()
        )

        # Send the embed to the user's DMs
        try:
            await interaction.user.send(embed=embed)
            # Send a confirmation embed in the channel
            confirmation_embed = discord.Embed(
                description="✅ A list of commands has been sent to your DMs!",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)
        except discord.Forbidden:
            # If the user has DMs disabled, send an error message
            error_embed = discord.Embed(
                description="❌ I couldn't send you a DM. Please check your privacy settings!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)


    @bot.tree.command(name="about", description="Get information about the bot.")
    async def about(interaction: discord.Interaction):
        # Create the embed
        embed = discord.Embed(
            title="About the Bot",
            description="A fun and interactive bot designed to bring joy and entertainment to your server!",
            color=0xD30000
        )
        # Add fields to the embed
        user_id="691739332511531088"
        embed.add_field(name="Version", value="1.0.0", inline=True)
        embed.add_field(name="Creator", value=f"<@{user_id}>", inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Invite", value="[Invite the bot to your server!](https://discord.com/oauth2/authorize?client_id=1122526375157448714)", inline=True)
        embed.add_field(name="Support Server", value="[Join the bot's support server!](https://discord.gg/6apva2wVgs)", inline=True)

        # Set a thumbnail (optional)
        embed.set_thumbnail(url=bot.user.avatar.url)

        # Send the embed
        await interaction.response.send_message(embed=embed)