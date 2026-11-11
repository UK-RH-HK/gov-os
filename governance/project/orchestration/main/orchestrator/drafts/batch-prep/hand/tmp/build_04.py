import sys
sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/hand/tmp")
from parts import *

W2, TID, KIND = "W2-04", "DAEO-u4oz", "review"
OUT = PREP / "hand" / "W2-04-A5-r6-review.md"
IMPL = "CAP-15.d, DEC-860, DEC-1025, DEC-1052"
PATHS = "src/gov/context/**, src/gov/retrieval/supplementary*, tests/unit/context/**"

summary = ("The ticket: `gov context <ticket>` holds a packet ceiling of about 6,000 tokens, refuses a mandatory input that alone "
           "exceeds it, names each decision by its own hash, is reproducible on stores rebuilt from one commit, blocks on an unreadable "
           "or emptied mandatory record, builds its supplementary query from the KPIs and title, and takes supplementary evidence in "
           "batches within the ceiling (DEC-860).")

head = sub(ASSIGNMENT_HEAD, ID=TID, W2=W2, PROFILE="FULL (C2)", TITLE="gov context bounded and reproducible (W2-04): the independent review of the repaired code, and its probe record",
           SUMMARY=summary, USD="6", PATHS=PATHS + " (your own writes: the probe record under `docs/probes/DAEO-u4oz/` only, DEC-733)")

kpis = kpi_table(TID, W2)
dod = DOD.replace("@@DOD_NOTE@@", "DOD-4 is the point of this run: the reviewer's verdict block gives READY, and the probe record is committed")

mid = f"""
## What must be true (KPI lines and how each is checked)
{kpis}
Non-goals (the ticket states none; `gov brief`'s NON_GOALS_MISSING): out of this review are review 1's F4 (31 open tickets refuse their context at 6,000 tokens; the close builds the context after its runs; the session-start hook drops the error: DEC-1025 (4), a new ticket for the owner, DEC-974), F5 and F6 (Wave 3 rows), and anything under `src/gov/context/**` that the KPI lines do not name.
{dod}

## Inputs
- Sources: CAP-15.d, DEC-860, CAP-15.b, DEC-1025, DEC-1052. Read each by id in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md, or ask memory (below). Also DEC-1010 and DEC-1131 (one bar, two rounds), DEC-1120 (RUBRIC-2), DEC-1130 (1) (why this brief is hand-built).
- **What the lead knows of the ground** (state as of 2026-11-11 ~18:00 UTC; the CTO's helper read the ticket, the registers and the last lead return, not the code):
  - **State.** W2-04 is merged into `w2/integrate` as `70965cf61` "accepted as built" (D-1, DEC-1052 M-1; D9-FATES: all 8 lines met, `gov accept` to run once for the close). Branch `w2/W2-04` is 0 commits ahead of integrate and 1,551 behind. **There is no worktree and no `docs/probes/DAEO-u4oz/` record on integrate**: `gov close` would answer `PROBE_MISSING`. W2-05 waits on W2-04 (shared file `src/gov/context/__init__.py`), so this review is on the critical path of batch 4.
  - **Your tree.** The CTO creates `/home/usain/gov-os-worktrees/W2-04` before launching you, from `w2/integrate` (the branch holds nothing integrate lacks, so it is moved to integrate's head with `--ff-only`). Your first call checks that `git -C /home/usain/gov-os-worktrees/W2-04 rev-parse HEAD` equals `git -C /home/usain/Dynamic-Agentic-Engineering-OS rev-parse w2/integrate`, the tree is clean and `.gov-runtime/scratch/lead/CHECKPOINT.md` does not exist (a fresh run; if it exists, resume from it). Anything else: stop and return PACKAGES.
  - **History.** Review 1 (probed head `b37b5c8f1741`, Opus at max, 18.7 min, 11-02) FAILED: **F1** in scope, ordinary work yes, fails open: a mandatory capability file or dependency ticket emptied in the working tree was shown as read with the empty-content hash and 0 tokens (S5); **F2** the repaired room-ends-exactly case disagreed with S7 and S7a (`further_batch` must start at the first ranked item not stacked); **F3** the check read green when every ticket refused; F4, F5, F6 as above (F4 not this ticket's). DEC-1025 (delegated, ACCEPTED): one repair round, the last before the owner (a test-design batch, a fresh engineer, `gov accept`, the scoped run, then **review 2 with a different model or effort than review 1's**; this review is that one; review 1 ran at max, so run it at high, which is also RUBRIC-2's setting for a C2 FULL reviewer). The repair is on integrate: tests `42e73adb7` (designer, `Rewrite-Reason: DEC-1025`), the engineer's `de81824be` ("an emptied mandatory file blocks, the room ending exactly names what is left, an all-refused check is unmeasured"), the merge `a0c79a6c9`, then `fcfb9150b` and `98993db4e` (integrate merged in: W2-54's packet-hash case keeps W2-04's reads and W2-126's two caches), then `70965cf61`.
  - **Last lead return** (`log/W2-04-A5-review.json`, 11-02 09:38): PACKAGES with F1 as above, 12 small reviewer probes, nothing committed. **The repair round's own lead log is empty (0 bytes): there is no record of a scoped run or a review of `de81824be` or the merges after it.** So you run `gov accept` and the scoped verification yourself (below) and give the reviewer their results.
  - **Open points.** (1) This is the second and last review: a fail goes to the owner once with options, never a third round (DEC-1010, DEC-1131). (2) The reviewer must show F1, F2 and F3 repaired in ordinary use (an emptied or whitespace-only mandatory file and dependency ticket in `--brief`, `--dry-run` and the plain mode; the exact-fit and zero-room batch cases; the all-refused check), and that the later merges (W2-126's two caches) kept S3 and S4 (packet hash). (3) A `JUDGEMENT.md` finding in a file the KPI lines do not name is `scope: out`, a row. (4) Whether `gov context DAEO-u4oz` itself is over its ceiling is unknown: step 6a of the common brief (`context_ceiling`) answers it; report the figures, do not trim.
"""

