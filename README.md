
# Terminal-Based BBS System for Tabletop RPGs

## Overview

This system is a terminal-based **Bulletin Board System (BBS)** designed specifically for **tabletop RPGs**. It provides users with the ability to interact in text-based forums, manage characters and NPCs, send private messages, roll dice, and even post ANSI/ASCII images. This system is ideal for local hosting and can be used for offline interactions (e.g., over ham radio).

It features **authentication and access control**, where only the GM (Game Master) can manage specific aspects such as NPC creation and thread locking, while all users are free to post in threads and manage their own characters.

### Key Features
- **Thread Management**: Users can view and create posts in threads that are organized under categories, while only the GM can create new categories and lock threads.
- **Private Messaging**: Users can send and receive private messages.
- **Character and NPC Management**: Users can manage characters with customizable attributes (e.g., hit dice, saving throws), while the GM can exclusively manage NPCs.
- **Dice Roller**: Users can roll multi-sided dice (d4 to d100) with or without modifiers.
- **GM Access Control**: The GM sets a password that restricts certain operations such as posting replies, sending private messages, and accessing the inbox.
- **Image Posting**: Supports ANSI and ASCII image posting using the `/pic` command.
- **Custom Install Script**: Automates the setup of the system, including user creation, character/NPC fields, and database table creation.

---

## Table of Contents

