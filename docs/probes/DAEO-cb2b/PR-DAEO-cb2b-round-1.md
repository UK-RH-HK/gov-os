---
type: probe
task: DAEO-cb2b
reviewer_session: 0a387cad-2575-467f-8271-f858c654f95b
implementer_session: fe729e23-6763-475f-bcd4-65b9b9156251
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 1ec89f0efdbbb522e85f19941b715fc58ef642f9
decisions_applied: DEC-1007, DEC-1010, DEC-1014
---

# Probe record: W2-121 part a, round 1 (`gov dispatch tick` and `gov dispatch status`)

A fresh Independent Auditor session (`0a387cad-2575-467f-8271-f858c654f95b`, claude-opus-5-5, effort high, read-only, class C2) probed head `1ec89f0efdbb` and wrote nothing (`git status --porcelain` was empty at the end). Its one refused write was a `mkdir` of a folder that already existed.

The implementers were two engineer sessions:
- `fe729e23-6763-475f-bcd4-65b9b9156251` wrote the core, `30c0ed454`.
- `8d0899e9-10d9-46bb-986a-29de81f4ffe2` wrote the lock-first fix, `63130cf2d`.

The acceptance tests are the independent test designer's, `0384e71db` (session `42df48ad-9970-46f3-9d95-fd1f108f8400`). They are unchanged since that commit.

The findings are judged against ADR-0001's threat model (DEC-801).

## What was probed

- **Ticket, scope and baseline.** The auditor read the ticket's S1–S10 and F1, its Part a, Interface and P-W2-121-5 sections, all 11 files of `src/gov/dispatch/`, the lead's interface readings, and both test folders.
  - Scope: `git diff --name-only 2a35ec307 1ec89f0efdbb` lists only `src/gov/dispatch/**`, `tests/unit/dispatch/**` and `tests/acceptance/W2-121/**`.
  - S6 grep: this repository's branches, paths and ids over `src/gov/dispatch/` find 0 lines.
  - Baseline: `tests/acceptance/W2-121` and `tests/unit/dispatch` gave 189 passed.
- **Four planted scenarios and 21 planted mutations**, all on copies under the sandbox's temporary folder.
  - The tests caught 17 of the 21 mutations, among them the lock, OFF, the claim, the unread, running and room checks, the list order, the peaks ahead, the peaks' refresh, the round count, the timeouts, never-ran once, and the max_leads count.
  - The acceptance tests missed two: the gate check removed, and a list line with more than four fields accepted. The unit tests catch both.
- **Sound as probed:**
  - the lock and the losing pass;
  - OFF read before the lock;
  - the start recorded before the spawn, and a crash before the spawn becoming one never-ran item;
  - timeouts that kill the whole process group;
  - atomic writes of the status, the items and the peaks;
  - the identity marker matching `build_lead_settings`;
  - one start per pass, in list order, with every skip named;
  - the room formula, with the floor and working size read from `gate.json`;
  - S7's round count;
  - no watcher process.

## What it found

**F-1 (blocking, S4): a deleted inbox item comes back as unread.**
- `returns.py:109` and `:146` treat an item as already written only while its file is in `inbox/` or `inbox/read/`. `never-ran.txt` is written but never read.
- Planted: a finished return was read (moved to `inbox/read/`) and then deleted. The next pass wrote the same item into `inbox/` again as unread.
- Ordinary work: yes, because removing a handled item or pruning `inbox/read/` is ordinary.
- Consequence: fails open. The item is duplicated, the W2 is held as "unread return", and it is escalated again.

**F-2 (blocking, S4): a failed notification is never retried.**
- `returns.py:166` appends to `escalated.txt` before the notifier runs.
- Planted: the notifier exited 1 once. On the next pass, with a working notifier, it was called 0 times, and the problem was gone from the status.
- Ordinary work: yes, because a push service failing for a moment is ordinary.
- Consequence: fails open. The owner is never pushed about the unread item.

**F-3 (major, S5): a missing notifier hides the starts.**
- `notifier_command` is optional at load (`config.py:133`), but `returns.py:165` raises a configuration error in the middle of the pass, after the start.
- Planted: two passes started W2-1 and W2-2. Each exited 2, and the status said only `PASS FAILED`, without the starts or the running sessions.
- Ordinary work: yes. Consequence: other.

**F-4 (major, S9): an untracked path counts as resolved.**
- At `returns.py:85`, a path that is not committed but is on disk in the worktree counts as resolved.
- Planted: a return named two paths, one untracked and one missing. The item named only the missing one.
- Ordinary work: yes (a forgotten commit). Consequence: other.

**F-5 (minor, S6): the acceptance tests do not catch a removed gate check.**
- The shut-gate cases (`tests/acceptance/W2-121/test_s2_start_rules.py:346`) plant only a memory-shut gate and accept a "memory" reason. With the gate check removed they still pass. A unit test catches it.
- No load-, CPU- or GPU-shut gate is planted anywhere.
- Consequence: other (latent).

**F-6 (minor, S9): a hung git leaves a misleading item.**
- At `returns.py:128`, a hung git while resolving writes every id and path as `unresolved:` into a permanent item. The fault shows only in that pass's status.
- Ordinary work: rarely. Consequence: other.

Also noted: nothing in `src/gov` writes the job history (`history.jsonl`) that S3's peaks read. Until something does, a lead's peak is the gate's working size.

## Judgement

**Fail.** S4 fails on F-1 and F-2. Both are in scope, both are hit in ordinary work, and both fail open. The other KPI lines pass as probed, with F-3 to F-6 recorded against S5, S6 and S9.

By DEC-1010 item 1, the next round is the second and last. It starts with a test-design batch that is given each finding as a behaviour to test.

The ticket lead checked F-1 and F-2 against the code at `1ec89f0efdbb` and confirms both.
