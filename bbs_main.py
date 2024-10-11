from bbs_auth import register, login 
from bbs_message_board import create_thread, view_threads, reply_to_thread, edit_post
from bbs_private_messages import send_private_message, view_inbox
from character_npc_manager import character_npc_menu
import sqlite3
import re

# Function to validate the GM access password
def validate_access_password(password):   
    """Validate that the password is alphanumeric with at least one special character."""
    if len(password) >= 8 and re.search(r'\W', password) and re.search(r'[a-zA-Z0-9]', password):
        return True
    else:
        return False

def create_gm_access_password():
    """Function to create the GM access password on the first run of the program."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Ensure the system_settings table exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Check if the access password has been set before
    c.execute('SELECT password FROM system_settings WHERE setting = "access_password"')
    password = c.fetchone()

    if not password or password[0] is None:
        # First run, prompt GM to create a new access password
        while True:
            new_password = input("Please set an access password for restricted sections (min 8 characters, at least 1 special character): ")
            if validate_access_password(new_password):
                # Save the new access password to the database
                c.execute('INSERT INTO system_settings (setting, password) VALUES ("access_password", ?)', (new_password,))
                conn.commit()
                print("Access password set successfully.")
                break
            else:
                print("Invalid password. It must be at least 8 characters long and contain at least one special character.")
    else:
        print("Access password has already been set.")

    conn.close()

def check_user_access_password():
    """Prompt the user for the access password if not already validated."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check if the access password has been set by the GM
    c.execute('SELECT password FROM system_settings WHERE setting = "access_password"')
    password = c.fetchone()

    if not password or password[0] is None:
        print("Access password not set. Please ask the GM to set it.")
        return False
    else:
        # Prompt the user to enter the access password
        for _ in range(3):  # Allow up to 3 attempts
            input_password = input("Enter the access password to view restricted sections: ")
            if input_password == password[0]:
                return True
            else:
                print("Incorrect access password.")
        return False

def check_gm_access_password():
    """Prompt the GM to create or change an access password."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check if the access password has already been set
    c.execute('SELECT password FROM system_settings WHERE setting = "access_password"')
    password = c.fetchone()

    if not password or password[0] is None:
        create_gm_access_password()
    else:
        # Access password exists, offer the option to change it
        change_password = input("Would you like to change the existing access password? (yes/no): ").lower()
        if change_password == "yes":
            while True:
                new_password = input("Enter a new access password: ")
                if validate_access_password(new_password):
                    # Update the access password in the database
                    c.execute('UPDATE system_settings SET password = ? WHERE setting = "access_password"', (new_password,))
                    conn.commit()
                    print("Access password updated successfully.")
                    break
                else:
                    print("Invalid password. It must be at least 8 characters long and contain at least one special character.")

    conn.close()

def check_gm_login_password():
    """Check GM login password before allowing GM to log in."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Retrieve the GM login password from the database
    c.execute('SELECT password FROM users WHERE role = "gm"')
    gm_password = c.fetchone()[0]

    # Prompt for GM login password
    for _ in range(3):  # Allow up to 3 attempts
        input_password = input("Enter GM login password: ")
        if input_password == gm_password:
            return True
        else:
            print("Incorrect GM login password.")
    
    conn.close()
    return False

def main_menu(user):
    user_id = user[0]  # Assuming the first item in the user tuple is the user_id
    role = user[1]     # Assuming the second item is the user's role ('gm' or 'user')

    while True:
        print("\nMain Menu")
        print("1. View Threads")
        print("2. Reply to Thread")
        print("3. Send Private Message")
        print("4. View Inbox")
        print("5. Create Thread" if role == 'gm' else "SORRY GM ONLY")
        print("6. Edit Post")
        print("7. Character/NPC Management")  # Accessible to all users now
        print("8. Change Access Password" if role == 'gm' else "SORRY GM ONLY")
        print("9. Logout")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            view_threads(user_id)  # Pass user_id to view_threads()
        elif choice == "2":
            if role == 'gm' or check_user_access_password():
                reply_to_thread(user_id)
            else:
                print("Access denied.")
        elif choice == "3":
            if role == 'gm' or check_user_access_password():
                send_private_message(user_id)
            else:
                print("Access denied.")
        elif choice == "4":
            if role == 'gm' or check_user_access_password():
                view_inbox(user_id)
            else:
                print("Access denied.")
        elif choice == "5" and role == 'gm':
            create_thread(user_id)
        elif choice == "6" and role == 'gm':
            edit_post(user_id)
        elif choice == "7":
            if role == 'gm' or check_user_access_password():
                character_npc_menu(user_id)  # Now passes user_id
            else:
                print("Access denied.")
        elif choice == "8" and role == 'gm':
            check_gm_access_password()  # Allow GM to change the access password
        elif choice == "9":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    print("Welcome to the RPG TERMINAL BBS")
    
    # Check or set GM access password on first run of the program
    create_gm_access_password()
    
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            register()
        elif choice == "2":
            user = login()
            if user:
                main_menu(user)
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
