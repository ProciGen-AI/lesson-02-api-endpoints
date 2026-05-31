---
name: validate-lab
description: Validate a student's finished rebuild of Lesson 2 exercise 07 (validate-and-retry) against the reference lab. Scores the build out of 100 (can exceed 100 if it beats the reference), reports what's missing, weaker, or better per check, and offers a cheat prompt to close the gap.
---

# Validate Lab — Lesson 2, exercise 07 (validate + retry)

Score a finished `07-validate-and-retry.py` against the reference build — out of
100 — and report where it's missing, weaker, or better.

## What you're validating

The student's job was to build one script that (1) gets **tool-forced structured
output** matching `data/call_summary_schema.json`, (2) **validates** that output
against the schema, and (3) **retries** the call on failures worth retrying, with
backoff. The interesting, load-bearing decisions are in (2) and (3); (1) is the
foundation they were given.

## Locate the two builds

- **Student build:** `07-validate-and-retry.py` in the current working directory
  (the `SDD/` folder). If it's not there under that name, take the single `.py`
  build the student wrote here; if there's more than one and it's unclear, ask
  which is theirs rather than guessing.
- **Reference build:** `07-validate-and-retry.py` in the sibling `code/` folder of
  this lesson (`../code/07-validate-and-retry.py` from `SDD/`). If you can't find
  it, tell the student you're validating structure-and-behavior only, and skip the
  side-by-side semantic comparison.

Both use the same data: `data/call1.txt` and `data/call_summary_schema.json`.

---

## Check 1 — Structural / behavioral comparison (40 pts)

Read both files and confirm the student's build has the load-bearing pieces.
Award points; note anything missing concretely.

- **Tool-forced structured output (8):** declares one tool whose `inputSchema` is
  the loaded schema, and sets `toolChoice` to force that tool. Reads the result
  out of the `toolUse` block (not `text`), and raises if no tool call came back.
- **Schema loaded from the file (4):** `data/call_summary_schema.json` is read at
  runtime, not copy-pasted inline. (Inline is weaker — note it but don't fail it.)
- **Validation against the schema (12):** the returned object is validated against
  the schema *before* it's trusted, using a real JSON Schema validator (e.g.
  `jsonschema`) bound to the draft the file declares
  (`https://json-schema.org/draft/2020-12/schema` → `Draft202012Validator`). A
  validator that ignores the draft, or a hand-rolled "check a couple of keys"
  pass, is weaker — it won't catch enum/`additionalProperties`/`minItems`
  violations. Score on how completely it enforces the schema.
- **Retry with backoff (12):** the call is wrapped so it retries on a *defined set*
  of failures, with exponential (or at least incremental) backoff and a cap on
  attempts. Using `tenacity` is the reference path; a correct hand-rolled loop is
  fine and can score full marks.
- **A retry predicate that discriminates (4):** retries are gated by a predicate
  that distinguishes retryable from non-retryable failures — **not** a blanket
  "retry on any Exception." Blanket retry loses most of these points.
- **Config from env + dotenv (bonus, up to +3):** reads `BEDROCK_MODEL_ID` /
  `AWS_REGION` from the environment, loads `.env` via `find_dotenv()`, and fails
  with a clear message when the model ID is unset.

## Check 2 — Deterministic behavior (40 pts)

These have knowable answers and don't depend on model wording. Write a small
throwaway harness that imports the student's functions (adapt to their names) and
exercises each case. If a piece can't be imported cleanly, drive it via a tiny
script instead, but prefer importing.

**2a. The validator actually enforces the schema (16).** Build invalid objects and
confirm the student's validation step *rejects each one*. Use cases drawn from the
real schema:
- missing a required top-level key (e.g. drop `sentiment`);
- a bad `enum` value (e.g. `sentiment: "angry"` — not in the enum);
- an extra key under an `additionalProperties: false` object (e.g. add `foo` to
  `participants`);
- an empty `main_topics` array (violates `minItems: 1`).
A correct build raises a validation error on **all four**. Subtract for any it
lets through (that means the validation is too shallow). A build that hand-checks
only a few fields and passes some of these scores low here.

