# Brief: reviewer (FULL, read-only), DAEO-0mtg (W2-106), run 1

You are a fresh reviewer (the QA step, brief A3). Ticket DAEO-0mtg (W2-106), profile FULL, is implemented in the
worktree `/home/usain/gov-os-worktrees/W2-106` on branch `w2/W2-106`, at the head `c2c99e6c084f`, and its acceptance
tests pass. You probe that head for behaviour the tests miss. You write nothing in the repository and commit nothing;
you return the probe record's content and the lead commits it.

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0mtg','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-0mtg`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-106`, `w2/W2-106`), and
  `git rev-parse HEAD` (expect `c2c99e6c084f`). If anything differs, stop and say so.
- Run everything in the foreground. Write no file of the repository; no commit, no `git checkout` of another commit,
  no `git reset`, no `git clean`, no push, merge, rebase or tag; no subagents that write; install nothing.
- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src` set per
  command (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one
  giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`). A code
  question (DEC-859) uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and
  targeted, never a load of the whole graph.
- **Policy 2 (DEC-820):** you read everything, tests and code alike. Still refused: (a) secrets and keys, never
  printed; (b) the held-out qualification material's contents, and never read or name the qualification oracle;
  (d) the hidden half of any evaluation set. Never write in `~/gov-os-workbench`.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders. Count them in your return.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces. A probe script goes in your session's own temporary folder
  (your scratchpad), never in the repository.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A probe
  that needs a project builds a temporary one in your temporary folder, from scratch or generated from the template
  the way the acceptance support does it (copier and rulesync, file by file). A stand-in pin is built as W2-59's and
  W2-106's acceptance support build it (a wheel of this worktree with no network, a `--system-site-packages` venv in
  your temp folder, reached through `<temp HOME>/.local/bin/gov`). Never touch the real `~/.local/bin/gov`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in your return, write commit hashes as 12 digits, except `probed_commit`, which
  is the full id (the probe gate reads it); never write the keywords of the gitleaks rule that takes a bare 40-hex
  string for a token.
- **Disk budget (DEC-898):** your share is 4 GB and 200,000 files and folders outside the tracked tree; clean up
  your temp trees; give `du -sh` and `du -s --inodes` of your scratch at the end.
- **No suite re-runs (DEC-959 item 1):** you read the tests, the code and the lead's results (below); you run probes
  of your own, not the suites.

## What you read

- The ticket `.tickets/DAEO-0mtg.md`: its KPI lines and `allowed_paths` (template/governance/kernel/settings.json,
  template/.rulesync/hooks.jsonc, tests/unit/hooks/test_w2_106*, and the designer's tests/acceptance/W2-106/).
- Sources: DEC-966 (item 2), DEC-822, DEC-957, DEC-965, DEC-801, DEC-616, DEC-917, DEC-880 item 3, DEC-913 item 1,
  DEC-732; `governance/project/orchestration/packages/P-W2-90-1.md` (P1-B); W2-59's probe record
  `docs/probes/DAEO-kh9l/PR-DAEO-kh9l.md` (what was already found about this form, e.g. `PYTHONUSERBASE` under `-E`,
  a Wave 3 row: do not re-raise it as new).
- The change: `git diff 1f0bf2836dc2..c2c99e6c084f -- template/ tests/unit/` and the acceptance tests
  `tests/acceptance/W2-106/` with their README, and the W1-38 revision (`tests/acceptance/W1-38/w1_38_hooks_support.py`).
- The lead's results (this worktree's `src`, `gov.__file__` = `/home/usain/gov-os-worktrees/W2-106/src/gov/__init__.py`):
  - W2-106 acceptance: red on the base (tests branch, base + tests) 58 failed / 30 passed, for the README's reasons
    (the 30: 24 exit-mapping and 6 in-step cases that already hold); green on the ticket head: 88 passed.
  - The scoped selection (`scope: scoped`, `core_changed: []`, `unplaced: []`), in the close's form: parallel
    7041 run, 6982 passed, 53 failed, 4 errors, 2 skipped; W1-38 201/0 red, W1-47 980/0, W1-28 151/0, W2-65 10/0,
    W1-49 96/0, tests/unit 2843/0. The serial-route cases: 10 passed. W1-39 (KPI 4; the selection leaves it out):
    71 passed. Reds, none from this change: W1-05's two orchestrator-asks cases and W1-46's research npm-install case
    (P1-A, W2-105); four W2-59 cases on this repository's own five-rule hook (P1-B, moved by W2-90's next round);
    47 W1-50 read-merge cases (an import-path interaction with `tests/unit/adapters/test_portability.py`, pass alone,
    fail the same on the base); W1-08's path-map case (a base governance file); two W2-54 cases (a 1800 s time-out
    under load, pass alone).
  - The test designer measured that once the line is pinned, a harness whose stand-in home has only a user-site
    path file (W2-90's `install_gov_for`, W1-05's and W1-47's sandboxes) runs the owner's pin found on `PATH`, not the
    worktree's code; it revised W1-38's harness (an editable install's `gov` script in the stand-in home) and named
    the rest for W2-90's next round. Judge whether this matters for an adopted product (it is a test-harness fidelity
    question, not the product's behaviour) and say so.

## What you probe for

The generated project's guard hook lines, run, not only read: **any way they fall back to an unpinned interpreter
or let a refused call through.** Above all a case that could:
- make the guard or the containment check fail open (a PreToolUse line ending in anything but 2 or a deny decision
  when the guard could not decide; a post-tool line ending 0 when the containment check did not run);
- run guard code other than the installed gov's (the session's `PYTHONPATH`, `PYTHONHOME`, a `python3` or `gov` first
  on `PATH`, a project's own `src/gov`, the pin missing, a dangling link, an interpreter line with arguments or `env`,
  a pin re-installed mid-session);
- break an adopted product's ordinary work (an honest product with the release installed the documented way: does
  the line find it? `rulesync generate` output equal to the template's settings?);
- lose work, let a role write outside its scope, or let an implementer change acceptance tests.

## Judgement (governance/project/briefs/JUDGEMENT.md, word for word)

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

## Return

After the twelve fields, the probe record's content, ready for the lead to commit as
`docs/probes/DAEO-0mtg/PR-DAEO-0mtg.md`, in this form:

    ---
    type: probe
    task: DAEO-0mtg
    reviewer_session: <your session id, or "unknown" with why>
    implementer_session: unknown (the engineer's log was lost at the tool's time limit)
    reviewer_wrote_nothing: true
    commissioned_by: orchestrator
    judged_by: orchestrator
    judgement: pass|fail
    probed_commit: <the full commit id of the head, from git rev-parse HEAD>
    ---

    # Probe record: W2-106 (DAEO-0mtg)

    - **What was probed:** …
    - **What it found:** each finding as a described behaviour (never code, DEC-136): what was done, what
      happened, what should have happened, severity, and its two lines (`Ordinary work: …`, `Consequence: …`).
    - **What was sound:** …

`judgement: fail` only if a finding has "yes" to ordinary work with "fails open" or "loses work".

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
