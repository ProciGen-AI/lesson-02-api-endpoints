"""Exercise 03 — A realistic prompt: system role, user role, tunable knobs.

Diff against 02-basic-call.py: same Converse call, now with
  - a `system` prompt that shapes how the model responds,
  - a `user` prompt built from a transcript loaded from disk,
  - `inferenceConfig` knobs (maxTokens, temperature).

The `system`/`user` split and the `inferenceConfig` knobs are how every
chat-completion API surfaces "role" and "tunables." Subsequent exercises
build on this shape.
"""

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# data/ sits next to the exercises in this lab's code/ folder.
transcript = (Path(__file__).resolve().parent / "data" / "call1.txt").read_text()

client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

response = client.converse(
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
    messages=[
        {
            "role": "user",
            # The system prompt already specifies the task, so the user message
            # is just the payload — no need to repeat "Summarize the following..."
            "content": [{"text": transcript}],
        }
    ],
    inferenceConfig={"maxTokens": 1000, "temperature": 0.3},
)

print(response["output"]["message"]["content"][0]["text"])
