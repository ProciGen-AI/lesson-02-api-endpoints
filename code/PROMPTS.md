# Sample prompts for Lesson 2 — API Endpoints

These prompts let you explore and modify the lab using a coding agent. Open this `code/` folder as the agent's working directory; `data/` holds `call1.txt`.

## Explore — understand what each exercise does

- **"In `01-http-raw.py`, what fields in the HTTP body are Gemini-specific, and which ones would have a Bedrock-equivalent? Map field-by-field."**
  Forces a side-by-side comparison of two providers at the raw HTTP layer — sets up why Converse exists.

- **"Compare `01-http-raw.py` and `02-basic-call.py` line by line. Which lines in 02 replace which lines in 01, and which lines in 01 disappear entirely (handled by boto3)?"**
  Makes the "what does an SDK actually do for you" question concrete.

- **"In `03-summarize.py`, what would happen if I removed the `system=[...]` block? What concrete change in the output would you predict, and why?"**
  Probes how a system prompt shapes output before the student runs an A/B.

- **"Compare `03-summarize.py` and `04-streaming.py` line by line. Which lines are identical, which change, and what does the diff tell you about how streaming relates to the underlying Converse call?"**
  Surfaces that streaming is the *same call shape* with a different response delivery — not a different API.

- **"Compare `04-streaming.py` and `05-reasoning.py` line by line. Which single block turns reasoning on, and where in the event stream do the `reasoningContent` deltas appear versus the `text` deltas?"**
  Isolates the one knob (the `reasoningConfig` block in `additionalModelRequestFields`) and the new stream shape — the `reasoningContent` block streams *before* the answer (on Nova its text is redacted to `[REDACTED]`).

- **"In `06-prompt-template.py`, the request is driven by three menus (focus / format / length), not a free-text box. Trace how a menu choice becomes part of the prompt: which dict holds the options, where the chosen fragment is spliced in (`build_request_prompt`), and what stays in the static `SYSTEM_PROMPT`. Why does constraining the input to menus make the output more predictable than 'type what you want'?"**
  Surfaces both ideas at once: the static-prefix vs. dynamic-payload split, and "constrain the input → predictable output" — the input-side cousin of Lesson 3's structured output.

## Modify — change the code to see a concept in action

- **"In `03-summarize.py`, raise `temperature` from 0.3 to 1.0 and run the script 3 times. Then drop it to 0.0 and run 3 times. Report what changes."**
  The fastest way to feel what temperature actually does on the same prompt.

- **"Take the system prompt from `03-summarize.py` and apply it to `02-basic-call.py`. Keep the `What is 2+2?` user message. What changes in the output, if anything?"**
  Highlights that a system prompt influences *style*, not just *content* — the math answer becomes summary-shaped.

- **"In `04-streaming.py`, count tokens-per-second as they arrive (use `time.monotonic()` around the loop). Compare against `03-summarize.py`'s wall-clock time for the same prompt. Where does the latency win come from?"**
  Makes the "why stream" case quantitative.

- **"In `05-reasoning.py`, set `REASONING_EFFORT` to `'low'`, then `'medium'`, then `'high'`, running each. The reasoning text is redacted, so watch the **token counter** instead — how does the hidden-reasoning count change, and does the final answer stay correct? Then delete the `additionalModelRequestFields` block and re-run — what happens to the reasoning count and the `--- REASONING ---` section?"**
  Makes reasoning effort tangible through *cost*: higher effort → more (invisible) reasoning tokens; removing the block turns reasoning off (no `reasoningContent`, reasoning tokens → 0).

- **"In `05-reasoning.py`, set `REASONING_EFFORT = 'high'` and force `inferenceConfig={'maxTokens': MAX_TOKENS}` (drop the conditional), run it and read the error, then explain why **high** effort forbids `maxTokens`/`temperature`/`topP` and what the fix is."**
  Turns the Bedrock constraint (high-effort reasoning needs those params unset) into a hands-on `ValidationException` rather than a footnote.

- **"In `06-prompt-template.py`, add a fourth menu — `AUDIENCE` (e.g. 'executive', 'frontline agent', 'legal') — with an instruction fragment per option, wire it through `choose()` and `build_request_prompt()`, and run it. Did the new dimension change the output? How few lines did adding a whole dimension take?"**
  Shows the payoff of options-as-data + one builder: a new request dimension is a small, local change.

- **"In `06-prompt-template.py`, replace one menu with a free-text `input(\"Describe what you want: \")` spliced straight into the prompt. Run it a few times with vague requests, then compare the output's consistency against the menu version. What did you give up by un-constraining the input?"**
  Makes the determinism point concrete by breaking it — free text → unpredictable shape, the opposite of the menu's known input space.
