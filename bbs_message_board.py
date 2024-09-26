import sqlite3
from bbs_dice_roller import roll_dice
import re  # Needed for BBCode parsing
import bbs_image_converter  # Import the image conversion program

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

def list_categories(gm_only=False):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    c.execute('SELECT DISTINCT category FROM threads')
    categories = c.fetchall()

    if not categories and gm_only:
        print("No categories found. GM, please create a category to get started.")
        return []

    if not categories:
        print("No categories found.")
        return []

    for idx, category in enumerate(categories):
        print(f"{idx+1}. {category[0]}")

    conn.close()
    return [category[0] for category in categories]

def create_category(user_id):
    """Allow only the GM to create categories."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check if the user is a GM
    c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = c.fetchone()[0]

    if user_role != 'gm':
        print("Only the GM can create categories.")
        conn.close()
        return

    category_name = input("Enter the new category name: ")
    
    c.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
    conn.commit()
    conn.close()
    print("Category created successfully!")

def view_threads(user_id, page=0):
    """List threads in a selected category with pagination and allow post creation."""
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

            action = input("\nEnter thread number to view posts, 'n' for next page, 'p' for previous page, 'c' to create a post, or 'q' to quit: ").lower()
            if action == 'n' and page < num_pages - 1:
                page += 1
            elif action == 'p' and page > 0:
                page -= 1
            elif action.isdigit() and int(action) <= len(threads):
                thread_id = threads[int(action) - 1][0]  # Get the thread ID
                view_thread_content(thread_id, user_id)  # Pass user_id to view_thread_content
                break  # Exit after viewing the posts
            elif action == 'c':  # Create a post in the selected thread
                thread_id = threads[int(input("Choose a thread number: ")) - 1][0]
                create_post_in_thread(thread_id, user_id)
                break
            elif action == 'q':
                break
            else:
                print("Invalid choice, please try again.")
    else:
        print("No threads found.")
    
    conn.close()
    return threads  # Return the list of threads

def view_thread_content(thread_id, user_id, page=0):
    """Displays all posts in the selected thread with pagination, post creation, and return to main menu."""
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
            action = input("\n'n' for next page, 'p' for previous page, 'c' to create a post, 'q' to quit viewing posts: ").lower()
            if action == 'n' and page < num_pages - 1:
                page += 1
            elif action == 'p' and page > 0:
                page -= 1
            elif action == 'c':  # Add logic to create a post in this thread
                create_post_in_thread(thread_id, user_id)
                print("\nReturning to thread view...\n")
            elif action == 'q':
                print("Returning to the main menu...")
                break
            else:
                print("Invalid choice, please try again.")
    else:
        print("No posts in this thread yet.")
        # Allow users to create a post if no posts exist
        action = input("\nWould you like to create the first post in this thread? (y/n): ").lower()
        if action == 'y':
            create_post_in_thread(thread_id, user_id)
        print("Returning to the main menu...")

    conn.close()

def create_post_in_thread(thread_id, user_id):
    """Allow all users to create a post in a specific thread."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    content = input("Enter your post content (use '/roll' to roll dice or '/pic <image_path>' to include an image): ")

    # Check for dice roll request using '/roll'
    if '/roll' in content:
        dice_expression = input("Enter your dice expression (e.g., 2d6+3): ")
        result, timestamp = roll_dice(dice_expression)
        if result is not None:
            content += f"\n[DICE ROLL: {dice_expression} = {result} at {timestamp}]"
        else:
            print("Invalid dice roll expression. Skipping dice roll.")

    # Check for /pic in the post content and call the image conversion module
    content = bbs_image_converter.bbcode_parser_with_pic(content)

    c.execute('INSERT INTO posts (thread_id, content, created_by) VALUES (?, ?, ?)', 
              (thread_id, content, user_id))
    conn.commit()
    conn.close()
    print("Post created successfully with image if /pic was used!")

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
    content = input("Enter the first post content (use '/roll' to roll dice or '/pic <image_path>' to include an image): ")

    # Check for dice roll using '/roll'
    if '/roll' in content:
        dice_expression = input("Enter your dice expression (e.g., 2d6+3): ")
        result, timestamp = roll_dice(dice_expression)
        if result is not None:
            content += f"\n[DICE ROLL: {dice_expression} = {result} at {timestamp}]"
        else:
            print("Invalid dice roll expression. Skipping dice roll.")

    # Check for /pic in the post content and call the image conversion module
    content = bbs_image_converter.bbcode_parser_with_pic(content)

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
    threads = view_threads(user_id)  # Display threads and return the list of threads

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
    
    return

