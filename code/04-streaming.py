"""Exercise 04 — Same summary as 03, now streamed token-by-token.

Diff against 03-summarize.py: the only changes are `converse` →
`converse_stream` and the response shape. Streaming returns an iterator of
typed events; for plain text generation, the one you care about is
`contentBlockDelta`, which carries one chunk of text per event.

Other events you'll see in the stream (messageStart, contentBlockStart/Stop,
messageStop, metadata) matter for richer UIs and usage tracking — we ignore
them here and keep the loop to the one shape that prints output.
"""

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

transcript = (Path(__file__).resolve().parent / "data" / "call1.txt").read_text()

client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

response = client.converse_stream(
    modelId=os.environ["BEDROCK_MODEL_ID"],
    system=[
        {
            "text": (
                "You are a helpful assistant that summarizes call transcripts. "
                "Provide a clear, concise summary that captures the main topics, "
                "outcomes, and any action items."
            )
        }
    ],
    messages=[{"role": "user", "content": [{"text": transcript}]}],
    inferenceConfig={"maxTokens": 1000, "temperature": 0.3},
)

for event in response["stream"]:
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"]["delta"]
        if "text" in delta:
            print(delta["text"], end="", flush=True)

print()
