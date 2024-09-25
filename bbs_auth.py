import sqlite3
import getpass

def register():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    username = input("Enter a username: ")
    password = getpass.getpass("Enter a password: ")
    role = 'user'  # default role for all users is 'user'

    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  (username, password, role))
        conn.commit()
        print("Registration successful.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    
    conn.close()

def login():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    c.execute('SELECT id, role FROM users WHERE username = ? AND password = ?', 
              (username, password))
    user = c.fetchone()

    if user:
        print(f"Login successful. Welcome, {username}!")
        return user  # return user ID and role
    else:
        print("Invalid credentials.")
        return None

def get_user_id(username):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = c.fetchone()
    conn.close()
    return user_id[0] if user_id else None
