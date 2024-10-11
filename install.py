import sqlite3
import os

# Create the users table in both databases
def create_users_table():
    """Create the users table in both bbs.db and characters_npcs.db."""
    # Create users table in bbs.db
    conn_bbs = sqlite3.connect('bbs.db')
    c_bbs = conn_bbs.cursor()
    c_bbs.execute('''  
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'gm')),
            password TEXT NOT NULL
        )
    ''')
    conn_bbs.commit()
    conn_bbs.close()
    
    # Create users table in characters_npcs.db
    conn_chars = sqlite3.connect('characters_npcs.db')
    c_chars = conn_chars.cursor()
    c_chars.execute('''  
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'gm')),
            password TEXT NOT NULL
        )
    ''')
    conn_chars.commit()
    conn_chars.close()
    
    print("Users table created in both 'bbs.db' and 'characters_npcs.db'.")

# Create default GM user with a password prompt
def create_gm_user():
    """Create a default user called GM with a user-defined password in both databases."""
    # Connect to bbs.db
    conn_bbs = sqlite3.connect('bbs.db')
    c_bbs = conn_bbs.cursor()

    # Prompt the user for the GM password
    password = input("Please enter the password for the GM account: ")

    # Insert GM user into bbs.db
    c_bbs.execute('''
        INSERT INTO users (username, role, password) VALUES ('GM', 'gm', ?)
    ''', (password,))
    gm_user_id = c_bbs.lastrowid  # Get the GM's user ID from bbs.db
    conn_bbs.commit()
    conn_bbs.close()

    # Connect to characters_npcs.db
    conn_chars = sqlite3.connect('characters_npcs.db')
    c_chars = conn_chars.cursor()

    # Insert GM user into characters_npcs.db with the same ID
    c_chars.execute('''
        INSERT INTO users (id, username, role, password) VALUES (?, 'GM', 'gm', ?)
    ''', (gm_user_id, password))
    conn_chars.commit()
    conn_chars.close()

    print(f"GM account created successfully in both databases.")
    print(f"Username: GM, Password: {password}")

