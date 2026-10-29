---
type: probe
task: DAEO-kl5e
reviewer_session: 621773c3-6783-4280-ac9c-0ff58adb1967
implementer_session: d5d425fa-5790-4340-8e17-9e72c616f73c
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 56240ffb7d02bf5dd0e841da8db10d9a4d177eca
---

# Probe record: W2-50, the resume's fresh FULL probe — the merge-back and DEC-853's scan fix

## What was probed
- Head `56240ffb` on `w2/W2-50`: the merge-back `e61b67f5`, the ticket file `c2b094da`, DEC-853's tests `878467c9` and change `a403309e`. A fresh read-only reviewer (independent-auditor, session 621773c3-6783-4280-ac9c-0ff58adb1967, 2026-10-20), sandboxed launch, code under test this worktree's `src/` (DEC-732). The change's engineer was session d5d425fa-5790-4340-8e17-9e72c616f73c.
- The merge-back against git's own merge; the outward merge against `w2/integrate` at `7bb02cb7`; the probe gate as W2-01 and W2-53 left it, read against this history.
- The scan, run in temporary projects with a temporary HOME and canaries made at run time:
  - SQLite stores with `-wal` and `-journal` files, an open or killed writer, and a file swapped mid-scan;
  - the reuse key under changes of the rules, an extended rules file, the gitleaks binary and the environment;
  - the record damaged, copied, raced by two checks, and checked for growth;
  - fails-closed cases;
  - links, including into a temporary `~/gov-os-runs`;
  - the reuse label;
  - the time limit, the pool and memory, on stand-ins of today's stores (260 MB `store.db`, 210 MB code graph, 7,600 files);
  - the runner's own timeout;
  - the pre-run-8 module side by side with the head's.
- Suites: W2-50 636 passed (DEC-853 file 23 passed, its 3 large cases run alone); `tests/unit/secrets` 26 passed; W1-15 124 passed; W1-17 65 passed. W1-16 cannot run in the sandbox (its folders are under `/tmp`, read-only there; every failure seen was that). The lead's own verification at this code ran W1-16 outside the sandbox: 167 passed.

## What it found
- **F1 (medium).** A SQLite store's clean result is reused because its main file is unchanged, though rows still in its write-ahead log hold a secret that stands across a WAL page boundary. The check is green; the pre-run-8 scan names the store. A secret whole inside the WAL is still found through the `-wal` file.
  Ordinary work: no, because it needs a secret past the pre-index filter, a WAL-mode store with frames not yet checkpointed during the check (only the external code-graph tool writes WAL), its main file unchanged since a clean scan, and the secret across a WAL page boundary, all at once.
  Consequence: fails open.
- **F2 (low).** `gitleaks stdin` misses different tokens in identical bytes depending on input timing, and reuse lets the first scan decide for later runs. Not reproduced end to end: 24 of 24 first scans by the check found the token.
  Ordinary work: no, because it needs a secret past the filter and a moving fragment boundary inside its only occurrence in that first scan.
  Consequence: fails open.
- **F3 (low).** A rules file that `.gitleaks.toml` extends by `path` is outside the reuse key: after it gains a rule, an unchanged store stays green.
  Ordinary work: no, because this repository and the kernel extend gitleaks' built-in defaults, never a file by path.
  Consequence: fails open.
- **F4 (low).** A store's rows are read after its bytes are hashed; a file replaced in between records clean bytes whose rows were never read. Shown by forcing the swap.
  Ordinary work: no, because it needs a writer inside that window and the same bytes returning later.
  Consequence: fails open.
- **F5 (low).** The reuse label echoes a clean file's name, so a secret in a file name under `.gov-runtime/` is printed on standard error.
  Ordinary work: no, because names there are made by tools.
  Consequence: other.
- **F6 (medium).** On the runner's timeout the check is RED, but the scan is orphaned (dash forks; only the shell is killed). It runs on with its gitleaks children and writes the record afterwards (only content it scanned clean).
  Ordinary work: yes, because a first full scan of stores at today's size takes minutes and may meet the declared limit under load.
  Consequence: other (fails closed).
- **F7 (low).** First full scans are within the limit but not far from it. "Decided at 1 MB/s" holds per gitleaks run, not for SQLite stores within the check's 900 s.
  Ordinary work: yes, because first full scans follow a rebuild, a rules change and a fresh worktree.
  Consequence: other (fails closed).
- **F8 (low, pre-existing).** A file that vanishes during the walk (for example a rotated hook snapshot) fails the check.
  Ordinary work: yes, because a lead may check while its worker makes tool calls.
  Consequence: other (fails closed).

## Found sound
- The merge-back equals git's own merge (no conflict), keeps every ticket path, and drops nothing of `w2/integrate`.
- The outward merge is clean and leaves the ticket's paths as at this head.
- The probe gate: this record makes the failed record (probing `fc9e6a2a`) an earlier round; `c2b094da` and `e61b67f5` lie before the probed head; nothing after it touches the ticket's paths.
- The scan: limits grow with size; the pool is bounded, largest first, at most two large files at once; a one-byte change is scanned in full; a finding is never recorded; damaged, copied and concurrent records are handled; every failure fails closed and records nothing.
- The indexers' filter and the path check decide as before; the link rule is unchanged; no content is printed.

## The lead's notes (judged by the orchestrator role, from the reviewer's return)
- The reviewer's F6 and F7 cited "876 s of 900 s" as a first full scan. 876 s was the whole first `gov check` after the rebuild (every declared check). The secrets scan alone on this worktree's real stores after the rebuild (`store.db` 258.5 MB, `code.db` 212.7 MB), with no record read or written, took 482.8 s at a 1-minute load of 7 to 28. The check alone with the record took 4.6 s (8,420 clean results reused, `store.db` and `code.db` labelled with their digests). The second `gov check` took 319 s. Both `gov check` runs: secrets-indexing GREEN. F6 and F7 stand as rows, with this figure.
- Judged under the judgement rules (`governance/project/briefs/JUDGEMENT.md`), DEC-779, DEC-785, DEC-790 and DEC-801: no finding is "Ordinary work: yes" with "fails open" or "loses work". F1 to F8 are rows, returned to the orchestrator.

## Judgement
- **pass.** No finding is both reachable in ordinary work and failing open or losing work (DEC-779, DEC-785, DEC-790, DEC-801). F1–F8 are rows; F1's fix is to never reuse a SQLite store with a `-wal` or `-journal` beside it.
