"""Exercise 08 — Enrich the prompt with CRM context.

This is where the lab stops being about "the API call" and starts being about
"what you put in front of the model." Same tool-forced structured-output
mechanic as 05-07 — but now the prompt is built from two halves:

  - a STATIC system prompt (prompts.SYSTEM_PROMPT) — the analyst's role and
    rules, identical on every call, so it's prompt-cache-friendly; and
  - a DYNAMIC user prompt (prompts.build_user_prompt) — assembled per customer
    from a CRM record loaded from `data/customer_crm.json`.

The schema also grows: `data/enriched_summary_schema.json` keeps the six
base fields from 06/07 and adds four CRM-driven ones — churn_risk,
churn_risk_rationale, personalized_next_actions, cross_sell_opportunities.
Those last fields are the point of the exercise: the model can only fill them
*well* because it was handed the CRM context. Try running once, then delete a
CRM section from the user prompt (e.g. products_held) and watch
cross_sell_opportunities degrade — that's the enrichment "doing work."

We validate the output against the schema (as in 07). We skip the retry
wrapper to keep the focus on enrichment; 07 shows how to add it back.
"""

import json
import os
import sys
from pathlib import Path

import boto3
import jsonschema
from dotenv import load_dotenv, find_dotenv

# prompts.py lives next to this script — the static system prompt and the
# dynamic user-prompt builder.
from prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv(find_dotenv())

DATA_DIR = Path(__file__).resolve().parent / "data"
TRANSCRIPT_PATH = DATA_DIR / "call1.txt"
CRM_PATH = DATA_DIR / "customer_crm.json"
SCHEMA_PATH = DATA_DIR / "enriched_summary_schema.json"


def analyze_call(transcript: str, crm: dict, schema: dict, model_id: str, region: str) -> dict:
    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "emit_enriched_summary",
                    "description": "Emit the post-call summary and CRM-informed assessment.",
                    "inputSchema": {"json": schema},
                }
            }
        ],
        "toolChoice": {"tool": {"name": "emit_enriched_summary"}},
    }

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        # Static prefix (cacheable) vs. dynamic payload (per-customer) — the
        # whole point of splitting the prompt into a constant + a builder.
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": build_user_prompt(transcript, crm)}]}],
        inferenceConfig={"maxTokens": 1500, "temperature": 0.2},
        toolConfig=tool_config,
    )

    data = None
    for block in response["output"]["message"]["content"]:
        if "toolUse" in block:
            data = block["toolUse"]["input"]
            break
    if data is None:
        raise RuntimeError("Model did not emit a tool call.")

    jsonschema.Draft202012Validator(schema).validate(data)
    return data


def main() -> None:
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    region = os.environ.get("AWS_REGION", "us-east-1")

    if not model_id:
        print("Error: BEDROCK_MODEL_ID not set. See 00-aws-setup.md.", file=sys.stderr)
        sys.exit(1)

    transcript = TRANSCRIPT_PATH.read_text(encoding="utf-8").strip()
    crm = json.loads(CRM_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    # Show the dynamic half of the prompt with the transcript omitted, so the
    # CRM enrichment scaffold is readable on its own. The actual call below
    # sends the same prompt WITH the full transcript spliced in.
    print("=== USER PROMPT (CRM enrichment scaffold; transcript omitted) ===")
    print(build_user_prompt("", crm))

    try:
        result = analyze_call(transcript, crm, schema, model_id=model_id, region=region)
    except jsonschema.ValidationError as e:
        print(f"Schema validation failed: {e.message}", file=sys.stderr)
        sys.exit(1)

    print("=== STRUCTURED RESPONSE ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
