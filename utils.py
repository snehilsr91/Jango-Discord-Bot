import random
import discord
from gifs import GIFS  # Ensure gifs.py exists
from database import update_counter  # Ensure database.py exists

async def interaction_command(interaction, target, action_name, header1, header2, footer1, footer2):
    if not target or target == interaction.user:
        await interaction.response.send_message("You can't perform this action on yourself!", ephemeral=True)
        return

    gif_url = random.choice(GIFS[action_name])

    # Update counters
    giver_count = update_counter(interaction.user.id, f"{action_name}_given")
    receiver_count = update_counter(target.id, f"{action_name}_received")
    giver_time="time" if giver_count==1 else "times"
    receiver_time="time" if receiver_count==1 else "times"
    embed = discord.Embed(title=f"{interaction.user.display_name} {header1} {target.display_name} {header2}!", color=0xD30000)
    embed.set_image(url=gif_url)
    embed.set_footer(text=f"{target.display_name} {footer1} {receiver_count} {giver_time}.\n"
                          f"{interaction.user.display_name} {footer2} {giver_count} {receiver_time}.")
    await interaction.response.send_message(embed=embed)

async def execute_solo_command(interaction, action, header, footer):
    """Handles solo GIF commands."""
    gif_url = random.choice(GIFS[action])
    count = update_counter(interaction.user.id, f"{action}_used")
    time="time" if count==1 else "times"
    embed = discord.Embed(title=f"{interaction.user.display_name} {header}", color=0xD30000)
    embed.set_image(url=gif_url)
    embed.set_footer(text=f"{interaction.user.display_name} {footer} {count} {time}!")
    
    await interaction.response.send_message(embed=embed)

async def execute_group_command(interaction, users, action, header, footer):
    """Handles group GIF commands."""
    if not users:  # Extra safety check
        await interaction.response.send_message("You need to mention at least one user!", ephemeral=True)
        return
    
    if action=="hug":
        group_action="grouphug"
    else:
        group_action=action
    gif_url = random.choice(GIFS[group_action])
    if action=="groupdance":
        action="solodance"
    sender_count = update_counter(interaction.user.id, f"{action}_used")

    # Update and collect receive counts for each mentioned user
    if action=="groupdance":
        receive_counts = {user: update_counter(user.id, f"{action}_used") for user in users}
    else:    
        receive_counts = {user: update_counter(user.id, f"{action}_received") for user in users}
    time="time" if sender_count==1 else "times"
    target_mentions = ", ".join(user.display_name for user in users)
    embed_title = f"{interaction.user.display_name} {header} {target_mentions}!"

    embed = discord.Embed(title=embed_title, color=0xD30000)
    embed.set_image(url=gif_url)

    # Format footer text with sender count and each receiver's count
    footer_text = f"{interaction.user.display_name} {footer} {sender_count} {time}!"

    embed.set_footer(text=footer_text)

    await interaction.response.send_message(embed=embed)