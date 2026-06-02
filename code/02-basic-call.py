"""Exercise 02 — Same call as 01, now through boto3.

Diff against 01-http-raw.py to see what the SDK gives you: URL construction,
SigV4 request signing, retries on transient errors. The response is still
raw — you still parse it yourself. To make that concrete, this prints the
whole response envelope first, then pulls out the one field we actually want.

We use Bedrock's Converse API (unified across model providers), not the
older provider-specific `invoke_model`.
"""

import json
import os

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

response = client.converse(
    modelId=os.environ["BEDROCK_MODEL_ID"],
    messages=[{"role": "user", "content": [{"text": "What is 2+2? Reply in one sentence."}]}],
)

# The Converse API hands back more than the answer. Dump the whole response
# to see the envelope: output.message.content is a LIST of blocks, and for a
# plain text call that one block is a `text` block. You also get stopReason,
# token usage, and request metadata. (In 06 we force a tool and this same
# content slot becomes a `toolUse` block instead — diff the two raw dumps.)
print("=== RAW CONVERSE RESPONSE ===")
print(json.dumps(response, indent=2, default=str))

# The actual answer lives at content[0].text — reach into the envelope for it.
print("\n=== THE ANSWER (content[0].text) ===")
print(response["output"]["message"]["content"][0]["text"])
