import sqlite3
from bbs_dice_roller import roll_dice
import re  # Needed for BBCode parsing

PAGE_SIZE = 5  # Number of items per page

# BBCode parser: Handles basic BBCode formatting for bold, italics, and underline
def bbcode_parser(content):
    # Define color codes within the function
    def color_code(color_name):
        colors = {
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37'
        }
        return colors.get(color_name, '37')  # Default to white if color not found

    # Bold, Italics, Underline
    content = re.sub(r'\[b\](.*?)\[/b\]', '\033[1m\\1\033[0m', content)  # Bold
    content = re.sub(r'\[i\](.*?)\[/i\]', '\033[3m\\1\033[0m', content)  # Italics
    content = re.sub(r'\[u\](.*?)\[/u\]', '\033[4m\\1\033[0m', content)  # Underline

    # Color parsing: Matches [color=colorname]...[/color]
    content = re.sub(r'\[color=(red|green|yellow|blue|magenta|cyan|white)\](.*?)\[/color\]', 
                     lambda m: f"\033[{color_code(m.group(1))}m{m.group(2)}\033[0m", 
                     content)
    return content

def list_categories():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    
    # Fetch unique categories from the threads table
    c.execute('SELECT DISTINCT category FROM threads')
    categories = c.fetchall()
    
    if not categories:
        print("No categories found. Please create a thread to populate categories.")
        return []
    
    for idx, category in enumerate(categories):
        print(f"{idx+1}. {category[0]}")
    
    conn.close()
    return [category[0] for category in categories]

def view_threads(page=0):
    """List threads in a selected category with pagination and return the list of threads."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    categories = list_categories()
    if not categories:
        print("No categories available.")
        return []

    category_choice = int(input("Choose a category number: "))

    c.execute('SELECT id, title, locked FROM threads WHERE category = ?', 
              (categories[category_choice - 1],))
    threads = c.fetchall()

    if threads:
        num_pages = (len(threads) + PAGE_SIZE - 1) // PAGE_SIZE
        while True:
            print(f"\nThreads (Page {page + 1}/{num_pages})")
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            for idx, thread in enumerate(threads[start:end], start=1):
                lock_status = "[Locked]" if thread[2] == 1 else ""
                print(f"{start + idx}. {thread[1]} {lock_status}")

            # Pagination controls
            action = input("\nEnter thread number to view posts, 'n' for next page, 'p' for previous page, or 'q' to quit: ").lower()
            if action == 'n' and page < num_pages - 1:
                page += 1
            elif action == 'p' and page > 0:
                page -= 1
            elif action.isdigit() and int(action) <= len(threads):
                thread_id = threads[int(action) - 1][0]  # Get the thread ID
                view_thread_content(thread_id)  # Load posts in the selected thread
                break  # Exit after viewing the posts
            elif action == 'q':
                break
            else:
                print("Invalid choice, please try again.")
    else:
        print("No threads found.")

    conn.close()
    return threads  # Return the list of threads

def view_thread_content(thread_id, page=0):
    """Displays all posts in the selected thread with pagination and sorting options."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Ask user if they want to sort by oldest or newest first
    sort_order = input("Sort by (1) Oldest first or (2) Newest first? Enter 1 or 2: ")

    if sort_order == "1":
        order_by = "ASC"
    else:
        order_by = "DESC"

    # Fetch posts in the selected order
    c.execute(f'SELECT content, created_by, created_at FROM posts WHERE thread_id = ? ORDER BY created_at {order_by}', 
              (thread_id,))
    posts = c.fetchall()

    num_pages = (len(posts) + PAGE_SIZE - 1) // PAGE_SIZE

    if posts:
        while True:
            print(f"\n--- Posts in this thread (Page {page + 1}/{num_pages}) ---")
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE
            for idx, post in enumerate(posts[start:end], start=1):
                # Apply BBCode parsing before displaying the content
                formatted_content = bbcode_parser(post[0])
                print(f"Post {start + idx}: {formatted_content} (By User ID: {post[1]}, On: {post[2]})\n")

            # Pagination controls
            action = input("\n'n' for next page, 'p' for previous page, 'q' to quit viewing posts: ").lower()
            if action == 'n' and page < num_pages - 1:
                page += 1
            elif action == 'p' and page > 0:
                page -= 1
            elif action == 'q':
                break
            else:
                print("Invalid choice, please try again.")
    else:
        print("No posts in this thread yet.")

    conn.close()

