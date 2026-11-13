# ACT-G14b: a coordination ticket's `{ticket_tests}` is its own folder only (DEC-1056, DEC-1058; DAEO-sdxk, W2-00)

Drafted 2026-11-03 by the CTO's emergency engineer (session 33b3628c). It is an (a) ACT for the owner's operator
(DEC-1058). It follows ACT-G14, live at 4edd196c. Nothing in it is live until the operator runs §3.

**Basis (DEC-1052):** it passes Q1 and Q2.
- Q1: it keeps role separation as DEC-1056 meant it: an engineer is refused its own ticket's tests, and other tickets'
  tests stay readable.
- Q2: without it, every engineer on W2-00 is refused 109 other tickets' acceptance files. That loses regression work.

## 1. The defect and the change
**The defect.** D-4's cut (merged 6008a41f) carries 101 test designer commits trailered `Task: DAEO-sdxk`. W2-00 is the
coordination ticket: `class: coordination`, no `tests/acceptance/W2-00/` and no acceptance tests of its own. The
refactoring has no ticket, so its commits use W2-00's.
- Link source (i) of `{ticket_tests}`, a test designer's `Task:` naming the ticket, now ties 109 of the 1,098
  acceptance files to W2-00. It was 4.
- So every engineer running under W2-00 (the CTO's in-session agents) is refused them as "its own ticket's tests".
- `tools/guard4_check.py --settings` shows it: `FAIL lifted engineer reads acceptance: want allow, got deny` (an
  engineer on DAEO-sdxk reading `tests/acceptance/W2-64/README.md`, one of the 109).

**The change** (`.claude/hooks/role_reads.py` only, +31/−2; `pretooluse.py`, `bash_writes.py` and the path map are
unchanged):
- A ticket whose front matter says `class: coordination` gets `{ticket_tests}` = its own folder only. Link sources
  (i) and (ii) are not used for it.
- Every other ticket is unchanged.
- The ticket's class is read lazily, only when the link source would be consulted (an engineer's read of another
  ticket's acceptance folder), so other calls cost nothing more.
- A ticket that cannot be read gives the existing fallback: its own folder only, and the refusal says so.

Measured on the main tree, engineers' linked files:

| Ticket | Before | After |
|---|---|---|
| W2-00 (DAEO-sdxk) | 109 | 0 (W2-54's and W2-64's tests readable; `tests/acceptance/W2-00/**` still refused) |
| W2-126 (DAEO-jpr0) | 8 | 8 (W2-54's revised `test_w2_54_query_cache.py` still refused) |

## 2. The evidence
**Planted cases.** `drafts/g14/test_g14.py`: **151 passed, 1 skipped**. The 6 new cases:
- 5 in a fixture repository with a coordination ticket and a test designer's commit under its `Task:` in another
  folder:
  - that commit's link is ignored;
  - a case revised for a normal ticket stays readable to the coordination ticket's engineer;
  - its own folder stays refused;
  - the normal ticket's links are kept;
  - the case cut under the coordination ticket is readable to the normal ticket's engineer;
- 1 on the real repository: W2-00's engineer reads W2-54's and W2-64's tests and is refused `tests/acceptance/W2-00/`.

The skip is `test_w2_91_tests_today`. W2-91 is now merged into `w2/integrate` (947da7a4, D-4b), so its tests tree
holds integrated code. The rule is still covered by the injected tests-tree case.

**`tests/unit/hooks/test_live_hook.py`** (63 cases, in the suite): 63 passed on the live hook, and 63 passed on the
candidate (rehearsal). No case is touched by the change: its fixture tickets carry no `class: coordination`. Nothing is
named for a test designer.

**The rest:**
- `tools/guard4_check.py` against the main tree with the candidate: PASS. It was FAIL on the live hook (the case
  above).
- `drafts/act-guard-fix-4/test_guard_fix_4.py`: 467 passed (rehearsal).

## 3. The commands (your operator, in the main tree)
Preconditions:
- **a fresh shell** (a new terminal, or `env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" PATH="$PATH" LANG="$LANG"
  bash --noprofile --norc`): `D` and `T` not exported;
- no merge-queue landing and no other ACT running;
- `git status --short -- .claude/` shows nothing.

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
rm -rf /tmp/gov-os-act-g14b
D=.gov-runtime/scratch/orchestrator/drafts/g14
T=.gov-runtime/scratch/orchestrator/tools
env | grep -c "^[DT]=" || true
git status --short -- .claude/
sha256sum .claude/hooks/pretooluse.py .claude/hooks/role_reads.py $D/pretooluse.py $D/role_reads.py | cut -c1-12
python3 $T/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS | grep -E '^FAIL|^PASS'
mkdir -p $D/backup-g14b
cp -p .claude/hooks/role_reads.py $D/backup-g14b/
cp $D/role_reads.py .claude/hooks/
python3 $T/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS | grep -E '^FAIL|^PASS'
TMPDIR=/tmp/gov-os-act-g14b bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider tests/unit/hooks/test_live_hook.py -rf | grep -E "^FAILED|failed|passed"
GUARD_FIX4_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14b bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py -rf | grep -E "^FAILED|failed|passed"
G14_HOOK=$PWD/.claude/hooks/pretooluse.py TMPDIR=/tmp/gov-os-act-g14b bash $T/heavy_slot.sh python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider $D/test_g14.py -rf | grep -E "^FAILED|failed|passed"
git add .claude/hooks/role_reads.py
git commit -m "ACT-G14b: a coordination ticket's {ticket_tests} is its own folder only (DEC-1056, DEC-1058): W2-00's Task: links no longer refuse other tickets' tests" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1056, DEC-1058" --trailer "Role: owner"
git rev-parse HEAD > $D/backup-g14b/act-commit && cut -c1-12 $D/backup-g14b/act-commit
```

What each line must show (exactly as the rehearsal printed; stop at the first that differs and tell the CTO):
- `rm`, `git status`, `mkdir`, `cp`: silent.
- `env | grep -c`: `0`.
- `sha256sum`, four lines:

  | File | Hash |
  |---|---|
  | `.claude/hooks/pretooluse.py` (live) | `e406653ef6c9` |
  | `.claude/hooks/role_reads.py` (live) | `8c1ea44b2313` |
  | `drafts/g14/pretooluse.py` | `e406653ef6c9` |
  | `drafts/g14/role_reads.py` (the candidate) | `5407aade9417` |

- The first `guard4_check.py` (before): `FAIL lifted engineer reads acceptance: want allow, got deny |`, then `FAIL`.
  That is the defect.
- The second `guard4_check.py` (after the copy): `PASS`.
- `test_live_hook.py`: `63 passed in …`.
- `test_guard_fix_4.py`: `467 passed in …`.
- `test_g14.py`: `151 passed, 1 skipped in …`.
- `git commit`: `1 file changed, 31 insertions(+), 2 deletions(-)`.
- `git rev-parse`: the commit's hash, saved in `backup-g14b/act-commit` for the rollback.
- **A red check after the `cp`:** the new `role_reads.py` is live from that line on. Restore it by hand
  (`cp -p $D/backup-g14b/role_reads.py .claude/hooks/`) and tell the CTO.

**Rehearsed end to end on 2026-11-03 20:59:36–21:00:24 GMT, from a fresh shell** (`env -i` with only HOME, USER,
LOGNAME, PATH and LANG), in a clone at `6cf2e7d2d3ff` (today's head of `w2/integrate`):
`~/gov-os-runs/G14b-rehearsal/Dynamic-Agentic-Engineering-OS`, by `drafts/g14/rehearse_act_g14b.sh` (§3 line for
line, then §4). Its output is attached as `drafts/g14/rehearsal-g14b.log`.
- The clone was prepared as ACT-G14's rehearsal prepared its own:
  - every local branch recreated with its reflog;
  - the untracked scratch copied in with the root's path written as the clone's (`role_reads.py` names no root, so
    its hash is the main tree's);
  - the same folder name, outside `/tmp`.
- Every line printed what this section says. The rehearsal clone is removed.

**When it takes effect:**
- The main tree: at the next tool call of a session in it.
- A worktree: when `w2/integrate` is merged into it, which brings the new `role_reads.py`.

## 4. The rollback (one command)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS && D=.gov-runtime/scratch/orchestrator/drafts/g14 && read -r H < $D/backup-g14b/act-commit && git revert --no-commit "$H" && git commit -m "Revert ACT-G14b (${H:0:12})" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1058" --trailer "Role: owner" && python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings $PWD | grep -E '^FAIL|^PASS'
```
- In the rehearsal: `1 file changed, 2 insertions(+), 31 deletions(-)`, then the defect's two lines again
  (`FAIL lifted engineer reads acceptance …`, `FAIL`), and `role_reads.py` back at `8c1ea44b2313`.
- The backup is `drafts/g14/backup-g14b/role_reads.py`.

## 5. The risk
- **A coordination ticket gets no linked cases.** Today only W2-00 is `class: coordination`. A revision made for a
  real ticket under W2-00's `Task:` is not tied to that real ticket by (i). It is tied only by (ii), if it was made on
  that ticket's own tests branch. That is the existing R2-F11 row, and the D-5 template line (`Task: <the ticket it is
  for>`) remains the remedy.
- **The class comes from the session's ticket file.** A ticket whose class is changed to `coordination` gets its own
  folder only. Changing a ticket's class is the CTO's.
- **No other behaviour changes:** `pretooluse.py`, the path map, `{ticket_impl}` and the other rules are untouched.

## 6. Recommendation
Apply. Confidence high: the change is small, it is pinned by 6 new planted cases, and the suite's
`test_live_hook.py`, `test_guard_fix_4.py` and `guard4_check.py` are green on it in a faithful rehearsal.
An independent review of the +31/−2 delta is the CTO's call.
