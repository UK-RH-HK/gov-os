# Brief: reviewer (FULL ticket, read-only), W2-107 (DAEO-kiar)

You are a fresh reviewer, the second and last of this ticket (DEC-413). Ticket `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-107` on branch `w2/W2-107`, at the head `654fd0e3e26c` (`git rev-parse HEAD` gives the full id; quote it whole in the probe record's `probed_commit`, and 12 digits everywhere else), and its acceptance tests pass (43 of 43). The first review (its record, kept as a failing draft, is `/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/probes/rev-1-draft-fail.md`) found F-1 (an upgrade behind a shim kept every verdict), F-2 (a gitleaks replaced during a scan was credited with the old one's verdict), F-3 (the filter's reading form was not in the fingerprint) and R-1 (a read-only cache was never read); round 2 fixed them to the addendum `/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/design-r2.md`. Judge whether each fix holds, and probe the round-2 code anew, above all its new paths (the version asked through PATH's gitleaks, the engine taken once per judgement, the read-only and immutable reads of the cache). Probe the final code for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. Write nothing except the probe record the lead names. Return each finding as a described behaviour, with its severity.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object --stdin` (without `-w`: you write nothing) must work. If (a) wrote the file, stop there and return, naming it (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107` and `w2/W2-107`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete. Never wait in the foreground for more than ten minutes for one command.
- Write no file of the repository and make no commit; no `git checkout` of another commit, no `git reset`, no `git clean`, no merge, no push, no tag. No subagents that write. Install nothing. You re-run no suite (the lead has run them; DEC-959 item 1): you run your own small probes.
- **Probes run the code** (judge by running, not by reading alone): small Python scripts or commands that import `gov.secrets` from this worktree, in a temporary folder of your own (the sandbox's temp folder, or `/tmp/gov-os-lead-W2-107/` if it is writable for you), building any project or repository there from scratch. **Every probe sets `GOV_SECRETS_CACHE` to a file in your temporary folder; never touch `~/.cache/gov-os/`.** Where you need a stand-in gitleaks, make a small script first on `PATH` that hands each call to the real one (`/home/usain/.local/bin/gitleaks`). Build any planted secret at run time from parts.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (`<this worktree>` is `/home/usain/gov-os-worktrees/W2-107`.)
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (the integration branch's store, a read; this worktree's own store is being rebuilt). **Never one giant query or context (DEC-860):** batches (`--batch-size`, then `--continue <token>`). **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never the whole graph.
- **Reads (DEC-820):** you read everything, tests and code alike, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`. **DEC-849:** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`): take a refusal as a refusal, never another form; search named folders instead; count every refusal and list each in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. You have no Write tool: a probe script that needs more than a short command goes into your temporary folder by a form the guard reads whole (for example `printf '%s\n' 'line one' 'line two' > /tmp/<literal path>.py`), or is returned as a probe you could not run.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits (but `probed_commit` whole, as above), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". Never print a secret or a planted secret's text.
- No copy of the tree (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). Inside a launched session `.gov-runtime/freeze` and the dotfiles in the worktree root show as placeholders: conclude nothing from them.
- **Budget (DEC-898):** your share is 2 GB and 50,000 files and folders, in your temporary folder; remove what you make when done.

## Judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

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

- The ticket file `.tickets/DAEO-kiar.md`: its KPI lines (7 success, 6 failure) and its `allowed_paths` (`src/gov/secrets/__init__.py`, `src/gov/secrets/cache.py`, `tests/unit/secrets/test_w2_107*`, and the test designer's `tests/acceptance/W2-107/`).
- The sources: `governance/project/orchestration/packages/P-SPEED-1.md` (§4, the design the owner approved as (a)); the lead's design note, `/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/design.md`, and its round 2 addendum, `design-r2.md` beside it (the specification both workers had).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-966 (item 4), DEC-967, DEC-911 (item 4, the commit-hash exemption), DEC-285 (the filter never lets an undecided path through), DEC-939 (item 2), DEC-853 (the check's own clean record), DEC-898.
- The ticket's change: `git diff 0062ed549674 654fd0e3e26c` (the code `src/gov/secrets/__init__.py` and `src/gov/secrets/cache.py`, the builder tests `tests/unit/secrets/test_w2_107_cache.py`, and the acceptance tests `tests/acceptance/W2-107/` with their README). The callers: `src/gov/retrieval/lexical.py` (line 115) and `src/gov/codeintel/__init__.py` (lines 185 to 187).

