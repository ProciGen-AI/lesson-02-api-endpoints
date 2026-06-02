"""Exercise 05 — Extended thinking (reasoning), streamed.

Diff against 04-streaming.py: the same `converse_stream` call, with one new
knob — `additionalModelRequestFields` turns on extended thinking and gives it a
token budget. With thinking enabled the stream carries a new block type:
`reasoningContent` deltas (the model's *summarized* reasoning) arrive first,
then the `text` answer. You watch the model think, live, before it answers.

Note the prompt asks for *only the answer* — no "show your work." So the
step-by-step never appears in the customer-facing `text`; it shows up only in
the `reasoningContent` block. That's the point: the reasoning happens
**backstage**, and `reasoningContent` is your window into it — separate from
whatever the user actually asked for.

Three things worth knowing, all Bedrock/Claude specifics:

  - Reasoning is OFF by default. A plain call (02–04) goes straight to the
    answer; you opt in with the `thinking` field below. There is no separate
    hidden reasoning step unless you ask for one.
  - `budget_tokens` is the "reasoning budget" — how many tokens the model may
    spend thinking. It must be < `maxTokens`, because thinking and the answer
    draw from the same output budget, so we keep headroom. A bigger budget
    buys deeper reasoning on harder problems, at a latency and token cost.
  - With thinking on, `temperature` must be 1.0 or omitted — Bedrock rejects
    any other value with a ValidationException. So we omit it here.
  - What you see is *summarized*: Claude 4 returns a summary of its full
    thinking, not the raw chain-of-thought, and there's no API switch to get
    the full version (it's gated; you're billed for the full thinking either
    way). "Summarized" is the most detail you can show — not a setting to fix.

The prompt is a small reasoning trap (the intuitive answer, $0.10, is wrong).
It's the kind of problem where thinking earns its keep. Try it, then lower
THINKING_BUDGET_TOKENS — or delete the `additionalModelRequestFields` block —
and watch the reasoning shrink or disappear (and the answer get less reliable).
"""

import os
from pathlib import Path

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# The reasoning budget. budget_tokens MUST be < maxTokens — thinking and the
# answer share the output allowance. Raise it for harder problems; lower it
# (or drop the thinking block entirely) to turn reasoning down or off.
MAX_TOKENS = 2048
THINKING_BUDGET_TOKENS = 1024

PROMPT = (
    "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the "
    "ball. How much does the ball cost? Give only the final answer in one "
    "sentence — no working shown."
)

client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

response = client.converse_stream(
    modelId=os.environ["BEDROCK_MODEL_ID"],
    messages=[{"role": "user", "content": [{"text": PROMPT}]}],
    # temperature is intentionally omitted: thinking requires temperature=1.0
    # (or unset), so leaving it out is the path of least resistance.
    inferenceConfig={"maxTokens": MAX_TOKENS},
    # The one new knob vs. 04: enable extended thinking with a token budget.
    # On Bedrock this lives in additionalModelRequestFields (model-specific
    # passthrough), not in the portable top-level Converse params.
    additionalModelRequestFields={
        "thinking": {"type": "enabled", "budget_tokens": THINKING_BUDGET_TOKENS}
    },
)

# With thinking on, the stream has two kinds of delta: `reasoningContent` (the
# summarized thinking) streams first, then `text` (the answer). We label each
# so the boundary between "thinking" and "answering" is visible as it arrives.
mode = None
for event in response["stream"]:
    if "contentBlockDelta" not in event:
        continue
    delta = event["contentBlockDelta"]["delta"]
    if "reasoningContent" in delta:
        # A reasoningContent delta carries either a `text` chunk or, at the
        # very end, a `signature` (a cryptographic marker) — we only print text.
        chunk = delta["reasoningContent"].get("text")
        if chunk:
            if mode != "thinking":
                print("--- THINKING (summarized) ---\n", flush=True)
                mode = "thinking"
            print(chunk, end="", flush=True)
    elif "text" in delta:
        if mode != "answer":
            print("\n\n--- ANSWER ---\n", flush=True)
            mode = "answer"
        print(delta["text"], end="", flush=True)

print()
