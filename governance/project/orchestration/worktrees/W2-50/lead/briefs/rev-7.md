# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50), the resume's fresh probe: the merge-back and the secrets scan's fix (DEC-853)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `{HEAD}` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

## Step 0, before any work: the sandbox check

Report it first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kl5e','w').write('x')"` must fail.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Where this ticket stands

- W2-50's earlier rounds were reviewed six times. The last review (probed `fc9e6a2ad67df3e9536e5236e957bc95930c3def`, record `docs/probes/DAEO-kl5e/PR-DAEO-kl5e-last-round-3.md`, judgement fail) found D1 to D4 and R1; the owner made them rows (DEC-779: run 7 was W2-50's last; DEC-785: rows W2-H062, W2-M368, W2-M369, and that record committed as it is; DEC-801: Wave 3 rows). **DEC-790: this resume's fresh probe judges under DEC-779 and DEC-785: a finding already accepted as a row does not fail it.** Its passing record makes the failed record an earlier round (W2-M209), so the probe gate passes.
- **DEC-779:** after run 7, any further guard text-parsing finding is a list row unless a launched, sandboxed worker can reach it. For each finding, say whether a launched, sandboxed worker could reach it, or only an unsandboxed session (the orchestrator, a ticket lead), or only with a precondition no session can create through the guard, with your reasons.
- This resume (run 8) did three things, which are what you probe:
  1. **The merge-back** `e61b67f5`: `w2/integrate` (`7f95e6f5`: W2-53, W2-54, W2-01's probe gate as it stands, and the owner's batches) merged into this branch, parents `0affa162` (the ticket) and `7f95e6f5`. The probe gate (`gov close`'s probe check, `src/gov/close/command.py`, as W2-01 and W2-53 left it) will next judge this ticket's merge into `w2/integrate`.
  2. **The ticket file** `c2b094da` (orchestrator): DEC-853's three KPI lines, `tests/unit/secrets/**` in `allowed_paths`.
  3. **DEC-853, the secrets scan's fix**: tests `878467c9` (`tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`, `w2_50_scan_support.py`, the README's DEC-853 section); the change `a403309e` (`src/gov/secrets/__init__.py`, builder tests `tests/unit/secrets/test_scan_scale.py`); the lead's checkpoint record at the head.

## The owner's DEC-853 (2026-10-19, P-W2-49 (a))

