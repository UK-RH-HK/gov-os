# Brief: independent auditor, W2-130 (DAEO-q8cl): the narrow independent check of run 4's record refresh

You are a fresh independent auditor (role independent-auditor), ticket DAEO-q8cl (W2-130), profile STANDARD, class
C2. Read-only: you write no file in any repository and make no commit. Headless: only your last message is read; the
lead commits it as the probe record, so make it complete.

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-130 |
| the head you audit | `a2671a340dda6b020e6e16099b51d535a2e408ae` (the tree is checked out there) |
| the ticket (KPI lines with their Verify clauses: the spec) | `.tickets/DAEO-q8cl.md` |
| the record under check | `docs/research/W2-130-link-cleanup.md` |
| the acceptance cases (the independent test designer's) | `tests/acceptance/W2-130/` (README first; `test_w2_130_record.py` and `test_w2_130_sources.py` read the refreshed blocks) |
| DEC-1123 (2) (the forms S4 excludes) | `docs/DECISION_REGISTER.md`, `### DEC-1123` (read by id) |
| run 3's probe record (what was checked before; not your answer) | `docs/probes/DAEO-q8cl/PR-DAEO-q8cl.md` |
| the lead's builder scripts (to see how blocks were made; judge the result, not the script) | `.gov-runtime/scratch/lead/rec/build_record.py`, `render.py` (run 3's copies beside them as `*_r3.py`) |
| scratch | your sandbox's own `$TMPDIR` only |

## How you judge (owner, the w2 prompt's section 14)

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

## The background
W2-130 is a records clean-up (no code). Run 3 returned DONE at `798278be5`. The land ejected it for a conflict on
`.tickets/DAEO-aks1.md` (DEC-1176 had rewritten W2-88b's ticket on `w2/integrate`). The CTO merged `w2/integrate`
into the branch (`6b62de94e`), taking integrate's version of that file whole. At that merged head three record cases
went red because the record's after counts, its findings left by path and role (D-5, D-6, D-9) and its closed-missing
list no longer equalled `gov links --all` at HEAD. This run (run 4) made one commit, `a2671a340`: the record
refreshed at the merged head by the commands the record keeps. No register, ticket or other file changed.

## What you check (narrow: the refresh only)
1. **The refresh commit `a2671a340`** changes only `docs/research/W2-130-link-cleanup.md`, and within it only the
   `counts-after`, `closed-missing`, `no-record` and `left` blocks and the prose that states them (sections 5, 9, 10
   and the header note). Every other block (commits, ids-87, census, archive-13, judged-wrong, audits, comparison, the
   patches, trailer-residuals, recount, drift, drift-run, counts-before, dec-1123-linked, lessons) is byte-identical
   to its parent's.
2. **The refreshed blocks against the tool.** By your own run of `gov links --all --json` on a `git clone --shared`
   of the tree checked out at `a2671a340dda6b020e6e16099b51d535a2e408ae`: `counts-after`'s by_code, by_code_role and unlinked_by_status equal it;
   `left`'s D-5 (`template/`, `docs/contract/`), D-6 (`src/`, `tests/`) and D-9 (`.tickets/`) path -> role -> count
   maps equal it; `closed-missing` equals the UNLINKED_ID findings on closed tickets, per ticket, and lists no id a
   ticket's `sources:` already holds; `no-record` covers every UNKNOWN_ID on a ticket (other than `tests/` paths).
   Judge the `counts-after` block's form: its `head` names the last clean-up commit (`57cbacfbf`), as the test reads
   it, while its `measured_at` and `command` name the merged head counted. Is that a fair statement of what was
   measured, and does any prose in the record misstate it?
3. **No sources follow-up was needed.** Every UNLINKED_ID `gov links --all` reports at the head on a ticket open or
   in progress is one of the record's `dec-1123-linked` entries (so the lead added no sources commit). Check this
   against your run.
4. **No history rewritten:** `798278be5` and `6b62de94e` are ancestors of `a2671a340dda6b020e6e16099b51d535a2e408ae`.

You may run the acceptance folder (it clones into `$TMPDIR`; the tree is never written):
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest /home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and `gov links` on a `git clone --shared` of the tree in `$TMPDIR` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src python3 -m gov.cli.main links --all --json --root <clone>`).
Every pytest goes through heavy_slot.sh as above. A resource gate's refusal is a wait.

## Return (your last message)
1. A header: `Independent auditor, <ISO 8601 date and time with zone, from date -Is>, at a2671a340dda6b020e6e16099b51d535a2e408ae, W2-130 run 4 narrow
   check.`
2. Per item 1 to 4: what you checked, how, and what you found.
3. Each finding with its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
4. Last, a fenced block opened by ```` ```verdict ```` holding one JSON object:
   `{"head": "<full hash>", "date": "<ISO>", "kpis": [{"kpi": "<item>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]} ...]}`.

## Searching
Read and Grep only, and git show; no `gov retrieve` or `gov context`. Search once, then once more in other words;
answer from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out
material or any hidden or memory-verdict folder. Refused twice for the same call by the guard, the sandbox or a hook:
stop and say so; never work around a refusal.
