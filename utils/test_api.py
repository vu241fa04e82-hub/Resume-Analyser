import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("Key loaded:", bool(api_key))
print("Key prefix:", api_key[:5] if api_key else "NONE")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello in one sentence."
)

print("SUCCESS!")
print(response.text)