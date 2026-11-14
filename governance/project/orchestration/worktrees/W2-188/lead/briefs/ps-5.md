# W2-188 (DAEO-zlog): one red in the CIT-P record, product-spec (brief ps-5, from the ticket lead)

You are a fresh product-spec worker for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2, by the CIT-P route (a
kernel skill change: the owner approves its bytes after an independent review, before any merge; CAP-33). You make the
**smallest wording change** in one file to turn one red green.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188 |
| branch | w2/W2-188 |
| the ticket (read S5, I6 and its last paragraph `P-W2-188-S5 (a)`: the re-baselined clause) | /home/usain/gov-os-worktrees/W2-188/.tickets/DAEO-zlog.md |
| the one file you change | /home/usain/gov-os-worktrees/W2-188/docs/changes/W2-188-CIT-P.md (§5, the impact table) |
| your scratch | the sandbox's own `$TMPDIR` (never a new folder under `.gov-runtime/scratch/`) |

**Do not change** the skill's three copies (`template/governance/kernel/skills/adopt/SKILL.md`,
`.rulesync/skills/adopt/SKILL.md`, `template/.rulesync/skills/adopt/SKILL.md`, sha256
`6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`), the practice record
`docs/research/W2-88-memory-practice.md`, anything under `docs/probes/`, any test (`tests/**`) or `.claude/` (F2).
Do not read `tests/acceptance/W2-188/`: you work from the failing output and the ticket's clause only. Read the register by
id only (`docs/DECISION_REGISTER.md`, 1.6 MB; `### DEC-1157`). You may read `tests/acceptance/W2-11/test_w2_11_skills.py`
(line 124 and the version case) to state the facts.

## The failing output
```
FAILED tests/acceptance/W2-188/test_w2_188_citp.py::test_s5_the_impact_table_says_w2_11_does_not_cover_adopt_adapter_portability_differs_until_the_copies_act_and_w2_88a_unchanged
E       AssertionError: docs/changes/W2-188-CIT-P.md's impact table: no table row says W2-11's body and version cases do not cover `adopt` and so stay as they are
```
The re-baselined clause: the impact table states that W2-11's body and version cases do not cover `adopt` (parametrized
over test-design, orchestration, audit and qa-review, `tests/acceptance/W2-11/test_w2_11_skills.py:124`), so they stay
as they are after the merge; that `adapter-portability` reports `GENERATED_DIFFERS` on `.claude/skills/adopt/SKILL.md`
until the copies ACT (the "Generated copies" row already says this); and that W2-88a's cases are unchanged (already said).

The "W2-11's cases" row of §5's table says the facts, but not in one statement. Re-word that row so it says plainly, in
one row, that W2-11's body and version cases do not cover `adopt` and so stay as they are after the merge; keep its
true facts (the parametrization, the version case and its round-2 twin, the run figures). Change nothing else in the
record: not the front matter, not the hashes, not the counts, not §6's review part or its `verdict: PASS` line, and keep
`owner_approval: 'pending'`.

## Check
Run the one test file through the heavy slot, from the tree (make `$TMPDIR/empty-home` first; a resource gate's refusal
is a wait):
`env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-188/test_w2_188_citp.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Every case must pass except `test_s5_the_owner_approval_line_names_the_after_sha256` (red by design until the owner's
yes). Also give `sha256sum` of the three skill copies (must still be `6a884cf1…9489`) and of the CIT-P after your commit,
and `git diff --stat HEAD~1` of your commit (one file).

## Commit (your path only; trailers in ONE final paragraph)
```
git commit -m "W2-188 (DAEO-zlog): the CIT-P's W2-11 row says in one statement that W2-11's body and version cases do not cover adopt and stay as they are (P-W2-188-S5 (a))" --trailer "Task: DAEO-zlog" --trailer "Role: product-spec" --trailer "Implements: DEC-1157, DEC-1179, DEC-105, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/changes/W2-188-CIT-P.md
```

## Rules
- Write files with the Write and Edit tools and absolute paths; anything longer than one line goes in a script under `$TMPDIR`.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- Never open the evaluation sets' root or any hidden or memory-verdict folder; never secrets.
- No new ticket; a gap comes back in `unresolved` as a question with options.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: your commit's hash; the row's old and new text; the pytest counts; the sha256 lines.
