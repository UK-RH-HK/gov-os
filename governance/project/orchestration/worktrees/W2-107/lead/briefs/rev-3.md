# Brief: reviewer (FULL ticket, read-only), W2-107 (DAEO-kiar), round 3: run 2 and the counts line (DEC-975)

You are a fresh reviewer, commissioned by the orchestrator (the CTO), who acts as this ticket's lead for its last batch. Ticket `DAEO-kiar` (W2-107, "gitleaks results remembered by content hash"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-107` on branch `w2/W2-107`. Its first two reviews judged the code at `654fd0e3e26c` (the second passed; its record is `docs/probes/DAEO-kiar/` on this branch). Since then, run 2 and a last batch changed the branch. **The owner asked that W2-107 be reviewed on its final head before it is merged (DEC-975 item 1). This review is that: judge what changed since `654fd0e3e26c`, nothing else.** Probe for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard or the secrets filter fail open. Write nothing. Return each finding as a described behaviour, with its severity.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kiar','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object --stdin` (without `-w`: you write nothing) must work. If (a) wrote the file, stop there and return, naming it (never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kiar`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-107` and `w2/W2-107`), and `git rev-parse HEAD` (the head you probe). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message. Never wait in the foreground for more than ten minutes for one command.
- Write no file of the repository and make no commit; no `git checkout` of another commit, no `git reset`, no `git clean`, no merge, no push, no tag. No subagents that write. Install nothing. You re-run no suite (the lead side has run them): you run your own small probes.
- **Probes run the code** (judge by running, not by reading alone), in a temporary folder of your own (the sandbox's temp folder). **Every probe that scans sets `GOV_SECRETS_CACHE` to a file in your temporary folder; never touch `~/.cache/gov-os/`.** Build any planted secret at run time from parts; never print it.
- **DEC-732, word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=<this worktree>/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. (`<this worktree>` is `/home/usain/gov-os-worktrees/W2-107`.)
- **Retrieval (DEC-836):** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (the integration branch's store, a read), in batches, never one giant query (DEC-860).
- **Reads (DEC-820):** you read everything, tests and code alike, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read it, never name the qualification oracle); (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`. Take a guard refusal as a refusal, never another form; count each and list it. Never read `.claude/settings.json`.
- **The guard's command forms:** no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. A probe script that needs more than a short command goes into your temporary folder by a form the guard reads whole (for example `printf '%s\n' 'line one' 'line two' > /tmp/<literal path>.py`), or is returned as a probe you could not run. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits (but `probed_commit` whole), and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- No copy of the tree. **Budget:** 2 GB and 50,000 files and folders in your temporary folder; remove what you make when done.

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

## What you read and judge

- `git log --oneline 654fd0e3e26c..HEAD` and `git diff 654fd0e3e26c HEAD -- src/gov/secrets src/gov/rebuild/command.py tests/unit/secrets_check tests/acceptance/W1-16 tests/acceptance/W2-107`. The merges of `w2/integrate` into this branch bring other tickets' merged work: not yours to judge, except where it meets this ticket's code (W2-76's `src/gov/rebuild/`, which the counts line now touches).
- The ticket `.tickets/DAEO-kiar.md` (KPIs; its body's "At merge" paragraph), DEC-970's W2-107 line and DEC-975 in `docs/DECISION_REGISTER.md`.
- The nightly's line that sets `GOV_SECRETS_FULL_SCAN=1` for its rebuild: `git -C /home/usain/Dynamic-Agentic-Engineering-OS diff -- governance/project/orchestration/nightly/nightly.sh` (uncommitted in the main tree; reviewed apart; read it only for how it meets this code).

## What you probe for

1. **The test move (P-W2-107-1 (a)):** the builder tests moved from `tests/unit/secrets/` to `tests/unit/secrets_check/` by renames only: did any test stop being collected, lose a fixture or an import, or change what it checks?
2. **W1-16's revised home case (P-W2-107-2 (a)):** it now leaves out exactly the scan cache's file and its `-wal`/`-shm` under the child's HOME. Can it now pass when an index file other than those three lands outside `.gov-runtime/` (that would hide a real leak: fails open)? Is the exclusion exact (path, name, place), and nothing else lowered?
3. **The counts line (P-W2-107-3):** the rebuild's JSON record's new `secrets_counts`. Does it change or remove any key W2-76's record had, its form or order? Can it make a rebuild fail, hang or raise where it did not (loses work)? Does it count what it says (texts given to gitleaks against texts answered from the cache, per kind, for this rebuild only), including when a stage runs the filter in a child process, when the cache is off (`GOV_SECRETS_CACHE` empty) and with `GOV_SECRETS_FULL_SCAN=1`?
4. **The full scan as the nightly sets it:** with `GOV_SECRETS_FULL_SCAN=1`, does a rebuild read nothing from the cache and refresh it, so that the nightly can never answer a file clean from a stale verdict? Is any value other than the one the nightly sets silently ignored?

The residual rows run 1 returned (rule sets evicting each other's verdicts, an extended rule file outside the fingerprint, the held lock's waits, a relative `GOV_SECRETS_CACHE`, R-A, R-B, R-D, R-E) stay rows; judge one again only if run 2 made it worse.

Say also what you probed and found sound.

## Return

The head you probed (12 digits, and whole for `probed_commit`); each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, whether you reproduced it, and its two lines (`Ordinary work: …`, `Consequence: …`); what you probed and found sound; your verdict (pass: no finding is both "yes" and "fails open" or "loses work"; fail otherwise). Then **the probe record's content**, ready to commit, in this form:

    ---
    type: probe
    task: DAEO-kiar
    reviewer_session: <your session id, if you know it; else "lead fills">
    implementer_session: lead fills
    reviewer_wrote_nothing: true
    commissioned_by: orchestrator
    judged_by: orchestrator
    judgement: <pass|fail>
    probed_commit: <the whole commit id>
    ---

    # Probe record: W2-107 (DAEO-kiar), round 3 (run 2 and the counts line, DEC-975)

    ## Summary
    ## What was probed and found sound
    ## Findings (each with its two lines)

You repair nothing (MR-4).

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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
