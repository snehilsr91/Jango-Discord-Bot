import os
import discord
from discord import app_commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
from database import is_jailed, get_bounty

async def wanted(interaction: discord.Interaction, user: discord.User = None):
    await interaction.response.defer()

    user = user or interaction.user

    # Determine the bounty based on the user type
    if user.bot:
        if user.id == interaction.client.user.id:  # Check if the user is this bot
            bounty = 10**15
        else:
            bounty = 0  # Bounty for other bots
    else:
        bounty = get_bounty(user.id)  # Fetch bounty from the database for non-bot users

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).convert("RGBA")

    # Load the old paper background template
    poster = Image.open("old_paper.png").convert("RGBA")
    poster = poster.resize((700, 1000))

    # Load overlay image
    overlay_image = Image.open("wanted.png").convert("RGBA")
    overlay_image = overlay_image.resize((700, 1000))

    # Paste overlay on top of the poster
    poster.paste(overlay_image, (0, 0), overlay_image)

    # Prepare avatar
    avatar = avatar.resize((600, 600)).convert("RGBA")
    if user.id == interaction.client.user.id:
        avatar = avatar.crop((0, 100, 600, 450))
    else:
        avatar = avatar.crop((0, 25, 600, 375))

    # Apply sepia effect
    sepia = Image.new("RGBA", avatar.size, (112, 66, 20, 80))
    avatar = Image.blend(avatar, sepia, 0.4)

    # Add black border
    border_thickness = 3
    bordered_avatar = Image.new("RGBA", (avatar.width + 2 * border_thickness, avatar.height + 2 * border_thickness), "black")
    bordered_avatar.paste(avatar, (border_thickness, border_thickness))

    # Paste avatar onto the poster
    poster.paste(bordered_avatar, (50, 450), bordered_avatar)

    # Add text
    draw = ImageDraw.Draw(poster)

    # Font paths
    font_path = "shadser.TTF"
    bounty_font_path = "Magnificent West.ttf"
    footer_font_path = "CLRNDNC.TTF"

    # Extract user's display name
    display_name = user.display_name.upper()

    # Adjust font size dynamically for the name
    max_width = poster.width - 100
    font_size = 60

    while font_size > 20:
        try:
            font_name = ImageFont.truetype(font_path, font_size)
        except OSError:
            font_name = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), display_name, font=font_name)
        text_width = text_bbox[2] - text_bbox[0]

        if text_width <= max_width:
            break
        font_size -= 2

    # Position username
    text_x = (poster.width - text_width) // 2
    text_y = 385
    draw.text((text_x, text_y), display_name, font=font_name, fill=(40, 40, 40))

    # Format bounty
    bounty_text = f"${bounty:,}"

    # **Increased the max width for bounty**
    bounty_max_width = poster.width - 150  # More width to fit better
    bounty_font_size = 140  # Start with a bigger font

    # Adjust font size dynamically for bounty
    while bounty_font_size > 90:
        try:
            bounty_font_name = ImageFont.truetype(bounty_font_path, bounty_font_size)
        except OSError:
            bounty_font_name = ImageFont.load_default()

        bounty_text_bbox = draw.textbbox((0, 0), bounty_text, font=bounty_font_name)
        bounty_text_width = bounty_text_bbox[2] - bounty_text_bbox[0]

        if bounty_text_width <= bounty_max_width:
            break
        bounty_font_size -= 2  # Decrease if too wide

    # **Center and widen bounty text**
    bounty_x = (poster.width - bounty_text_width) // 2
    bounty_y = 805
    draw.text((bounty_x, bounty_y), bounty_text, font=bounty_font_name, fill=(202, 33, 40))

    footer_text="INFORM YOUR NEAREST SHERIFF IMMEDIATELY!!"
    
    try:
        footer_font_name = ImageFont.truetype(footer_font_path, 30)
    except OSError:
        footer_font_name = ImageFont.load_default()
    footer_text_bbox = draw.textbbox((0, 0), footer_text, font=footer_font_name)
    footer_text_width = footer_text_bbox[2] - footer_text_bbox[0]
    footer_x = (poster.width - footer_text_width) // 2
    draw.text((footer_x, 940), footer_text, font=footer_font_name, fill=(40, 40, 40))

    
    if is_jailed(user.id):
        # Load overlay image
        arrested_image = Image.open("arrested.png").convert("RGBA")
        arrested_image = arrested_image.resize((700, 700))

        # Paste overlay on top of the poster
        poster.paste(arrested_image, (0, 280), arrested_image)

    # Save final image
    buffer = BytesIO()
    poster.save(buffer, format="PNG")
    buffer.seek(0)

    await interaction.followup.send(file=discord.File(fp=buffer, filename="wanted_poster.png"))

# ✅ Setup function
def setup(bot):
    bot.tree.add_command(app_commands.Command(
        name="wanted_poster",
        description="Create a WANTED poster with a classic style.",
        callback=wanted
    ))