import sqlite3, time, random
from badges import BADGES

# --- Database Initialization ---
DB_NAME = 'interaction_counts.db'
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# --- Table Creation ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS interactions (
    user_id INTEGER,
    type TEXT,
    count INTEGER,
    PRIMARY KEY (user_id, type)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bar_fight_stats (
    user_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    max_streak INTEGER DEFAULT 0
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS tic_tac_toe_stats (
    user_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0
)
""")

# --- Modify Table for Tracking Fastest Answer and Total Questions ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS trivia_stats (
    user_id INTEGER PRIMARY KEY,
    correct_count INTEGER DEFAULT 0,
    fastest_time REAL DEFAULT NULL,
    total_questions INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0
)
""")
conn.commit()

# --- Add RPS Stats Table ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS rps_stats (
    user_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    rock_count INTEGER DEFAULT 0,
    paper_count INTEGER DEFAULT 0,
    scissors_count INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS translator_stats (
    user_id INTEGER PRIMARY KEY,
    count INTEGER DEFAULT 0
)
""")
conn.commit()


# --- General Interaction Functions ---
def update_counter(user_id, action_type):
    """Update the interaction count for a specific action."""
    cursor.execute("SELECT count FROM interactions WHERE user_id = ? AND type = ?", (user_id, action_type))
    result = cursor.fetchone()
    
    count = (result[0] + 1) if result else 1
    if result:
        cursor.execute("UPDATE interactions SET count = ? WHERE user_id = ? AND type = ?", (count, user_id, action_type))
    else:
        cursor.execute("INSERT INTO interactions (user_id, type, count) VALUES (?, ?, ?)", (user_id, action_type, count))
    
    conn.commit()
    return count

# --- Bar Fight Functions ---
async def update_bar_fight_stat(user, result, interaction):
    user_id=user.id
    """Update the wins/losses/streaks for a user in bar fights."""
    cursor.execute("SELECT wins, losses, current_streak, max_streak FROM bar_fight_stats WHERE user_id = ?", (user_id,))
    result_data = cursor.fetchone()

    wins, losses, current_streak, max_streak = (result_data if result_data else (0, 0, 0, 0))

    if result == "win":
        wins += 1
        current_streak += 1
        # Update max streak if the current streak exceeds it
        if current_streak > max_streak:
            max_streak = current_streak
    else:
        losses += 1
        current_streak = 0  # Reset current streak on a loss

    cursor.execute("""
        INSERT INTO bar_fight_stats (user_id, wins, losses, current_streak, max_streak) 
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET wins = ?, losses = ?, current_streak = ?, max_streak = ?
    """, (user_id, wins, losses, current_streak, max_streak, wins, losses, current_streak, max_streak))

    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT wins FROM bar_fight_stats WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    if result == "win":
        if count == 1:
            emoji_id = "🩸"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif count == 20:
            emoji_id = "💥"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif count == 100:
            emoji_id = "<:sf_beer:1341493938267226222>"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")


def get_bar_fight_stats(user_id):
    """Retrieve bar fight stats for a user."""
    cursor.execute("SELECT wins, losses, current_streak, max_streak FROM bar_fight_stats WHERE user_id = ?", (user_id,))
    return cursor.fetchone() or (0, 0, 0, 0)


# --- Tic-Tac-Toe Functions ---
async def update_tic_tac_toe_stat(user_id, result, interaction):
    """Update the wins/losses/ties for a user in Tic-Tac-Toe."""
    cursor.execute("SELECT wins, losses, ties FROM tic_tac_toe_stats WHERE user_id = ?", (user_id,))
    result_data = cursor.fetchone()

    wins, losses, ties = (result_data if result_data else (0, 0, 0))
    if result == "win":
        wins += 1
    elif result == "tie":
        ties += 1
    else:
        losses += 1

    cursor.execute("""
        INSERT INTO tic_tac_toe_stats (user_id, wins, losses, ties) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET wins = ?, losses = ?, ties = ?
    """, (user_id, wins, losses, ties, wins, losses, ties))

    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT wins FROM tic_tac_toe_stats WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    if result=="win" and count == 20:
        emoji_id = "❌"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")


def get_tic_tac_toe_stats(user_id):
    """Retrieve Tic-Tac-Toe stats for a user."""
    cursor.execute("SELECT wins, losses, ties FROM tic_tac_toe_stats WHERE user_id = ?", (user_id,))
    return cursor.fetchone() or (0, 0, 0)

# --- Correct Answers Tracking ---
async def increment_correct_count(interaction):
    user_id = interaction.user.id

    # Ensure the user exists in the trivia_stats table
    cursor.execute("INSERT OR IGNORE INTO trivia_stats (user_id) VALUES (?)", (user_id,))
    cursor.execute("""
        UPDATE trivia_stats
        SET correct_count = correct_count + 1
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT correct_count FROM trivia_stats WHERE user_id = ?", (user_id,))
    correct_count = cursor.fetchone()[0]

    if correct_count == 1:
        emoji_id = "🔰"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 {interaction.user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    elif correct_count == 10:
        emoji_id = "🥉"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 {interaction.user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    elif correct_count == 50:
        emoji_id = "🥈"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 {interaction.user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    elif correct_count == 200:
        emoji_id = "🥇"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 {interaction.user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")



def update_fastest_time(user_id, time):
    # Ensure the user exists in the trivia_stats table
    cursor.execute("INSERT OR IGNORE INTO trivia_stats (user_id) VALUES (?)", (user_id,))
    cursor.execute("""
        SELECT fastest_time FROM trivia_stats WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()

    if result is None or result[0] is None or time < result[0]:
        cursor.execute("""
            UPDATE trivia_stats
            SET fastest_time = ?
            WHERE user_id = ?
        """, (time, user_id))
        conn.commit()

def increment_total_questions(user_id):
    # Ensure the user exists in the trivia_stats table
    cursor.execute("INSERT OR IGNORE INTO trivia_stats (user_id) VALUES (?)", (user_id,))  
    cursor.execute("""
        UPDATE trivia_stats
        SET total_questions = total_questions + 1
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()

def increment_total_sessions(user_id):  
    # Ensure the user exists in the trivia_stats table
    cursor.execute("INSERT OR IGNORE INTO trivia_stats (user_id) VALUES (?)", (user_id,))
    cursor.execute("""
        UPDATE trivia_stats
        SET total_sessions = total_sessions + 1
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()

def get_trivia_stats(user_id):   
    cursor.execute("""
        SELECT correct_count, fastest_time, total_questions, total_sessions 
        FROM trivia_stats WHERE user_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    # Return default values if the user is not found
    return result or (0, None, 0, 0)  # Default values as per table schema

async def update_rps_stats(user_id, result, choice, interaction):
    """Update the wins, losses, and selection counts for a user in RPS."""
    
    # Get the user's current stats
    cursor.execute("SELECT wins, losses, ties, rock_count, paper_count, scissors_count FROM rps_stats WHERE user_id = ?", (user_id,))
    result_data = cursor.fetchone()

    if result_data:
        wins, losses, ties, rock_count, paper_count, scissors_count = result_data
    else:
        # Initialize stats if the user does not exist in the database
        wins, losses, ties, rock_count, paper_count, scissors_count = (0, 0, 0, 0, 0, 0)

    # Update the result (win/loss)
    if result == "You win!":
        wins += 1
    elif result == "You lose!":
        losses += 1
    elif result == "It's a tie!":
        ties+=1

    # Update the count for the chosen option
    if choice == "rock":
        rock_count += 1
    elif choice == "paper":
        paper_count += 1
    elif choice == "scissors":
        scissors_count += 1

    # Insert or update the user's stats in the database
    cursor.execute("""
        INSERT INTO rps_stats (user_id, wins, losses, ties, rock_count, paper_count, scissors_count) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET wins = ?, losses = ?, ties=?, rock_count = ?, paper_count = ?, scissors_count = ?
    """, (user_id, wins, losses, ties, rock_count, paper_count, scissors_count, wins, losses, ties, rock_count, paper_count, scissors_count))

    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT wins FROM rps_stats WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    if result=="You win!" and count == 100:
        emoji_id = "✂️"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

def get_rps_stats(user_id):
    """Retrieve the RPS stats for a user."""
    cursor.execute("SELECT wins, losses, ties, rock_count, paper_count, scissors_count FROM rps_stats WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    # Return default values if the user does not have any stats
    return result or (0, 0, 0, 0, 0, 0)  # Default values: 0 wins, 0 losses, 0 selections for each choice


async def increment_translator_stats(user_id, interaction):  
    # Ensure the user exists in the trivia_stats table
    cursor.execute("INSERT OR IGNORE INTO translator_stats (user_id) VALUES (?)", (user_id,))
    cursor.execute("""
        UPDATE translator_stats
        SET count = count + 1
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT correct_count FROM trivia_stats WHERE user_id = ?", (user_id,))
    correct_count = cursor.fetchone()[0]

    if correct_count == 100:
        emoji_id = "🤓"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 {interaction.user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

#cowboy thing

# --- Create Tables ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_coins (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 1000
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_inventory (
    user_id INTEGER,
    item_type TEXT,
    item_name TEXT,
    PRIMARY KEY (user_id, item_type, item_name)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS equipped_items (
    user_id INTEGER PRIMARY KEY,
    gun TEXT DEFAULT 'Rust Fang',
    boots TEXT DEFAULT 'Dusty-Trail Boots',
    holster TEXT DEFAULT 'Worn Leather Holster',
    hat TEXT DEFAULT NULL,
    jacket TEXT DEFAULT NULL
)
''')

cursor.execute("""
CREATE TABLE IF NOT EXISTS shootout_stats (
    user_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0
)
""")


# --- Add Tables for Train Heist ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS cooldowns (
    user_id INTEGER PRIMARY KEY,
    last_join_time REAL
)
''')

# --- Add Jail Timestamp to Table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS jailed_users (
    user_id INTEGER PRIMARY KEY,
    jailed_time REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS jail_stats (
    user_id INTEGER PRIMARY KEY,
    times_jailed INTEGER DEFAULT 0,
    times_escaped INTEGER DEFAULT 0
)
''')

# Add Train Heist Stats Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS train_heist_stats (
    user_id INTEGER PRIMARY KEY,
    successful_heists INTEGER DEFAULT 0,
    guards_killed INTEGER DEFAULT 0,
    safes_cracked INTEGER DEFAULT 0,
    total_loot_collected INTEGER DEFAULT 0
)
''')

# Add Bottle Shooting Stats Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bottle_shooting_stats (
    user_id INTEGER PRIMARY KEY,
    bottles_shot INTEGER DEFAULT 0,
    contests_won INTEGER DEFAULT 0
)
''')
conn.commit()


# --- Ensure Default Items Exist ---
def ensure_default_items(user_id):
    default_items = {"gun": "Rust Fang", "holster": "Worn Leather Holster", "boots": "Dusty-Trail Boots"}
    
    for item_type, item_name in default_items.items():
        # Check if the user already owns this item
        cursor.execute("SELECT * FROM user_inventory WHERE user_id = ? AND item_name = ?", (user_id, item_name))
        result = cursor.fetchone()

        if not result:
            cursor.execute("INSERT INTO user_inventory (user_id, item_type, item_name) VALUES (?, ?, ?)", 
                           (user_id, item_type, item_name))
    conn.commit()



# --- Functions ---
def get_user_coins(user_id):
    cursor.execute("SELECT coins FROM user_coins WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0  # Default to 0 if user not found

def update_user_coins(user_id, amount):
    # Ensure the user exists
    cursor.execute("INSERT OR IGNORE INTO user_coins (user_id, coins) VALUES (?, ?)", (user_id, 0))

    # Update coins (ensure coins don't go negative)
    cursor.execute("UPDATE user_coins SET coins = MAX(0, coins + ?) WHERE user_id = ?", (amount, user_id))

    conn.commit()

def add_item_to_inventory(user_id, item_type, item_name):
    """Adds an item to the user's inventory if they don't already own it."""
    cursor.execute("SELECT 1 FROM user_inventory WHERE user_id = ? AND item_name = ?", (user_id, item_name))
    if cursor.fetchone() is None:  # If item isn't owned, add it
        cursor.execute("INSERT INTO user_inventory (user_id, item_type, item_name) VALUES (?, ?, ?)", (user_id, item_type, item_name))
    
    conn.commit()

def equip_item(user_id, item_type, item_name):
    """Equips an item of the given type."""
    cursor.execute("INSERT OR IGNORE INTO equipped_items (user_id) VALUES (?)", (user_id,))
    cursor.execute(f"UPDATE equipped_items SET {item_type} = ? WHERE user_id = ?", (item_name, user_id))
    conn.commit()

def get_equipped_items(user_id):
    """Returns a dictionary of the user's equipped items."""

    # Ensure the user exists in the table with default items
    cursor.execute("""
        INSERT OR IGNORE INTO equipped_items (user_id, gun, boots, holster, hat, jacket)
        VALUES (?, 'Rust Fang', 'Dusty-Trail Boots', 'Worn Leather Holster', NULL, NULL)
    """, (user_id,))
    conn.commit()  # Commit the insertion if it happens

    # Now fetch the user's equipped items
    cursor.execute("SELECT gun, boots, holster, hat, jacket FROM equipped_items WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    return {"gun": row[0], "boots": row[1], "holster": row[2], "hat": row[3], "jacket": row[4]}


def get_user_inventory(user_id):
    # Ensure default items exist for the user
    ensure_default_items(user_id)
    
    # Retrieve the user's inventory
    cursor.execute("SELECT item_type, item_name FROM user_inventory WHERE user_id = ?", (user_id,))
    items = cursor.fetchall()
    
    # Organize items by type
    inventory = []
    for item_type, item_name in items:
        inventory.append(item_name)
    
    return inventory

async def update_shootout_stats(user, result, interaction):
    """Update the wins/losses/ties for a user in Tic-Tac-Toe."""
    user_id=user.id
    cursor.execute("SELECT wins, losses, ties FROM shootout_stats WHERE user_id = ?", (user_id,))
    result_data = cursor.fetchone()

    wins, losses, ties = (result_data if result_data else (0, 0, 0))
    if result == "win":
        wins += 1
    elif result == "tie":
        ties += 1
    else:
        losses += 1

    cursor.execute("""
        INSERT INTO shootout_stats (user_id, wins, losses, ties) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET wins = ?, losses = ?, ties = ?
    """, (user_id, wins, losses, ties, wins, losses, ties))

    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT wins FROM shootout_stats WHERE user_id = ?", (user_id,))
    correct_count = cursor.fetchone()[0]
    if result == "win":
        if correct_count == 1:
            emoji_id = "<:blobCowboy:1341492890274369678>"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif correct_count == 10:
            emoji_id = "<:cat_cowboy:1341495301839519806>"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif correct_count == 25:
            emoji_id = "⏳"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif correct_count == 50:
            emoji_id = "🌵"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif correct_count == 100:
            emoji_id = "🏜️"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

def get_shootout_stats(user_id):
    """Retrieve Tic-Tac-Toe stats for a user."""
    cursor.execute("SELECT wins, losses, ties FROM shootout_stats WHERE user_id = ?", (user_id,))
    return cursor.fetchone() or (0, 0, 0)


def get_cooldown(user_id):
    """Get the last join time for a user."""
    cursor.execute("SELECT last_join_time FROM cooldowns WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def update_cooldown(user_id, cooldown_time=None):
    """Update the last join time for a user."""
    
    if cooldown_time is not None:
        # If cooldown_time is provided, set last_join_time to 5 hours before the current time
        last_join_time = time.time() - (5 * 60 * 60)  # 5 hours in seconds
    else:
        # If cooldown_time is None, set last_join_time to NULL
        last_join_time = time.time()

    cursor.execute("""
        INSERT INTO cooldowns (user_id, last_join_time) 
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET last_join_time = ?
    """, (user_id, last_join_time, last_join_time))
    conn.commit()

async def jail_user(user_id, interaction):
    """Add a user to the jailed_users table with the current timestamp and increment times_jailed."""
    cursor.execute("""
        INSERT INTO jailed_users (user_id, jailed_time) 
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET jailed_time = ?
    """, (user_id, time.time(), time.time()))
    conn.commit()

    # Increment the times_jailed count
    await increment_times_jailed(user_id, interaction)

def is_jailed(user_id):
    """Check if a user is jailed and return the time they were jailed."""
    cursor.execute("SELECT jailed_time FROM jailed_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Return the timestamp when the user was jailed
    return None

async def free_user(user_id, escaped=False, interaction=None):
    """Remove a user from the jailed_users table and optionally increment times_escaped."""
    if escaped:
        await increment_times_escaped(user_id, interaction)  # Increment the times_escaped count
        cursor.execute("DELETE FROM jailed_users WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("DELETE FROM jailed_users WHERE user_id = ?", (user_id,))
    conn.commit()

async def increment_times_jailed(user_id, interaction):
    """Increment the number of times a user has been jailed."""
    cursor.execute("""
        INSERT INTO jail_stats (user_id, times_jailed) 
        VALUES (?, 1)
        ON CONFLICT(user_id) DO UPDATE 
        SET times_jailed = times_jailed + 1
    """, (user_id,))
    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT times_jailed FROM jail_stats WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    if count == 1:
        emoji_id = "👮"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    
    if count == 20:
        emoji_id = "🏴‍☠️"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    

async def increment_times_escaped(user_id, interaction):
    """Increment the number of times a user has escaped from jail."""
    cursor.execute("""
        INSERT INTO jail_stats (user_id, times_escaped) 
        VALUES (?, 1)
        ON CONFLICT(user_id) DO UPDATE 
        SET times_escaped = times_escaped + 1
    """, (user_id,))
    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT times_escaped FROM jail_stats WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    if count == 1:
        emoji_id = "🏃‍♂️"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    
    if count == 15:
        emoji_id = "⛓️"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

    if count == 50:
        emoji_id = "🪂"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

def get_jail_stats(user_id):
    """Retrieve the jail stats for a user."""
    cursor.execute("SELECT times_jailed, times_escaped FROM jail_stats WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result or (0, 0)  # Default to (0, 0) if the user has no stats


def get_cooldowns(user_id):
    """Get the train heist, jail, and daily cooldowns for a user."""
    # Train heist cooldown
    cursor.execute("SELECT last_join_time FROM cooldowns WHERE user_id = ?", (user_id,))
    train_heist_cooldown = cursor.fetchone()

    # Jail cooldown
    cursor.execute("SELECT jailed_time FROM jailed_users WHERE user_id = ?", (user_id,))
    jail_cooldown = cursor.fetchone()

    # Daily cooldown
    cursor.execute("SELECT last_daily_time FROM daily_cooldowns WHERE user_id = ?", (user_id,))
    daily_cooldown = cursor.fetchone()

     # Jail cooldown
    cursor.execute("SELECT last_vote_time FROM user_votes WHERE user_id = ?", (user_id,))
    vote_cooldown = cursor.fetchone()

    return {
        "train_heist": train_heist_cooldown[0] if train_heist_cooldown else None,
        "jail": jail_cooldown[0] if jail_cooldown else None,
        "daily": daily_cooldown[0] if daily_cooldown else None,
        "vote": vote_cooldown[0] if vote_cooldown else None,
    }

#---Train Heist Functions---
async def update_train_heist_stats(user_id, successful_heists=0, guards_killed=0, safes_cracked=0, total_loot_collected=0, interaction=None):
    """Update the train heist stats for a user."""
    cursor.execute("""
        INSERT INTO train_heist_stats (user_id, successful_heists, guards_killed, safes_cracked, total_loot_collected) 
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET successful_heists = successful_heists + ?,
            guards_killed = guards_killed + ?,
            safes_cracked = safes_cracked + ?,
            total_loot_collected = total_loot_collected + ?
    """, (user_id, successful_heists, guards_killed, safes_cracked, total_loot_collected, 
          successful_heists, guards_killed, safes_cracked, total_loot_collected))
    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT successful_heists, guards_killed, safes_cracked, total_loot_collected FROM train_heist_stats WHERE user_id = ?", (user_id,))
    heist,guards,safes,loot = cursor.fetchone()
    if successful_heists!=0:
        if heist == 1:
            emoji_id = "🚆"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif heist == 20:
            emoji_id = "💥"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
        elif heist == 50:
            emoji_id = "🚧"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

    if guards_killed!=0:
        if guards == 500:
            emoji_id = "💀"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 <@{user_id}>, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

    if safes_cracked!=0:
        if safes == 20:
            emoji_id = "🔓"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

    if total_loot_collected!=0 and loot == 5000:
        emoji_id = "💰"
        add_badge(user_id, emoji_id)
        badge_name = BADGES[emoji_id]
        await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")



def get_train_heist_stats(user_id):
    """Retrieve the train heist stats for a user."""
    cursor.execute("SELECT successful_heists, guards_killed, safes_cracked, total_loot_collected FROM train_heist_stats WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result or (0, 0, 0, 0)  # Default to (0, 0, 0, 0) if the user has no stats


async def update_bottle_shooting_stats(user, bottles_shot=0, contests_won=0, interaction=None):
    user_id=user.id
    """Update the bottle shooting stats for a user."""
    cursor.execute("""
        INSERT INTO bottle_shooting_stats (user_id, bottles_shot, contests_won) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET bottles_shot = bottles_shot + ?,
            contests_won = contests_won + ?
    """, (user_id, bottles_shot, contests_won, bottles_shot, contests_won))
    conn.commit()

    # Check if the user has reached a milestone and award a badge
    cursor.execute("SELECT bottles_shot, contests_won FROM bottle_shooting_stats WHERE user_id = ?", (user_id,))
    bottles,contests = cursor.fetchone()

    if bottles_shot!=0:
        if bottles == 100:
            emoji_id = "<:bottle:1341494505752232087>"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")

    if contests_won!=0:
        if contests == 25:
            emoji_id = "🎯"
            add_badge(user_id, emoji_id)
            badge_name = BADGES[emoji_id]
            await interaction.followup.send(f"🎉 {user.mention}, you earned the **{badge_name}** badge! 🎉\n Check your profile to see your badges won!")
    

def get_bottle_shooting_stats(user_id):
    """Retrieve the bottle shooting stats for a user."""
    cursor.execute("SELECT bottles_shot, contests_won FROM bottle_shooting_stats WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result or (0, 0)  # Default to (0, 0) if the user has no stats

#BOUNTY STUFF FROM HERE AND DAILY COOLDOWN

# Create the bounty table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bounty (
    user_id INTEGER PRIMARY KEY,
    bounty INTEGER DEFAULT 1
)
''')

# Add Daily Cooldown Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS daily_cooldowns (
    user_id INTEGER PRIMARY KEY,
    last_daily_time REAL
)
''')
conn.commit()

def update_bounty(user_id: int, action_type: str):
    # Define bounty increases for each action type
    bounty_increases = {
        "bar_fight_win": 100,          # Flat increase for bar fight win
        "jail_escape": 300,             # Flat increase for jail escape
        "cowboy_duel": 0.15,            # 15% of current bounty for cowboy duel
        "train_heist": 1000              # Flat increase for train heist
    }

    # Get the current bounty
    current_bounty = get_bounty(user_id)

    if(current_bounty==500000000000000):
        return
    
    if(current_bounty==1):
        current_bounty=0
    # Calculate the new bounty based on the action type
    if action_type in bounty_increases:
        increase = bounty_increases[action_type]

        if isinstance(increase, float):  # Percentage-based increase (e.g., cowboy duel)
            new_bounty = min((current_bounty if current_bounty != 0 else 100) + int(current_bounty * increase), current_bounty+500)
        else:  # Flat increase (e.g., bar fight win, jail escape, train heist)
            new_bounty = current_bounty + increase
    else:
        raise ValueError(f"Unknown action type: {action_type}")

    # Update the bounty in the database
    cursor.execute('''
    INSERT OR REPLACE INTO bounty (user_id, bounty)
    VALUES (?, ?)
    ''', (user_id, new_bounty))

    conn.commit()


def get_bounty(user_id: int) -> int:
    cursor.execute('''
    SELECT bounty FROM bounty WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    bounty=result[0] if result else 1
    if user_id==822421293286293534:
        bounty=bounty+68 if bounty==1 else bounty+69
    return bounty # Default to 1 if no bounty exists

def get_daily_cooldown(user_id):
    """Get the last time a user claimed their daily coins."""
    cursor.execute("SELECT last_daily_time FROM daily_cooldowns WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def update_daily_cooldown(user_id):
    """Update the last time a user claimed their daily coins."""
    cursor.execute("""
        INSERT INTO daily_cooldowns (user_id, last_daily_time) 
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE 
        SET last_daily_time = ?
    """, (user_id, time.time(), time.time()))
    conn.commit()



#-----BADGES-----
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_badges (
    user_id INTEGER,
    emoji_id TEXT,
    PRIMARY KEY (user_id, emoji_id)
)
""")
conn.commit()

# --- Badge Management Functions ---
def add_badge(user_id, emoji_id):
    """Add a badge to a user."""
    cursor.execute("""
        INSERT INTO user_badges (user_id, emoji_id) 
        VALUES (?, ?)
        ON CONFLICT(user_id, emoji_id) DO NOTHING
    """, (user_id, emoji_id))
    conn.commit()

def remove_badge(user_id, emoji_id):
    """Remove a badge from a user."""
    cursor.execute("""
        DELETE FROM user_badges 
        WHERE user_id = ? AND emoji_id = ?
    """, (user_id, emoji_id))
    conn.commit()

def get_badges(user_id):
    """Retrieve all badges for a given user."""
    cursor.execute("""
        SELECT emoji_id FROM user_badges
        WHERE user_id = ?
    """, (user_id,))
    badges = [row[0] for row in cursor.fetchall()]
    return badges  # Returns an empty list if no badges are found


# --- Levelling System Tables ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_levels (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
)
""")
conn.commit()


def add_xp(user_id: int, xp_gained: int):
    """Add XP to a user and check if they leveled up."""
    cursor.execute("SELECT xp, level FROM user_levels WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        xp, level = result
        xp += xp_gained
        required_xp = 100 * (level ** 2)  # XP required for next level (quadratic scaling)
        if xp >= required_xp:
            level += 1
            xp = 0  # Reset XP after leveling up
        cursor.execute("UPDATE user_levels SET xp = ?, level = ? WHERE user_id = ?", (xp, level, user_id))
    else:
        # Add new user to the database
        cursor.execute("INSERT INTO user_levels (user_id, xp, level) VALUES (?, ?, ?)", (user_id, xp_gained, 1))
    
    conn.commit()

def get_user_level(user_id: int):
    """Retrieve a user's XP and level."""
    cursor.execute("SELECT xp, level FROM user_levels WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result or (0, 1)  # Default to 0 XP and level 1 if user not found


#----VOTING STUFF----

# --- Add Table for Vote Tracking ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_votes (
    user_id INTEGER PRIMARY KEY,
    vote_count INTEGER DEFAULT 0,
    last_vote_time REAL
)
''')
conn.commit()



#----Config Stuff----

# Add Config Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS server_config (
    server_id INTEGER PRIMARY KEY,
    anime_enabled INTEGER DEFAULT 1,  -- 1 for enabled, 0 for disabled
    restricted_channel_id INTEGER DEFAULT NULL  -- Channel ID for restricted commands
)
""")
conn.commit()

def get_server_config(server_id):
    """Retrieve the server's configuration."""
    cursor.execute("SELECT anime_enabled, restricted_channel_id FROM server_config WHERE server_id = ?", (server_id,))
    result = cursor.fetchone()
    if result:
        return {"anime_enabled": bool(result[0]), "restricted_channel_id": result[1]}
    return {"anime_enabled": True, "restricted_channel_id": None}  # Default values

def update_server_config(server_id, anime_enabled=None, restricted_channel_id=None):
    """Update the server's configuration."""
    cursor.execute("""
        INSERT INTO server_config (server_id, anime_enabled, restricted_channel_id)
        VALUES (?, ?, ?)
        ON CONFLICT(server_id) DO UPDATE SET
        anime_enabled = COALESCE(?, anime_enabled),
        restricted_channel_id = COALESCE(?, restricted_channel_id)
    """, (server_id, anime_enabled, restricted_channel_id, anime_enabled, restricted_channel_id))
    conn.commit()



#-----LEADERBOARD-----
def get_top_bounty_users():
    """Retrieve the top 10 users with the highest bounty."""
    cursor.execute("SELECT user_id, bounty FROM bounty ORDER BY bounty DESC LIMIT 10")
    return cursor.fetchall()

def get_top_xp_users():
    """Retrieve the top 10 users with the highest XP."""
    cursor.execute("SELECT user_id, xp FROM user_levels ORDER BY xp DESC LIMIT 10")
    return cursor.fetchall()