import sqlite3

def ensure_locked_and_edited_at_columns():
    """Ensure that the 'locked' and 'edited_at' columns exist in the 'posts' table."""
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check and add 'locked' column to 'posts' table if it doesn't exist
    try:
        c.execute('SELECT locked FROM posts LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE posts ADD COLUMN locked INTEGER DEFAULT 0')
        print("Added 'locked' column to 'posts' table.")

    # Check and add 'edited_at' column to 'posts' table if it doesn't exist
    try:
        c.execute('SELECT edited_at FROM posts LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE posts ADD COLUMN edited_at TIMESTAMP')
        print("Added 'edited_at' column to 'posts' table.")

    conn.commit()
    conn.close()

def edit_post(user_id):
    """Edit an existing post, with pagination showing 5 most recent posts at a time. GMs can lock/unlock posts."""

    # Ensure 'locked' and 'edited_at' columns exist in the 'posts' table
    ensure_locked_and_edited_at_columns()

    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check if the user is a GM
    c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = c.fetchone()[0]
    is_gm = (user_role == 'gm')

    # Fetch total number of posts by the user
    c.execute('SELECT id, content, created_at, locked FROM posts ORDER BY created_at DESC')
    posts = c.fetchall()

    if not posts:
        print("There are no posts to edit.")
        conn.close()
        return

    PAGE_SIZE = 5
    num_pages = (len(posts) + PAGE_SIZE - 1) // PAGE_SIZE
    page = 0

    while True:
        print(f"\n--- Posts (Page {page + 1}/{num_pages}) ---")
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        for idx, post in enumerate(posts[start:end], start=1):
            lock_status = "[Locked]" if post[3] == 1 else "[Unlocked]"
            print(f"{start + idx}. Post ID: {post[0]} | Created At: {post[2]} {lock_status}\nContent: {post[1]}\n")

        # Pagination controls and options for editing/locking posts
        action = input("\n'n' for next page, 'p' for previous page, 'e' to edit a post, 'l' to lock/unlock (GM only), 'q' to quit: ").lower()

        if action == 'n' and page < num_pages - 1:
            page += 1
        elif action == 'p' and page > 0:
            page -= 1
        elif action == 'e':  # Edit post
            post_id = int(input("Enter the Post ID you want to edit: "))

            # Fetch the post's author to ensure only the author can edit it
            c.execute('SELECT created_by, locked FROM posts WHERE id = ?', (post_id,))
            post_info = c.fetchone()

            if post_info and post_info[0] == user_id and post_info[1] == 0:  # Check if post is not locked
                new_content = input("Enter the new content for your post (use '/roll' to roll dice or '/pic <image_path>' to include an image): ")

                # Check for dice roll command using '/roll'
                if '/roll' in new_content:
                    dice_expression = input("Enter your dice expression (e.g., 2d6+3): ")
                    result, timestamp = roll_dice(dice_expression)
                    if result is not None:
                        new_content += f"\n[DICE ROLL: {dice_expression} = {result} at {timestamp}]"
                    else:
                        print("Invalid dice roll expression. Skipping dice roll.")

                # Check for image command using '/pic <image_path>'
                new_content = bbs_image_converter.bbcode_parser_with_pic(new_content)

                # Update 'edited_at' field manually with the current timestamp
                c.execute('UPDATE posts SET content = ?, edited_at = CURRENT_TIMESTAMP WHERE id = ?', 
                          (new_content, post_id))
                conn.commit()
                print("Post edited successfully.")
            elif post_info[1] == 1:
                print("This post is locked and cannot be edited.")
            else:
                print("You do not have permission to edit this post or the post does not exist.")
        elif action == 'l' and is_gm:  # Lock or unlock a post if GM
            post_id = int(input("Enter the Post ID you want to lock/unlock: "))

            # Fetch current lock status
            c.execute('SELECT locked FROM posts WHERE id = ?', (post_id,))
            lock_status = c.fetchone()

            if lock_status is not None:
                new_lock_status = 0 if lock_status[0] == 1 else 1
                c.execute('UPDATE posts SET locked = ? WHERE id = ?', (new_lock_status, post_id))
                conn.commit()
                status = "locked" if new_lock_status == 1 else "unlocked"
                print(f"Post {post_id} has been {status}.")
            else:
                print("Post not found.")
        elif action == 'q':  # Quit editing
            print("Returning to the previous menu...")
            break
        else:
            print("Invalid choice, please try again.")

    conn.close()

