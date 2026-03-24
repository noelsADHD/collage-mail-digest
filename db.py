# db.py
# This module handles all database operations for our email digest bot.
# It creates a local SQLite database to track which emails have been processed.

# --- IMPORTS ---

import sqlite3
# sqlite3 is Python's built-in library for working with SQLite databases.
# No installation needed — it comes with Python by default.

# --- CONFIGURATION ---

DB_FILE = 'seen_emails.db'
# This is the name of our database file.
# SQLite stores the entire database as a single file on your computer.
# It will be created automatically in your project folder when we first connect.

# --- FUNCTION: Initialise the database ---

def init_db():
    # This function creates the database file and the table inside it.
    # A table is like a spreadsheet — it has columns and rows.
    # We call this function once at the start of our program.

    conn = sqlite3.connect(DB_FILE)
    # Connect to the database file.
    # If the file doesn't exist yet, SQLite creates it automatically.
    # 'conn' is our connection object — our link to the database.

    cursor = conn.cursor()
    # A cursor is like a pen that writes to and reads from the database.
    # We use it to execute SQL commands.

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seen_emails (
            id TEXT PRIMARY KEY
        )
    ''')
    # Execute a SQL command to create our table.
    # SQL (Structured Query Language) is the language databases understand.
    # Breaking down this command:
    #   CREATE TABLE IF NOT EXISTS — only create if it doesn't already exist.
    #   seen_emails — the name of our table.
    #   id TEXT PRIMARY KEY — one column called 'id' that stores text.
    #   PRIMARY KEY means each value must be unique — no duplicate email IDs allowed.

    conn.commit()
    # 'commit' saves the changes permanently to the database file.
    # Without this, changes exist only in memory and are lost when the program ends.

    conn.close()
    # Close the connection when we're done.
    # Always close connections to avoid memory leaks and file locking issues.

# --- FUNCTION: Check if an email has been seen ---

def is_seen(email_id):
    # This function checks if a given email ID is already in our database.
    # It returns True if we've seen this email before, False if we haven't.
    # 'email_id' is the parameter — the ID we want to check.

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Open a fresh connection and cursor for this operation.

    cursor.execute('SELECT id FROM seen_emails WHERE id = ?', (email_id,))
    # Execute a SQL SELECT command to look for this email ID in the table.
    # SELECT id FROM seen_emails — look in our table for the 'id' column.
    # WHERE id = ? — only return rows where the id matches our value.
    # The '?' is a placeholder — we pass the actual value separately as (email_id,)
    # This is called a parameterised query and prevents SQL injection attacks.
    # The comma after email_id makes it a tuple — SQLite requires this format.

    result = cursor.fetchone()
    # fetchone() retrieves the first matching row.
    # If the email ID exists, result will be a tuple like ('19cf641f87892ae1',)
    # If it doesn't exist, result will be None.

    conn.close()
    # Close the connection.

    return result is not None
    # Return True if we found a result (email was seen before).
    # Return False if result is None (email is new).

# --- FUNCTION: Mark an email as seen ---

def mark_seen(email_id):
    # This function saves a new email ID to the database.
    # We call this after successfully processing an email.
    # 'email_id' is the ID we want to save.

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO seen_emails (id) VALUES (?)', (email_id,))
    # Execute a SQL INSERT command to add this email ID to our table.
    # INSERT INTO seen_emails (id) VALUES (?) — add a new row with this ID.
    # OR IGNORE means if this ID already exists, do nothing instead of crashing.
    # This is a safety net in case we accidentally try to insert a duplicate.

    conn.commit()
    # Save the change permanently.

    conn.close()
    # Close the connection.

# --- MAIN BLOCK: Test the database ---

if __name__ == '__main__':
    # This block only runs when we execute db.py directly.
    # We use it to test that everything works correctly.

    print("Initialising database...")
    init_db()
    print(f"Database created: {DB_FILE}")

    # Test: insert a fake email ID and check if it's found
    test_id = "test_email_123"

    print(f"\nChecking if '{test_id}' is in database...")
    print(f"Result: {is_seen(test_id)}")
    # Should print False — we haven't added it yet.

    print(f"\nMarking '{test_id}' as seen...")
    mark_seen(test_id)

    print(f"\nChecking again if '{test_id}' is in database...")
    print(f"Result: {is_seen(test_id)}")
    # Should print True — we just added it.

    print("\nDatabase module working correctly!")