# Create BBS-related tables, excluding users table
def create_bbs_tables():
    """Create the BBS-related tables, excluding the users table."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Threads table
    c.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            locked INTEGER DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Posts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER,
            content TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Automatically stores the last edit time
            locked INTEGER DEFAULT 0,  -- Add a lock for posts as well
            FOREIGN KEY (thread_id) REFERENCES threads(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')

    # Private messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS private_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("BBS tables (threads, posts, private messages) created successfully in 'bbs.db'.")

# Character/NPC database creation and setup with pre-populated fields
def create_character_npc_table():
    """Create a table for characters and NPCs with D&D 3.5 fields."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # D&D 3.5 Edition Character Sheet fields, now with user_id to link to users in both databases
    c.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,  -- Links to the users table in both databases
            name TEXT NOT NULL,
            role BOOLEAN NOT NULL,  -- 1 for NPC, 0 for character
            
            -- Basic Info
            race TEXT NOT NULL,
            class TEXT NOT NULL,
            alignment TEXT,
            deity TEXT,
            level INTEGER NOT NULL DEFAULT 1,
            experience_points INTEGER,
            
            -- Attributes
            strength INTEGER NOT NULL,
            dexterity INTEGER NOT NULL,
            constitution INTEGER NOT NULL,
            intelligence INTEGER NOT NULL,
            wisdom INTEGER NOT NULL,
            charisma INTEGER NOT NULL,
            
            -- Combat Stats
            armor_class INTEGER NOT NULL,
            hit_points INTEGER NOT NULL,
            initiative INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            base_attack_bonus INTEGER,
            grapple INTEGER,
            
            -- Saving Throws
            fortitude_save INTEGER NOT NULL,
            reflex_save INTEGER NOT NULL,
            will_save INTEGER NOT NULL,
            
            -- Skills
            skills TEXT,  -- List of skills
            
            -- Equipment
            weapons TEXT,  -- List of weapons
            armor TEXT,    -- List of armor
            gear TEXT,     -- List of other gear
            gold INTEGER,

            -- Miscellaneous
            feats TEXT,     -- List of feats
            spells TEXT,    -- List of known/prepared spells
            special_abilities TEXT,  -- List of special abilities

            FOREIGN KEY(user_id) REFERENCES users(id)  -- Links character to the user
        )
    ''')

    conn.commit()

    # Display the fields that were created in the characters table
    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall()]
    print("Fields in the 'characters' table: ", columns)

    conn.close()
    print("Character/NPC table created successfully in 'characters_npcs.db'.")

# Function to ensure 'id' and 'role' fields cannot be deleted
def prevent_id_and_role_deletion(field_name):
    """Helper function to prevent deletion of 'id' and 'role' fields."""
    if field_name in ['id', 'role']:
        print(f"Error: The '{field_name}' field cannot be deleted as it is essential.")
        return False
    return True

# Function to add new fields dynamically
def add_field_to_table():
    """Add a new field to the characters table dynamically."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    while True:
        field_name = input("Enter the name of the new field (or type 'done' to finish adding fields): ")
        if field_name.lower() == 'done':
            break

        field_type = input("Enter the type of the field (INTEGER, TEXT, REAL, BOOLEAN): ").upper()
        if field_type not in ['INTEGER', 'TEXT', 'REAL', 'BOOLEAN']:
            print("Invalid field type. Please choose from INTEGER, TEXT, REAL, BOOLEAN.")
            continue

        nullable = input("Can this field be NULL? (yes/no): ").lower()
        if nullable not in ['yes', 'no']:
            print("Invalid input for nullable. Please enter 'yes' or 'no'.")
            continue

        default_value = input("Enter the default value for this field (optional, press Enter to skip): ")

        query = f"ALTER TABLE characters ADD COLUMN {field_name} {field_type}"
        
        if nullable == 'no':
            query += " NOT NULL"
        if default_value:
            # Handle BOOLEAN default values
            if field_type == 'BOOLEAN':
                if default_value.lower() in ['true', '1']:
                    default = 1
                elif default_value.lower() in ['false', '0']:
                    default = 0
                else:
                    print("Invalid default value for BOOLEAN type. Using NULL.")
                    default = None
                if default is not None:
                    query += f" DEFAULT {default}"
            else:
                query += f" DEFAULT '{default_value}'"

        try:
            c.execute(query)
            conn.commit()
            print(f"Field '{field_name}' of type '{field_type}' added to the characters table.")
        except sqlite3.OperationalError as e:
            print(f"Error: {e}")

    conn.close()

# Function to remove fields dynamically
def remove_field_from_table():
    """Remove a field from the characters table dynamically."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Get the list of existing columns
    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall()]
    print("Existing fields:", columns)

    field_name = input("Enter the name of the field to remove: ")

    if not prevent_id_and_role_deletion(field_name):
        conn.close()
        return

    if field_name not in columns:
        print(f"Field '{field_name}' does not exist in the table.")
        conn.close()
        return

    # Remove the column by creating a new table without the unwanted field
    columns.remove(field_name)
    columns_str = ", ".join(columns)
    try:
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS characters_new AS
            SELECT {columns_str} FROM characters
        ''')
        c.execute("DROP TABLE characters")
        c.execute("ALTER TABLE characters_new RENAME TO characters")
        conn.commit()
        print(f"Field '{field_name}' removed from the characters table.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

    conn.close()

# Combined add/remove fields function based on user's choice
def modify_fields():
    """Give the user the option to add or remove fields."""
    while True:
        print("\nChoose an option:")
        print("1. Add fields")
        print("2. Remove fields")
        print("3. Done")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            add_field_to_table()
        elif choice == '2':
            remove_field_from_table()
        elif choice == '3':
            print("Modification complete.")
            break
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")

# Set thread categories during installation
def set_thread_categories():
    """Allow the user to create thread categories without threads during the installation."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    print("Let's create some thread categories for your BBS:")
    while True:
        category = input("Enter thread category (e.g., General, Tech, Gaming): ").strip()
        if not category:
            print("Category cannot be empty. Try again.")
            continue
        # Insert the user-defined category into the database
        c.execute('INSERT INTO threads (category, title, created_by) VALUES (?, ?, 0)', (category, "Placeholder"))

        more_categories = input("Would you like to add another category? (yes/no): ").lower()
        if more_categories == 'no':
            break
        elif more_categories != 'yes':
            print("Invalid input. Assuming 'no'.")
            break

    conn.commit()
    conn.close()
    print("Categories created successfully.")

# Main installation process
def install():
    """Run the full installation for the BBS and Character/NPC system."""
    # Delete the existing database files if they exist to ensure a fresh start
    if os.path.exists('bbs.db'):
        os.remove('bbs.db')
        print("'bbs.db' removed.")
    if os.path.exists('characters_npcs.db'):
        os.remove('characters_npcs.db')
        print("'characters_npcs.db' removed.")

    # Create users table in both databases
    create_users_table()

    # Create the BBS tables (no default threads)
    create_bbs_tables()

    # Create the GM user with user-defined password, inserted into both databases
    create_gm_user()

    # Create the Character/NPC table
    create_character_npc_table()

    # Allow user to add or remove dynamic fields to/from the character table
    modify_fields()

    # Set thread categories without creating threads
    set_thread_categories()

    # Inform the user of completion and ask if they want to close the window
    print("Installation is complete!")
    close_window = input("Would you like to close the window? (yes/no): ").lower()
    if close_window == 'yes':
        print("Closing installation window...")
        exit()
    else:
        print("Installation window remains open.")

# Run the install script
if __name__ == "__main__":
    install()
