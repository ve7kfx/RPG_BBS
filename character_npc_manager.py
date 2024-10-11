import sqlite3

# Pagination constants
PAGE_SIZE = 5  # Number of characters/NPCs to display per page

# Helper function to get numeric input with validation
def get_numeric_input(field_name):
    """Prompt for and validate numeric input."""
    while True:
        try:
            return int(input(f"Enter {field_name}: "))
        except ValueError:
            print(f"Invalid input. Please enter a valid number for {field_name}.")

# Helper function to get real (floating-point) input with validation
def get_real_input(field_name):
    """Prompt for and validate real number (float) input."""
    while True:
        try:
            return float(input(f"Enter {field_name}: "))
        except ValueError:
            print(f"Invalid input. Please enter a valid real number for {field_name}.")

# Helper function to get text input
def get_text_input(field_name):
    """Prompt for text input."""
    return input(f"Enter {field_name}: ")

# Helper function for role selection (1 for NPC, 0 for character)
def get_role_input():
    """Prompt for and validate role input (1 for NPC, 0 for character)."""
    print("You are about to create a new entry in the system.")
    print("Please choose whether you want this to be an NPC or a Character.")
    print("Enter '1' for NPC or '0' for Character.")
    
    while True:
        role = input("Enter role (1 for NPC, 0 for character): ").strip()
        if role in ['0', '1']:
            return int(role)
        else:
            print("Invalid input. Please enter '1' for NPC or '0' for character.")

# Function to get skills with values from the user
def get_skills_with_values():
    """Prompt for D&D 3.5 skills and their corresponding values."""
    dnd_skills = [
        "Appraise", "Balance", "Bluff", "Climb", "Concentration", "Craft", 
        "Decipher Script", "Diplomacy", "Disable Device", "Disguise", 
        "Escape Artist", "Forgery", "Gather Information", "Handle Animal", 
        "Heal", "Hide", "Intimidate", "Jump", "Knowledge (Arcana)", 
        "Knowledge (Dungeoneering)", "Knowledge (Geography)", "Knowledge (History)", 
        "Knowledge (Local)", "Knowledge (Nature)", "Knowledge (Nobility and Royalty)", 
        "Knowledge (Religion)", "Listen", "Move Silently", "Open Lock", "Perform", 
        "Profession", "Ride", "Search", "Sense Motive", "Sleight of Hand", 
        "Speak Language", "Spellcraft", "Spot", "Survival", "Swim", "Tumble", 
        "Use Magic Device", "Use Rope"
    ]
    
    print("\nEnter the skill values for the following D&D 3.5 skills:")
    
    # Create a dictionary to store skill names and their values
    skill_values = {}
    
    # Loop through the skills and prompt the user for a value for each one
    for skill in dnd_skills:
        while True:
            try:
                value = int(input(f"{skill}: "))  # Prompt for the skill value
                skill_values[skill] = value  # Store the skill and its value
                break  # Exit the loop once a valid value is entered
            except ValueError:
                print("Please enter a valid number for the skill value.")
    
    # Return the skill values as a formatted string, e.g., "Tumble 12, Use Rope 1"
    return ', '.join(f"{skill} {value}" for skill, value in skill_values.items())

# Helper function to check if the user is a GM
def is_gm(user_id):
    """Check if the user is a GM based on their user_id."""
    conn = sqlite3.connect('bbs.db')  # Assuming GM info is stored in the 'bbs.db' database
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    role = c.fetchone()
    conn.close()

    # Assuming 'gm' is the role for a GM user
    return role is not None and role[0] == 'gm'

# Function to create the character and NPC table
def create_character_npc_table():
    """Create a table for characters and NPCs with additional fields for D&D style game, including skills, hit dice, and saving throws."""
    conn = sqlite3.connect('characters_npcs.db')  # Separate database
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS characters ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role BOOLEAN NOT NULL,  -- 1 for NPC, 0 for character
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
        skills TEXT,  -- New column for skills
        non_consumable_inventory TEXT,
        consumable_inventory TEXT,
        spells_known TEXT
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Character/NPC, was created in 'characters_npcs.db'.")

import sqlite3

