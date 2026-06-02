# Lesson 2 — API Endpoints · Spec-Driven Build (SDD)

The build-it-yourself half of Lesson 2. You've studied the worked lab in
[`../code/`](../code/); now **rebuild** its culminating script —
`06-prompt-template.py` — from a spec, driving a coding agent with `PROMPT.md`,
then score yourself with the `validate-lab` skill.

## How it works

You build in a **separate, clean repo** so your agent starts from a blank slate —
no answer key, no rubric to game, no dependency hints. This `SDD/` folder (inside
the lesson repo) holds the **task** (`PROMPT.md`) and the **validator**
(`validate-lab/`); the building happens in the other repo.

## 1. Get a clean build workspace

```bash
git clone https://github.com/ProciGen-AI/lesson-02-api-endpoints-sdd.git
cd lesson-02-api-endpoints-sdd
source setup.sh                  # venv + base deps (boto3, python-dotenv) + Bedrock smoke test
mv CLAUDE.md-example CLAUDE.md   # activate the build conventions your agent reads
```

> The build repo is deliberately bare — **setup + data + conventions only**, no
> `PROMPT.md`, no `requirements.txt`, no answer. It has no `.env.example` either:
> **bring your own `.env`** — copy the one you already filled in for this lesson
> (e.g. `cp ../lesson-02-api-endpoints/.env .env`, adjust the path to wherever you
> cloned the lesson repo).
>
> **On Windows?** Run these from Git Bash (easiest via VS Code's integrated terminal).

## 2. Build

Hand your agent the task — **`PROMPT.md` in this `SDD/` folder** (open it and paste
it, or point your agent at it). It's a *partial* spec; the load-bearing decisions
are yours (the `▢ YOU DECIDE` block). Build `06-prompt-template.py` in the build
repo, run it, iterate:

```bash
python 06-prompt-template.py
```

## 3. Validate

Back here in the lesson repo's `SDD/` folder, invoke the **validate-lab** skill. It
asks for the path to your build repo, then scores your `06-prompt-template.py`
against the reference `../code/06-prompt-template.py` out of 100 — naming what's
missing / weaker / better, with a cheat prompt if you're out of time.
