"""Exercise 02 — Same call as 01, now through boto3.

Diff against 01-http-raw.py to see what the SDK gives you: URL construction,
SigV4 request signing, retries on transient errors. The response is still
raw — you still parse it yourself.

We use Bedrock's Converse API (unified across model providers), not the
older provider-specific `invoke_model`.
"""

import os

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

response = client.converse(
    modelId=os.environ["BEDROCK_MODEL_ID"],
    messages=[{"role": "user", "content": [{"text": "What is 2+2? Reply in one sentence."}]}],
)

print(response["output"]["message"]["content"][0]["text"])
