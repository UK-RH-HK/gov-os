---
id: EXP-hook-time-limit
type: research
status: ACTIVE
state_class: EVIDENCE
---

# Evidence record: what Claude Code does with a PreToolUse hook that passes its time limit

- **Ordered by:** DEC-578 (owner, delegated to the orchestrator; a delegated experiment under DEC-102).
- **Run:** 2026-10-09, by the orchestrator, on this machine, with Claude Code 2.1.288 (headless, `-p`, model
  `claude-haiku-4-5-20251001`, `--allowedTools "Bash"`). Nothing of this repository was touched: three
  throwaway projects under `/tmp/gov-hook-timeout-exp/`, each with a settings file of its own that
  registers one PreToolUse hook for the Bash tool with a time limit of 5 seconds. Each session was asked to
  run one command that creates a file `ran.txt` in its project.

## Question

When a PreToolUse hook is still running at its time limit, does the harness allow the tool call, block it,
or end with an error?

## Result

**The call is allowed.** The hook's process is ended at the limit and the tool call runs as if no hook had
answered. This holds also for a hook that would have refused: the refusal is lost.

| Project | The hook | Did the hook finish | Was the command run | What the session saw |
|---|---|---|---|---|
| a | writes "started", sleeps 25 s, would exit 0 | no ("started" only) | **yes** (`ran.txt` exists) | an ordinary tool result, no error |
| b | writes "started", sleeps 25 s, would refuse (exit 2 with a message) | no ("started" only) | **yes** (`ran.txt` exists) | an ordinary tool result, no error |
| c (control) | writes "started", refuses at once (exit 2 with a message) | yes | no | the tool result is the hook's refusal |

Whole sessions took 10.9 s (a), 15.6 s (b) and 5.7 s (c), so the wait for the hook ended near the 5 seconds
set, not at the 25 the hook slept. No line of the session's output names the timeout: neither the model nor
a reader of the stream is told that a hook did not answer.

## What it means for the guard

- A guard decision that takes longer than the hook's time limit **fails open**. DEC-110 and DEC-179 recorded
  this from reading; it is now observed.
- The time limit that applies to this repository's guard hooks is not known to any agent (the settings file
  is not read by agents, DEC-525). An explicit limit is to be set through the owner (DEC-578).
- The read rule's own decision stays under 0.4 s for every slow input the reviewer of W1-02's root-search
  round found (DEC-571). The older held-out check took 40 s and more for a megabyte of path-like text in a
  field that is not a path; DEC-574 orders that changed in the current round.

## Limits of this evidence

One version of the harness, one tool (Bash), one hook per call, headless mode, one run per project. Not
observed: a hook's time limit when none is set; several hooks on one call; an interactive session; other
hook events.

## How to repeat it

The script is kept with the orchestrator's working files (`exp-hook-timeout.py`, its output
`exp-hook-timeout.txt`): it writes the three projects' settings, starts one session in each and prints the
hook's log, whether `ran.txt` exists, and the tool result.
