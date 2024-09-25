import sqlite3

# Function to create the character and NPC table
def create_character_npc_table():
    """Create a table for characters and NPCs with additional fields for D&D style game, including hit dice and saving throws."""
    conn = sqlite3.connect('characters_npcs.db')  # Separate database
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('character', 'npc')),
        race TEXT NOT NULL,
        class TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        health INTEGER NOT NULL,
        strength INTEGER NOT NULL,
        intelligence INTEGER NOT NULL,
        armor_class INTEGER NOT NULL,
        hit_dice TEXT NOT NULL,
        fortitude INTEGER NOT NULL,
        reflex INTEGER NOT NULL,
        will INTEGER NOT NULL,
        abilities TEXT,
        non_consumable_inventory TEXT,
        consumable_inventory TEXT,
        spells_known TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Character/NPC table with Hit Dice and Saving Throws created in 'characters_npcs.db'.")

# Function to retrieve column names from the characters table
def get_table_columns():
    """Retrieve the list of columns from the characters table dynamically."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall()]

    conn.close()
    return columns

# Function to add a new character or NPC dynamically based on database fields
def add_character_npc():
    """Add a new character or NPC to the system, dynamically retrieving fields from the database."""
    conn = sqlite3.connect('characters_npcs.db')  # Separate database
    c = conn.cursor()

    # Get the column names dynamically from the characters table, excluding 'id'
    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall() if col[1] != 'id']
    
    values = []  # To store the values entered by the user
    for field in columns:
        if field in ["level", "health", "strength", "intelligence", "armor_class", "fortitude", "reflex", "will"]:
            # Numerical fields require integer input
            value = int(input(f"Enter {field.replace('_', ' ').capitalize()}: "))
        else:
            value = input(f"Enter {field.replace('_', ' ').capitalize()}: ")
        values.append(value)
    
    # Construct the SQL query dynamically
    columns_string = ', '.join(columns)
    placeholders = ', '.join('?' * len(columns))
    
    query = f"INSERT INTO characters ({columns_string}) VALUES ({placeholders})"
    c.execute(query, values)
    
    conn.commit()
    conn.close()
    print("Character/NPC added successfully.")

# Function to edit characters or NPCs
def edit_character_npc():

    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    char_id = int(input("Enter the ID of the character/NPC to edit: "))
    user_id = int(input("Enter your user ID: "))

    # Fetch the role of the user
    c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = c.fetchone()[0]

    # Fetch the role of the character (npc or character)
    c.execute('SELECT role FROM characters WHERE id = ?', (char_id,))
    character_role = c.fetchone()[0]

    # Allow modification if the character is NPC and the user is GM
    if character_role == 'npc' and user_role != 'gm':
        print("Only the GM can modify NPCs.")
        return
    else:
        # Allow the user to proceed with modifying the NPC
        new_value = input("Enter the new value for the NPC: ")
        field = input("Enter the field you want to modify (e.g., health, level, etc.): ")
        c.execute(f'UPDATE characters SET {field} = ? WHERE id = ?', (new_value, char_id))
        conn.commit()
        print(f"{field} of NPC with ID {char_id} updated successfully.")
        conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    char_id = int(input("Enter the ID of the character/NPC to edit: "))
    user_id = int(input("Enter your user ID: "))

    # Fetch the role of the user
    c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = c.fetchone()[0]

    # Fetch the role of the character (npc or character)
    c.execute('SELECT role FROM characters WHERE id = ?', (char_id,))
    character_role = c.fetchone()[0]

    # Allow modification if the character is NPC and the user is GM
    if character_role == 'npc' and user_role != 'gm':
        print("Only the GM can modify NPCs.")
        return
    else:
        # Allow the user to proceed with modifying the NPC
        new_value = input("Enter the new value for the NPC: ")
        field = input("Enter the field you want to modify (e.g., health, level, etc.): ")
        c.execute(f'UPDATE characters SET {field} = ? WHERE id = ?', (new_value, char_id))
        conn.commit()
        print(f"{field} of NPC with ID {char_id} updated successfully.")
        c = conn.cursor()
    
    char_id = int(input("Enter the ID of the character/NPC to edit: "))
    columns = get_table_columns()
    print(f"Available fields: {', '.join(columns)}")
    
    field = input(f"Which field would you like to edit? (choose from: {', '.join(columns)}): ").lower()
    new_value = input(f"Enter new value for {field}: ")
    
    # Ensure numerical fields are stored as integers
    if field in ['level', 'health', 'strength', 'intelligence', 'armor_class', 'fortitude', 'reflex', 'will']:
        new_value = int(new_value)
    
    c.execute(f'UPDATE characters SET {field} = ? WHERE id = ?', (new_value, char_id))
    
    conn.commit()
    conn.close()
    print(f"Character/NPC with ID {char_id} updated successfully.")

# Function to view characters and NPCs dynamically
def view_characters_npcs():
    """View all characters and NPCs dynamically based on the fields in the database."""
    conn = sqlite3.connect('characters_npcs.db')  # Separate database
    c = conn.cursor()

    # Dynamically retrieve the column names
    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall()]

    # Fetch all character/NPC data
    c.execute('SELECT * FROM characters')
    characters = c.fetchall()

    if characters:
        for character in characters:
            print("\n--- Character/NPC Details ---")
            # Dynamically print each column and its corresponding value
            for index, column in enumerate(columns):
                value = character[index]
                print(f"{column.replace('_', ' ').capitalize()}: {value}")
    else:
        print("No characters or NPCs found.")

    conn.close()

# Function to delete characters or NPCs
def delete_character_npc():
    """Delete a character or NPC from the system."""
    conn = sqlite3.connect('characters_npcs.db')  # Separate database
    c = conn.cursor()
    
    char_id = int(input("Enter the ID of the character/NPC to delete: "))
    
    c.execute('DELETE FROM characters WHERE id = ?', (char_id,))
    
    conn.commit()
    conn.close()
    print(f"Character/NPC with ID {char_id} deleted successfully.")

# Function to add new fields dynamically
def add_field_to_table():
    """Add a new field to the characters table dynamically."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    field_name = input("Enter the name of the new field: ")
    field_type = input("Enter the type of the field (INTEGER, TEXT, REAL, BOOLEAN): ").upper()
    nullable = input("Can this field be NULL? (yes/no): ").lower()
    default_value = input("Enter the default value for this field (optional, press Enter to skip): ")

    query = f"ALTER TABLE characters ADD COLUMN {field_name} {field_type}"
    
    if nullable == 'no':
        query += " NOT NULL"
    if default_value:
        query += f" DEFAULT {default_value}"

    try:
        c.execute(query)
        conn.commit()
        print(f"Field '{field_name}' of type '{field_type}' added to the characters table.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    
    conn.close()

# Function to remove fields dynamically
def remove_field_from_table():
    """Remove a field from the characters table."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    field_name = input("Enter the name of the field to remove: ")

    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall() if col[1] != field_name]

    c.execute(f"CREATE TABLE IF NOT EXISTS new_characters ({', '.join(columns)})")
    c.execute(f"INSERT INTO new_characters ({', '.join(columns)}) SELECT {', '.join(columns)} FROM characters")
    c.execute("DROP TABLE characters")
    c.execute("ALTER TABLE new_characters RENAME TO characters")
    
    conn.commit()
    conn.close()
    print(f"Field '{field_name}' removed successfully.")

# Function to manage customization of fields
def customize_fields_menu():
    while True:
        print("\n--- Customize Character/NPC Fields ---")
        print("1. Add a new field")
        print("2. Remove a field")
        print("3. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_field_to_table()
        elif choice == "2":
            remove_field_from_table()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

# Character/NPC main menu
def character_npc_menu():
    while True:
        print("\n--- Character/NPC Management ---")
        print("1. Add Character/NPC")
        print("2. View Characters/NPCs")
        print("3. Edit Character/NPC")
        print("4. Delete Character/NPC")
        print("5. Customize Fields")
        print("6. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_character_npc()
        elif choice == "2":
            view_characters_npcs()
        elif choice == "3":
            edit_character_npc()
        elif choice == "4":
            delete_character_npc()
        elif choice == "5":
            customize_fields_menu()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")
