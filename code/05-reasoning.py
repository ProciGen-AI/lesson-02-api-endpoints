"""Exercise 05 — Extended thinking (reasoning), streamed.

Diff against 04-streaming.py: the same `converse_stream` call, with one new
knob — `additionalModelRequestFields` turns on extended thinking and picks how
hard the model thinks. With reasoning enabled the stream carries a new block
type: `reasoningContent`, which arrives before the `text` answer.

Here's the catch, and the real lesson: **Nova redacts the reasoning.** The
`reasoningContent` block streams as the literal string `[REDACTED]` — you can
see *that* the model reasoned, but not *what* it reasoned. You're still billed
for those reasoning tokens (they count as output), you just don't get to read
them. That's a provider choice, not a bug: Anthropic's Claude returns a
*summarized* trace, Nova *redacts* it, some models hide it entirely. Reasoning
transparency is a decision the model maker makes for you.

The token counter at the end makes the cost concrete. Bedrock reports input and
output tokens, but folds the reasoning tokens INTO `outputTokens` — there's no
separate field — so the visible answer is a handful of tokens while the output
bill is far larger. The gap is the invisible reasoning you paid for. (We can
only *estimate* the answer/reasoning split, because the API won't itemize it —
that's part of the lesson too.)

Three things worth knowing, all Bedrock/Nova specifics:

  - Reasoning is OFF by default. A plain call (02–04) goes straight to the
    answer; you opt in with the `reasoningConfig` field below.
  - `maxReasoningEffort` is the dial — "low", "medium", or "high": how hard the
    model thinks before answering. Higher buys deeper reasoning on harder
    problems, at a latency and token cost. (Nova uses these effort levels
    instead of a numeric token budget like some other models do.)
  - Constraint at the top end: with `maxReasoningEffort: "high"`, Bedrock
    requires `temperature`, `topP`, and `maxTokens` to be UNSET — so we drop
    maxTokens at "high" (the course default is "low", where it's fine).

The prompt is a small reasoning trap (the intuitive answer, $0.10, is wrong).
It's the kind of problem where thinking earns its keep. Try it, then drop
REASONING_EFFORT a level — or delete the `additionalModelRequestFields` block —
and watch the reasoning-token count shrink toward zero (and the answer get less
reliable).
"""

import os

import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# How hard the model thinks before answering: "low", "medium", or "high".
# Higher = deeper reasoning, more latency/tokens. NOTE: "high" requires
# temperature/topP/maxTokens to be unset (see the call below); "low"/"medium"
# don't — which is why the course default is "low".
REASONING_EFFORT = "low"
MAX_TOKENS = 2048

PROMPT = (
    "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the "
    "ball. How much does the ball cost? Give only the final answer in one "
    "sentence — no working shown."
)

client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])

response = client.converse_stream(
    modelId=os.environ["BEDROCK_MODEL_ID"],
    messages=[{"role": "user", "content": [{"text": PROMPT}]}],
    # At "high" effort Bedrock requires temperature/topP/maxTokens to be UNSET,
    # so we drop maxTokens there; at low/medium it's allowed. (Temperature is
    # omitted at every level anyway.) This keeps any REASONING_EFFORT value valid.
    inferenceConfig=({} if REASONING_EFFORT == "high" else {"maxTokens": MAX_TOKENS}),
    # The one new knob vs. 04: enable extended thinking and set its effort level.
    # On Bedrock this lives in additionalModelRequestFields (model-specific
    # passthrough), not in the portable top-level Converse params.
    additionalModelRequestFields={
        "reasoningConfig": {"type": "enabled", "maxReasoningEffort": REASONING_EFFORT}
    },
)

# The stream carries `reasoningContent` deltas first (Nova sends "[REDACTED]"
# here — see the note above), then the `text` answer. We label each so the
# boundary is visible, tally the answer's characters to size it later, and grab
# the token usage from the final `metadata` event.
answer_chars = 0
usage = None
mode = None
for event in response["stream"]:
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"]["delta"]
        if "reasoningContent" in delta:
            # The reasoning delta arrives under `text` (some models nest it under
            # `reasoningText.text`), so we check both. On Nova this is "[REDACTED]".
            rc = delta["reasoningContent"]
            chunk = rc.get("text") or rc.get("reasoningText", {}).get("text")
            if chunk:
                if mode != "thinking":
                    print("--- REASONING (Nova redacts this) ---\n", flush=True)
                    mode = "thinking"
                print(chunk, end="", flush=True)
        elif "text" in delta:
            if mode != "answer":
                print("\n\n--- ANSWER ---\n", flush=True)
                mode = "answer"
            print(delta["text"], end="", flush=True)
            answer_chars += len(delta["text"])
    elif "metadata" in event:
        # The final metadata event carries token usage for the whole call.
        usage = event["metadata"].get("usage")

print()

# --- Token breakdown --------------------------------------------------------
# inputTokens / outputTokens are exact (from the API). Nova bills reasoning as
# OUTPUT tokens with no separate field, so to show reasoning vs. answer we
# estimate the visible answer (~4 chars per token — Nova's tokenizer isn't local)
# and treat the rest of the output as reasoning. The size of that gap is the
# whole point: you paid for reasoning you can neither see nor itemize.
if usage:
    input_tokens = usage.get("inputTokens", 0)
    output_tokens = usage.get("outputTokens", 0)
    answer_est = max(1, round(answer_chars / 4))
    reasoning_est = max(0, output_tokens - answer_est)
    print("\n--- TOKENS ---")
    print(f"  input:                {input_tokens}")
    print(f"  output (total):       {output_tokens}   (reasoning + answer — Nova bills reasoning as output)")
    print(f"    answer (visible):   ~{answer_est}   (estimated from the {answer_chars} chars you read)")
    print(f"    reasoning (hidden): ~{reasoning_est}   (you paid for it; Nova redacts the text)")
