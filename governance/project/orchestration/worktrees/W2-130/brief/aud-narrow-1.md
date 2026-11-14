Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-130 (DAEO-q8cl): the narrow independent check of run 3's follow-ups

You are a fresh independent auditor (role independent-auditor), ticket DAEO-q8cl (W2-130), profile STANDARD, class
C2. Read-only: you write no file in any repository and make no commit. Headless: only your last message is read; the
lead commits it as the probe record, so make it complete.

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-130 |
| the head you audit | `58b52ccb0` (`git -C /home/usain/gov-os-worktrees/W2-130 rev-parse 58b52ccb0`); the tree is checked out there |
| the ticket (eleven KPI lines, each with its Verify clause: the spec) | `.tickets/DAEO-q8cl.md` |
| the record under check | `docs/research/W2-130-link-cleanup.md` and `governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md` |
| the acceptance cases (the independent test designer's) | `tests/acceptance/W2-130/` (README first) |
| the owner's sitting list and ruling | `governance/project/orchestration/packages/W2-130-SITTING.md` (at 2f9c80b1f); DEC-1098 (3) in `docs/DECISION_REGISTER.md` (read by id) |
| DEC-1123 (2) (the forms S4 now excludes) | `docs/DECISION_REGISTER.md`, `### DEC-1123`; the commit that applied it, `66303c373` |
| the earlier audits the record copies (for checking the copy, not as your answer) | `.gov-runtime/scratch/ref/w2-130-marks.md` (parts 1 and 2), `.gov-runtime/scratch/lead/aud-marks-1-return.md` |
| the lead's builder scripts (to see how blocks were made; judge the result, not the script) | `.gov-runtime/scratch/lead/rec/` (build_record.py, render.py, drift.py, recount.py), `.gov-runtime/scratch/lead/apply_sources2.py` |
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

## The background
W2-130 is a records clean-up (no code). Its main commits are history: e12f8a30c and c4420040f (2026-11-08/09), and
run 2's follow-ups 8d245901b (R-12), 8f8d707f0 (lessons), bce798c3a (the two marks, after an independent check). The
CTO re-baselined S4 to DEC-1123 (2) (P-W2-130-4 (a), c2d10bb45). This run (run 3) added, after bce798c3a:
- `11c4d7a5a`: a merge of `w2/integrate` (brings c2d10bb45);
- `57cbacfbf`: follow-up (1), the open and in-progress tickets' `sources:` from `gov links --propose-sources` at its
  parent, less the ids DEC-1123 (2)'s forms link;
- `ba9f5ed4d` and `58b52ccb0`: merges of the independent test designer's revisions (d5b07cc72: S4 to DEC-1123 (2);
  a606a530f: five marks cases cut back to their Verify lines after the lead's findings);
- `fcf5f5038`: the record and LINK-RECONCILIATION.md.
At 58b52ccb0 the acceptance folder passes 81 of 81 in the lead's run.

## What you check (narrow: this run's commits; the earlier history only as the record copies it)
1. **The sources follow-up `57cbacfbf`.** It changes only `sources:` lines of tickets open or in progress at its
   parent, and nothing else in any file. The ids it adds equal `gov links --propose-sources --all` at its parent
   (open and in-progress tickets) less the record's `dec-1123-linked` pairs. Each `dec-1123-linked` entry really is
   of its form at the head (a backlog or plan row in the ticket's `list_rows`; a WBS id whose ticket's id is in
   `sources:`; DEC-798 with DEC-1033 in `sources:`), and every UNLINKED_ID `gov links --all` reports on an open or
   in-progress ticket at the head is one of them. Judge the two choices the record names: W2-H046 added to
   DAEO-6w5n's `sources:` (a backlog row not in its `list_rows`), and W3-P09 left as a form on DAEO-ecac.
2. **The record's blocks against git and the tools.** Check, by your own reads and runs: `commits` (each hash, the
   order, the lists); `audits` (each audit's head, date and source against the audit texts named above; that every
   committed free-text mark is listed with verdict right; that no committed mark is one judged wrong); `judged-wrong`
   (each verdict quoted from aud-marks-1's B and C tables, the 8 `in_gov_links: true` ones equal to what
   `gov links --all` reports); `trailer-residuals` against the `recount` block run at 232efc47d; `drift` run at the
   head; `counts-after` against `gov links --all --json` at the head; `left`, `closed-missing`, `lessons`. Any block
   that misstates history or the tools is a finding.
3. **LINK-RECONCILIATION.md** carries the sitting's 150 rows (groups A to F) with the sitting's proposal and reason
   verbatim and DEC-1098 (3)'s ruling, and names the sitting file and DEC-1098 (3).
4. **The test designer's revisions** (d5b07cc72, a606a530f): does each revised case still check what its Verify
   line states (S1, S2, S4), and nothing less? A case weakened below its line is a finding; a case that reads more
   than its line is not.
5. **No register or ticket text changed in this run** other than `57cbacfbf`'s `sources:` lines
   (`git diff bce798c3a 58b52ccb0 -- docs/DECISION_REGISTER.md .tickets/` less what the merge 11c4d7a5a brought from
   `w2/integrate`).
You may run the acceptance folder (it clones into `$TMPDIR`; the tree is never written):
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest /home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
and `gov links` on a `git clone --shared` of the tree in `$TMPDIR` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src python3 -m gov.cli.main links --all --json --root <clone>`).
A resource gate's refusal is a wait.

## Return (your last message)
1. A header: `Independent auditor, <ISO 8601 date and time with zone, from date -Is>, at <full hash of 58b52ccb0>,
   W2-130 run 3 narrow check.`
2. Per item 1 to 5: what you checked, how, and what you found.
3. Each finding with its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
4. Last, a fenced block opened by ```` ```verdict ```` holding one JSON object:
   `{"head": "<full hash>", "date": "<ISO>", "kpis": [{"kpi": "<item>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]} ...]}`.

## Searching
Read and Grep only, and git show; no `gov retrieve` or `gov context`. Search once, then once more in other words;
answer from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out
material or any hidden or memory-verdict folder. Refused twice for the same call by the guard, the sandbox or a hook:
stop and say so; never work around a refusal.
