# Batch 7 (round 3, DEC-1005): two behaviours the proving ground still gets wrong (W2-81, DAEO-l78m)

Your batch 6 is committed (`56af0a59973b`; the branch head is now `5ec8242c1a4a`, which adds only a checkpoint record, nothing under `tests/acceptance/W2-81/`). A further independent review probed batch 6 and found behaviour the self-tests miss. The orchestrator's decision (DEC-1005) declares a round 3 for it, fixed in the suite only (`tests/acceptance/W2-81/**`, your only allowed path). This is the round's only test-design batch; one review follows it, and it is the last.

Every standing rule of your first brief still holds, word for word: step 0's sandbox check (report it first again: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l78m','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work; otherwise stop and return); Policy 2 (c) and (d): you never read this ticket's implementation (here there is none outside your own tests) and you never read the real hidden half or any hidden evaluation material, only stand-ins you build in your temp folder; the guard's command forms (no shell variable as a write target, no here-document, no backticks, no `bash -c`, no long inline `python3 -c` with braces: put anything longer in a script file in your temp folder and run it); the guard's read refusals until W2-58 (searches from the repository root, `governance/project/` or `.claude/` may be refused: take the refusal, search named folders instead, and count the refusals in your return); refused twice for the same call, stop and say so; no copy of the tree; protected material (never read the held-out material's contents, never print a secret, never write in `~/gov-os-workbench`, `GOV_DEV_TIERS` by name only); the disk share (yours: 8 GB and 400,000 files and folders of the lead's 20 GB / 1,000,000, in your sandbox's temp folder; pytest's own retention, never `--basetemp`; clean as you go, and name what you cannot remove); row W2-L423's rule (12-digit hashes under `.gov-runtime/`, never the keywords of the rule that takes a bare 40-hex string for a token); the hooks check before your commit (`/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds only `*.sample` files, else stop); no amend, no rebase, no reset; the trailers; the twelve fields first.

**The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src` set **per command** (never in a session's `--settings` env).

**Retrieval (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m gov.cli.main retrieve "<question>" --json`, small questions, `--batch-size` and `--continue <token>` for a large one; code questions through the code graph's own small traversals) for what you need to know before reading files at random. If one try answers STORE_MISSING, FACET_UNAVAILABLE or a network error inside your sandbox, do not try again and do not route round the sandbox; read the named files directly and say so in your return. Drop unread any result under this ticket's implementation paths (none outside `tests/acceptance/`) and name any you were served (P-R1).

For each behaviour below: make the proving ground behave as stated, and add a self-test that fails on the current head and passes after your change (say which in your return). Lower no existing expectation. Keep the whole suite under about 80 s alone on this machine; report plain and `-n auto` timings.

## First: a self-test writes inside this repository (a case writing in this repository is lost work by this ticket's definition)

1. **A runner case creates a folder inside this repository.** The runner module's options helper gives every case a hidden-half folder by creating an empty folder beside the run folder it is handed (in the run folder's parent). For the case that aims its run folder at a place inside this repository (to show the runner refuses it), that helper creates an empty folder inside the suite's own folder before the runner refuses anything. The case still passes, since it checks only that the run folder itself was not made, and `git status` (and so the tripwire) never shows an empty folder. One such folder exists now: `tests/acceptance/W2-81/no-hidden-questions/`, empty.
   - Every folder a case makes must be made under that case's own pytest temporary folder (`tmp_path`, or the session's temporary folder factory), never beside a run folder the case was handed; the review module's own helper already works this way. Look for any other helper or case in the suite that makes a file or folder relative to a path it was handed rather than under its own temporary folder, and fix it the same way.
   - **Remove the stray empty folder** `tests/acceptance/W2-81/no-hidden-questions/` in this batch (it is inside your path; an empty folder has nothing to commit, so just remove it and say in your return that it is gone, with `ls -la tests/acceptance/W2-81` after).
   - **The self-test:** a check that a run of the runner module (or of the whole suite) creates no new file or folder anywhere inside this repository, empty folders included (for example a before-and-after listing of the suite's folder and the worktree's top level, or a recorder on folder creation that fails on any target inside this repository). Show it failing on the head and passing after your change.
   - Also list, by path only, any other untracked folder you see under `tests/acceptance/W2-81/` that the suite did not make (for example harness marker folders); do not remove those, just name them.

## Riding along (DEC-802; no round of its own)

2. **A typo in a hidden forbidden citation is dropped without a word.** A forbidden citation in the hidden half whose template names a fact no builder knows (a mistyped fact name) is silently dropped, the same way a citation naming a fact the clean twin legitimately lacks is dropped. Once the hidden half exists, one such typo removes a forbidden citation from the measurement, and a run that should be NOT_READY (a forbidden source ranked in the top five, the stacked share short of its target) reads READY.
   - A forbidden citation that names a fact unknown to every builder must be refused (`refused: <id>: <reason>`, exit 2, never the template's text or a fact's value), or at the least named by the hidden question's id in the run's output, the JSON report and the markdown report, and counted, so that it can never pass unnoticed. Only facts a repository is known to lack (the clean twin's absent stale spec, old plan and dead module, as the README states today) may be dropped silently. State in your return which of the two you chose and why.
   - **The self-test:** a stand-in hidden half in your temp folder with one forbidden citation's fact name mistyped; on the head it is dropped (show it), after your change it is refused or named. Keep the clean twin's legitimate drop working (a case for it too, if none exists).

Update the README for each (the handling, the new cases), commit with your trailers (`Task: DAEO-l78m`, `Role: independent-test-designer`, `Implements:` with the ids this batch implements, for example `DEC-993, DEC-968, DEC-936, DEC-941, DEC-820, DEC-802, CAP-44.b, CAP-44.e`, each checked to exist in this worktree's register or the Contract (DEC-997 and DEC-1005 are not in this worktree's register: leave them out and say so), and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`), then run the whole suite to the end plain and with `-n auto`, then check that no new untracked file or folder appeared under `tests/acceptance/W2-81/` after those runs (`find tests/acceptance/W2-81 -type d` before and after, `__pycache__` aside), the collect-only check once (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src python3 -m pytest tests/acceptance/W2-81 --collect-only -q -p no:cacheprovider --no-header`), and `gitleaks` on the suite (count only). Commit before you run the long suites.

## Return

Your commit's 12-digit hash and trailers; files; for items 1 and 2, what changed and the self-test that shows it (and that it failed before); that the stray folder is gone, and any other stray folder by path; the suite's count and both timings; the before-and-after folder check; the collect-only line; gitleaks count; whether you used `gov retrieve` and what it answered; guard refusals and read refusals; temp folder size (`du -sh` and `du -s --inodes`).

Your last message has the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.

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
