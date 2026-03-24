# gmail_reader.py (Updated - now with database tracking)
# This script connects to Gmail, fetches recent emails, and only processes
# emails it has never seen before. Processed email IDs are saved to the database.

# --- IMPORTS ---

import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from auth import get_gmail_credentials
from db import init_db, is_seen, mark_seen

# --- HELPER FUNCTION: Strip HTML tags ---

def strip_html(html_text):
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

# --- HELPER FUNCTION: Extract email body ---

def get_email_body(payload):
    body_text = ""

    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')

            if mime_type == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                    break

            elif mime_type == 'text/html' and not body_text:
                data = part['body'].get('data', '')
                if data:
                    html = base64.urlsafe_b64decode(data).decode('utf-8')
                    body_text = strip_html(html)

            elif mime_type.startswith('multipart/'):
                body_text = get_email_body(part)
                if body_text:
                    break
    else:
        data = payload.get('body', {}).get('data', '')
        if data:
            body_text = base64.urlsafe_b64decode(data).decode('utf-8')

    return body_text.strip()

# --- MAIN FUNCTION: Fetch and process emails ---

def fetch_emails():

    print("Initialising database...")
    init_db()

    print("Connecting to Gmail...")
    creds = get_gmail_credentials()

    # ✏️ CHANGE 1: We now build a list to collect new emails
    # and return it at the end so main.py can pass it to summariser.py
    new_emails = []

    try:
        service = build('gmail', 'v1', credentials=creds)
        print("Connected! Fetching emails...\n")

        results = service.users().messages().list(
            userId='me',
            maxResults=20,
            labelIds=['INBOX']
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            print("No emails found in inbox.")
            return []
            # ✏️ CHANGE 2: Return empty list instead of just returning None
            # This means main.py always gets a list back, never None

        print(f"Found {len(messages)} emails. Checking for new ones...\n")

        new_count = 0
        skipped_count = 0

        for i, message in enumerate(messages, start=1):

            email_id = message['id']

            if is_seen(email_id):
                skipped_count += 1
                print(f"[{i}] SKIPPED (already seen): {email_id}")
                continue

            msg = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()

            headers = msg['payload']['headers']

            subject = next(
                (h['value'] for h in headers if h['name'] == 'Subject'),
                'No Subject'
            )
            sender = next(
                (h['value'] for h in headers if h['name'] == 'From'),
                'Unknown Sender'
            )
            date = next(
                (h['value'] for h in headers if h['name'] == 'Date'),
                'Unknown Date'
            )

            body = get_email_body(msg['payload'])

            if not body:
                body = "[No readable body content]"

            print("=" * 60)
            print(f"EMAIL {i} of {len(messages)}  [NEW]")
            print(f"ID      : {email_id}")
            print(f"From    : {sender}")
            print(f"Date    : {date}")
            print(f"Subject : {subject}")
            print(f"Body    :\n{body[:500]}")
            print("=" * 60)

            mark_seen(email_id)
            new_count += 1

            # ✏️ CHANGE 3: Add the email as a dictionary to our list
            # This is the format summariser.py expects
            new_emails.append({
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body
            })

        print(f"\nDone! {new_count} new emails processed, {skipped_count} already seen emails skipped.")

        # ✏️ CHANGE 4: Return the collected emails list
        return new_emails

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
        # Return empty list on error so main.py doesn't crash