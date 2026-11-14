# Brief: independent test designer, W2-116 (DAEO-f58b) pass 2b: S2's acceptance cases and R2-F3

You are the independent test designer (MR-3) for ticket DAEO-f58b (W2-116), profile STANDARD. You write acceptance
tests from the KPI line and the stated interface below, before and without reading the implementation of this pass
(the engineer builds it in parallel in /home/usain/gov-os-worktrees/W2-116; never read its uncommitted work or its
new commits on w2/W2-116 after e51b1fdf6, the counterpart's work, DEC-820). You may read the existing code on your
own branch to learn the public interface (CLI options, envelopes) as it stands.

## Where you work
- Your worktree: /home/usain/gov-os-worktrees/W2-116-tests, branch w2/W2-116-tests (at e51b1fdf6). Write only under
  `tests/acceptance/W2-116/` there. Commit there; never merge, never push.
- The existing suite of this ticket is in `tests/acceptance/W2-116/` (pass 1's cases, `w2_116_support.py`,
  `conftest.py`, `README.md`). Reuse the support code (a planted project with a branch `integrate`, a stand-in
  embedder, `gov(...)` runs as `sys.executable -m gov.cli.main` with the pytest process's PYTHONPATH). Extend it in
  place only by adding; never change what pass 1's cases rely on. Add a section to the README for pass 2b.
- Scratch: /home/usain/gov-os-worktrees/W2-116-tests/.gov-runtime/scratch/td/ (checkpoint and notes).
- Search with the Read and Grep tools; no `gov retrieve`, no `gov context` in the sandbox (DEC-1065). If a search does
  not answer, search once more in other words; then answer from both or say "not found".

## What to write: S2 and R2-F3 cases (new files `tests/acceptance/W2-116/test_w2_116_<name>.py`)
KPI S2: "It is refreshed after the nightly's verdict and at a set second time each day (both in the project's
configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982]. Verify: pass 2's
cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the
second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid
time refuses by name."

At least these, each a named case (name them `test_s2_success_...`, `test_s2_failure_...`, `test_r2f3_...`):
1. A planted config's two times are read: with `GOV_NOW` before `latest` and no verdict file, `--when-due` says
   `not_due` and builds nothing (no half, no record); moving `GOV_NOW` past `second` makes it due with reason `second`
   (so the times were read from the planted config, not defaults).
2. A refresh runs after a newer verdict file (a `verdict:` line file, and a JSON `"verdict"` file), with reason
   `after_nightly`, and writes `<link>.refresh.json` with the stated fields; a matching file without a verdict does not
   count; a verdict file older than the record's `at` does not make it due.
3. `latest` passes without a verdict: due with `after_nightly`; run again the same day: `not_due`.
4. `second`: due once after `second`; the next tick the same day says `not_due`.
5. `gov status --json`'s `integration_store` part: head, branch head, built time and age (age follows `GOV_NOW`), and
   `stale: false` for a fresh store; a store behind the branch (land a commit after the build) is `stale: true` with a
   `behind_branch` reason; a store built before the last due time (plant `GOV_NOW` and the times relative to the
   record's real `written_at`) is `stale: true` with `built_before_due`; no store configured gives the part
   `{"read": false, ...}` and `gov status` still exits 0.
6. A missing or invalid time refuses `REBUILD_CONFIG_INVALID` naming the key (`details.key` and the message): at least
   a missing `second`, an invalid `after_nightly.latest` (e.g. `"25:00"`), and no `integration_refresh` with
   `--when-due`; nothing is built.
7. R2-F3: two store folders at the same commit; a continuation made on one, used against the other, refuses
   `CONTINUATION_INVALID`; used against the same folder it pages. Through the link: a token made through the link, the
   link then pointed at the other half (at the same commit), refuses.

Keep each case's runtime low: one built store reused where the support code allows; plant the clock with `GOV_NOW`
and verdict file times with `os.utime`; never sleep for the clock.

## Check red
Run your new cases on your branch (the code before pass 2b) and record that each fails for the stated reason (an
unknown `--when-due` option, no `integration_store` part, a token accepted on the other folder ...), not for a
fault of the test. A case that passes on the old code: say why in the README (e.g. a guard that already holds), or
make it test the new behaviour. Write the red record (each case, its failure line) to your scratch and into the README.

## How to run pytest (every run)
```
env TMPDIR=/tmp/w2-116-td PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116-tests/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-116/<file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(`mkdir -p /tmp/w2-116-td` first; put a multi-line command in a script under your scratch and run it with `bash`.) A
resource gate's refusal is a wait, not a refusal (DEC-1146). Never open the evaluation sets' root or any hidden or
memory-verdict folder.

## Commit
```
git -C /home/usain/gov-os-worktrees/W2-116-tests commit -m "<subject>" --trailer "Task: DAEO-f58b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983, DEC-982, DEC-966, DEC-963, DEC-1087" -- tests/acceptance/W2-116/
```

## Rules
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it (DEC-1142 (9)).
- A gap in the interface below: do not guess it into a case; name it in `unresolved` and test what is stated.
- Keep a checkpoint in your scratch (STATE / HEAD / NEXT).

## Return (your last message)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES, ESCALATION) /
work_completed / files_changed / evidence (the red run: each case and its failure line, the JUnit or `-q` tail) /
tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` with
hash12 and subject.