**2b. Retry classification (16).** Inspect how the student decides what to retry —
read the predicate, or call it with sample exceptions. Confirm:
- a **transient** Bedrock error is treated as retryable. Construct a
  `botocore.exceptions.ClientError` with `Error.Code` in
  `{ThrottlingException, ServiceUnavailableException, InternalServerException,
  ModelTimeoutException}` → should retry;
- a **deterministic** Bedrock error is **not** retried. A `ClientError` with code
  `AccessDeniedException` or `ValidationException` → should fail fast;
- the **validation-failure** decision. The reference *does* retry on a
  `jsonschema.ValidationError` (the model sometimes self-corrects on a re-roll).
  If the student also retries validation failures **and can justify it**, award
  full marks and note it as matching the reference's trust-but-verify design. If
  they deliberately *don't* and justify that too (a deterministically-wrong prompt
  won't fix itself), give most of the marks — it's a defensible call. Penalize
  only an unconsidered choice (retries on *everything*, or never retries at all).

**2c. Happy path (8).** Run the student's script end-to-end on `data/call1.txt`.
It must exit 0 and print JSON that validates against
`data/call_summary_schema.json`. (This makes a real Bedrock call — needs a working
`.env`, e.g. via `source setup.sh`. If credentials aren't available, say so and
skip 2c rather than guessing.)

## Check 3 — Semantic comparison of model output (20 pts)

Run **both** builds on `data/call1.txt`, capture both JSON summaries, and judge
them for *semantic* equality — the content is model-generated, so don't expect a
literal match. Compare field by field:

- `participants` — same agent (Marcus) and customer (David Miller);
- `sentiment` — same value, or an adjacent defensible one (`mixed`/`positive`);
- `main_topics` / `outcomes` — cover the same real events (premium increase &
  expired protective-device discount, the waived late fee + expired card,
  the escalated open claim, the declined water-backup upsell);
- `action_items` — capture the customer emailing the alarm certificate and the
  agent escalating the claim, with `due` correctly null where no date was given;
- `reference_ids` — include the policy number `88-Delta-4922` (and the claim if
  present).

Award full marks when the student's summary is as faithful as the reference's;
note any field where it's thinner or hallucinates something not in the transcript.

---

## Scoring and report

Total the four buckets into a score **out of 100** — and **let it exceed 100**
when the student's build is genuinely better than the reference. Award the bonus
for real improvements, e.g.:
- a cleaner / more readable retry predicate, or one that also handles the
  "model returned a `text` block instead of `toolUse`" case;
- clearer failure messages when retries are exhausted (distinguishing "gave up
  after transient errors" from "output never validated");
- validating with the streamed/iterative validator to report *all* schema errors
  at once instead of just the first;
- thoughtful handling the reference skips.

Report back, concretely and anchored in *this* exercise (never a generic diff):

1. **Score** (e.g. `92 / 100`, or `108` if it beats the reference) with a one-line
   justification per check.
2. **What's missing or weaker**, per check — name the exact gap ("your validator
   passed the bad-enum object through, so `sentiment: 'angry'` wouldn't be
   caught"; "you retry on `AccessDeniedException`, which will just burn 5 attempts
   on a permissions problem").
3. **What's better than the reference**, if anything — say so explicitly.

Then **offer a cheat prompt** the student can paste to bring their build up to (or
past) the reference — but tell them to use it **only if they're out of time**,
since closing the gap themselves is the whole point. The cheat prompt should name
the specific gaps you found, e.g.:

> "Update `07-validate-and-retry.py`: load `data/call_summary_schema.json` and
> validate the model's `toolUse` output with `jsonschema.Draft202012Validator`
> before returning it. Wrap the call with `tenacity` —
> `stop_after_attempt(5)`, `wait_exponential(multiplier=1, min=2, max=60)` — and a
> `retry_if_exception` predicate that retries on `jsonschema.ValidationError` and
> on `ClientError`s whose code is one of ThrottlingException /
> ServiceUnavailableException / InternalServerException / ModelTimeoutException,
> and fails fast on everything else. In `main`, catch a final `ValidationError`
> and exit non-zero with a clear message."