# Function to view all characters/NPCs for GM or only characters for regular users
def view_character_npc_details(user_id):
    """View all characters/NPCs for GM or only characters for regular users with pagination and search."""
    
    # Helper function for pagination
    def paginate_list(items, page_size):
        """Generator for paginating a list."""
        for i in range(0, len(items), page_size):
            yield items[i:i + page_size]
	   
    def display_character_sheet(character, column_names):
        """Display a formatted character sheet for a selected character/NPC, grouped into sections with extra fields at the bottom."""
        
        print("\n--- Character Sheet ---")
        
        # Define the columns for each section
        general_info = ['name', 'race', 'class', 'alignment', 'deity', 'level', 'experience_points']
        attributes = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma', 'armor_class', 'hit_points', 'initiative', 'speed']
        saves = ['fortitude_save', 'reflex_save', 'will_save']
        combat = ['base_attack_bonus', 'grapple']
        inventory = ['weapons', 'armor', 'gear', 'gold']
        feats_spells = ['feats', 'spells']
        special_abilities = ['special_abilities']

        # Track displayed columns
        displayed_columns = set(general_info + attributes + saves + combat + inventory + feats_spells + special_abilities + ['skills'])

        # Display general info
        for col_name, value in zip(column_names, character):
            if col_name in general_info:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        # Attributes section
        print("\n--- Attributes ---")
        for col_name, value in zip(column_names, character):
            if col_name in attributes:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        # Saves section
        print("\n--- Saves ---")
        for col_name, value in zip(column_names, character):
            if col_name in saves:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        # Combat section
        print("\n--- Combat ---")
        for col_name, value in zip(column_names, character):
            if col_name in combat:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        # Skills section (displayed as an ASCII table)
        skills_str = character[column_names.index('skills')]
        if skills_str:
            print("\n--- Skills ---")
            print(f"{'Skill':<25} | {'Value':<5}")
            print("-" * 32)
            
            skills_list = [skill.strip() for skill in skills_str.split(',')]
            for skill in skills_list:
                skill_name, skill_value = skill.rsplit(' ', 1)  # Split skill name and value
                print(f"{skill_name:<25} | {skill_value:<5}")

        # Inventory section
        print("\n--- Inventory ---")
        for col_name, value in zip(column_names, character):
            if col_name in inventory:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        # Feats & Spells section
        print("\n--- Feats & Spells ---")
        for col_name, value in zip(column_names, character):
            if col_name in feats_spells:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        # Special Abilities section
        print("\n--- Special Abilities ---")
        for col_name, value in zip(column_names, character):
            if col_name in special_abilities:
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")
        
        # Append any additional information that doesn't fit into these categories
        print("\n--- Other Information ---")
        for col_name, value in zip(column_names, character):
            if col_name not in displayed_columns and value is not None and value != '':
                display_name = col_name.replace('_', ' ').title()
                print(f"{display_name}: {value}")

        print("\n--- End of Character Sheet ---")
        print("=" * 40)
    
    # Helper function to search characters/NPCs by name
    def search_characters_by_name(search_term):
        """Search characters/NPCs by name."""
        if is_gm(user_id):
            c.execute("SELECT * FROM characters WHERE name LIKE ?", ('%' + search_term + '%',))
        else:
            c.execute("SELECT * FROM characters WHERE role = 0 AND name LIKE ?", ('%' + search_term + '%',))
        return c.fetchall()

    # Helper function to check if the user is a GM
    def is_gm(user_id):
        """Check if the user is a GM based on their user_id."""
        c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        role = c.fetchone()
        return role is not None and role[0] == 'gm'

    # Constants
    PAGE_SIZE = 5  # Number of characters/NPCs to display per page

    # Connect to database
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Fetch all column names dynamically
    c.execute("PRAGMA table_info(characters)")
    columns_info = c.fetchall()
    column_names = [col[1] for col in columns_info]  # Extract column names

    # Fetch characters or NPCs depending on user role
    if is_gm(user_id):
        c.execute('SELECT * FROM characters')
        characters = c.fetchall()
        print("Displaying all characters and NPCs (GM view):")
    else:
        c.execute('SELECT * FROM characters WHERE role = 0')  # Only show characters
        characters = c.fetchall()
        print("Displaying all characters:")

    # If no characters/NPCs are found
    if not characters:
        print("No characters or NPCs found. You may want to add some using the 'Add Character/NPC' option.")
        conn.close()
        return

    # Paginate and display results by name
    pages = list(paginate_list(characters, PAGE_SIZE))
    total_pages = len(pages)
    page_num = 0

    while True:
        # Display current page
        print(f"\n--- Page {page_num + 1} of {total_pages} ---")
        current_page = pages[page_num]

        # Numbered list of characters/NPCs by name on the current page
        for idx, character in enumerate(current_page, start=1 + page_num * PAGE_SIZE):
            print(f"{idx}. {character[2]}")  # Display name with index (name is in column 2)

        # Prompt to select a character or navigate pages
        action = input(f"\nSelect a character by number, or 'n' for next page, 'p' for previous page, 'q' to quit: ").strip().lower()

        # Handle navigation or selection
        if action.isdigit():
            char_index = int(action) - 1
            if 0 <= char_index < len(characters):
                selected_character = characters[char_index]
                display_character_sheet(selected_character, column_names)  # Display the character sheet
            else:
                print("Invalid selection.")
        elif action == 'n' and page_num < total_pages - 1:
            page_num += 1
        elif action == 'p' and page_num > 0:
            page_num -= 1
        elif action == 'q':
            break
        else:
            print("Invalid input. Please try again.")

    # Close the connection
    conn.close()

