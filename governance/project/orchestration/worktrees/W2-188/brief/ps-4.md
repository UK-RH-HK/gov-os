Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-188 (DAEO-zlog): the adopt skill's step 6 and the practice record, product-spec (brief ps-4, from the ticket lead: a red to fix and two review findings)

You are the product-spec worker for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2, by the CIT-P route (a
kernel skill change: the owner approves its bytes after an independent review, before any merge; CAP-33, DEC-1166 (4)).
Use your skill `spec-writing` where it applies.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188 |
| branch | w2/W2-188 (from w2/integrate at 5336a6fca, the base) |
| the ticket (read whole; its **Interface** I1-I6 first: it is binding) | /home/usain/gov-os-worktrees/W2-188/.tickets/DAEO-zlog.md |
| the CIT-P draft to start from (a copy of the CTO's) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/draft-W2-188-CIT-P.md |
| the context packet (`gov context DAEO-zlog --role product-spec`, JSON: ticket and decisions' texts) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/ctx-ps.md |
| the reconciliation (G4, G6) | /home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/briefs/MEMORY-AUDIT.md |
| the decision package | /home/usain/gov-os-worktrees/W2-188/governance/project/orchestration/packages/MEMORY-AUDIT-P1.md |
| the figures' sources | governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md, .../LIFT-1/E3-RESULT.md |
| the step matcher | tests/acceptance/W2-88a/w2_88a_support.py (`a9_regions`, `check_steps`, `check_pointer`, `heading_section`) |
| your scratch | the sandbox's own `$TMPDIR` (the sandbox's permission settings deny creating a folder under `.gov-runtime/scratch/`) |

Allowed paths, and the only ones you write: `template/governance/kernel/skills/adopt/SKILL.md`,
`.rulesync/skills/adopt/SKILL.md`, `template/.rulesync/skills/adopt/SKILL.md`, `docs/research/W2-88-memory-practice.md`,
`docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**`. Never `.claude/` (the copies ACT regenerates
`.claude/skills/adopt/SKILL.md` after the owner's yes) and never any test file (`tests/**`): F2.

Read the register by id only (`docs/DECISION_REGISTER.md`, 1.6 MB; grep `### DEC-1179` and the others in the ticket's
`sources:`). Search with the Read and Grep tools; if the first search does not answer, search once more in other words.

## The state
The work is written, committed and reviewed: head `b75472d48` was probed by an independent auditor, verdict PASS; its
record is `docs/probes/DAEO-zlog/PR-DAEO-zlog.md` (committed by the lead). **Do not change the skill's three copies or
the practice record**: they stand as reviewed (the skill at sha256 `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`).
You change only `docs/probes/DAEO-zlog/checks.md` and `docs/changes/W2-188-CIT-P.md`. Never `tests/**`, never `.claude/`.

## The failing output (the whole verification run's reds that are yours)
```
FAILED tests/acceptance/W1-08/test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records
    AssertionError: checks.md: no YAML frontmatter (the file does not open with a '---' line) and it is not a .yaml, .yml or .json file
FAILED tests/acceptance/W1-26/test_w1_26_probe_records.py::test_this_repository_s_probe_records_are_well_formed
    AssertionError: checks.md has no frontmatter
assert '# DAEO-zlog ...phrase checks' == '---'
```
Every file under `docs/probes/` is read as a probe record. Read the schema the tests use (find `probe.schema.json`
under `src/` or `template/`) and the two tests, and give `checks.md` front matter the schema accepts (string fields
where it wants strings), saying it is the product-spec session's own I5 check record, not a review. Then run those two
test files (and nothing else) through the heavy slot, from the tree:
`env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-08/test_w1_08_probe.py tests/acceptance/W1-26/test_w1_26_probe_records.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
(make `$TMPDIR/empty-home` first; a resource gate's refusal is a wait). Both must pass.

## Two review findings, accepted by the lead, as behaviour the CIT-P must show (`docs/changes/W2-188-CIT-P.md`)
- **F2:** the impact table's "Generated copies" row must say that `adapter-portability` (`python3 -m gov.adapters.portability`,
  a G1 hard-block check that `gov check`'s structural pass runs when a diff touches the kernel skills or `.rulesync/`)
  reports one finding, `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md`, from the merge of these bytes until the
  copies ACT regenerates that copy, so the copies ACT should ride in the same landing. Run the check yourself
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-188/src python3 -m gov.adapters.portability`) and quote what it gives.
- **F3:** §3's parenthesis that says the first sub-bullet of §5 item 6's practice lines is "unchanged" misreads against
  the base (that line changed from "judge" to "choose or judge", as §2.2 shows); say "unchanged by the re-word in
  be8b99ccb".
Leave the W2-11 row as it is (it is true; the ticket's clause about it goes to the CTO as a package).

## The review's verdict (the last thing you write in the CIT-P)
In §6, replace "Review: PENDING ..." with the round's facts: round 1 by a fresh read-only independent auditor (au-1,
session `2bd2339c-ba97-4e67-bf75-69f84af5a970`, Opus, high), probed commit `b75472d4825cece64936451f21b259787b5ecf97`,
record `docs/probes/DAEO-zlog/PR-DAEO-zlog.md`, four findings: F1 (the ticket's S5/I6 premise, to the CTO), F2 and F3
(fixed in this record), F4 (ordinary work no, a Wave 3 row); none blocks (DEC-1010). Then end §6's review part with the
line `verdict: PASS` on a line of its own (the only `verdict:` line in the record). Set the front matter's `review:` to
`'PASS (round 1, docs/probes/DAEO-zlog/PR-DAEO-zlog.md)'`. Keep `owner_approval: 'pending'` and the owner paragraph.

Commit `checks.md` first, then the CIT-P last.

## Commits (your paths only; trailers in ONE final paragraph, no blank line inside it)
Commit in batches (the skill's three copies; the practice record; the probe record; the CIT-P last), each as:
```
git commit -m "<subject>" --trailer "Task: DAEO-zlog" --trailer "Role: product-spec" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1074, DEC-1072, DEC-1071, DEC-105, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>
```
`Implements:` lists only ids from the ticket's `sources:`. If anything changes the skill after the CIT-P is written,
recompute the after hash and commit the CIT-P again last.

## Rules
- Write files with the Write and Edit tools and absolute paths; anything longer than one line goes in a script in the sandbox's own `$TMPDIR` (find it with `echo $TMPDIR`; write
  it there with the Write tool at its absolute path), run with `python3 <file>` or `bash <file>`. `docs/probes/DAEO-zlog/`
  exists already; write into it with the Write tool.
- Use the sandbox's own `$TMPDIR`. You run no pytest; if you ever do, through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
  `PYTHONUSERBASE=/home/usain/.local -p no:cacheprovider -o tmp_path_retention_policy=failed`.
- Never open the evaluation sets' root (`~/gov-os-eval`), any hidden or memory-verdict folder, or secrets.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- No new ticket; a gap comes back in `unresolved` as a question with options, cost and a recommendation.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: each commit's hash and subject; the skill's sha256 after; the CIT-P record's sha256; the I5 results in one line each.
