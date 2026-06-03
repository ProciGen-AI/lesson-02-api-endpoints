# Lesson 2 — API Endpoints

This lesson is about **what an LLM API endpoint actually is, what knobs it exposes, and what you put in front of the model**. Six small exercises that build on each other — mostly on the same call-summary task, so you can diff between exercises and see exactly what each new concept adds.

This is the **foundations** half: *calling* the model and its knobs. Getting *machine-reliable structured data* back out (tool-forcing, schema design, validation) and engineering richer context is the focus of **Lesson 3 — API Endpoints, Advanced**, which builds directly on this one.

Everything lives under [`code/`](code/): a one-time setup walkthrough (`00-aws-setup.md`), then six runnable exercises.

## The exercises

| # | File | What it adds vs. the previous one |
|---|---|---|
| 00 | [`00-aws-setup.md`](code/00-aws-setup.md) | One-time setup: create an IAM user, configure `.env`, run the smoke test. No Python. |
| 01 | `01-http-raw.py` | The minimum: an LLM API is just an HTTP POST. Uses Gemini so we don't have to write SigV4 by hand. |
| 02 | `02-basic-call.py` | The same idea via `boto3` Converse against Bedrock. Diff against 01 to see what an SDK gives you (URL, auth, retries). |
| 03 | `03-summarize.py` | A realistic prompt: `system` role, `user` role, `inferenceConfig` (maxTokens, temperature). Introduces the call-summary use case used throughout the lab. |
| 04 | `04-streaming.py` | Same prompt as 03, now via `converse_stream`. Tokens print as they arrive; the response is an iterator of typed events. Same call, different delivery. |
| 05 | `05-reasoning.py` | Turn on **extended thinking** with a `reasoningConfig` effort level (`low`/`medium`/`high`) — off by default, this is the knob. The twist: **Nova redacts the reasoning** (`reasoningContent` streams as `[REDACTED]`), so you see *that* it thought and pay for the tokens but can't read them — a real provider-transparency lesson. A token counter shows the cost: a few visible answer tokens vs. a much larger hidden reasoning bill. |
| 06 | `06-prompt-template.py` | Prompts are **code**: an interactive tool that builds the prompt from three menus — **focus**, **format** (customer email / manager email / CRM note), **length**. Constraining the request to fixed choices (vs. a free-text box) makes the output predictable — the input-side cousin of structured output. |

The arc: 01–03 build the basic call. 04 (streaming) and 05 (reasoning) are quick "behavior knob" detours on that same call. 06 makes the prompt itself the lesson — a static prefix plus a builder that assembles the request from constrained menu choices (the input-side cousin of structured output), the "retrieve → assemble → render" seam Lesson 3 takes further with live CRM context.

## Learning objectives

By the end of this lesson you should be able to answer:

- What's the minimum HTTP request that gets a model to respond?
- What does an SDK like `boto3` hide compared to that raw HTTP call?
- What does a "real" prompt look like — `system` role, `user` role, `maxTokens`, `temperature`?
- How do you stream tokens as they arrive?
- What is extended thinking, why is it off by default — and why might a provider bill you for reasoning tokens it won't let you read?
- Why build prompts from a static prefix + a dynamic builder — and why constrain inputs to fixed menu choices rather than a free-text request?

> Forcing JSON output, schema design, validation/retry, and context enrichment build on these and live in **Lesson 3 — API Endpoints, Advanced**.

## Prerequisites

- Python 3.11+
- An AWS account with Bedrock model access (`00-aws-setup.md` walks you through getting this)
- A Google AI Studio API key (free tier is fine — get one at https://aistudio.google.com/apikey) for the raw-HTTP example in exercise 01

## How to run

> **On Windows?** Run every lab command from **Git Bash**, not PowerShell or cmd — they can't source a `.sh` file. Easiest setup: open this project in VS Code and set the integrated terminal to Git Bash (`Ctrl+Shift+P` → *Terminal: Select Default Profile* → *Git Bash*), then use that terminal for everything below. No Git Bash? Install [Git for Windows](https://git-scm.com/download/win), or use [WSL](https://learn.microsoft.com/windows/wsl/install) (which behaves like native Linux). If you start in PowerShell by mistake, run `.\setup.ps1` and it'll bounce you to Git Bash. macOS/Linux: ignore this — the commands work as-is.

Start with **`code/00-aws-setup.md`**. It walks you into the `code/` folder and ends with sourcing `setup.sh` to confirm Bedrock works end-to-end:

```bash
git clone https://github.com/ProciGen-AI/lesson-02-api-endpoints.git
cd lesson-02-api-endpoints/code
source setup.sh
```

That leaves you in `code/` — run each exercise from there:

```bash
python 01-http-raw.py
python 02-basic-call.py
python 03-summarize.py
python 04-streaming.py
python 05-reasoning.py
python 06-prompt-template.py
```

Prefer exploring by chatting with a coding agent rather than reading every line? [`code/PROMPTS.md`](code/PROMPTS.md) has sample explore-and-modify prompts for each exercise.

## Build it yourself (spec-driven rebuild)

Once you've studied the lab above, practice *producing* the culminating exercise from a spec rather than reading it — see **[`SDD/`](SDD/)**. You build in a separate **clean** repo (so your coding agent gets no answer key and no rubric to game), driven by [`SDD/PROMPT.md`](SDD/PROMPT.md), then score yourself with the `validate-lab` skill from `SDD/`.

Start here: **[`SDD/README.md`](SDD/README.md)**.

## Homework

[`homework/README.md`](homework/README.md) has three optional extensions: multi-turn conversation, prompt caching, and letting the model drive the menu (reasoning → autonomy). Each one builds on a specific exercise from this lab.

## Next

**Lesson 3 — API Endpoints, Advanced** picks up here: tool-forced structured output, production schema design, validation + retry, and context enrichment.
