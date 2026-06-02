---
name: validate-lab
description: Validate a student's finished rebuild of Lesson 2 exercise 06 (prompt-template) against the reference lab. Scores the build out of 100 (can exceed 100 if it beats the reference), reports what's missing, weaker, or better per check, and offers a cheat prompt to close the gap.
---

# Validate Lab — Lesson 2, exercise 06 (prompt template)

Score a finished `06-prompt-template.py` against the reference build — out of
100 — and report where it's missing, weaker, or better.

## What you're validating

The student's job was to build an interactive summary tool whose prompt is
assembled **as code from constrained menu choices**, not from a free-text
request. The reference offers three menus — **focus**, **format**, **length** —
each option carrying an instruction fragment; a **builder function** splices the
chosen fragments + the transcript into the user prompt, kept separate from a
**static** system prompt. The interesting decisions are the menu/constraint
design and the static/dynamic split — not the Converse call. The student may
have picked different dimensions or options; judge the *shape*, not the exact
labels.

## Locate the two builds

You're running from the lesson's **reference repo**, inside its `SDD/` folder — so
the answer key is local (`../code/`) and the student's build lives in a separate repo.

- **Student build:** the student built in a **separate** clean repo (the `…-sdd`
  repo they cloned). **Ask them for the path to it**, then read
  `<their-path>/06-prompt-template.py` — it reads its transcript from
  `<their-path>/data/call1.txt`. If they've `cd`'d into that repo the path may
  just be `.`; if there's more than one `.py` there, ask which is theirs.
- **Reference build:** `../code/06-prompt-template.py` — the worked answer sitting
  beside this `SDD/` folder in the same reference repo (its data is at
  `../code/data/`). If `../code/` isn't there, validate structure-and-behavior
  only and skip the semantic comparison.

---

## Check 1 — Structural comparison (45 pts)

Read both files and confirm the student's build has the load-bearing pieces.

- **Constrained menus, not free text (15):** the request is driven by a small
  set of fixed options the user *picks from* (≥2 menus; the reference has 3 —
  focus/format/length), each defined in one place (a dict/constant), each with a
  short example shown to the user. A free-text `input()` ("what do you want?")
  scores near zero here — defeating that is the whole exercise.
- **A prompt builder function (12):** a function that returns the user-message
  string, assembled from the chosen options + the transcript. Inline f-strings
  at the call site score low — the template must live in one named place.
- **Static system prompt (8):** a constant system prompt (role/rules), passed
  via `system=[...]`, that does **not** contain the per-call menu choices.
- **Input validation (6):** an out-of-range / non-numeric pick is rejected and
  re-asked, not crashed on or silently accepted.
- **Config from env + dotenv (bonus, up to +4):** `BEDROCK_MODEL_ID` /
  `AWS_REGION` from the environment, `.env` via `find_dotenv()`, clear message
  when the model ID is unset.

## Check 2 — Deterministic behavior (35 pts)

The builder is a **pure function** — exercise it with **no model call**. Import
it (adapt to the student's names); if it can't be imported cleanly, drive it
with a tiny script, but prefer importing.

**2a. Each choice reaches the prompt (20).** Call the builder with one concrete
combination of choices + the transcript. Confirm the returned string contains
the instruction fragment for *each* chosen option (the focus, the format, and
the length the student defined) and the transcript. A choice that's read but
never appears in the prompt is the headline bug — dock heavily.

**2b. Different choices → different prompts (15).** Call the builder with two
combinations that differ in at least one dimension; confirm the returned prompts
**differ** in the spot that dimension controls, while the system prompt stays
identical. Also confirm the menu/selection rejects an invalid pick (call the
chooser with a bad value, or inspect the validation branch).

## Check 3 — Semantic comparison of model output (20 pts)

Run **both** builds end-to-end, feeding the same menu picks via stdin — the
student build with
`printf '2\n3\n1\n' | python <their-path>/06-prompt-template.py`, the reference
with `printf '2\n3\n1\n' | python ../code/06-prompt-template.py` (each
resolves its own `data/call1.txt`). This makes
real Bedrock calls — needs a working `.env` (e.g. `source setup.sh`); if creds
aren't available, say so and skip this check. Confirm:

- each run summarizes the same call faithfully (David Miller / Marcus; premium
  increase, waived late fee, escalated water-damage claim);
- the deliverable **obeys the chosen options** — a "CRM note" has no
  greeting/sign-off, a "customer email" does; a "concise" pick is 1-2 sentences,
  a "medium" pick is a paragraph; the focus leads with the right material.

A build whose output ignores the chosen format/length/focus is weaker even if
each summary is individually fine.

---

## Scoring and report

Total the three buckets into a score **out of 100** — and **let it exceed 100**
when the student's build is genuinely better than the reference, e.g.:
- a fourth useful dimension, or options defined as a clean data structure that
  makes adding one a one-liner;
- a chooser that also accepts the option label (not just its number);
- a builder docstring that names the "constrain input → predictable output"
  rationale and the static/dynamic split.

Report back, concretely and anchored in *this* exercise (never a generic diff):

1. **Score** (e.g. `88 / 100`, or `107` if it beats the reference) with a
   one-line justification per check.
2. **What's missing or weaker**, per check — name the exact gap ("your `length`
   choice is collected but never spliced into the prompt, so every run came back
   the same length"; "the request is a free-text `input()`, so there's no
   constraint — that's the concept the exercise is testing").
3. **What's better than the reference**, if anything — say so explicitly.

Then **offer a cheat prompt** the student can paste to bring their build up to
(or past) the reference — but tell them to use it **only if they're out of
time**. Name the specific gaps you found, e.g.:

> "Refactor `06-prompt-template.py`: define three option dicts — `FOCUSES`,
> `FORMATS`, `LENGTHS` — each mapping a label to an instruction fragment. Add a
> `choose(label, options)` helper that prints a numbered menu (option + example),
> reads a pick, and re-asks on invalid input. Add
> `build_request_prompt(transcript, focus, fmt, length)` that splices the three
> chosen fragments + the transcript into the user message; keep a module-level
> `SYSTEM_PROMPT` (role only, no choices) passed via `system=[...]`. In `main()`,
> run the three menus, then print the model's deliverable."