#Function to add Characters and NPCs
def add_character():
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Retrieve the column names and types from the 'characters' table, starting from column 2
    c.execute("PRAGMA table_info(characters)")
    columns_info = c.fetchall()[2:]  # Skip the 'id' column

    # Initialize a dictionary to hold column names and user input values
    user_input = {}

    # Loop through each column starting from the second and prompt the user for input
    for column in columns_info:
        column_name = column[1]  # Column name is at index 1
        column_type = column[2]  # Column type is at index 2

        if column_name == 'skills':  # Special case for skills input
            user_input[column_name] = get_skills_with_values()
        else:
            user_input[column_name] = get_input_for_column(column_name, column_type)

    # Prepare SQL placeholders for the insert query
    columns_string = ', '.join(user_input.keys())
    placeholders = ', '.join(['?' for _ in user_input])

    # Insert the new character/NPC data into the database
    query = f"INSERT INTO characters ({columns_string}) VALUES ({placeholders})"
    c.execute(query, list(user_input.values()))

    conn.commit()
    conn.close()

    print(f"Character/NPC '{user_input.get('name', 'Unknown')}' added successfully.")

# Function to retrieve input for each field based on its type
def get_input_for_column(column_name, column_type):
    """Prompt user for input based on column type."""
    if column_type == 'INTEGER':
        return get_numeric_input(column_name.replace('_', ' ').capitalize())
    elif column_type == 'REAL':
        return get_real_input(column_name.replace('_', ' ').capitalize())
    elif column_type == 'TEXT':
        return get_text_input(column_name.replace('_', ' ').capitalize())
    elif column_type == 'BOOLEAN':
        return get_role_input()
    else:
        return get_text_input(column_name.replace('_', ' ').capitalize())

# Function to edit characters or NPCs dynamically based on table fields

