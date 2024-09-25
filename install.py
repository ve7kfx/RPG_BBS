import sqlite3

# Create default GM user with a password prompt
def create_gm_user():
    """Create a default user called GM with a user-defined password."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Create the users table if not exists (NO UNIQUE constraint on username)
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'gm')),
        password TEXT NOT NULL
    )
    ''')

    # Prompt the user for the GM password
    password = input("Please enter the password for the GM account: ")

    # Create the GM user with the user-defined password
    c.execute('''
    INSERT INTO users (username, role, password) VALUES ('GM', 'gm', ?)
    ''', (password,))

    conn.commit()
    conn.close()
    print(f"GM account created successfully.")
    print(f"Username: GM, Password: {password}")

# Character/NPC database creation and setup with pre-populated fields
def create_character_npc_table():
    """Create a table for characters and NPCs with hit dice and saving throws."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    # Initial fields for characters and NPCs, including hit dice and saving throws
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

    # Display the fields that were created in the characters table
    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall()]
    print("Fields in the 'characters' table: ", columns)

    conn.close()
    print("Character/NPC table created successfully in 'characters_npcs.db'.")

# Function to add new fields dynamically
def add_field_to_table(c, conn):
    """Add a new field to the characters table dynamically."""
    while True:
        field_name = input("Enter the name of the new field (or type 'done' to finish adding fields): ")
        if field_name.lower() == 'done':
            break

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

# Function to remove fields dynamically
def remove_field_from_table(c, conn):
    """Remove a field from the characters table dynamically."""
    # Get the list of existing columns
    c.execute("PRAGMA table_info(characters)")
    columns = [col[1] for col in c.fetchall()]
    print("Existing fields:", columns)

    field_name = input("Enter the name of the field to remove: ")

    if field_name not in columns:
        print(f"Field '{field_name}' does not exist in the table.")
        return

    # Remove the column by creating a new table without the unwanted field
    columns.remove(field_name)
    column_definitions = ", ".join(columns)

    try:
        c.execute(f'''
        CREATE TABLE IF NOT EXISTS characters_new AS
        SELECT {", ".join(columns)} FROM characters
        ''')
        c.execute("DROP TABLE characters")
        c.execute("ALTER TABLE characters_new RENAME TO characters")
        conn.commit()
        print(f"Field '{field_name}' removed from the characters table.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

# Combined add/remove fields function based on user's choice
def modify_fields():
    """Give the user the option to add or remove fields."""
    conn = sqlite3.connect('characters_npcs.db')
    c = conn.cursor()

    while True:
        print("\nChoose an option:")
        print("1. Add fields")
        print("2. Remove fields")
        print("3. Done")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            add_field_to_table(c, conn)
        elif choice == '2':
            remove_field_from_table(c, conn)
        elif choice == '3':
            print("Modification complete.")
            break
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")

    conn.close()

# BBS Database and user-created thread categories during installation
def create_bbs_tables():
    """Create the BBS threads and posts tables without creating actual threads."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Create the threads table if not exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        locked INTEGER DEFAULT 0
    )
    ''')

    # Create the posts table if not exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("BBS tables (threads and posts) created successfully in 'bbs.db'.")

# Set thread categories during installation
def set_thread_categories():
    """Allow the user to create thread categories without threads during the installation."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    print("Let's create some thread categories for your BBS:")
    while True:
        category = input("Enter thread category (e.g., General, Tech, Gaming): ")
        if not category.strip():
            print("Category cannot be empty. Try again.")
            continue
        # Insert the user-defined category into the database
        c.execute('INSERT INTO threads (category, title, created_by) VALUES (?, ?, 0)', (category, "Placeholder"))

        more_categories = input("Would you like to add another category? (yes/no): ").lower()
        if more_categories == 'no':
            break

    conn.commit()
    conn.close()
    print("Categories created successfully.")

# Main installation process
def install():
    """Run the full installation for the BBS and Character/NPC system."""
    # Create the GM user with user-defined password
    create_gm_user()

    # Create the Character/NPC table
    create_character_npc_table()

    # Allow user to add or remove dynamic fields to/from the character table
    modify_fields()

    # Create the BBS tables (no default threads)
    create_bbs_tables()

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
