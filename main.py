# main.py
# This is the entry point for the entire application.
# It connects Phase 1 (Gmail fetching) and Phase 2 (AI summarisation).
# Run this file to get your email digest printed to the terminal.

# --- IMPORTS ---

from gmail_reader import fetch_emails
# Import the fetch_emails function from our Phase 1 gmail_reader module.
# This will connect to Gmail and return a list of new unseen emails.

from summariser import summarise_emails
# Import the summarise_emails function from our Phase 2 summariser module.
# This will send the emails to Gemini and return a formatted digest string.

# --- MAIN FUNCTION ---

def main():
    print("=" * 60)
    print("   COLLEGE MAIL DIGEST BOT - Starting up...")
    print("=" * 60)
    print()

    # --- STEP 1: Fetch new emails from Gmail ---
    print("STEP 1: Fetching emails from Gmail...")
    print("-" * 40)

    emails = fetch_emails()
    # fetch_emails() returns a list of email dictionaries.
    # Each dictionary has: subject, sender, date, body
    # If there are no new emails, it returns an empty list []

    print()

    # --- STEP 2: Check if we got any new emails ---
    if not emails:
        # If the list is empty, there's nothing to summarise.
        # Print a friendly message and exit cleanly.
        print("=" * 60)
        print("📭 No new emails found. Nothing to summarise.")
        print("   Run again later when new emails arrive.")
        print("=" * 60)
        return
        # 'return' exits the main() function here — nothing more to do

    print(f"✅ {len(emails)} new email(s) ready for summarisation.")
    print()

    # --- STEP 3: Send emails to Gemini for summarisation ---
    print("STEP 2: Sending emails to Gemini AI for summarisation...")
    print("-" * 40)

    digest = summarise_emails(emails)
    # summarise_emails() takes our list of email dictionaries,
    # sends them to Gemini, parses the JSON response,
    # and returns a clean formatted digest string.

    print()

    # --- STEP 4: Print the final digest ---
    print("STEP 3: Here is your digest:")
    print("-" * 40)
    print()
    print(digest)
    # Print the final formatted digest to the terminal.
    # Phase 3 will send this to Telegram/WhatsApp instead.

    print()
    print("=" * 60)
    print("✅ Digest complete!")
    print("=" * 60)

# --- ENTRY POINT ---
if __name__ == "__main__":
    main()
    # This means: only run main() when this file is executed directly.
    # If another script imports main.py, this block won't run.