run = f"""
## Your run: review (only this section is in your brief)
**review**: one review round (FULL, C2), then the probe record. The role template's steps, made specific:
1. First calls: {{identity}} (expect `orchestrator` and `{TID}`), {{where}} (expect `/home/usain/gov-os-worktrees/W2-04` and `w2/W2-04`), the head check above, `test -f /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/CHECKPOINT.md && echo resume`, read the ticket file, then write a first CHECKPOINT.md (STATE, HEAD as 12 digits, NEXT, WAITING ON). Run {{hooks_check}} before any commit.
2. Rebuild the tree's store once, in the background with an exit-code file ({{rebuild}}; run {{disk_gate}} first; a new worktree has no store). Held over 90 minutes by the slot queue: stop waiting, checkpoint, return PACKAGES (DEC-943).
3. When the rebuild has ended: run {{accept}} once and keep its per-line counts (S1-S7, F1) for the reviewer's brief. Start {{lead_verify}} once in the background (the scoped verification, DOD-2; it writes only scratch) and let it run beside the reviewer; name a red only from the known-reds list (`{TOOLS}/skip_known.json`), and re-run a load-sensitive case alone once. A red this ticket owns is PACKAGES; the review does not wait for it.
4. Write the reviewer's brief into `/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/briefs/rev-2.md` (a model: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/D10-W2-96-probe-r3.md`; the role template: `template/governance/kernel/templates/role-reviewer.md` in your tree; `gov context` first, by hand if it refuses). It holds: the sandbox check as step 0 (EMG-d4b-launched.md's form: a write outside the tree must fail, `git hash-object -w` and `update-index --refresh` must work); the head to probe (12 digits) and that `git rev-parse HEAD` must equal it at the start and the end; the judged paths (`src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`, `tests/acceptance/W2-04/**`, the ticket file); the history above (review 1's F1 to F6, the repair commits, the merges after it); your `gov accept` counts; that it re-runs nothing the lead ran and runs code only to reproduce a finding in a temporary folder with `PYTHONDONTWRITEBYTECODE=1`; that the session-start hook is a second caller of `gov.context.context` (a review-1 gap); `gov retrieve` is not available in its sandbox (it reads with Read and Grep; it searches again once the same way); DEC-849 read refusals taken, never routed round; the hidden-half and secrets rule (DEC-820); row W2-L423's rule; DEC-1010's two-round bar; the KPI ids for its verdict block (S1 to S7 and F1, as in the table above); and that it writes nothing in any tree. **It carries the judgement rules below, word for word.** It ends with the twelve fields, each finding with its `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other` lines and `scope: in|out`, what would reverse it (DEC-1014), and the fenced `verdict` block; refused twice for the same call: stop and say so.
5. Launch it read-only with {{launch_worker}} (worker tree `/home/usain/gov-os-worktrees/W2-04`, role `independent-auditor`, class C2, `--model claude-opus-5-5`, effort high, `--projection-usd 5`), wait with {{wait_for}}. Check its twelve fields (one resume with the missing list), the launcher's tripwire and sandbox line, and `git status --short` (clean).
6. Compute READY from the reviewer's record with `verdict.ready` (`{TOOLS}/verdict.py`, a script file; a KPI line marked fail blocks on its own, DEC-1131 (3)). **READY:** write `docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md` in the schema form (see `docs/probes/DAEO-ouet/PR-DAEO-ouet.md`: front matter `type: probe`, `task: {TID}`, `reviewer_session`, `implementer_session` (the repair engineer's and designer's), `reviewer_wrote_nothing: true`, `commissioned_by: orchestrator`, `judged_by: orchestrator`, `judgement: pass`, `probed_commit` the **full** id of the probed head; a one-paragraph header; the reviewer's record as returned, with its verdict block), commit it alone (trailers above) and nothing else after the probed head. **Not READY:** the draft stays under `.gov-runtime/scratch/lead/probes/`, no record is committed, and you return PACKAGES with every finding triaged (scope, ordinary work, consequence), the classification on one line before your recommendation (DEC-809), and the options for the owner (no third round).
7. Before you return: {{links}} (`gov links --since <the head you started from>`, first line quoted in `evidence`), {{keyword_warn}}, {{context_ceiling}} once, the scratch measures, CHECKPOINT.md rewritten. `git status --short` empty. DONE adds: the probed head, `gov accept` counts per line, the scoped run's counts and JUnit path, the `gov.__file__` line (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -c "import gov; print(gov.__file__)"`), the reviewer's verdict path, residuals as rows, lines against the estimate of 220.
Estimated at 0.5 lead-hour and about $6 (E: review 1's lead 0.4 h and $1.6, plus one reviewer about $4 to 5, M); the scoped run and the rebuild queue are the uncertain part.
"""

