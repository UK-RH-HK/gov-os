# Brief: product-spec fix for DAEO-wahn (W2-175), round 1, one named red

You are a fresh **product-spec** session (template `role-product-spec` 1.0.0, in your system prompt), started by the ticket lead to fix one red in the change record the previous product-spec session wrote (commit `c816990fcdb4`). Where this brief and the copied `EMG-common.md` / `EMG-d4b-launched.md` differ, **this brief holds** (your `Implements:` is the list below, not `DEC-1065`).

## Identity
- Check: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec`, `DAEO-wahn`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-175`, `w2/W2-175`). Different: stop and say so.
- **Step 0, the sandbox check, reported first in your return:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wahn','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop and return.

## The one path you may write
`docs/changes/W2-175-CIT-P.md`. Nothing else: not the templates (their bytes are final and their sha256 are in the record), not `tests/`, `.tickets/`, `.claude/`, the register.

## The failing output (the acceptance run's result; you never read `tests/acceptance/W2-175/`)
`gov accept DAEO-wahn` on head `ac461dd324ee`: success-1 to success-5 and failure-1 pass; **success-7 fail, 0 passed, 18 failed**. Every success-7 case fails reading the record's front matter:
```
yaml.scanner.ScannerError: mapping values are not allowed here
  in "<unicode string>", line 12, column 22:
    state: draft (round 1: the text; the review, the appr ...
                         ^
```
(line 12 of the front matter block, i.e. file line 13: an unquoted YAML value holding `: `.)

## What to do
1. Make the front matter of `docs/changes/W2-175-CIT-P.md` valid YAML without changing its meaning: the `state:` value must not hold a bare `: ` (rephrase it as W2-128's record does, e.g. `state: draft (round 1, the text; the review, the approval and the promotion are pending)`, or quote it). Check every other front matter line the same way. Change nothing else in the file (the sha256 table stays as it is).
2. Check: a script file under `/home/usain/gov-os-worktrees/W2-175/.gov-runtime/scratch/` (that folder exists; Write tool) that loads the front matter with `yaml.safe_load` and prints `status`, `decisions_read`, `decisions_carried`; run it with `python3 <file>`. Then run `env PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src gov accept DAEO-wahn --root /home/usain/gov-os-worktrees/W2-175` once and report its per-line reading (names, pass or fail, messages only). If the sandbox refuses `gov accept`, say so and stop after the YAML check.
3. Commit: `git commit -m "W2-175: CIT-P record front matter parses as YAML (the state line)" --trailer "Task: DAEO-wahn" --trailer "Role: product-spec" --trailer "Implements: DEC-1137, DEC-820, DEC-861, DEC-1116, DEC-1073, CAP-33" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- docs/changes/W2-175-CIT-P.md`. Before it: `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit`. Never amend, rebase, merge, push or `--no-verify`.

## Rules
- Policy 2 (c): never read `tests/acceptance/W2-175/` (every Grep/Glob excludes `!tests/acceptance/W2-175/**`; recursive searches `--exclude-dir=W2-175`); if a line from there shows anyway, stop reading it and say so. (d): never the hidden half of an evaluation set (`~/gov-os-eval`), the held-out material's contents, or a secret.
- DEC-732, word for word: **every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-175/src` set per command.**
- Memory: `gov retrieve` is not available in your sandbox (DEC-1065): Read and Grep; search again once in different words if a search does not answer; two searches in all (DEC-1092 (1)). DEC-849: a refused read is taken, never re-spelled; count it.
- Command forms: one simple command per Bash call; no `cd ... &&`, here-documents, backticks, `$(...)` or shell variables as a write target; no long inline `python3 -c` with braces.
- Row W2-L423's rule (DEC-911): in your return, commit hashes and sha256 as 12 digits; never the keywords of the secrets rule that takes a bare 40-hex string.
- Scratch budget (DEC-898): 200 MB and 10,000 files; clean as you go. No installs.
- **Refused twice for the same call: stop and say so. Never work around a refusal: report it.**

## Return (your last message; nothing else is read)
Sandbox check first; in `evidence` the commit (12 digits) with trailers, the YAML check's output, `gov accept`'s per-line reading.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
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

The twelve fields come first, each as a labelled line, any payload after them. Refused twice for the same call: stop and say so.
