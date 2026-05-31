"""Exercise 01 — An LLM API endpoint is just an HTTP POST.

We hit Gemini because its API-key auth is the simplest of any major
provider. Bedrock requires SigV4 signing, which would bury the "it's just
HTTP" point under signing code — we'll get to Bedrock through an SDK in 02.
"""

import os

import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{os.environ['GEMINI_MODEL_ID']}:generateContent"
)

response = requests.post(
    url,
    headers={"x-goog-api-key": os.environ["GOOGLE_API_KEY"]},
    json={"contents": [{"role": "user", "parts": [{"text": "What is 2+2? Reply in one sentence."}]}]},
)

print(response.json()["candidates"][0]["content"]["parts"][0]["text"])
