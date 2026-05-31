# Sample prompts for Lesson 2 — API Endpoints

These prompts let you explore and modify the lab using a coding agent. Open this `code/` folder as the agent's working directory; `data/` holds `call1.txt`, the schema files, and `customer_crm.json`.

## Explore — understand what each exercise does

- **"In `01-http-raw.py`, what fields in the HTTP body are Gemini-specific, and which ones would have a Bedrock-equivalent? Map field-by-field."**
  Forces a side-by-side comparison of two providers at the raw HTTP layer — sets up why Converse exists.

- **"Compare `01-http-raw.py` and `02-basic-call.py` line by line. Which lines in 02 replace which lines in 01, and which lines in 01 disappear entirely (handled by boto3)?"**
  Makes the "what does an SDK actually do for you" question concrete.

- **"In `03-summarize.py`, what would happen if I removed the `system=[...]` block? What concrete change in the output would you predict, and why?"**
  Probes how a system prompt shapes output before the student runs an A/B.

- **"Compare `03-summarize.py` and `04-streaming.py` line by line. Which lines are identical, which change, and what does the diff tell you about how streaming relates to the underlying Converse call?"**
  Surfaces that streaming is the *same call shape* with a different response delivery — not a different API.

- **"In `05-structured-output.py`, walk through what `toolChoice` does. What would happen if I deleted it? Show me the exact response shape difference."**
  The `toolChoice` line is the load-bearing piece of "structured output" on Bedrock — most students skim past it.

- **"Compare the inline `SCHEMA` dict in `05-structured-output.py` against `data/call_summary_schema.json` used by `06-rich-schema.py`. List the schema features that 06 introduces (nested objects, arrays of objects, enums, nullables, etc.) and what each one buys you."**
  Makes the simple-vs-production schema jump explicit so students see schema design as its own concern.

- **"In `07-validate-and-retry.py`, the `_should_retry` predicate retries on schema-validation errors. Why is that a reasonable thing to do? When would it be a bad idea?"**
  Surfaces the trust-but-verify pattern and its limits (e.g., a deterministically-wrong prompt won't fix itself by retrying).

- **"Compare `06-rich-schema.py` and `07-validate-and-retry.py` side by side. Which lines in 07 are about validation, which are about retrying, and what would break if you kept the retries but dropped the schema validation?"**
  Forces the student to separate the two productionization concerns and see that they're independent layers.

- **"In `04-streaming.py`, what would I need to change to stream a structured-output call from `05`-`07` instead of plain text? Specifically, where would the `toolUse` data appear in the event stream?"**
  Connects 04 to the structured-output trilogy. Answer involves `contentBlockStart` events with a `toolUse` field — students rarely discover this on their own.

- **"In `08-context-enrichment.py`, the prompt is split into a static `SYSTEM_PROMPT` (in `prompts.py`) and a dynamic `build_user_prompt()`. Why is that split the whole point of the exercise? What goes in each half, and what breaks if you move CRM data into the system prompt?"**
  Surfaces the static-prefix (cache-friendly) vs. dynamic-payload distinction — the core idea of 08.

- **"In `prompts.py`, `build_user_prompt()` reads CRM data passed in as a dict. The docstring calls it the 'retrieve → assemble → render' seam. If the CRM came from a live API instead of `customer_crm.json`, what would change in this function — and what wouldn't? Why is that a good property?"**
  Drives home that data access belongs in the builder, and rendering stays pure.

- **"In `08`'s output for `call1.txt`, `cross_sell_opportunities` came back empty even though the customer doesn't hold auto or life. Trace the rules in `SYSTEM_PROMPT` that produced that. Where did the cross-sell reasoning go instead?"**
  Shows the system-prompt rules genuinely shaping output — the model deferred the upsell into `personalized_next_actions` because a claim is open.

## Modify — change the code to see a concept in action

- **"In `03-summarize.py`, raise `temperature` from 0.3 to 1.0 and run the script 3 times. Then drop it to 0.0 and run 3 times. Report what changes."**
  The fastest way to feel what temperature actually does on the same prompt.

- **"Take the system prompt from `03-summarize.py` and apply it to `02-basic-call.py`. Keep the `What is 2+2?` user message. What changes in the output, if anything?"**
  Highlights that a system prompt influences *style*, not just *content* — the math answer becomes summary-shaped.

- **"In `04-streaming.py`, count tokens-per-second as they arrive (use `time.monotonic()` around the loop). Compare against `03-summarize.py`'s wall-clock time for the same prompt. Where does the latency win come from?"**
  Makes the "why stream" case quantitative.

- **"In `05-structured-output.py`, add a fifth field `escalation_needed` (boolean) to the inline `SCHEMA` dict and update the system prompt to ask for it. Run the script. Did the model fill it in correctly for `call1.txt`?"**
  Practices the smallest edit cycle for structured output: add a field, update the prompt, observe.

- **"In `06-rich-schema.py`, edit `data/call_summary_schema.json` to add a required field `urgency` with enum `[low, medium, high]`. Run the script. Did the model fill it in? How would you verify it's not just guessing?"**
  Teaches that the schema is a contract the model will follow — and forces them to think about ground truth.

- **"Add a fifth retry case to `07-validate-and-retry.py`'s `_should_retry`: retry if the model returned a `text` block instead of a `toolUse` block. Force the failure by temporarily changing `toolChoice` to `{\"auto\": {}}`. Verify the retry kicks in."**
  Drives home the difference between `toolChoice: tool` (forced) and `toolChoice: auto` (suggested).

- **"In `08`, edit `data/customer_crm.json` so the customer already holds `auto` and `life` (add them to `products_held`). Re-run. How do `cross_sell_opportunities` and `personalized_next_actions` change? This shows the model reading the CRM, not guessing."**
  The cleanest demonstration that the enrichment is doing work — change the data, watch the recommendations follow.

- **"In `08`, change `customer_crm.json` to a brand-new customer (`tenure_years: 0`, no open claims, no churn signals). Re-run and compare `churn_risk` and the recommendations to the original. What did the CRM context change?"**
  Isolates the effect of the relationship context on the assessment.

- **"In `prompts.py`, the static `SYSTEM_PROMPT` says 'never recommend a product the customer already holds.' Delete that rule and re-run `08` with the original CRM. Did the model start recommending homeowners (which they hold)? What does that tell you about how load-bearing each rule line is?"**
  Makes the system prompt's rules tangible by removing one and watching the output drift.

- **"In `08-context-enrichment.py`, wrap `analyze_call` in `tenacity` retry the way `07` does. What exceptions should trigger a retry here, and which should fail fast? Explain your `_should_retry` predicate."**
  Connects 08 back to 07's productionization — 08 deliberately left retry out to stay focused.
