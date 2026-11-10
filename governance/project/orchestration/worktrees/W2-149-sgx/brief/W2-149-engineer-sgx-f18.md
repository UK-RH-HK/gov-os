Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the engineer's brief: the wiring review's F18 to F23 (DAEO-52ku)

You are a fresh engineer for **W2-149** (`.tickets/DAEO-52ku.md`). Set-up A's wiring is merged (`7f0e71519`). The CTO
decided (DEC-1112 (3)) that its review's **F18 to F23 are fixed now**, before the owner is asked for the install ACT.

What to read:
- The review: `.gov-runtime/scratch/ref/W2-149-sgx-review-r1.md` (F18 to F23).
- The ticket: the changed lines **S25** and **S27**, the new lines **S29, S30 and S31** (each marked
  `[changed, DEC-1112 (3)]`) and the last note.
- The interface: the test designer's interface section, copied for you as `.gov-runtime/scratch/lead/INTERFACE.md`.
  Build to it exactly.
- The five briefs: `.gov-runtime/scratch/ref/sgx1-briefs/`.

## What to build (in `indep_launch.py`, its unit tests and the evidence)
- **F18 (S25):** at labeller 1's round-1 delivery, run the same confined check on `out/label_rules.py` over the half's
  staged lines. A failure is `rejected`, 20, and nothing lands. Round 2 keeps its check.
- **F19 (S29):** a set-up A result whose `stopped` is not `none` delivers nothing: `rejected`, 20, every destination
  unchanged.
- **F20 (S30):** labeller 2's `labels-2.jsonl` is checked line by line against the staged sample before it lands, and
  stored with `rule_class` as an integer.
- **F21 (S27):** in the auditor's disputes, when either side's `reason` is empty, both are empty.
- **F22 (S27):** a settled case's line takes the auditor's `label`, `rule_class`, `clauses` (= `basis`) and `reason`,
  with `how: "audit"`.
- **F23 (S31):** `rule_class` is accepted as an integer 1–14 or a decimal string `"1"`–`"14"` everywhere a session
  writes one, and stored as an integer in every file the script writes.

Also:
- **F26 of the same review:** your network-wall unit test aims at the shared Ollama port 127.0.0.1:11434. Use a
  planted listener instead.
- Keep every other behaviour as it is, and keep the confinement code small and plain.
- Add an "F18-F23 (DEC-1112 (3))" section to `docs/changes/W2-149-evidence.md`.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149-sgx`, branch `w2/W2-149-sgx`, made from the designer's branch at `939da2755` (fast-forwarded; `w2/integrate` at `944f39165` with the F18-F23 cases).
  Your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-149/`.** You see only `gov accept`'s results and failure messages.
- **The exclusion line:** recursive grep carries `--exclude-dir=W2-149`; Grep and Glob carry
  `!tests/acceptance/W2-149/**` (a separate pattern).
- Never name the template's folder in a Bash line. Stage with `git add -u`.

## Verify
Run through the heavy slot `EMG-common.md` names, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx/src`, your
sandbox's TMPDIR, a scratch HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`:
1. `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx`. Expect every line green but
   the live and `bwrap` cases, which skip. A nested `bwrap` cannot start in your sandbox, so the lead runs those
   outside it after your return.
2. `tests/unit/orchestration/test_w2_149*`.

## Rules
- The hidden-half rule of `EMG-common.md`. Never run the script against the real `~/gov-os-eval`, `~/gov-os-runs`,
  `~/gov-os-wall-trees` or `~/.claude`. No real `claude` session. No GPU, network or installs.
- Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`. **DEC-1080:** one simple command per Bash call. Waits
  and stops by pid only. Do not merge `w2/integrate`.
- **Commit as you go**, on `w2/W2-149-sgx`, with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Report your scratch size.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`, first, as single-line labelled fields;
- the commits;
- `gov accept` per line;
- the unit counts;
- the script's sha256 (and the template files' sha256s, if you changed either; you should not need to).

Refused twice for the same call: stop and say so; no third try.
