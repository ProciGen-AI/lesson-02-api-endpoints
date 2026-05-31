"""Exercise 07 — Productionize the structured-output call: validate + retry.

Diff against 06-rich-schema.py: same Converse + tool-forcing call with the
same production schema, now wrapped with two pieces of robustness you'd
want before this code touches a real system.

  1. Validate the model's output against the schema with `jsonschema`.
     Tool-forcing strongly constrains the shape, but the model can still
     produce e.g. a wrong enum value or violate `additionalProperties`.
     Trust but verify.

  2. Wrap the call in `tenacity` so it retries on:
     - transient AWS errors (throttling, 5xx)
     - schema-validation failures (the model sometimes self-corrects on
       a re-roll — and if it doesn't, you want to fail loudly, not silently)

The retry uses exponential backoff so we don't hammer the API after a
throttling response.
"""

import json
import os
import sys
from pathlib import Path

import boto3
import jsonschema
from botocore.exceptions import ClientError
from dotenv import load_dotenv, find_dotenv
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

load_dotenv(find_dotenv())

DATA_PATH = Path(__file__).resolve().parent / "data" / "call1.txt"
SCHEMA_PATH = Path(__file__).resolve().parent / "data" / "call_summary_schema.json"


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, jsonschema.ValidationError):
        return True
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "")
        return code in {
            "ThrottlingException",
            "ServiceUnavailableException",
            "InternalServerException",
            "ModelTimeoutException",
        }
    return False


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception(_should_retry),
)
def summarize_structured(transcript: str, model_id: str, region: str) -> dict:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "emit_summary",
                    "description": "Emit the call summary as structured data.",
                    "inputSchema": {"json": schema},
                }
            }
        ],
        "toolChoice": {"tool": {"name": "emit_summary"}},
    }

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        system=[
            {
                "text": (
                    "You are a precise assistant that summarizes call transcripts. "
                    "Extract participants, main topics, outcomes, action items, "
                    "overall sentiment, and any policy/claim/reference IDs."
                )
            }
        ],
        messages=[{"role": "user", "content": [{"text": transcript}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0.2},
        toolConfig=tool_config,
    )

    data = None
    for block in response["output"]["message"]["content"]:
        if "toolUse" in block:
            data = block["toolUse"]["input"]
            break
    if data is None:
        raise RuntimeError("Model did not emit a tool call.")

    # Draft202012Validator matches the $schema declared in the schema file.
    # Raising here triggers a retry via _should_retry.
    jsonschema.Draft202012Validator(schema).validate(data)
    return data


def main() -> None:
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    region = os.environ.get("AWS_REGION", "us-east-1")

    if not model_id:
        print("Error: BEDROCK_MODEL_ID not set. See 00-aws-setup.md.", file=sys.stderr)
        sys.exit(1)

    transcript = DATA_PATH.read_text(encoding="utf-8").strip()
    try:
        summary = summarize_structured(transcript, model_id=model_id, region=region)
    except jsonschema.ValidationError as e:
        print(f"Schema validation failed after retries: {e.message}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
