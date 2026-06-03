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

The cache only activates above a model-specific minimum-token threshold (~1K tokens for Nova 2 Lite). The single transcript is shorter than that — repeat it 2–3× in the cached section so the prefix clears the threshold.

**Prompt hint.**
> "Starting from `code/03-summarize.py`, build a new script `homework-caching.py` that asks three different questions about the same transcript. Put the transcript in a `system=[...]` block with a `{\"cachePoint\": {\"type\": \"default\"}}` content block immediately after it; questions go in the user message. Repeat the transcript 3× in the cached block so the prefix is large enough to actually cache (~3KB+). Print `usage` after each call and verify that `cacheWriteInputTokens` is non-zero on call 1, and `cacheReadInputTokens` is non-zero on calls 2 and 3."

## 3. Let the model drive the menu (reasoning → autonomy)

**Goal.** Exercise 06 keeps a human in the loop — *you* pick focus, format, and length. The same constrained option space can be handed to the *model*, and **reasoning** (exercise 05) is what lets it choose well. This is the first step from "a tool a human operates" toward "an agent that decides," with the menu surviving as the model's *bounded action space*.

**What to build.** Start from `code/06-prompt-template.py` and remove the interactive `choose()` calls. Instead, put the `FOCUSES` / `FORMATS` / `LENGTHS` options *into the prompt* and ask the model to pick the best one of each for **this** transcript, justify each pick from the call, then produce the deliverable with its own choices. Turn on **extended thinking** so it chooses well, and have it **write its justifications into the output** (Nova redacts the raw `reasoningContent`, so the reasoning you can inspect has to live in the visible answer). Print its picks, its justifications, and the final output. Run it on `call1.txt` — did its autonomous choices match what you'd have picked?

**The "something more" — keep it bounded, then let it act.** Constrain the model to the *existing* menu labels only (no inventing new ones): autonomy over a *known* action space, not a free-for-all. Then add a routing rule and watch reasoning act on it — *"if you judge churn risk high, you must pick 'email to manager' and flag the call for escalation."* That **reason → choose-from-a-bounded-set → act** loop is an agent in miniature, and the bounded action space is exactly what keeps it safe.

**Prompt hint.**
> "Starting from `code/06-prompt-template.py`, build `homework-autonomous.py` that drops the `choose()` prompts. Build one prompt that lists the FOCUSES/FORMATS/LENGTHS options and asks the model to (1) pick the best focus, format, and length for this transcript and justify each from the call, then (2) write the deliverable accordingly. Enable extended thinking with `additionalModelRequestFields={'reasoningConfig': {'type': 'enabled', 'maxReasoningEffort': 'low'}}` and `maxTokens=2048` (omit temperature; at `'high'` effort you'd also drop `maxTokens`/`topP`). Print the chosen options, the model's written justifications, and the output (note: `reasoningContent` is redacted to `[REDACTED]` on Nova, so the inspectable reasoning has to be in the answer text). Constrain it to the existing menu labels only. Then add a rule: if churn risk is high it must choose 'email to manager' and flag the call for escalation — and confirm its reasoning routes accordingly."