# Function to edit an existing character or NPC with pagination and search
def edit_character_npc(user_id):
    """Edit an existing character or NPC with quick field search and option to modify all fields."""
    
    # Helper function for pagination
    def paginate_list(items, page_size):
        """Generator for paginating a list."""
        for i in range(0, len(items), page_size):
            yield items[i:i + page_size]

    # Helper function to search characters/NPCs by name
    def search_characters_by_name(search_term):
        """Search characters/NPCs by name."""
        if is_gm(user_id):
            c.execute("SELECT * FROM characters WHERE name LIKE ?", ('%' + search_term + '%',))
        else:
            c.execute("SELECT * FROM characters WHERE role = 0 AND name LIKE ?", ('%' + search_term + '%',))
        return c.fetchall()

    # Helper function to get input for a specific field
    def get_input_for_column(column_name, current_value):
        """Prompt user for input based on column type, allowing them to keep the current value."""
        new_value = input(f"Enter new value for {column_name.replace('_', ' ').title()} (leave blank to keep '{current_value}'): ").strip()
        return new_value if new_value else current_value

    # Helper function to check if the user is a GM
    def is_gm(user_id):
        """Check if the user is a GM based on their user_id."""
        conn = sqlite3.connect('bbs.db')  # Use the correct database here
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        role = c.fetchone()
        conn.close()
        
        return role is not None and role[0] == 'gm'

    # Constants
    PAGE_SIZE = 5  # Number of characters/NPCs to display per page

    # Connect to the database
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Fetch all column names dynamically
    c.execute("PRAGMA table_info(characters)")
    columns_info = c.fetchall()
    column_names = [col[1] for col in columns_info]  # Extract column names

    # Fetch characters or NPCs depending on user role
    if is_gm(user_id):
        c.execute('SELECT * FROM characters')
        characters = c.fetchall()
        print("Displaying all characters and NPCs (GM view):")
    else:
        c.execute('SELECT * FROM characters WHERE role = 0')  # Only show characters
        characters = c.fetchall()
        print("Displaying all characters:")

    # If no characters/NPCs are found
    if not characters:
        print("No characters or NPCs found.")
        conn.close()
        return

    # Search option
    search_term = input("Enter a name to search or press Enter to skip: ").strip()
    if search_term:
        characters = search_characters_by_name(search_term)
        if not characters:
            print(f"No characters found with the name '{search_term}'.")
            conn.close()
            return

    # Paginate and display results
    pages = list(paginate_list(characters, PAGE_SIZE))
    total_pages = len(pages)
    page_num = 0

    while True:
        # Display current page
        print(f"\n--- Page {page_num + 1} of {total_pages} ---")
        current_page = pages[page_num]

        # Numbered list of characters/NPCs on the current page
        for idx, character in enumerate(current_page, start=1 + page_num * PAGE_SIZE):
            print(f"{idx}. {character[1]}")  # Display name with index

        # Prompt to select a character or navigate pages
        action = input(f"\nSelect a character by number, 'n' for next page, 'p' for previous page, 'q' to quit: ").strip().lower()

        # Handle navigation or selection
        if action.isdigit():
            char_index = int(action) - 1
            if 0 <= char_index < len(characters):
                selected_character = characters[char_index]
                
                # Fetch the selected character
                c.execute("SELECT * FROM characters WHERE id = ?", (selected_character[0],))  # Assuming ID is in the first column
                character = c.fetchone()

                if not character:
                    print("Character/NPC not found.")
                    conn.close()
                    return

                # Initialize a dictionary to hold column names and updated values
                updated_values = {col: character[i] for i, col in enumerate(column_names) if col != 'id'}

                # Main loop for editing fields
                while True:
                    # Display current values
                    print("\n--- Current Character Information ---")
                    for col_name, value in updated_values.items():
                        display_name = col_name.replace('_', ' ').title()
                        print(f"{display_name}: {value}")

                    # Ask the user if they want to search for a specific field or run through all fields
                    edit_mode = input("\nDo you want to (1) search a specific field or (2) run through all fields? (1/2): ").strip()

                    if edit_mode == '1':  # Search and modify a specific field
                        field_to_modify = input("Enter the field name to modify: ").strip().lower()
                        
                        if field_to_modify in updated_values:
                            updated_values[field_to_modify] = get_input_for_column(field_to_modify, updated_values[field_to_modify])

                            # Ask if the user wants to continue editing or save and exit
                            continue_editing = input("\nDo you want to modify another field? (y/n): ").strip().lower()
                            if continue_editing == 'n':
                                break
                        else:
                            print(f"Field '{field_to_modify}' does not exist. Please enter a valid field.")
                    elif edit_mode == '2':  # Run through all fields
                        for col_name in updated_values.keys():
                            updated_values[col_name] = get_input_for_column(col_name, updated_values[col_name])
                        
                        # Ask if the user wants to continue editing or save and exit
                        continue_editing = input("\nDo you want to modify another field? (y/n): ").strip().lower()
                        if continue_editing == 'n':
                            break
                    else:
                        print("Invalid option. Please enter '1' or '2'.")
                        continue

                # Prepare the query to update the character
                set_clause = ', '.join(f"{col} = ?" for col in updated_values.keys())
                query = f"UPDATE characters SET {set_clause} WHERE id = ?"

                # Execute the update query with the updated values
                c.execute(query, list(updated_values.values()) + [character[0]])

                conn.commit()
                print(f"Character/NPC '{updated_values.get('name', 'Unknown')}' updated successfully.")
                break  # Exit the loop after successful update
            else:
                print("Invalid selection.")
        elif action == 'n' and page_num < total_pages - 1:
            page_num += 1
        elif action == 'p' and page_num > 0:
            page_num -= 1
        elif action == 'q':
            break
        else:
            print("Invalid input. Please try again.")

    conn.close()

import sqlite3

import sqlite3

