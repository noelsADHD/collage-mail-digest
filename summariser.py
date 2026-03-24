# summariser.py
# This module takes a list of emails, sends them to Gemini,
# and returns a clean formatted digest string.

# --- IMPORTS ---

import os
import json
# json is a built-in Python library for working with JSON data.
# We use it to parse Gemini's response into a Python dictionary.

from dotenv import load_dotenv
# Loads our .env file so we can access GEMINI_API_KEY

from google import genai
# The Google GenAI SDK for talking to Gemini

# --- LOAD ENVIRONMENT VARIABLES ---

load_dotenv()
# Must be called before os.getenv() or the key won't be found

# --- CONSTANTS ---

GEMINI_MODEL = "gemini-2.5-flash"
# We define the model name once here at the top.
# If Google changes model names again, we only update one line.

# --- THE SYSTEM PROMPT ---
# This is the instruction set we send to Gemini before giving it the emails.
# It tells Gemini exactly how to behave and what format to return.

SYSTEM_PROMPT = """You are a college email assistant. Your job is to read a batch of 
emails and extract only the important information for a student.

You must return ONLY a valid JSON object. No explanation, no 
preamble, no markdown code blocks. Just raw JSON.

The JSON must have exactly these four keys:
- "deadlines": list of strings about assignments, submissions, exams, due dates
- "clubs": list of strings about club events, society meetings, extracurriculars  
- "admin": list of strings about admin notices, fee payments, college policies, 
           timetable changes, official announcements
- "general": list of strings about anything else worth knowing

Rules you must follow:
1. Each bullet point must be under 20 words
2. Include the date or deadline if mentioned in the email
3. Ignore promotional emails, newsletters, and spam
4. If a category has no relevant emails, return an empty list [] for it
5. Do not repeat the same information across categories
6. Do not make up or infer information not present in the emails"""

# --- HELPER FUNCTION: FORMAT EMAILS FOR THE PROMPT ---

def format_emails_for_prompt(emails):
    # This function takes our list of email dictionaries and converts them
    # into a single readable text block we can paste into the prompt.
    # 
    # Input: a list like [{"subject": "...", "sender": "...", "date": "...", "body": "..."}, ...]
    # Output: a single formatted string with all emails listed clearly

    if not emails:
        # If the list is empty, return a message saying so.
        # This prevents us from sending a blank prompt to Gemini.
        return "No emails to summarise."

    formatted = ""
    # Start with an empty string and build it up

    for i, email in enumerate(emails, start=1):
        # enumerate() gives us a counter (i) alongside each email.
        # start=1 means we count from 1 instead of 0 — more readable.

        formatted += f"""
--- EMAIL {i} ---
Subject: {email.get('subject', 'No Subject')}
From: {email.get('sender', 'Unknown')}
Date: {email.get('date', 'Unknown')}
Body:
{email.get('body', 'No content')}
"""
        # email.get('subject', 'No Subject') safely gets the value.
        # If the key doesn't exist, it returns the default instead of crashing.

    return formatted
    # Returns the full block of all emails as one string

# --- MAIN FUNCTION: SUMMARISE EMAILS ---

