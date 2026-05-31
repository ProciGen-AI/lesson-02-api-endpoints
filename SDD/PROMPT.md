<!-- ──────────────────────────────────────────────────────────────────────────
  HOW TO USE THIS FILE  (guidance to you, the student — NOT part of the prompt)

  Everything inside these <!-- ... --> comments is for you. Your editor greys
  them out, so what's left in plain text is the prompt itself.

  1. Rename CLAUDE.md-example -> CLAUDE.md so your agent reads the conventions.
  2. The plain text below is a *partial* prompt. Hand it to your coding agent
     to build 07-validate-and-retry.py.
  3. It's deliberately incomplete. The decisions listed at the bottom are left
     out on purpose — that's the exercise. Work them into the prompt (or into
     follow-up turns with the agent) yourself.
  4. When you think it's done: run `python 07-validate-and-retry.py`, then
     invoke the validate-lab skill to score it against the reference.
─────────────────────────────────────────────────────────────────────────── -->

# Build: 07-validate-and-retry.py

Summarize a customer-support call transcript into JSON, then make the call
production-safe.

Build a single script that:

- forces the model (Bedrock Converse) to return JSON matching
  `data/call_summary_schema.json` — the structured data comes back in a
  tool-call block, not as plain text
- validates that JSON against the schema before the code trusts it
- retries the call, with backoff, when it fails for a reason worth retrying

Inputs:

- `data/call1.txt` — the transcript to summarize
- `data/call_summary_schema.json` — the shape the output must match (nested
  objects, an enum, a nullable field, `additionalProperties: false`, …)

Use the standard shape from the rest of this lab: read `BEDROCK_MODEL_ID` /
`AWS_REGION` from the environment, run from a `main()`, print the result as
indented JSON.

<!-- ▢ YOU DECIDE — left out of the prompt on purpose; this is the exercise:
       - which library/validator enforces a JSON Schema, and which draft
         matches the one declared in the file?
       - which Bedrock failures count as "transient" (worth a retry) vs. ones
         that will fail identically every time (fail fast)?
       - is a *validation* failure something you'd retry the model on? justify.
       - backoff curve + how many attempts before you give up?
     Don't leave these blank — fold the choices you make into the prompt above. -->
