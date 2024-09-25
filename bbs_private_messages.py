import sqlite3
from bbs_auth import get_user_id

def send_private_message(sender_id):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    receiver_username = input("Enter the receiver's username: ")
    receiver_id = get_user_id(receiver_username)

    if receiver_id:
        content = input("Enter your message: ")
        c.execute('INSERT INTO private_messages (sender_id, receiver_id, content) VALUES (?, ?, ?)', 
                  (sender_id, receiver_id, content))
        conn.commit()
        print("Message sent successfully!")
    else:
        print("User not found.")
    
    conn.close()

def view_inbox(user_id):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    c.execute('''
    SELECT sender_id, content, sent_at 
    FROM private_messages 
    WHERE receiver_id = ? 
    ORDER BY sent_at DESC
    ''', (user_id,))
    messages = c.fetchall()

    if messages:
        print("\nInbox:")
        for message in messages:
            print(f"From {message[0]}: {message[1]} (Sent at {message[2]})")
    else:
        print("No messages.")

    conn.close()