rubric = sub(RUBRIC, RUBRIC_ROWS="""| worker | role | class | model | effort | when |
|---|---|---|---|---|---|
| the reviewer | independent-auditor (read-only) | C2 (FULL) | Opus (`claude-opus-5-5`) | high | once; review 1 was Opus at max, so this one differs, as DEC-1025 (1) asks |
| none other | | | | | a fail returns PACKAGES; no repair starts here (DEC-1131, DEC-1010) |""")

jud = f"""
## Judgement rules for the reviewer's brief (governance/project/briefs/JUDGEMENT.md, word for word; copy it into the reviewer's brief unchanged)

{judgement()}
"""

body = (HAND_NOTICE.replace("@@REFUSAL@@", refusal("W2-04", "review")) + head + mid
        + "\n## Commands (copy them as they are)\n" + commands(W2, TID) + "\n" + FORMS + "\n" + rubric + run + jud)
body = sub(body, ID=TID, W2=W2, KIND=KIND, IMPL=IMPL, PROFILE="FULL")
body = body.replace("{identity}", "`printenv GOV_ROLE GOV_TICKET`")
# command references in the run text point at the table; spell them by name
for name in ("identity", "where", "hooks_check", "rebuild", "disk_gate", "accept", "lead_verify", "launch_worker", "wait_for", "links", "keyword_warn", "context_ceiling"):
    body = body.replace("{" + name + "}", f"(command `{name}`)")

tail = "\n\n---\n\n# The common lead brief (committed, `governance/project/briefs/LEAD-w2-common.md`), appended whole\n\n" + \
    common(W2, TID, "FULL", PATHS, ", ".join(ticket(TID)["list_rows"]), "CAP-15.d, DEC-860, CAP-15.b, DEC-1025, DEC-1052", IMPL, "220 lines of code")
OUT.write_text(body + tail)
print(OUT, len(body + tail))
