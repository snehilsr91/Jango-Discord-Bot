import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
from database import get_user_coins, update_user_coins, get_user_inventory, add_item_to_inventory, equip_item, ensure_default_items, get_equipped_items
from items import names, descriptions, lore

# Item data
HOLSTERS = [
    {"name": "Worn Leather Holster", "price": 0, "factor": 0, "url": names["holster1"], "lore":lore["holster1"], "description":descriptions["holster1"]},
    {"name": "Silver Spur Holster", "price": 100, "factor": 1, "url": names["holster2"], "lore":lore["holster2"], "description":descriptions["holster2"]},
    {"name": "Rattlesnake Coil", "price": 250, "factor": 2, "url": names["holster3"], "lore":lore["holster3"], "description":descriptions["holster3"]},
]

BOOTS = [
    {"name": "Dusty-Trail Boots", "price": 0, "factor": 0, "url": names["boot1"], "lore":lore["boot1"], "description":descriptions["boot1"]},
    {"name": "Rosewood Ramblers", "price": 500, "factor": 10, "url": names["boot2"], "lore":lore["boot2"], "description":descriptions["boot2"]},
    {"name": "Sunfire Stompers", "price": 1250, "factor": 30, "url": names["boot3"], "lore":lore["boot3"], "description":descriptions["boot3"]},
]

GUNS = [
    {"name": "Rust Fang", "price": 0, "factor": 0, "url": names["gun1"], "lore":lore["gun1"], "description":descriptions["gun1"]},
    {"name": "Grim Spur", "price": 200, "factor": 5, "url": names["gun2"], "lore":lore["gun2"], "description":descriptions["gun2"]},
    {"name": "Deadshot Relic", "price": 350, "factor": 10, "url": names["gun3"], "lore":lore["gun3"], "description":descriptions["gun3"]},
    {"name": "Crimson Reaper", "price": 500, "factor": 15, "url": names["gun4"], "lore":lore["gun4"], "description":descriptions["gun4"]},
    {"name": "Steel Revenant", "price": 1000, "factor": 25, "url": names["gun5"], "lore":lore["gun5"], "description":descriptions["gun5"]},
]

HATS = [
    {"name": "Wayfarer's Oath", "price": 500, "factor": 5, "url": names["hat1"], "lore":lore["hat1"], "description":descriptions["hat1"]},
    {"name": "Sheriff's Pride", "price": 1000, "factor": 10, "url": names["hat2"], "lore":lore["hat2"], "description":descriptions["hat2"]},
]

JACKETS = [
    {"name": "Dustrunner's Hide", "price": 500, "factor": 1, "url": names["jacket1"], "lore":lore["jacket1"], "description":descriptions["jacket1"]},
    {"name": "Nightstalker's Cloak", "price": 1000, "factor": 2, "url": names["jacket2"], "lore":lore["jacket2"], "description":descriptions["jacket2"]},
]

# Reusable function to fetch item details
def get_item_details(item_name):
    for item_list in [HOLSTERS, BOOTS, GUNS, HATS, JACKETS]:
        for item in item_list:
            if item["name"] == item_name:
                return item
    return None

def get_item_type(item_name):
    gun_names = [gun["name"] for gun in GUNS]
    holster_names = [holster["name"] for holster in HOLSTERS]
    boot_names = [boot["name"] for boot in BOOTS]
    hat_names = [hat["name"] for hat in HATS]
    jacket_names = [jacket["name"] for jacket in JACKETS]
    if item_name in gun_names:
        return "gun"
    elif item_name in holster_names:
        return "holster"
    elif item_name in boot_names:
        return "boots"
    elif item_name in hat_names:
        return "hat"
    elif item_name in jacket_names:
        return "jacket"
    else: 
        return None

