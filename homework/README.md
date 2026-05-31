# Homework — Lesson 2

Three optional extensions that push the lab's concepts further. Each one is a 30–60 minute exercise you can drive yourself or hand to a coding agent using the included prompt hint.

## 1. Multi-turn conversation

**Goal.** See how Converse handles state. Spoiler: it doesn't — *you* hold the history, and you pass it back in the `messages` list every turn. Understanding this is the difference between "the model remembers" (it doesn't) and "I'm choosing what to remind the model of every call" (the real story).

**What to build.** Extend `code/03-summarize.py` into a script that does two turns:

  1. Send the transcript, get the summary (turn 1 — same as today).
  2. Append the model's response as a `{"role": "assistant", "content": [...]}` message, then add a `{"role": "user", "content": [...]}` follow-up like *"From your summary, what's the single most urgent action item and why?"*. Call Converse again with both turns plus the new user message.

Print both replies. Then experiment: drop the assistant turn from the second call and re-run — observe what the model can no longer reference. Print `usage` for both calls to see how input tokens grow as conversation length grows.

**Prompt hint.**
> "Starting from `code/03-summarize.py`, build a new script `homework-multiturn.py` that does two Converse calls in sequence. Turn 1: get the summary as today. Turn 2: append the model's response to the `messages` list as `{\"role\": \"assistant\", \"content\": response[\"output\"][\"message\"][\"content\"]}`, then add a new user message asking for the single most urgent action item. Print both replies and both `usage` blocks. Then comment out the assistant turn from the second call, re-run, and write a one-paragraph reflection at the top of the script: *what is the model unable to do without the assistant turn, and what does that tell you about Converse's statelessness?*"

## 2. Prompt caching on a stable prefix

**Goal.** See how prompt caching changes the cost shape of a repeated-context workload — and learn what the cache actually rewards (large, stable prefix; varying suffix).

**What to build.** Extend `code/03-summarize.py` into a script that takes the same transcript and asks the model **three different questions about it back-to-back** (e.g., "why did the premium go up?", "what fixed the late fee?", "what's the next action item?"). Add a `cachePoint` content block between the long reference context and the user question so the transcript is cached once and read on every subsequent call. Print the `cacheWriteInputTokens` / `cacheReadInputTokens` from the `usage` block after each call.

The cache only activates above a model-specific minimum-token threshold (~1024–2048 tokens for current Claude models). The single transcript is shorter than that — repeat it 2–3× in the cached section so the prefix clears the threshold.

**Prompt hint.**
> "Starting from `code/03-summarize.py`, build a new script `homework-caching.py` that asks three different questions about the same transcript. Put the transcript in a `system=[...]` block with a `{\"cachePoint\": {\"type\": \"default\"}}` content block immediately after it; questions go in the user message. Repeat the transcript 3× in the cached block so the prefix is large enough to actually cache (~3KB+). Print `usage` after each call and verify that `cacheWriteInputTokens` is non-zero on call 1, and `cacheReadInputTokens` is non-zero on calls 2 and 3."

## 3. Extended thinking for a reasoning-heavy task

**Goal.** Feel the tradeoff of extended thinking — the model spends extra output tokens "reasoning" before answering. When is the extra cost worth it? When isn't it?

**What to build.** Extend `code/02-basic-call.py` into a script that prompts the model with a multi-step reasoning puzzle (a water-jug measurement problem, a logic grid, a tricky math word problem — pick one). Run it twice: once without extended thinking, once with `additionalModelRequestFields={"thinking": {"type": "enabled", "budget_tokens": 2048}}`. Print both answers, both token counts (input + output + thinking), and compare wall-clock time.

You'll need a model that supports thinking — Claude 3.7+, all Claude 4.x. Claude 3.5 Sonnet returns `ValidationException`. Also: when thinking is enabled, `temperature` must be 1.0 or omitted.

**Prompt hint.**
> "Starting from `code/02-basic-call.py`, build a new script `homework-thinking.py`. Use this prompt: *'You have a 3-gallon jug and a 5-gallon jug, both empty. Measure exactly 4 gallons. Show your steps then state the answer in one sentence.'* Run it twice — once as plain Converse, once with `additionalModelRequestFields={\"thinking\": {\"type\": \"enabled\", \"budget_tokens\": 2048}}` and `maxTokens=4096`. The response will include `reasoningContent` blocks alongside `text` blocks when thinking is on — print both. Compare token usage and wall-clock for the two runs."
