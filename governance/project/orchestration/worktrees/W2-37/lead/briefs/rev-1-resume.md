The lead has resumed this same session outside the sandbox (the owner's launch form, known limit P-W2-38), so `gov.codeintel.index` can now build a code graph for a temporary repository in your temporary folder. Every rule of your first brief still holds: you write nothing in the repository, everything runs in the foreground, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` is set per command, and the head is still `6b5640b0b0662a4d81ff0415f454acd9731db7a0` (check it with `git rev-parse HEAD`, and quote `git status --short` at the start and the end). There is no sandbox now, so take extra care: write only under your own temporary folder (make one with `mktemp -d` and say its path), never in this worktree, any other worktree, the main tree or `~/gov-os-workbench`.

DEC-732, the code under test: in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.

Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round. Only a finding an honest agent can hit in ordinary work, and that fails open or loses work, justifies a round.

Ask of every finding these two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?" Every finding carries the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

Run now the four code-graph probes you listed as unresolved:
1. F1 carried to `complete: true`: an uncommitted ticket that implements DEC-001 (and/or an uncommitted edit dropping an edge), then a current code index built, then `gov impact DEC-001`: does the report read `complete: true` and `graphs.record: ok`?
2. The symbol name clash: a live symbol sharing its bare name with a dead one: is the live one read as deletable, and what radius, depth and affected lists result (anything dropped, or only gaps)?
3. An error from the code index's callers or callees during the walk: a refusal, a gap, or a traceback; and does the report still read complete?
4. A code file changed with its modification time kept: is the code graph still called `ok`?
Also run the 13 `local_only` cases of the acceptance suite once: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -rs -m local_only` and give its counts.

Refused twice for the same call: stop and say so; no third try.

Then give your full return again, covering the whole review (F1 to F5 as before, plus anything new, each with its two lines), with the judgement by the rule of your first brief. One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
