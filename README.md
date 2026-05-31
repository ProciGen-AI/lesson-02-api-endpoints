# Lesson 2 — API Endpoints

This lesson is about **what an LLM API endpoint actually is, what knobs it exposes, and what you put in front of the model**. It's one lab of nine small exercises that build on each other — all targeting the same call-summary task, so you can diff between exercises and see exactly what each new concept adds.

Everything lives under [`code/`](code/): a one-time setup walkthrough (`00-aws-setup.md`), then eight runnable exercises.

## The exercises

| # | File | What it adds vs. the previous one |
|---|---|---|
| 00 | [`00-aws-setup.md`](code/00-aws-setup.md) | One-time setup: create an IAM user, configure `.env`, run the smoke test. No Python. |
| 01 | `01-http-raw.py` | The minimum: an LLM API is just an HTTP POST. Uses Gemini so we don't have to write SigV4 by hand. |
| 02 | `02-basic-call.py` | The same idea via `boto3` Converse against Bedrock. Diff against 01 to see what an SDK gives you (URL, auth, retries). |
| 03 | `03-summarize.py` | A realistic prompt: `system` role, `user` role, `inferenceConfig` (maxTokens, temperature). Introduces the call-summary use case used throughout the lab. |
| 04 | `04-streaming.py` | Same prompt as 03, now via `converse_stream`. Tokens print as they arrive; the response is an iterator of typed events. Same call, different delivery. |
| 05 | `05-structured-output.py` | Force the model to emit JSON matching a schema via tool-forced output. Tiny inline schema (4 flat fields) so the mechanic is the whole lesson. |
| 06 | `06-rich-schema.py` | Same mechanic as 05, but the schema graduates to a production shape: nested objects, arrays of objects, enums, nullable fields. Teaches schema design. |
| 07 | `07-validate-and-retry.py` | Productionize 06: validate the model's output with `jsonschema`, and wrap the call with `tenacity` to retry on transient AWS errors or validation failures. |
| 08 | `08-context-enrichment.py` | Enrich the prompt with **CRM context**. A static system prompt (cache-friendly) plus a dynamic, per-customer user prompt built in `prompts.py`, producing an extended schema whose new fields (churn risk, personalized next actions, cross-sell) only fill well *because* of the context. |

The arc: 01–03 build the basic call. 04 is a quick "delivery mode" detour to see streaming. 05–07 dive into structured output as a three-step build (mechanic → realistic schema → production hardening). 08 shifts the focus from *the call* to *what you feed it* — context engineering.

## Learning objectives

By the end of this lesson you should be able to answer:

- What's the minimum HTTP request that gets a model to respond?
- What does an SDK like `boto3` hide compared to that raw HTTP call?
- What does a "real" prompt look like — `system` role, `user` role, `maxTokens`, `temperature`?
- How do you stream tokens as they arrive?
- How do you force a model to return JSON matching a schema, how do you design that schema, and how do you validate the result?
- Why split a prompt into a static system prefix and a dynamic user payload — and what does that buy you (caching, separation of concerns)?
- How does enriching the prompt with external context (a CRM record) change the model's output, and where does that context-assembly logic belong in your code?

## Prerequisites

- Python 3.11+
- An AWS account with Bedrock model access (`00-aws-setup.md` walks you through getting this)
- A Google AI Studio API key (free tier is fine — get one at https://aistudio.google.com/apikey) for the raw-HTTP example in exercise 01

## How to run

Start with **`code/00-aws-setup.md`**. It ends with sourcing `setup.sh` to confirm Bedrock works end-to-end:

```bash
source course/Lesson-02-API-Endpoints/code/setup.sh
```

After setup passes, run each exercise:

```bash
python course/Lesson-02-API-Endpoints/code/01-http-raw.py
python course/Lesson-02-API-Endpoints/code/02-basic-call.py
python course/Lesson-02-API-Endpoints/code/03-summarize.py
python course/Lesson-02-API-Endpoints/code/04-streaming.py
python course/Lesson-02-API-Endpoints/code/05-structured-output.py
python course/Lesson-02-API-Endpoints/code/06-rich-schema.py
python course/Lesson-02-API-Endpoints/code/07-validate-and-retry.py
python course/Lesson-02-API-Endpoints/code/08-context-enrichment.py
```

Prefer exploring by chatting with a coding agent rather than reading every line? [`code/PROMPTS.md`](code/PROMPTS.md) has sample explore-and-modify prompts for each exercise.

## Homework

[`homework/README.md`](homework/README.md) has three optional extensions: multi-turn conversation, prompt caching, and extended thinking. Each one builds on a specific exercise from this lab.