## What you probe for

Above all, any way a secret reaches an index because of the cache (that fails open), and any content written to the cache. At least:

1. **A stale fingerprint:** a gitleaks or rule set changed while a process runs, or between processes (the binary's digest kept per process; what the record keeps of an engine it has checked); a rule set changed in `.gitleaks.toml` between two calls; two projects with different rules in one process; the cache format's version.
2. **A collision of the key or kind:** a content verdict answering a path, or the reverse; any joining of fields that two different inputs could share; the bytes hashed against the bytes actually scanned (could they ever differ?).
3. **An exempt finding remembered:** a text whose only match is row W2-L423's rule's match naming a commit of the repository is let through but must never be remembered, so that the same bytes in another repository (where it names no commit) are scanned and dropped; also a finding whose report gitleaks gives in a form the filter cannot read; a scan that one rule set finished and the next could not decide.
4. **A race between threads or processes:** the filter's own thread pools (`indexable`, and `path_holds_secret` from the code index's pool), two rebuilds at once, and two engines (or rule sets) at once against one cache file: can a row of one engine ever answer the other, can a clearing be lost so an old row answers, can a lock make a call raise or hang?
5. **Content in the cache:** after scans of distinctive content, names and a planted secret, does any of it appear in the cache file, its `-wal` or `-shm`, or anywhere the code writes?
6. **Fails closed:** a cache that cannot be opened or made, is corrupt, of another form, locked, read-only or full; a write that fails; gitleaks missing, failing or timing out: always a scan or a raise, never a clean answer and never a stopped rebuild.
7. **The settings:** `GOV_SECRETS_FULL_SCAN` (reads nothing, writes fresh), `GOV_SECRETS_CACHE` (empty = no cache; a named file), the default place under `HOME`, and the rule that a pytest test without a named cache uses none. Could an ordinary rebuild, close or nightly end up never using the cache, or could a test reach the machine's real cache?
8. **Unchanged behaviour:** `indexable` and `path_holds_secret` keep their signatures, order and raising; the secrets-indexing check (`stores_with_secrets`) is unchanged; the existing tests of `tests/unit/secrets_check/` still hold (read them; do not re-run the suites).

9. **Round 2's own paths:** the version asked through `PATH`'s gitleaks (once per process and binary; an unreadable, empty, failing or hanging answer; a version call seen by tests that patch `subprocess.run`); the engine taken once per judgement and the check that the binary on `PATH` is unchanged before a write; the read-only read and the immutable read of a cache in a read-only file or folder (can either answer a row of another engine, a damaged or half-written row, or a verdict a concurrent clearing removed?); the reading form raised the module's way.

The lead returns as residuals, not a round: a gitleaks upgraded behind a shim during one process's run; rule sets evicting each other's verdicts; an extended rule file outside the fingerprint; a held lock's two-second waits; a relative `GOV_SECRETS_CACHE`. Judge any of them again only if you find it worse than that.

Say also what you probed and found sound.

## Return

The head you probed (12 digits, and whole for `probed_commit`); each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, whether you reproduced it, and its two lines (`Ordinary work: …`, `Consequence: …`); what you probed and found sound; your verdict (pass: no finding is both "yes" and "fails open" or "loses work"; fail otherwise). Then **the probe record's content**, ready for the lead to commit, in this form (the lead fills the front matter's sessions):

    ---
    type: probe
    task: DAEO-kiar
    reviewer_session: <your session id, if you know it; else "lead fills">
    implementer_session: b13fb711-df4f-4b90-8459-574321099009
    reviewer_wrote_nothing: true
    commissioned_by: orchestrator
    judged_by: orchestrator
    judgement: <pass|fail>
    probed_commit: <the whole commit id>
    ---

    # Probe record: W2-107 (DAEO-kiar)

    ## Summary
    ## What was probed and found sound
    ## Findings (each with its two lines)

You repair nothing (MR-4); the lead passes findings to a test designer.

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

Refused twice for the same call: stop and say so.