class ItemView(View):
    def __init__(self, items, item_type, user_id):
        super().__init__(timeout=None)
        self.items = items
        self.index = 0
        self.item_type = item_type
        self.user_id = user_id  # Store the ID of the command caller

        self.dropdown = Select(
            placeholder="Choose Item Type",
            options=[
                discord.SelectOption(label="Guns", value="guns"),
                discord.SelectOption(label="Holsters", value="holsters"),
                discord.SelectOption(label="Boots", value="boots"),
                discord.SelectOption(label="Hats", value="hats"),
                discord.SelectOption(label="Jackets", value="jackets"),
            ],
        )
        self.dropdown.callback = self.dropdown_callback
        self.add_item(self.dropdown)

        self.buy_button = Button(label="Buy", style=discord.ButtonStyle.success)
        self.buy_button.callback = self.buy_item
        self.add_item(self.buy_button)

    async def dropdown_callback(self, interaction: discord.Interaction):
        self.item_type = self.dropdown.values[0]
        self.items = globals()[self.item_type.upper()]
        self.index = 0
        await self.update_embed(interaction)

    async def buy_item(self, interaction: discord.Interaction):
        #check if user of button is user of command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't use this button. Use /cowboy_shop yourself to make use of this button.", ephemeral=True)
            return
        
        user_id = interaction.user.id
        item = self.items[self.index]
        coins = get_user_coins(user_id)
        inventory = get_user_inventory(user_id)

        if item["name"] in inventory:
            await interaction.response.send_message("You already own this item.", ephemeral=True)
            return

        if coins >= item["price"]:
            update_user_coins(user_id, -item["price"])
            add_item_to_inventory(user_id, self.item_type, item["name"])
            await interaction.response.send_message(f"You bought {item['name']}!", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have enough 🪙.", ephemeral=True)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        self.index = (self.index - 1) % len(self.items)
        await self.update_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.index = (self.index + 1) % len(self.items)
        await self.update_embed(interaction)

    async def update_embed(self, interaction):
        item = self.items[self.index]
        embed = discord.Embed(title=f"{item['name']}", description=f"Price: {item['price']}🪙")
        embed.set_thumbnail(url=item["url"])
        embed.add_field(name="Lore", value=f"*{item['lore']}*", inline=False)
        embed.add_field(name="Description", value=item['description'])
        embed.set_footer(text="Tip: Use the Buy button to purchase this item.")
        await interaction.response.edit_message(embed=embed, view=self)

class InventoryView(View):
    def __init__(self, inventory, user_id):
        super().__init__(timeout=None)
        self.full_inventory = inventory  # Store the full inventory
        self.items = [get_item_details(item) for item in inventory if get_item_details(item)]
        self.index = 0
        self.user_id = user_id

        self.dropdown = Select(
            placeholder="Choose Item Type",
            options=[
                discord.SelectOption(label="All", value="all"),
                discord.SelectOption(label="Guns", value="guns"),
                discord.SelectOption(label="Holsters", value="holsters"),
                discord.SelectOption(label="Boots", value="boots"),
                discord.SelectOption(label="Hats", value="hats"),
                discord.SelectOption(label="Jackets", value="jackets"),
            ],
        )
        self.dropdown.callback = self.dropdown_callback
        self.add_item(self.dropdown)

        self.equip_button = Button(label="Equip", style=discord.ButtonStyle.success)
        self.equip_button.callback = self.equip_item_fn
        self.add_item(self.equip_button)

    async def dropdown_callback(self, interaction: discord.Interaction):
        selected_type = self.dropdown.values[0]

        if selected_type == "all":
            self.items = [get_item_details(item) for item in self.full_inventory if get_item_details(item)]
        else:
            item_list = globals()[selected_type.upper()]
            self.items = [item for item in item_list if item["name"] in self.full_inventory]

        self.index = 0
        if self.items:
            await self.update_embed(interaction)
        else:
            await interaction.response.edit_message(content="No items of this type in your inventory.", embed=None, view=self)

    async def equip_item_fn(self, interaction: discord.Interaction):
        #check if user of button is the user of the command
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You can't use this button. Use /cowboy_inventory yourself to make use of this button.", ephemeral=True)
            return
        
        if not self.items:
            await interaction.response.send_message("No item to equip.", ephemeral=True)
            return

        user_id = interaction.user.id
        item = self.items[self.index]
        item_type = get_item_type(item["name"])
        equip_item(user_id, item_type, item["name"])
        await interaction.response.send_message(f"You equipped {item['name']}!", ephemeral=True)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.items:
            self.index = (self.index - 1) % len(self.items)
            await self.update_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.items:
            self.index = (self.index + 1) % len(self.items)
            await self.update_embed(interaction)

    async def update_embed(self, interaction):
        item = self.items[self.index]
        embed = discord.Embed(title=f"{item['name']}")
        embed.set_thumbnail(url=item["url"])
        embed.add_field(name="Lore", value=f"*{item['lore']}*", inline=False)
        embed.add_field(name="Description", value=item['description'])
        embed.set_footer(text="Tip: Use the Equip button to equip this item.")
        await interaction.response.edit_message(embed=embed, view=self)


def setup(bot):
    @bot.tree.command(name="cowboy_shop", description="View the cowboy shop")
    async def cowboy_shop(interaction: discord.Interaction):
        default_item = GUNS[0]
        view = ItemView(GUNS, "guns", interaction.user.id)

        embed = discord.Embed(
            title=f"{default_item['name']}",
            description=f"`Price:` {default_item['price']}🪙"
        )
        embed.set_thumbnail(url=default_item["url"])
        embed.add_field(name="Lore", value=f"*{default_item['lore']}*", inline=False)
        embed.add_field(name="Description", value=default_item['description'])
        embed.set_footer(text="Tip: Use the Buy button to purchase this item.")

        await interaction.response.send_message(embed=embed, view=view)

    @bot.tree.command(name="cowboy_inventory", description="View your cowboy inventory")
    async def cowboy_inventory(interaction: discord.Interaction):
        user_id = interaction.user.id
        ensure_default_items(user_id)
        inventory = get_user_inventory(user_id)

        if not inventory:
            await interaction.response.send_message("Your inventory is empty.", ephemeral=True)
            return

        view = InventoryView(inventory, user_id)
        first_item = view.items[0]

        embed = discord.Embed(title=f"{first_item['name']}")
        embed.set_thumbnail(url=first_item["url"])
        embed.add_field(name="Lore", value=f"*{first_item['lore']}*", inline=False)
        embed.add_field(name="Description", value=first_item['description'])
        embed.set_footer(text="Tip: Use the Equip button to equip this item.")

        await interaction.response.send_message(embed=embed, view=view)


    @bot.tree.command(name="cowboy_equipped", description="View your currently equipped cowboy items")
    async def cowboy_equipped(interaction: discord.Interaction):
        user_id = interaction.user.id
        equipped_items = get_equipped_items(user_id)  # Assuming this fetches equipped items

        if not equipped_items:
            await interaction.response.send_message("You have no items equipped.", ephemeral=True)
            return

        embed = discord.Embed(title=f"{interaction.user.display_name}'s Equipped Items", color=0xD30000)
        embed.add_field(name="GUN", value=equipped_items["gun"])
        embed.add_field(name="BOOTS", value=equipped_items["boots"])
        embed.add_field(name="HOLSTER", value=equipped_items["holster"])
        embed.add_field(name="HAT", value=equipped_items["hat"])
        embed.add_field(name="JACKET", value=equipped_items["jacket"])
        embed.set_footer(text="Tip: Equip items from /cowboy_inventory.")

        await interaction.response.send_message(embed=embed)