def create_post_in_thread(thread_id, user_id):
    """Create a new post within a specific thread."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    content = input("Enter your post content (use '/roll XdY+Z' to roll dice): ")

    # Check for dice roll request using '/roll'
    if '/roll' in content:
        dice_expression = input("Enter your dice expression (e.g., 2d6+3): ")
        result, timestamp = roll_dice(dice_expression)
        if result is not None:
            content += f"\n[DICE ROLL: {dice_expression} = {result} at {timestamp}]"
        else:
            print("Invalid dice roll expression. Skipping dice roll.")

    c.execute('INSERT INTO posts (thread_id, content, created_by) VALUES (?, ?, ?)', 
              (thread_id, content, user_id))
    conn.commit()
    conn.close()
    print("Post created successfully!")

def create_thread(user_id):
    """Create a new thread with an initial post and optional dice roll."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    categories = list_categories()
    if not categories:
        print("No categories available. Please create a category first.")
        return

    category_choice = int(input("Choose a category number: "))

    title = input("Enter the new thread title: ")
    content = input("Enter the first post content (use '/roll XdY+Z' to roll dice): ")

    # Check for dice roll using '/roll'
    if '/roll' in content:
        dice_expression = input("Enter your dice expression (e.g., 2d6+3): ")
        result, timestamp = roll_dice(dice_expression)
        if result is not None:
            content += f"\n[DICE ROLL: {dice_expression} = {result} at {timestamp}]"
        else:
            print("Invalid dice roll expression. Skipping dice roll.")

    c.execute('INSERT INTO threads (category, title, created_by) VALUES (?, ?, ?)', 
              (categories[category_choice - 1], title, user_id))
    thread_id = c.lastrowid

    # Insert the first post in the thread
    c.execute('INSERT INTO posts (thread_id, content, created_by) VALUES (?, ?, ?)', 
              (thread_id, content, user_id))
    
    conn.commit()
    conn.close()
    print("Thread created successfully!")

def reply_to_thread(user_id):
    """Reply to an existing thread with optional dice roll."""
    threads = view_threads()  # Display threads and return the list of threads

    if threads:  # Check if threads were returned
        thread_choice = int(input("Choose a thread number: "))

        # Ensure the chosen number corresponds to the correct thread ID
        thread_id = threads[thread_choice - 1][0]  # Get the thread ID from the selected index

        # Check if the thread is locked
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute('SELECT locked FROM threads WHERE id = ?', (thread_id,))
        is_locked = c.fetchone()[0]
        conn.close()
        
        if is_locked == 1:
            print("This thread is locked and cannot be replied to.")
            return

        create_post_in_thread(thread_id, user_id)
        print("Reply posted successfully!")
    else:
        print("No threads available to reply to.")
    
    # Ensure the function completes and control returns to the main menu
    return

def edit_post(user_id):
    """Edit an existing post."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    post_id = int(input("Enter the ID of the post you want to edit: "))

    # Fetch the post's author to ensure only the author can edit it
    c.execute('SELECT created_by FROM posts WHERE id = ?', (post_id,))
    post_owner = c.fetchone()

    if post_owner and post_owner[0] == user_id:
        new_content = input("Enter the new content for your post: ")
        c.execute('UPDATE posts SET content = ?, edited_at = CURRENT_TIMESTAMP WHERE id = ?', 
                  (new_content, post_id))
        conn.commit()
        print("Post edited successfully.")
    else:
        print("You do not have permission to edit this post or the post does not exist.")

    conn.close()

def lock_thread(user_id):
    """Lock or unlock a thread, GM only."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check if the user is a GM
    c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = c.fetchone()[0]
    
    if user_role != 'gm':
        print("Only the GM can lock or unlock threads.")
        conn.close()
        return

    threads = view_threads()  # Display threads and return the list of threads
    if threads:  # Check if threads were returned
        thread_choice = int(input("Choose a thread number to lock/unlock: "))
        thread_id = threads[thread_choice - 1][0]  # Get the thread ID from the selected index

        # Check if the thread is currently locked
        c.execute('SELECT locked FROM threads WHERE id = ?', (thread_id,))
        is_locked = c.fetchone()[0]

        # Toggle lock status
        new_lock_status = 0 if is_locked else 1
        c.execute('UPDATE threads SET locked = ? WHERE id = ?', (new_lock_status, thread_id))
        conn.commit()
        status = "locked" if new_lock_status == 1 else "unlocked"
        print(f"Thread {thread_id} has been {status}.")
    else:
        print("No threads available to lock/unlock.")

    conn.close()
