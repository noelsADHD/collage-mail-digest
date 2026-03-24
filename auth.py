# auth.py
# This script handles the one-time Gmail login and saves a token for future use.

# --- IMPORTS ---
# We import the tools (libraries) our script needs to work.

import os
# 'os' is a built-in Python library that lets us interact with the operating system.
# We use it here to check if files exist on your computer.

from google.auth.transport.requests import Request
# 'Request' is used to make HTTP requests to Google's servers.
# When our token expires, this is used to automatically refresh it.

from google.oauth2.credentials import Credentials
# 'Credentials' is an object that holds our authentication token.
# Think of it as a container for the access pass Google gives us.

from google_auth_oauthlib.flow import InstalledAppFlow
# 'InstalledAppFlow' handles the full OAuth login process for desktop apps.
# It opens the browser, waits for you to log in, and captures the result.

# --- SCOPES ---
# Scopes define exactly what permissions we are requesting from Gmail.
# We are requesting read-only access — our script can read emails but
# cannot send, delete, or modify anything. This is the safest option.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_credentials():
    # This is a function — a reusable block of code we can call from other scripts.
    # It returns a valid credentials object that other scripts use to access Gmail.

    creds = None
    # We start with no credentials. We'll either load them from token.json
    # or create them fresh by going through the login flow.

    if os.path.exists('token.json'):
        # Check if token.json already exists from a previous login.
        # os.path.exists() returns True if the file is found, False if not.
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If it exists, load the credentials from that file.
        # This means we don't need to open the browser again.

    if not creds or not creds.valid:
        # Check if we have no credentials at all, or if they have expired.
        # 'creds.valid' is True only if the token is still usable.

        if creds and creds.expired and creds.refresh_token:
            # If we have credentials but they expired, try to refresh them.
            # Google allows us to get a new token without logging in again
            # as long as we have a refresh_token saved in token.json.
            creds.refresh(Request())
            # This silently gets a new access token from Google.

        else:
            # If there is no token at all, or it cannot be refreshed,
            # we need to go through the full login flow.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Load our app's identity from credentials.json and set the
            # permissions we are requesting (SCOPES defined above).

            creds = flow.run_local_server(port=0)
            # This opens a browser window on your computer asking you to
            # log in and approve access. port=0 means Python picks any
            # available port automatically.

    with open('token.json', 'w') as token:
        # Save the credentials to token.json so we don't have to log in again.
        # 'with open(...)' safely opens a file — it closes it automatically when done.
        # 'w' means write mode — it creates the file if it doesn't exist.
        token.write(creds.to_json())
        # Convert the credentials object to JSON text and write it to the file.

    return creds
    # Send the credentials back to whatever script called this function.

# --- MAIN BLOCK ---
if __name__ == '__main__':
    # This block only runs when you execute auth.py directly.
    # It does NOT run when another script imports this file.
    # This is a standard Python pattern.

    print("Starting Gmail authentication...")
    creds = get_gmail_credentials()
    # Call our function to start the login process.

    print("Authentication successful!")
    print("token.json has been saved to your project folder.")
    print("You will not need to log in again unless the token expires.")

