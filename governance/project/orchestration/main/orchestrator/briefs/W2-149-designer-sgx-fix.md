# W2-149 — the independent test designer's brief: one defect in set-up A's S16 writer case (DAEO-52ku)

You are a fresh independent test designer for **W2-149** (`.tickets/DAEO-52ku.md`). The cases for set-up A's wiring
were written on `w2/W2-149-sgx-tests` (commits `f65c0c992`, `59030819b`; the README's "Set-up A's wiring"). **One small
pass: one defect, found by the lead.**

## The defect
`test_w2_149_setup_a_delivery.py::test_s16_set_up_a_writers_deliver_their_cases_to_the_half_s_planted_folder` (both
params) fails against the engineer's build with "the aims outside the wall's tar: [<the wall's own tar>]". The case
passes `skip=[world.tar(line)]` (a `pathlib.Path`) to `w2_149_setup_a.files_holding`, which compares each walked file
`p` (a `str`) with `p == s`: a `str` never equals a `Path`, so the wall's own tar, where `aims.jsonl` belongs (the
writer brief §6, S16), is never skipped and counts as a leak. Fix the comparison so a skip entry matches its own file
and anything under it (compare as strings or as resolved paths), and check every other caller of `files_holding` still
means what it says. Nothing else changes; no expectation is weakened: a copy of the aims marker anywhere but the wall's
tar must still fail the case.

Verify the fix both ways in your own scratch (never committed): with a planted extra copy of the marker outside the
tar the case still fails; without it the skip works. Say in the README's set-up A notes what changed and why.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149-sgx-tests`, branch `w2/W2-149-sgx-tests`, head `27d1ad7d9` (`w2/integrate`
  merged in). Write only `tests/acceptance/W2-149/`.
- **Your record:** your whole return is your session's final message, in full.

## Rules
- You never read the implementation: not `governance/project/orchestration/tools/indep_launch.py`, not
  `tests/unit/orchestration/test_w2_149*`, not `docs/changes/W2-149-evidence.md`, never the engineer's worktree
  (`W2-149-sgx`).
- No GPU, model, network or installs; no real `claude` session. Every case on planted roots; never the real
  `~/gov-os-eval`, `~/gov-os-runs`, `~/gov-os-wall-trees` or `~/.claude`. The hidden-half rule of `EMG-common.md`.
- Run through the heavy slot `EMG-common.md` names, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx-tests/src`,
  your sandbox's TMPDIR, a scratch HOME with `.local` linked in, `PYTHONUSERBASE=/home/usain/.local`; then
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx-tests` (expected unchanged
  but for this case: the set-up A cases red against today's integrate script).
- **DEC-1080:** one simple command per Bash call. Waits by pid only.
- **Commit** on `w2/W2-149-sgx-tests`, only `tests/acceptance/W2-149/`, with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1112 (3) (S16's writer case: the skip of the wall's own tar compared a str with a Path)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Report your scratch size.

## Return
The twelve labelled fields of `EMG-common.md` first, as labelled lines; then the commit, the change in one line, the
both-ways check, `gov accept`'s counts, and `TESTS-READY`. Refused twice for the same call: stop and say so.