def delete_character_npc(user_id):
    """Delete a character or NPC from the system, with restrictions based on user role."""

    # Check if the user is a GM
    def is_gm(user_id):
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        role = c.fetchone()
        conn.close()
        return role is not None and role[0] == 'gm'

    # Connect to the characters database
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Fetch characters based on user role
    if is_gm(user_id):
        c.execute('SELECT id, name, role FROM characters')
    else:
        c.execute('SELECT id, name, role FROM characters WHERE role = 0')  # Non-GMs can only delete characters, not NPCs
    characters = c.fetchall()

    if not characters:
        print("No characters or NPCs found to delete.")
        conn.close()
        return

    # Display the list of characters/NPCs
    print("\n--- Character/NPC List ---")
    for idx, character in enumerate(characters, start=1):
        char_id, char_name, char_role = character
        role_name = "NPC" if char_role == 1 else "Character"
        print(f"{idx}. {char_name} ({role_name})")

    # Deletion by selecting number from the list
    while True:
        try:
            selection = input("\nSelect a character by number to delete, or 'q' to quit: ").strip().lower()
            if selection == 'q':
                print("Deletion canceled.")
                conn.close()
                return
            selection = int(selection)
            if 1 <= selection <= len(characters):
                selected_character = characters[selection - 1]  # Get the selected character
                char_id, char_name, char_role = selected_character
                break
            else:
                print(f"Please select a valid number between 1 and {len(characters)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Fetch creator information for the selected character
    c.execute("SELECT role, user_id FROM characters WHERE id = ?", (char_id,))
    char_role, creator_id = c.fetchone()

    # Ensure that only GMs can delete NPCs and users can delete their own characters
    if char_role == 1 and not is_gm(user_id):
        print("Only GMs can delete NPCs.")
    elif char_role == 0 and user_id != creator_id:
        print("You can only delete your own characters.")
    else:
        # Confirm and delete
        confirm = input(f"Are you sure you want to delete '{char_name}'? (y/n): ").strip().lower()
        if confirm == 'y':
            c.execute("DELETE FROM characters WHERE id = ?", (char_id,))
            conn.commit()
            print(f"Character/NPC '{char_name}' deleted successfully.")
        else:
            print("Deletion canceled.")

    conn.close()
# Function to add or remove fields dynamically
def modify_fields(user_id):
    """Add or remove fields in the character table."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Check if the user is GM
    gm_status = is_gm(user_id)

    # Fetch current columns from 'characters' table
    def get_existing_columns():
        c.execute("PRAGMA table_info(characters)")
        return [col[1] for col in c.fetchall()]

    while True:
        print("\n--- Modify Fields ---")
        print("1. Add Field (GM only)")
        print("2. Remove Field (GM only)")
        print("3. Done")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            if not gm_status:
                print("Only the GM can add fields.")
                continue

            # Add a new field
            field_name = input("Enter the name of the new field: ").strip()
            field_type = input("Enter the type of the field (TEXT, INTEGER, BOOLEAN, REAL): ").upper().strip()

            if not field_name or ' ' in field_name:
                print("Invalid field name. Field name cannot be empty or contain spaces.")
                continue

            existing_columns = get_existing_columns()

            if field_name in existing_columns:
                print(f"Field '{field_name}' already exists.")
                continue

            if field_type not in ('TEXT', 'INTEGER', 'BOOLEAN', 'REAL'):
                print(f"Invalid field type: {field_type}. Must be TEXT, INTEGER, BOOLEAN, or REAL.")
                continue

            try:
                c.execute(f"ALTER TABLE characters ADD COLUMN {field_name} {field_type}")
                conn.commit()
                print(f"Field '{field_name}' added successfully.")
            except sqlite3.OperationalError as e:
                print(f"Error adding field: {e}")
        elif choice == '2':
            if not gm_status:
                print("Only the GM can remove fields.")
                continue

            # Remove an existing field
            field_name = input("Enter the name of the field to remove: ").strip()

            existing_columns = get_existing_columns()

            if field_name not in existing_columns:
                print(f"Field '{field_name}' does not exist.")
                continue

            # Get user confirmation before proceeding
            confirm = input(f"Are you sure you want to remove the field '{field_name}'? This cannot be undone. (y/n): ").lower().strip()
            if confirm != 'y':
                continue

            try:
                columns_to_keep = [col for col in existing_columns if col != field_name]
                c.execute(f"CREATE TABLE characters_new AS SELECT {', '.join(columns_to_keep)} FROM characters")
                c.execute("DROP TABLE characters")
                c.execute("ALTER TABLE characters_new RENAME TO characters")
                conn.commit()
                print(f"Field '{field_name}' removed successfully.")
            except sqlite3.OperationalError as e:
                print(f"Error removing field: {e}")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

# Character/NPC main menu
def character_npc_menu(user_id):
    while True:
        print("\n--- Character/NPC Management ---")
        print("1. Add Character/NPC")
        print("2. View Character/NPC Details")
        print("3. Edit Character/NPC")
        print("4. Delete Character/NPC")
        print("5. Modify Fields")
        print("6. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_character()
        elif choice == "2":
            view_character_npc_details(user_id)  # Modified to view characters/NPCs based on user role
        elif choice == "3":
            edit_character_npc(user_id)
        elif choice == "4":
            delete_character_npc(user_id)
        elif choice == "5":
            modify_fields(user_id)  # Pass user_id to modify_fields
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")