def lock_thread(user_id):
    """Lock or unlock a thread, GM only, with pagination to list all threads in a given category."""
    
    # Ensure 'locked' column exists in the 'threads' table
    def ensure_locked_column_for_threads():
        """Ensure that the 'locked' column exists in the 'threads' table."""
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()

        # Check and add 'locked' column to 'threads' table if it doesn't exist
        try:
            c.execute('SELECT locked FROM threads LIMIT 1')
        except sqlite3.OperationalError:
            c.execute('ALTER TABLE threads ADD COLUMN locked INTEGER DEFAULT 0')
            print("Added 'locked' column to 'threads' table.")

        conn.commit()
        conn.close()

    # Call the function to ensure 'locked' column is present in threads
    ensure_locked_column_for_threads()

    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()

    # Check if the user is a GM
    c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = c.fetchone()[0]

    if user_role != 'gm':
        print("Only the GM can lock or unlock threads.")
        conn.close()
        return

    # List categories and allow the GM to select one
    categories = list_categories(gm_only=True)
    if not categories:
        print("No categories available.")
        conn.close()
        return

    category_choice = int(input("Choose a category number to view threads: "))

    # Fetch threads in the selected category
    c.execute('SELECT id, title, locked FROM threads WHERE category = ?', (categories[category_choice - 1],))
    threads = c.fetchall()

    if not threads:
        print("No threads available in this category.")
        conn.close()
        return

    PAGE_SIZE = 5
    num_pages = (len(threads) + PAGE_SIZE - 1) // PAGE_SIZE
    page = 0

    while True:
        print(f"\n--- Threads in Category '{categories[category_choice - 1]}' (Page {page + 1}/{num_pages}) ---")
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        for idx, thread in enumerate(threads[start:end], start=1):
            lock_status = "[Locked]" if thread[2] == 1 else "[Unlocked]"
            print(f"{start + idx}. Thread ID: {thread[0]} | Title: {thread[1]} {lock_status}")

        # Pagination controls and lock/unlock options
        action = input("\n'n' for next page, 'p' for previous page, 'l' to lock/unlock a thread, 'q' to quit: ").lower()

        if action == 'n' and page < num_pages - 1:
            page += 1
        elif action == 'p' and page > 0:
            page -= 1
        elif action == 'l':  # Lock or unlock a thread
            thread_choice = int(input("Enter the thread number to lock/unlock: "))
            thread_id = threads[thread_choice - 1][0]  # Get the thread ID from the selected index

            # Check if the thread is currently locked
            c.execute('SELECT locked FROM threads WHERE id = ?', (thread_id,))
            is_locked = c.fetchone()[0]

            # Toggle lock status
            new_lock_status = 0 if is_locked else 1
            c.execute('UPDATE threads SET locked = ? WHERE id = ?', (new_lock_status, thread_id))
            conn.commit()
            status = "locked" if new_lock_status == 1 else "unlocked"
            print(f"Thread '{threads[thread_choice - 1][1]}' has been {status}.")
        elif action == 'q':
            print("Returning to the previous menu...")
            break
        else:
            print("Invalid choice, please try again.")

    conn.close()