1. [Installation Instructions](#installation-instructions)
2. [File Descriptions](#file-descriptions)
   - `bbs_auth.py`
   - `bbs_database.py`
   - `bbs_dice_roller.py`
   - `bbs_image_converter.py`
   - `bbs_main.py`
   - `bbs_message_board.py`
   - `bbs_private_messages.py`
   - `character_npc_manager.py`
   - `install.py`
3. [Usage Instructions](#usage-instructions)
4. [Program Workflow](#program-workflow)
5. [Advanced Configuration](#advanced-configuration)
6. [Customization](#customization)
7. [Known Issues](#known-issues)
8. [Future Features](#future-features)
9. [Contributing](#contributing)
10. [License](#license)

---

## Installation Instructions

### Prerequisites

Ensure you have the following installed:
- **Python**: Version 3.6 or later.
- **SQLite**: For database management.
- **Terminal**: Any terminal emulator that supports UTF-8 encoding for ANSI/ASCII art.

### Steps to Install

1. **Clone or Download the Repository**:
   Clone this repository using Git, or download it as a ZIP file and extract it to your local machine.

   ```bash
   git clone https://github.com/ve7kfx/RPG_BBS.git
   cd RPG_BBS
   ```

2. **Run the Installation Script**:
   Navigate to the directory where the `install.py` script is located and run it. This will initialize the database, create tables, and guide you through creating the GM account and configuring the RPG system.

   ```bash
   python install.py
   ```

   During installation, you will:
   - Set up the GM (Game Master) account.
   - Create thread categories.
   - Set character/NPC attributes such as health, armor class, hit dice, saving throws, etc.
   - Define the GM password that will restrict certain actions in the system.

3. **Start the BBS**:
   Once the installation is complete, you can start the BBS by running the main script.

   ```bash
   python bbs_main.py
   ```

---

## File Descriptions

Here’s an in-depth look at each file in the system:

### 1. `bbs_auth.py`
This module handles user authentication and password management. It includes functionality to:
- Create user accounts during installation.
- Log in users with username and password.
- Authenticate the GM with a special GM password for restricted access to specific actions.

### 2. `bbs_database.py`
Handles all database operations for the system, including creating tables for:
- Users
- Threads and Posts
- Private Messages
- Characters and NPCs

This file provides SQL queries for inserting, updating, and deleting data, ensuring smooth interaction between the BBS and the underlying SQLite database.

### 3. `bbs_dice_roller.py`
Implements the dice-rolling functionality. Users can roll various types of dice:
- d4, d6, d8, d10, d12, d20, and d100
- Add modifiers to dice rolls (e.g., rolling 2d6+3)

The results of dice rolls are displayed with timestamps, ensuring accurate tracking during RPG sessions.

### 4. `bbs_image_converter.py`
This module allows users to post ANSI or ASCII images in threads by converting standard images into text-based formats. When users type `/pic` in their posts, this module processes the image and displays it in the thread.

It supports:
- **ANSI Art**: Colorful, retro-style graphics.
- **ASCII Art**: Simplified monochrome images.

### 5. `bbs_main.py`
The main entry point for the BBS system. It handles:
- User login and authentication
- Main menu navigation (view threads, post, private messaging, dice roller, character management)
- GM control over restricted areas (e.g., replying to threads, sending private messages)

This module acts as the core interface between the user and the other system components.

### 6. `bbs_message_board.py`
This module handles the forum-like message board. Users can:
- View and post in existing threads.
- Only the GM can create new categories and lock threads.
- All users can create posts under unlocked threads.

It dynamically reads from the database to populate the message board with existing threads and posts.

### 7. `bbs_private_messages.py`
Manages user-to-user communication via private messages. Users can:
- Send private messages to other users.
- Receive and view messages in their inbox.
  
The GM controls access to private messages by using a password to unlock the inbox.

### 8. `character_npc_manager.py`
This module provides functionality for managing characters and NPCs. Features include:
- Creating and managing RPG characters with attributes like health, armor class, hit dice, and saving throws.
- Only the GM can create and manage NPCs.
- Characters and NPCs are stored in a dedicated SQLite table for easy retrieval and updates.

### 9. `install.py`
The installation script that initializes the system. It:
- Creates the GM account.
- Configures the database with default tables and values.
- Sets up character/NPC attributes.
- Prompts for a GM password for securing restricted actions.

This script must be run before using the BBS system.

---

## Usage Instructions

### Logging In
- **GM**: Logs in with the GM username and password created during installation.
- **Users**: Other users log in with their respective accounts.
  
### GM Functions
- Create new thread categories.
- Manage NPCs.
- Lock or unlock threads.
- Manage restricted menu items using the GM password.

### Regular User Functions
- Post in threads.
- Manage their own characters.
- Send and receive private messages.
- Roll dice with the dice roller.

### Dice Roller
To roll dice, select the dice roller option from the main menu. Specify the type of dice (e.g., d6, d20) and any modifiers to apply. The results are timestamped and stored.

### Posting Images
To include an ANSI or ASCII image in your post, type `/pic` followed by the file path or image details. The `bbs_image_converter.py` module will convert the image into text-based art and display it in the thread.

---

## Program Workflow

1. **Login Process**: User logs in using their credentials (GM has special access).
2. **Main Menu**: After logging in, the main menu displays options like viewing threads, posting, managing characters/NPCs, sending private messages, and rolling dice.
3. **Thread Interaction**: Users can browse threads, create posts, and reply (based on their access level).
4. **Private Messages**: Users can send private messages through the private messaging system.
5. **Character Management**: Users can create and edit their own characters, while the GM can manage NPCs.
6. **Dice Roller**: Users can roll dice for various in-game mechanics.

---

## Advanced Configuration

### Adding New Dice Types
To add new dice types, modify the `bbs_dice_roller.py` module. Add the desired dice type (e.g., d3, d50) by expanding the dice roll logic.

### Custom Character Attributes
You can customize the character/NPC attributes (e.g., special skills, equipment) by adding new fields in the `character_npc_manager.py` module and adjusting the database schema in `bbs_database.py`.

---

## Customization

This system is designed to be flexible for different RPG settings. Here are a few ways you can customize it:
- **Thread Categories**: Modify `bbs_message_board.py` to create additional categories or alter permissions.
- **Character Attributes**: Use `character_npc_manager.py` to add more detailed stats, inventory, or skills.
- **User Roles**: You can add new roles (e.g., co-GM, moderator) by modifying the `bbs_auth.py` and `bbs_database.py` files to assign different permissions.
