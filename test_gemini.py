# test_gemini.py
# This script does ONE thing: confirms your Gemini API key works.
# It sends a simple test message and prints the response.
# Run this before building anything else.

# --- IMPORTS ---

import os
# Built-in Python library to access environment variables

from dotenv import load_dotenv
# load_dotenv() reads your .env file and loads the values into
# Python's environment so os.getenv() can find them

from google import genai
# This is the new Google GenAI SDK (google-genai package)
# The old package was google-generativeai — that is now deprecated

# --- LOAD ENVIRONMENT VARIABLES ---

load_dotenv()
# This must be called before os.getenv() or your key won't be found.
# It looks for a .env file in the current folder and loads it.

# --- GET API KEY ---

api_key = os.getenv("GEMINI_API_KEY")
# os.getenv() fetches the value of GEMINI_API_KEY from the environment.
# If the .env file is missing or the key name is wrong, this returns None.

if not api_key:
    # Safety check — if the key is None or empty, stop immediately
    # and tell the user exactly what went wrong.
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

print("✅ API key loaded successfully.")

# --- SET UP GEMINI CLIENT ---

client = genai.Client(api_key=api_key)
# This creates a Gemini client object using your API key.
# All your future API calls will go through this client.

print("✅ Gemini client created.")

# --- SEND A TEST MESSAGE ---

print("Sending test message to Gemini...")

response = client.models.generate_content(
    model="gemini-2.5-flash",       # Free tier model — fast and capable
    contents="Say hello and confirm you are working correctly."
    # This is the message we're sending to Gemini.
    # 'contents' is the user message — like typing in a chat box.
)
# generate_content() sends our message to Gemini and waits for a reply.
# The whole response object is stored in 'response'.

# --- PRINT THE RESPONSE ---

print("\n--- Gemini Response ---")
print(response.text)
# response.text extracts just the text content from the response object.
# The full response object contains metadata, safety ratings etc.
# We only need the text for now.

print("\n✅ Test complete. Gemini is connected and working.")