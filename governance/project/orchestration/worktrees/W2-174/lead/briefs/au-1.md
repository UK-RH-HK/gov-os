# Brief: independent auditor, W2-174 (DAEO-zmo4), the narrow independent check (read-only)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-zmo4 (W2-174), profile STANDARD, class C2.
Read-only: you write nothing in any tree; your record is your last message, which the lead commits word for word under
`docs/probes/DAEO-zmo4/`. Headless: only your last message is read.

## What you check
| what | value |
|---|---|
| tree (read only) | /home/usain/gov-os-worktrees/W2-174 |
| head to probe | 7920da077ac2 (full: run `git -C /home/usain/gov-os-worktrees/W2-174 rev-parse HEAD`; it must be 7920da077ac2…) |
| base | f2b1d38af (`git diff f2b1d38af 7920da077ac2`) |
| the ticket | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-zmo4.md (all eight KPI lines, Interface, Rabbit holes, the two owner sections) |
| the lead's interface decisions given to both workers | /home/usain/gov-os-worktrees/W2-174/.gov-runtime/scratch/lead/briefs/interface.md (L1-L9) |
| the change | `src/gov/adopt/verify_pass.py`, `src/gov/adopt/facts.py`, `src/gov/adopt/command.py`, `tests/unit/adopt/test_w2_174_*.py` (engineer, session ac8f55ac-c057-4f53-8cee-c78f5bddf205), `tests/acceptance/W2-174/` (independent test designer, session 4a5dfbba-55f7-4401-9ee8-3998e551b8e4) |
| reads | `src/gov/brief/build.py` (`kpi_rows`, `ready_check`, `build`, `Filler`), `template/governance/kernel/schemas/facts.schema.json`, `tests/acceptance/W2-152/` |

The lead's evidence so far (check it, do not take it on trust): `gov accept W2-174` passes 94/94 at 7920da077 (S1 9,
S2 15, S3 2, S4 36, S5 12, F1 15, F2 2, F3 5, none unmapped); the whole-suite run had 5,897 tests with 2 red: W2-23 S6
(`tests/acceptance/W2-23/test_w2_23_space.py:94`, a known red: the template lacks `context_watch.py`, another ticket's)
and `tests/unit/retrieval/test_w2_112_shared_reranker.py:563` (green alone, 33 passed; a load-sensitive case).

Known by both workers, judge it: a plain YAML scalar cannot hold ` Verify: <clause>` (its `: ` opens a mapping), so the
tool rewrites an answered plain KPI line as one single-quoted scalar (its trailing comment kept); quoted lines get the
clause inside their quotes. S2's "every other byte unchanged" is read as: only the answered items and the marker line
change. Say whether that reading keeps S2's point.

## How to check
Per KPI line (S1-S5, F1-F3), against the ticket's own line and Verify clause:
- read the code and the cases that claim it; ask whether the cases would fail if the line were broken;
- probe by hand where the cases are thin: build small fixture repositories under your sandbox's own `$TMPDIR` (never in
  the tree) and run `python3 -m gov.cli.main adopt ... --root <fixture>` with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-174/src`.
  Ideas: an answers file naming a ticket by its `wbs_id`; a KPI line with a trailing comment; a ticket whose front
  matter ends with a list; CRLF line ends; a clause holding `'`, `"`, `#`, `: `; a ticket already carrying a
  `verify_pass:` line; a second apply; a status other than open, in_progress or closed; `--facts` twice; `gov brief`
  on the facts file written (which placeholders it names).
- F2: `git diff --name-only f2b1d38af 7920da077ac2` names nothing under `src/gov/brief/`,
  `template/governance/kernel/templates/` or `template/governance/kernel/schemas/`.
Any pytest you run goes through the heavy slot with a short TMPDIR outside the repo (a long one breaks AF_UNIX sockets):
```
env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-174/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Read and Grep only for searching; no `gov retrieve` or `gov context`. Never open the evaluation sets' root, held-out
material or any hidden or memory-verdict folder. Refused twice for the same call: stop and say so; never work around a
refusal. Write nothing in any tree, no commit, no merge.

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
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## Return (your last message; the lead commits it as the probe record's body)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then the record:
- `reviewer_session:` your session id if you can read it (else "unknown"), `probed_commit:` the full hash you probed;
- per KPI line: pass or fail, what you read and ran (commands and their count lines), each finding with its two lines
  `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`, and in scope or out;
- the fenced `verdict` block, last, exactly in this form:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
with one entry for each of S1, S2, S3, S4, S5, F1, F2, F3 (an empty `findings` list where none).