def summarise_emails(emails):
    # This is the main function other scripts will call.
    # Input: list of email dictionaries
    # Output: a formatted digest string ready to print or send

    # Step 1: Check we actually have emails to process
    if not emails:
        return "📭 No new emails to summarise."

    # Step 2: Get the API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # If the key is missing, stop and explain clearly
        raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

    # Step 3: Set up the Gemini client
    client = genai.Client(api_key=api_key)

    # Step 4: Format the emails into a text block
    emails_text = format_emails_for_prompt(emails)

    # Step 5: Build the full prompt
    # We combine the system instructions with the actual email content
    full_prompt = f"""{SYSTEM_PROMPT}

Here are the emails to process:

{emails_text}"""

    # Step 6: Call the Gemini API
    print(f"📤 Sending {len(emails)} email(s) to Gemini for summarisation...")

    try:
        # try/except means: attempt the code inside try, and if anything
        # goes wrong, run the code inside except instead of crashing.

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt
            # We send the full prompt as the user message.
            # It contains both the instructions and the email data.
        )

        raw_response = response.text
        # Extract just the text from the response object

        print("📥 Response received from Gemini.")

    except Exception as e:
        # If the API call fails for any reason (network error, quota, etc.)
        # we catch the error and return a friendly message instead of crashing.
        return f"❌ Gemini API call failed: {str(e)}"

    # Step 7: Parse the JSON response
    try:
        # Gemini sometimes wraps JSON in ```json ``` markdown blocks
        # even when we tell it not to. This cleaning step handles that.
        cleaned = raw_response.strip()
        # strip() removes leading and trailing whitespace/newlines

        if cleaned.startswith("```"):
            # If it starts with backticks, remove the first and last lines
            lines = cleaned.split("\n")
            # Split the text into individual lines
            cleaned = "\n".join(lines[1:-1])
            # Rejoin everything except the first and last line (the ``` lines)

        digest_data = json.loads(cleaned)
        # json.loads() converts a JSON string into a Python dictionary.
        # After this line, digest_data is like:
        # {"deadlines": [...], "clubs": [...], "admin": [...], "general": [...]}

    except json.JSONDecodeError:
        # If the JSON parsing fails (Gemini returned something unexpected),
        # return the raw response so we can see what happened
        return f"⚠️ Could not parse Gemini response as JSON.\nRaw response:\n{raw_response}"

    # Step 8: Format the parsed data into a readable digest
    return format_digest(digest_data)
    # We call format_digest() to turn the dictionary into a nice message


# --- FORMATTING FUNCTION ---

def format_digest(data):
    # This function takes the parsed JSON dictionary and turns it into
    # a human-readable message with clear headers and bullet points.
    #
    # Input: {"deadlines": [...], "clubs": [...], "admin": [...], "general": [...]}
    # Output: a nicely formatted string

    lines = []
    # We build the message as a list of lines, then join them at the end.
    # This is cleaner than concatenating strings one by one.

    lines.append("📬 YOUR COLLEGE EMAIL DIGEST")
    lines.append("=" * 32)
    # "=" * 32 creates a divider line like: ================================

    # Define the four sections with their emoji, key name, and display title
    sections = [
        ("⏰", "deadlines", "DEADLINES & ASSIGNMENTS"),
        ("�club", "clubs",     "CLUB ANNOUNCEMENTS"),
        ("🏫", "admin",     "ADMIN NOTICES"),
        ("ℹ️",  "general",   "GENERAL INFO"),
    ]

    for emoji, key, title in sections:
        # Loop through each section definition

        items = data.get(key, [])
        # Get the list for this category from the dictionary.
        # If the key doesn't exist for some reason, default to empty list.

        lines.append(f"\n{emoji} {title}")
        lines.append("-" * 28)
        # Add the section header and a divider line

        if items:
            for item in items:
                lines.append(f"  • {item}")
                # Add each bullet point with a bullet character and indent
        else:
            lines.append("  Nothing to report.")
            # If the list is empty, say so clearly

    lines.append("\n" + "=" * 32)
    lines.append("End of digest.")

    return "\n".join(lines)
    # Join all lines with newline characters into one final string


# --- TEST BLOCK ---
# This only runs when you execute summariser.py directly.
# It will NOT run when main.py imports this file.

if __name__ == "__main__":

    # Create some fake test emails to verify everything works
    test_emails = [
        {
            "subject": "Assignment 2 Due Friday",
            "sender": "professor@college.edu",
            "date": "2026-03-22",
            "body": "Dear students, please submit Assignment 2 by Friday 22nd March at 5pm via the portal."
        },
        {
            "subject": "Photography Club Meeting",
            "sender": "photoclub@college.edu",
            "date": "2026-03-22",
            "body": "Hi everyone, our next meeting is on Thursday at 4pm in Room B12. We will be reviewing entries for the competition."
        },
        {
            "subject": "Library Closure Notice",
            "sender": "admin@college.edu",
            "date": "2026-03-22",
            "body": "Please note the library will be closed on Monday 25th March for maintenance. Plan accordingly."
        }
    ]

    print("Testing summariser with 3 fake emails...\n")
    result = summarise_emails(test_emails)
    print(result)