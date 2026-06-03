<!-- ──────────────────────────────────────────────────────────────────────────
  HOW TO USE THIS FILE  (guidance to you, the student — NOT part of the prompt)

  Everything inside these <!-- ... --> comments is for you. Your editor greys
  them out, so what's left in plain text is the prompt itself.

  1. Rename CLAUDE.md-example -> CLAUDE.md so your agent reads the conventions.
  2. The plain text below is a *partial* prompt. Hand it to your coding agent
     to build 06-prompt-template.py.
  3. It's deliberately incomplete. The decisions at the bottom are left out on
     purpose — that's the exercise.
  4. When you think it's done: run `python 06-prompt-template.py`, answer the
     menus, then invoke the validate-lab skill to score it against the reference.
─────────────────────────────────────────────────────────────────────────── -->

# Build: 06-prompt-template.py

Turn a call summary into a small interactive tool — and build the prompt **as
code from constrained choices**, not from a free-text box where the user types
whatever they want.

Write the script as `06-prompt-template.py` at the root of your build repo (your
working directory) — that's where you'll run it from.

<!-- ▢ YOU DECIDE — left out of the prompt on purpose; this is the exercise:
       - which request dimensions become menus, and what options (with examples)
         does each offer?
       - what's the instruction fragment behind each option — i.e. what does
         picking it actually change in the assembled prompt?
       - what stays in the STATIC system prompt vs. the DYNAMIC builder?
       - WHY menus instead of a free-text request? What does constraining the
         input buy you? (Hint: a known set of inputs → predictable prompts →
         predictable output — the input-side cousin of the structured *output*
         you'll force in Lesson 3.)
     Don't leave these blank — fold the choices you make into the prompt above. -->
