"""Exercise 06 — Prompts are code: a template driven by *constrained* choices.

Diff against 03-summarize.py: the prompt is no longer one hardcoded string, and
the user doesn't type a free-text request. Instead the script offers three
menus — **focus**, **format**, **length** — and a builder assembles the prompt
from the chosen options.

Why menus instead of "type what you want": constraining the inputs to a known
set of options makes the request — and therefore the output's shape — far more
predictable. A free-text box lets the user ask for anything (and the model
answer in any shape); a menu of {focus} × {format} × {length} can only produce
prompts you've already designed. This is the *input-side* cousin of the
structured **output** you'll force in Lesson 3 — same instinct (pin things down),
applied to what goes in rather than what comes back.

Two pieces you'll reuse everywhere:
  - a STATIC system prompt (the analyst's role), identical on every call; and
  - a DYNAMIC user prompt built by build_request_prompt() from the three chosen
    options + the transcript.

Run it and answer the three prompts; the same template + different choices
produce different deliverables (a terse CRM note vs. a warm customer email, etc.).
"""

import os
import sys
from pathlib import Path

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TRANSCRIPT_PATH = Path(__file__).resolve().parent / "data" / "call1.txt"

# Static half: role only. The variable parts live in the menus below, never here.
SYSTEM_PROMPT = (
    "You are a support-call analyst. Produce exactly what the user asks for, in "
    "the requested focus, format, and length. Stick to what the transcript "
    "supports — don't invent details."
)

# The three menus. Each option maps a short label (shown to the user) to the
# instruction fragment the builder splices into the prompt. Adding/auditing an
# option is a one-line change — and the set of possible prompts stays known.
FOCUSES = {
    "billing": "Focus on billing — the premium change, fees, and payment issues.",
    "retention": "Focus on retention — the churn risk and what kept (or could keep) the customer.",
    "claim": "Focus on the open claim — its status and the next steps that were promised.",
}
FORMATS = {
    "email to customer": "Write it as a short, warm email to the customer, with a greeting and sign-off.",
    "email to manager": "Write it as an internal email to the team manager — lead with status and risk, skip customer pleasantries.",
    "CRM note": "Write it as a terse CRM note: no greeting or sign-off, just compact factual bullet points.",
}
LENGTHS = {
    "concise": "Keep it to 1-2 sentences.",
    "short": "Keep it to 3-4 sentences.",
    "medium": "Keep it to a short paragraph (about 5-7 sentences).",
}


def choose(label: str, options: dict) -> str:
    """Print a numbered menu (with the instruction as the example) and return the
    chosen key. Looping until a valid number is the 'constrain the input' part —
    the user can't ask for something the template doesn't support."""
    keys = list(options)
    print(f"\nSupport-call Agent: choose a {label} —")
    for i, k in enumerate(keys, 1):
        print(f"  {i}) {k}  ({options[k]})")
    while True:
        raw = input("You: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            return keys[int(raw) - 1]
        print(f"  (enter a number 1-{len(keys)})")


def build_request_prompt(transcript: str, focus: str, fmt: str, length: str) -> str:
    """Assemble the dynamic user prompt from the three chosen options + transcript.

    The seam where values get filled in — here from menu choices, in Lesson 3
    from a CRM record. Pure function: no I/O, easy to test.
    """
    return (
        "Summarize this support call to these specs:\n"
        f"- {FOCUSES[focus]}\n"
        f"- {FORMATS[fmt]}\n"
        f"- {LENGTHS[length]}\n\n"
        f"Transcript:\n{transcript}"
    )


def summarize(transcript: str, focus: str, fmt: str, length: str, model_id: str, region: str) -> str:
    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": build_request_prompt(transcript, focus, fmt, length)}]}],
        inferenceConfig={"maxTokens": 600, "temperature": 0.3},
    )
    return response["output"]["message"]["content"][0]["text"]


def main() -> None:
    model_id = os.environ.get("BEDROCK_MODEL_ID")
    region = os.environ.get("AWS_REGION", "us-east-1")
    if not model_id:
        print("Error: BEDROCK_MODEL_ID not set. See 00-aws-setup.md.", file=sys.stderr)
        sys.exit(1)

    transcript = TRANSCRIPT_PATH.read_text(encoding="utf-8").strip()

    focus = choose("focus", FOCUSES)
    fmt = choose("format", FORMATS)
    length = choose("length", LENGTHS)

    print("\nSupport-call Agent: here's what you asked for:\n")
    print(summarize(transcript, focus, fmt, length, model_id=model_id, region=region))


if __name__ == "__main__":
    main()
