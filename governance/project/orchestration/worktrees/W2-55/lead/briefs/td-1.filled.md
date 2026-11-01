# Brief: independent test designer, DAEO-arrl (W2-55), profile STANDARD, run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-arrl` (`W2-55`, "Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see"), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-55-tests` on branch `w2/W2-55-tests` (DEC-963); you never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-55`). You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with the engineer, and you show them red.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-arrl','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-arrl`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-55-tests` and `w2/W2-55-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return. Your tests must call the code of the tree they run in (a child process with that tree's `src/` on `PYTHONPATH`, as `tests/acceptance/W2-87/w2_87_support.py` and `tests/acceptance/W2-03/w2_03_support.py` do), so that once merged into the ticket's worktree they exercise its code; your README says how.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, **only from the integration branch's store:** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store or files. For what changed on `w2/integrate` since that store's refresh, read `git show w2/integrate:<path>`. **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/decisions/**`, `src/gov/context/**`, `src/gov/retrieve/**`, `template/governance/kernel/schemas/decision*`, `tests/unit/decisions/**`, `docs/research/W2-55-backfill.md`), and name in your return any such result you were served (DEC-820 (c)). You may read those files **as they stand on `w2/integrate`** (`git show w2/integrate:<path>`): that is the existing code, not this ticket's work.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, the files `git -C /home/usain/gov-os-worktrees/W2-55 diff --name-only w2/integrate...HEAD` names other than tests, nor anything in `/home/usain/gov-os-worktrees/W2-55` that differs from `w2/integrate`; (d) the hidden half of any evaluation set. Writes stay inside `tests/acceptance/W2-55/` in this worktree.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-55-tests/.gov-runtime/scratch/td/` with the Write tool and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one from scratch (`tmp_path`). No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in copies single named files, never `governance/project/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 5 GB and 250,000 files and folders, outside the tracked tree. Use `TMPDIR=/tmp/gov-os-lead-W2-55` for your runs unless the sandbox sets its own temp folder (keep that one). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the register or plan files.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-arrl.md` (read-only): its seven success KPI lines and four failure lines, its `allowed_paths` and its sources; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-55`) and §0 (rules for every ticket).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-791 item 1, DEC-825 items 2 and 4, DEC-866, DEC-851, DEC-786, DEC-833 item 3, DEC-941, DEC-952 item 5, DEC-953 item 7, DEC-982, DEC-983, DEC-221 (tests in proportion), DEC-462, DEC-491.
- The fixture of KPI 5: `governance/project/orchestration/packages/SWEEP-2026-10-20.md` (§3 and §5); `governance/project/orchestration/packages/SMART-WORK-1.md` (practice 15).
- Lens B's Q05 and F4: `docs/assessment/2026-10/B-memory-retrieval.md`.
- The existing public interfaces as they stand on `w2/integrate`: `gov.decisions.check(root)` (W2-03's checker), `gov.store.load(root)`, `gov.records.records(root)`, `gov context <ticket> --json`, `gov retrieve <query> --json` (`python3 -m gov.cli.main …`), the store's register entries (W2-03), and how earlier suites drive them: `tests/acceptance/W2-03/`, `tests/acceptance/W2-87/` (temporary repositories with a planted register and path map, child processes on this tree's `src/`).

The specification below fixes the public forms. It is the same text the engineer has.

## The specification of W2-55's public behaviour (the lead's interface spec, the same text in both workers' briefs)

The ticket's KPI lines say what must be true; they do not say what the register's tags look like or where the
checks are called. So that the test designer and the engineer, working in parallel and never reading each
other's work, meet on the same behaviour, these public forms are fixed for this run (a P3 choice of the lead,
inside the ticket's paths, reversible). Everything not fixed here is the implementer's choice, and the tests do
not depend on it.

### S1. The register and its entries

- The register is the file the project's path map (`governance/project/path-map.yaml`) names under
  `decision_register`, read from `HEAD`, exactly as the store reads it (`gov.store.load(root)`; W2-03's entry
  grammar: a heading `### DEC-<n> — <title>` or `### DEC-<n>: <title>`, then a line `- **Status:** <WORD> …`).
  A test commits its register in a temporary git repository and loads the store before calling anything.
- An entry's **tags** are one line of the entry, beginning `- **Tags:**`, of the form
  `- **Tags:** domain: <domain> · scope: <scope> · lands in: <places>` with an optional final ` · done`.
  - `<domain>`: one word of the closed list: `guard`, `close`, `retrieval`, `context`, `adopt`, `launch`,
    `checks`, `plan`, `roles`, `records`, `release` (DEC-791 item 1).
  - `<scope>`: `repository` (this repository only) or `kernel` (kernel-wide) (DEC-791 item 1).
  - `<places>`: one or more paths, separated by `, `, of files `HEAD` holds, that state the rule (DEC-825
    item 2, DEC-851): for scope `kernel` at least one under `template/governance/kernel/`; for scope
    `repository` at least one under `governance/project/` (the prompt or the project briefs). `none` is allowed
    only for an entry that is superseded or done.
  - ` · done`: the entry was a one-off whose action is finished; it stays in the register, and it is not in
    force.
- **Superseded:** an entry whose status word is `SUPERSEDED`, or which another entry's status line names after
  `**Supersedes:**`.
- **Changed:** an entry which another entry's status line names after `**Changes:**`, `**Settles:**`,
  `**Corrects:**`, `**Reverses:**` or `**Withdraws:**`, or whose own status line has a `**Changed by:**` note.
  A changed entry is still in force for its other parts.
- **The status names what superseded or changed it (DEC-791 item 1, DEC-866 item 1):** a `SUPERSEDED` entry's
  status line says `SUPERSEDED by DEC-<n>`, naming an entry of the register; an entry that another entry names
  as superseded or changed (the fields above) carries that entry's id on its own status line (`SUPERSEDED by
  DEC-<n>` or `**Changed by:** DEC-<n>`).

### S2. The decisions validator's register checks

- `gov.decisions.check_tags(root)` returns a list of findings, each a dict with `code`, `ids`, `paths` and
  `message`, as W2-03's `gov.decisions.check(root)` does; an empty list passes. `python3 -m gov.decisions.tags`,
  run in a project root, prints the findings and exits 1 when there are any, 0 when there are none (the form a
  `gov check` family's command takes).
- A finding names the entry (its id in `ids`, the register's path in `paths`) and what is wrong, with these
  codes: `TAG_MISSING` (no tags line, or a tags line without a domain, a scope or a lands-in part; the message
  names which), `TAG_DOMAIN_UNKNOWN` (a domain outside the closed list), `TAG_SCOPE_UNKNOWN`,
  `TAG_LANDS_IN_UNKNOWN` (a place `HEAD` does not hold), `TAG_LANDS_IN_MISPLACED` (no place where its scope
  says), `STATUS_SUCCESSOR_UNNAMED` (a `SUPERSEDED` entry naming no successor, or one the register does not
  hold), `STATUS_RELATION_UNMARKED` (an entry another entry supersedes or changes whose status line does not
  name that entry; `ids` holds both, the old first).
- W2-03's `gov.decisions.check(root)` keeps its own codes and results: the register checks are not added to its
  list (the close and the escalation lift read that list).

### S3. Supersession propagates (DEC-866)

- `gov.decisions.check_propagation(root)` returns findings in the same shape; `python3 -m
  gov.decisions.propagation`, run in a project root, prints them and exits 1 when there are any, 0 when there are
  none.
- **What enforces an old decision:**
  - for a **superseded** entry: any line of a searched place that cites its id (`DEC-<n>` as a whole word), in a
    file that does not also cite the entry that superseded it;
  - for a superseded **or changed** entry: any line of a searched place that holds one of the entry's recorded
    values. The values are on the old entry, one line: `- **Values:** "<text>", "<text>"` (literal strings
    that state the old rule, such as `"300000"` or `"LEAD_CHECKPOINT"`).
  - A changed entry's id alone is no finding (the id does not tell which part is cited).
- **The searched places,** read from `HEAD`: `tests/`, `src/`, `template/`, `governance/project/prompts/`,
  `governance/project/briefs/`, `governance/project/path-map.yaml`, and the ticket files `.tickets/*.md` whose
  frontmatter `status` is not `closed` (a closed ticket is a record). The register itself and other records
  (`docs/`, `governance/project/orchestration/`) are not searched.
- **A recorded reason:** a line of the old entry, or of the entry that superseded or changed it,
  `- **Kept:** <path> — <reason>`, one line per kept file; a kept file gives no finding for that old entry.
- **A finding** has code `ENFORCES_SUPERSEDED`, `ids` `[<old>, <new>]` (the old decision and the one that
  superseded or changed it), `paths` `[<the place>]`, and a message naming both decisions and the place with its
  line number.
- Its first fixture is the sweep of 2026-10-20 (`governance/project/orchestration/packages/SWEEP-2026-10-20.md`):
  W1-49's two window cases (DEC-636 and DEC-665 against DEC-838: tests asserting a 300k window) and W2-59's three
  earlier cases (DEC-605 against DEC-822 and DEC-835: tests where the judge imports the judged project's code)
  are found when the register records those relations and values.

### S4. What agents see: `gov context` and `gov retrieve`

- **`gov retrieve <query> --json`:** evidence from the register whose entry is superseded or done is left out of
  the bundle. When at least one was left out, the bundle (the envelope's `result`) has a key `left_out`:
  `{"count": <n>, "superseded": [<ids>], "done": [<ids>]}` (ids sorted, each id once; `count` the number of
  distinct entries left out). When none was left out the key is absent and the bundle is as before.
- **`gov context <ticket> --json`:** the supplementary context leaves out register evidence of superseded or done
  entries in the same way, and the packet has the same `left_out` key when at least one was left out (absent
  otherwise, so a packet with nothing left out, and its hash, stay as before). The mandatory inputs are as
  before: a superseded mandatory input still refuses (`BLOCKED`); a done entry the ticket declares as a source is
  still read.
- A changed entry (S1) is not left out.
- Lens B's Q05 (a superseded decision served unmarked, `F4`: the superseded filter did nothing for register
  decisions) no longer happens.

### S5. `gov context --in-force`

- `gov context --in-force --json` (no ticket) gives, in the envelope's `result`:
  - `lines`: one string per register entry in force, in the register's order, each beginning with the entry's id,
    then its title; an entry that is changed (S1) names, on its line, the entries that changed it;
  - `left_out`: `{"count": <n>, "superseded": [<ids>], "done": [<ids>]}`, the entries not in force and why;
  - `register`: the register's path.
- In force: every entry that is neither superseded nor done (S1). It is generated from the register at `HEAD`
  (the store's copy), never from a hand-made file such as `governance/project/orchestration/DECISIONS-IN-FORCE.md`.
- A project whose path map names no register gives an empty `lines` and a `left_out` count of 0; a named register
  that cannot be read refuses, never an empty digest.
- `gov context <ticket>` without `--in-force` is unchanged; `gov context` with neither a ticket nor `--in-force`
  is refused by the parser.
- The session-start hook's loading of the digest is not part of this run (the owner's CIT-P question, DEC-952
  item 5).

### S6. The backfill proposal (KPI 4)

- `docs/research/W2-55-backfill.md`, a proposal only: nothing is written to `docs/DECISION_REGISTER.md` (it is
  not in the ticket's paths; the orchestrator applies the accepted backfill).
- Sections, by these headings:
  - `## Proposed tags`: a Markdown table with one row per entry of the register at the ticket's base, in the
    register's order, columns `| id | domain | scope | lands in | status | reason |`: the proposed domain (from
    the closed list), scope (`repository` or `kernel`), lands in (paths, or `none`), status (the proposed status
    note: in force, `done`, `SUPERSEDED by DEC-<n>` or `Changed by: DEC-<n>`) and the reason for the proposal;
  - `## Amends and refines`: every relation DEC-825 item 4 left for this ticket (the entries whose text amends or
    refines an earlier entry, about 120), one line each, `DEC-<new> amends|refines DEC-<old>`, with the status
    note proposed for the old entry;
  - `## Sample for the owner's review`: the entries drawn for the owner, how they were drawn (a stated seed or
    rule, so the draw can be repeated), and what the owner is asked to check.
- How the proposal was made is stated in the file (the script or the rules), so it can be made again.

## The behaviour to test, by KPI line (STANDARD: every line's success and failure, plus the key edge cases)

1. KPI 1 and failure 1: an entry with no domain, no status naming its successor, or no scope fails the register check, naming the entry; a fully tagged register passes; a domain outside the list and a scope outside the two are refused (S1, S2).
2. KPI 2: a missing lands-in tag, a place `HEAD` does not hold, and a place outside where its scope says each fail, naming the entry (S1, S2).
3. KPI 3 and failure 2: `gov retrieve --json` and `gov context <ticket> --json` leave out register evidence of superseded and done entries and state how many (`left_out`); a changed entry is still served; nothing is left out and no key appears when no entry is superseded or done; a superseded entry that reaches the bundle or the packet fails a test (S4). Lens B's Q05 as a case.
4. KPI 4 and failure 4: the backfill proposal exists at `docs/research/W2-55-backfill.md` with the three sections, one row per register entry at the ticket's base (the ids of `docs/DECISION_REGISTER.md` as `w2/integrate` holds it), each with a domain from the list, a scope, a lands-in, a status and a reason; the amends-and-refines section; a repeatable sample; and the ticket's branch changes nothing in `docs/DECISION_REGISTER.md` against its merge base with `w2/integrate` (S6). These cases read the tree they run in; before the engineer has written the file they are red.
5. KPI 5 and failure 3: the propagation check finds a test, code, a skill, a brief, a non-closed ticket's KPI, the prompt and the path map that enforce a superseded decision, by id and by recorded value, naming both decisions and the place with its line; a kept place with its reason gives no finding; a place that cites the successor is updated; a changed entry's id alone is no finding; a closed ticket is not searched. **Its first fixture is the sweep of 2026-10-20:** W1-49's two window cases and W2-59's three earlier cases, reproduced in a planted repository from the sweep's description (S3).
6. KPI 7: `gov context --in-force --json`: one line per entry in force, in register order, beginning with its id; superseded and done entries left out with their count; a changed entry names what changed it; generated from the register (a change to the register changes the digest after the store is loaded again); no register named gives an empty digest; an unreadable named register refuses; `gov context` with no ticket and no `--in-force` is refused (S5).
7. KPI 6 (W2-61's measure after the merge) is the lead's own measurement: write no test for it; the README says so.

Edge cases worth a test: an entry tagged with two places; `none` as lands-in on an entry in force (a finding) and on a done one (none); `SUPERSEDED by` an id the register does not hold.

## What you write

- Only inside `tests/acceptance/W2-55/` in this worktree. No throwaway implementation is left in the tree. If the KPIs require revising an earlier ticket's acceptance test, do not revise it: name it (file, case, why) in your return.
- In proportion (STANDARD, DEC-221): every KPI line's success and failure plus the key edge cases; no combinatorial expansion. Behaviour through the public interfaces above, never internals. Deterministic, no network: no vector is built (the semantic route is unavailable and gives no hit, as W2-87's tests do), no reranker loaded. Each child-process call has a time limit.
- A `README.md` that maps each KPI line to its tests and gives the expected red reason of each, and says how the tests reach the code of the tree they run in.
- The test module names begin `test_w2_55_`; no test package or module may shadow a standard-library module; a `conftest.py`, if any, only for this folder.
- **Red first:** run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src TMPDIR=/tmp/gov-os-lead-W2-55 python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to its end (never `-x`); they fail for the reason the README states (the base has none of the new behaviour), and none fails for a defect of the test itself (a collection error, a typo, a missing fixture).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only `tests/acceptance/W2-55/`, in one commit, with the trailers in the final block:

    git commit -m "W2-55: acceptance tests (independent test designer)" --trailer "Task: DAEO-arrl" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-791, DEC-825, DEC-866, DEC-983" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After the commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red result as you saw it (counts, and the reason for each failing group); every earlier test the KPIs would revise, with its reason; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; any P-R1 result you were served; any package.

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Right after the twelve fields: a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