The secrets-indexing check (`python3 -m gov.secrets` in the project root; hard-block; CAP-38.b) scans every file under `.gov-runtime/` with gitleaks: the bytes and, for SQLite, the rows as text, once per rule set (two when the project's `.gitleaks.toml` extends gitleaks' defaults, DEC-347). With a fixed 60 s limit per gitleaks run and about 24 runs at once, it timed out on the main tree's stores (`store.db` 250 MB, `code.db` 210 MB), so every close would be refused. The ruling:
1. The time limit grows with the content's size (or a large store is scanned in bounded chunks, each within the limit), and the pool is bounded so that large files are not starved. The check finishes on stores of today's size.
2. Every file is still scanned with every rule set; a scan that cannot finish still fails closed.
3. A store whose hash has not changed since its last clean scan is not re-scanned; the clean result is reused, keyed on the store's hash. A changed store is always scanned in full. **A finding is never reused.**
Working figures the lead gave both test designer and engineer: a store is decided whenever gitleaks reads at 1 MB/s or faster; a reused clean result is labelled in the check's output with the store's project-relative path and the SHA-256 of its bytes.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Say in your return which questions you asked and whether they helped.
- **Reads open, writes closed (Policy 2, DEC-820).** You read everything, tests and code alike. Only these are refused: (a) secrets and keys, never printed (a canary included); (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart rule binds the test designer and the engineer, not you: you read both sides; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Protected material (DEC-820).** Never read the held-out material's contents and never print a secret. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Never create, write or remove anything in the real `~/gov-os-runs/` or in another worktree.
- **You write nothing in this worktree or any repository, and commit nothing** (DEC-137, DEC-826 Q3). `git status --short` must be the same before and after your probe (show both). **Never run the secrets check, `gov check` or `gov rebuild` in this worktree's root or the main tree's**: the check now writes its record of clean results under the project's `.gov-runtime/`. Every probe that runs the scan runs it in a temporary project you build from scratch in your session's temporary folder (Python's `tempfile.gettempdir()`, which is your session's own; `/tmp` itself is read-only in the sandbox), as `tests/acceptance/W2-50/w2_50_scan_support.py` and `tests/acceptance/W1-15/` build theirs, with a canary of your own made at run time. To see what the real stores would do, read their sizes only (`ls -l`), never their contents.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: run long files in separate commands.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git merge`, no `git worktree`, no `git clone` of this repository. Read-only git (`log`, `show`, `diff`, `merge-base`, `merge-tree --write-tree`, `rev-parse`, `cat-file`) is yours. No subagents that write. Install nothing. No push, rebase or tag.
- Never copy the repository or a folder of it anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder of this worktree or the main tree (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild` (with or without `--no-embeddings`).
- Never ask or notify the owner (no question box, never `owner-ping`).
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## Judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines (the DEC-853 ones in particular), its `allowed_paths` and its last note.
- DEC-853, DEC-779, DEC-785, DEC-790, DEC-801, DEC-750, DEC-754, DEC-757, DEC-347, DEC-290 in `docs/DECISION_REGISTER.md`; `governance/project/orchestration/packages/P-W2-49.md` (by its path).
- The change: `git show a403309e`, `git show 878467c9`, `git show c2b094da`, `git show --stat e61b67f5`; the probe gate in `src/gov/close/command.py` (the probe check and its merge measure, `src/gov/close/_history.py`).

## What you probe for

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

1. **The scan's fix (DEC-853)**, behaviour the tests miss, above all a case where the check says green while a store holds a secret (fails open), or where a clean result is reused when it should not be:
   - a clean result reused for content that differs from what was scanned: a store changed between the hash and the scan; a SQLite store whose bytes are unchanged but whose rows read differently (a `-wal` or `-journal` file beside it, a hot journal); the same bytes at another path; a store replaced by a link (to a file inside the project, or into `~/gov-os-runs` of a temporary HOME, the ticket's link rule);
   - the key: a change of `.gitleaks.toml` (its rules, its `extend`, an allowlist, a disabled rule), of the gitleaks binary or version on `PATH`, or of `GITLEAKS_CONFIG`-like environment, and whether each makes an earlier clean result stop counting where it should;
   - the record: missing, empty, damaged, of another form, written by an older or newer scan, written by two scans at once (two checks run in parallel in one project), left half-written; a record that grows without bound; a record copied from another project; whether any of these makes a store count as clean without a scan;
   - a finding is never reused: a store with a canary, on every run, also when another store's result is reused;
   - fails closed: gitleaks missing, hanging, killed, an unexpected exit code; a file that cannot be read; a file that vanishes or changes size during the walk; whether any of these leaves a clean result recorded;
   - the time limit and the pool: a store at today's sizes (build a large one in your temporary folder, a few hundred MB at most; see the README's DEC-853 section for the stand-in `gitleaks` the tests use), many small files with one or two large ones, memory held at once; whether the check as a whole still fits its declared `timeout-seconds` (900) on stores of today's size, and what happens when it does not (fails closed?);
   - the indexers' filter (`indexable`) and `path_holds_secret`, which share the scan's helper: unchanged in what they decide;
   - **the ticket's link rule** in `stores_with_secrets` (DEC-728, DEC-743 §6.1 (i), DEC-751 item 2): kept as before;
   - whether the label or any output prints a secret.
2. **The merge-back under the probe gate as W2-01 and W2-53 leave it:**
   - `e61b67f5` keeps both sides: its tree equals `git merge-tree --write-tree 0affa162 7f95e6f5`; no file of the ticket's paths was dropped or reverted; nothing of `w2/integrate` was dropped;
   - the ticket's merge into `w2/integrate` will be clean (`git merge-tree --write-tree w2/integrate HEAD`), and its result on the ticket's paths will be this head's;
   - reading the probe gate as it stands at this head: a passing record of this head, committed after it by the orchestrator role alone, makes the failed record (probed `fc9e6a2a`) an earlier round; the ticket file commit `c2b094da` (orchestrator, ticket file alone) and the inward merge `e61b67f5` (Task: DAEO-kl5e) do not refuse the gate; nothing else on the ticket's paths lies after this head. Say whether you find anything in the gate that would refuse a passing record of this head, or let a stale probe pass.
3. **Nothing earlier now refuses that should pass, or passes that should refuse:** the W2-50 suite and the earlier suites on the scan (W1-15, W1-16, W1-17) as far as your sandbox runs them; name any you cannot run and why.

Out of scope (report only if they fail open in a way the owner's answers did not accept): the guard and launcher changes of runs 1 to 7, which six reviews probed, and their rows (W2-H062, W2-M368, W2-M369, W2-L354, W2-L350, W2-H055, W2-M359); the sandbox itself (W2-21).

Run `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py` once to its end (its three large cases, `-k large`, in a command of their own) and report its count.

## Return

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the fields, the payload:
- the sandbox check (step 0); the full id of the head you probed; the `gov.__file__` line; `git status --short` before and after; the `gov retrieve` questions you asked; the guard read refusals you met (count);
- your judgement, `pass` or `fail`, under the judgement rules above and DEC-790 (a finding already accepted as a row does not fail it; only "Ordinary work: yes" with "Consequence: fails open" or "loses work" fails the probe);
- each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, whether you reproduced it, **the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`**, and whether a launched, sandboxed worker could reach it or only an unsandboxed session, or only with a precondition no session can create through the guard, with your reasons;
- what you probed and found sound;
- then the body of the probe record in Markdown, as you would have it committed: a "What was probed", "What it found" (each finding with its two lines), "Found sound" and "Judgement" list.

The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so.
