You are a fresh reviewer. Ticket DAEO-zflj (W2-02, "Record types: decision entry, audit report, adoption verdict, close record; core-schema green here"), profile STANDARD, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-02` on branch `w2/W2-02`, at the head `@@HEAD@@`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing. You are a headless session: nobody answers questions while you work, and only your final message is read.

Ticket DAEO-zflj is implemented in this worktree and its acceptance tests pass. Probe the final code for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. Write nothing except the probe record the lead names. Return each finding as a described behaviour, with its severity.
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). The full text is `governance/project/briefs/JUDGEMENT.md`, which this brief carries word for word.
- You read everything, tests and code alike (DEC-820); you commit nothing (DEC-826 Q3).

"The probe record the lead names": you write no file at all. You return the probe record's content in your final message, and the lead writes it.

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

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zflj','w').write('x')"` must fail.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, saying which.

## Standing rules (read first)

- Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-zflj`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-02` and `w2/W2-02`) and `git log --oneline -1` (expect `@@HEAD_SHORT@@`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete. Your session has a hard limit of two hours: keep every suite you run to the ones named below.
- **The code under test (DEC-732, owner):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random, and say in your return whether you used it and for what. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. (If the code graph is not reachable from your sandbox, say so and use Grep and Read on named folders.)
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-02/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests) — you are the reviewer, and reviewers read everything; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals until W2-58 lands (DEC-849):** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and list them in your return.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never print a secret.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. A probe that needs a repository builds a temporary one in your temporary folder from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no `git merge` (use `git merge-tree` to compute a merge without touching the tree) in this worktree. Write no file of the repository and make no commit. No subagents that write. Install nothing. No push, merge, rebase or tag.
- Never run `gov rebuild` (any form; never `--no-embeddings`), `gov close`, `gov adopt`, `gov pause` or `gov checkpoint` against this worktree or the main tree.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status `AUTH_REQUIRED`.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-zflj.md`: its KPI lines and its `allowed_paths` (`template/governance/kernel/schemas/**`, `schemas/**`, `template/governance/kernel/templates/decision-record.md`, `src/gov/check/schema.py`, `tests/unit/check/test_schema*`, `tests/unit/check/test_check.py`).
- The sources: DEC-441, CAP-44.h (`docs/contract/contract.yaml`), DEC-730, DEC-741, DEC-746, in `docs/DECISION_REGISTER.md`; also DEC-565, DEC-626, DEC-737 item 6, DEC-750, DEC-754. Two decisions are not in this worktree's register; their text, as the orchestrator gave it, holds:
  - **DEC-749 (delegated, 2026-10-17):** core-schema's shape check measures, for a standalone type, `type: array` with `items`, `type: object` with `properties` and `required`, and one `if`/`then` on a `const`; every other keyword is a fault at every depth; findings name the top-level field. The adoption verdict requires a list of named conditions, each `{name, source, state ∈ {met, not met, accepted}, owner_entry}`, an `accepted` one requiring its owner entry.
  - **DEC-872 (delegated, 2026-10-20):** this resume merges `w2/integrate` back into `w2/W2-02` (`--no-ff`, never `-s ours`, never dropping a side), resolves the `STANDALONE_TYPES` conflict to this ticket's line keeping every type both sides name, checks the close type against the close record `gov close` wrote for W2-53 (`docs/close/DAEO-7rr2/CL-DAEO-7rr2.md`) with no schema change, and takes a fresh probe. The widening (the full validator through check-jsonschema, a planted ticket as a case, `docs/imported/` out of the schema check) moves to a follow-on ticket, W2-64, after this merge: a gap it covers is a residual for W2-64, not a finding against this ticket.
- The ticket's acceptance tests `tests/acceptance/W2-02/` (README first) and the code at the head to probe: `git diff --stat w2/integrate...HEAD` names this ticket's change.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard or a gate fail open. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Three areas first:

1. **The close type.** `template/governance/kernel/schemas/close.schema.json` against the close record `gov close` actually writes: the real record `docs/close/DAEO-7rr2/CL-DAEO-7rr2.md`, and the writer in `src/gov/close/` (find where it builds the record's frontmatter). Does core-schema accept every record the close writes, today and for a ticket with a lower-case suffix `wbs_id` or other ordinary variations? Does it still refuse a record with an unknown `type` (`SCHEMA_INVALID_TYPE` / `SCHEMA_UNKNOWN_TYPE`) and a close record missing what the schema requires? Would any ordinary close be refused by its own pre-close `gov check` (that is a fail-closed stop of every close: say so with its consequence)?
2. **The `STANDALONE_TYPES` resolution** in `src/gov/check/schema.py`: the merge resolved the one conflict to `("probe", "audit-report", "adoption-verdict")`. Check that W2-54's audit-report behaviour (a record under `docs/audit` with no `type` is an audit report, held to its standalone schema) is kept, that W2-54's acceptance suite passes on this head, and that the audit report missing its milestone or pack hash is still invalid.
3. **The merge-back** `666f56d1` (parents `2a35fd7b` and `c74a7d43`): compute git's own merge of its parents (`git merge-tree --write-tree 2a35fd7b c74a7d43`) and compare it with the merge commit's tree; any path where the commit differs from git's merge other than the conflicted `src/gov/check/schema.py` is a finding (DEC-750, DEC-754). Check the conflicted file keeps every line of both sides' meaning, and the merge's trailers (`Task: DAEO-zflj`, `Role: orchestrator`, `Implements: DEC-441`). Check that nothing under `tests/acceptance/` differs from `w2/integrate` except W2-02's own suite and W1-26's one test DEC-746 revised.

Then the ticket's KPI lines on this head: core-schema green on this repository (`cd /home/usain/gov-os-worktrees/W2-02 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m gov.check.schema; echo exit=$?`), a type with no schema file unmeasured and not green, the `wbs_id` grammar (`W2-15a` and `W2-15` accepted; `W2-15ab`, `W2-15A`, `W2-1` refused), the decision entry, the audit report and the adoption verdict with its named conditions.

Suites you may run, each to its end, never with `-x`, each in its own process, in the foreground:
- `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/acceptance/W2-02 -q -p no:cacheprovider -rs`
- `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/acceptance/W2-54/test_w2_54_audit_report.py tests/acceptance/W2-54/test_w2_54_green_here.py -q -p no:cacheprovider -rs`
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/unit/check -q -p no:cacheprovider`

Probes of your own run in a temporary root you build (single named schema files copied in, records you write), never in this worktree.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, its two lines (`Ordinary work: …` and `Consequence: …`), and whether it loses work or fails open. Say also what you probed and found sound, and your judgement: `pass` or `fail` by the rules above. After the twelve fields, give the probe record's body as a payload: a short Markdown record in the form of `docs/probes/DAEO-7rr2/PR-DAEO-7rr2.md` ("What was probed", "What was found", "Judgement"), with every finding's two lines. Give also your own session id if you can read it.

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
