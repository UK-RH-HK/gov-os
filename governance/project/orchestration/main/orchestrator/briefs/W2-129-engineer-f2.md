# W2-129 — the engineer's brief, S18: a settlement is a change (DAEO-q7lk)

You are a fresh engineer for **W2-129** (`.tickets/DAEO-q7lk.md`). Read the new line **S18** and the note "D-6 part 2
item F2's round 2 placed here". **One small pass, S18 only.**

## The point
`gov links`' UNMARKED_CHANGE counts the loader's `register_statements` classes supersede and amend
(`src/gov/links/check.py`, `CHANGE_CLASSES` and its users). S18 makes it count the class **`settle`** as well, a
`**Settles:** DEC-x` label, as a change. Then:
- a settled entry whose own text names no such changer gives UNMARKED_CHANGE `[DEC-x, DEC-y]`, in the same order and
  form as an amendment;
- `--propose-marks` adds `**Changed by:** DEC-y`, as for a part change;
- a PROPOSED, REJECTED or WITHDRAWN settler gives nothing, as today for the other forms.

Every other code and count is unchanged. Check on the repository that only `**Settles:**` pairs are added: the register
holds 4 `**Settles:**` labels. Record the before and after `--all` counts in `docs/research/W2-129-links.md`.

**The designer's interface line (its README):**
> a register statement the loader's `register_statements` gives the class `settle` (`**Settles:** DEC-x` in DEC-y's
> status line), from an entry that is not PROPOSED, to an entry whose own text names neither DEC-y nor any changer,
> gives `UNMARKED_CHANGE <DEC-x> ... <DEC-y> ... | docs/DECISION_REGISTER.md:<line> | <role> | <fix>`; in `--json`
> its `ids` are exactly DEC-x and DEC-y, in the order the same run gives a supersession's (changed, changer).

## Where you work
- `/home/usain/gov-os-worktrees/W2-129-f2`, branch `w2/W2-129-f2`, head `b4b4b18cb` (the S18 cases merged).
- Your paths: `src/gov/links/**`, `tests/unit/links/**` and `docs/research/W2-129-links.md`.
- **You never read `tests/acceptance/W2-129/`.**
  - Recursive grep carries `--exclude-dir=W2-129`.
  - Grep and Glob carry `!tests/acceptance/W2-129/**` as a separate pattern.

## Verify
Run everything through the heavy slot that `EMG-common.md` names, with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-129-f2/src`, a scratch HOME with `.local` linked in, and
`PYTHONUSERBASE=/home/usain/.local`:
- `tests/unit/links`, with a new case;
- `python3 -m gov.cli.main accept W2-129 --root /home/usain/gov-os-worktrees/W2-129-f2`, all green.

Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- No GPU, network or installs. Never touch `tests/acceptance/**`, `.tickets/`, `.claude/` or `src/gov/decisions/**`.
- **DEC-1080:** one simple command per Bash call. Waits by pid only. Do not merge `w2/integrate`.
- **Commit** on `w2/W2-129-f2` with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1109, DEC-866" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the commits;
- `gov accept W2-129` per line;
- the unit counts;
- the `--all` counts before and after.
