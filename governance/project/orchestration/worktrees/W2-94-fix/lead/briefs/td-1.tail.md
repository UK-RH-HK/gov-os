
## What the cases must show (one test or a parametrized table per line; each must be red against the unchanged script)
- **S6:** each wrong form of item 1 exits 17 with nothing built (no wall, no run folder, no seed line): `--fix` alone,
  `--reason` alone, `--kind checker`/`auditor` with both flags, round 1 and no `--round`, `--counts-only` with them, bad
  ids, an unknown code, a lower-case code. One good form passes the argument stage (it may be refused later for a
  planted reason; that is fine to show it is not 17).
- **S7 / F4:** a planted set of several questions (at least 5 in `hidden/`, some in `hidden/visible/`, a
  `hidden/dropped/` file, `DRAW.txt`, an `XCHECK-r1.md`, a `visible/` folder and `.release-visible.record`), each file
  holding a unique planted content marker; a `--dry` fix run on the planted root (`--seed` allowed with `--dry`): the
  wall's file list is exactly item 3's, `input/<id>.yaml` equals the set's bytes, `verdict.txt` is `<id> <code>\n`,
  `sample.json` parses to the latest delivered round-1 run's sample in order; no other marker is anywhere in the wall.
  The staging refusals: `hidden/<id>.yaml` absent, a link, a folder; no delivered round-1 run; its archive missing;
  its member missing or malformed: each 10 with nothing built.
- **S8 / F5:** with the stub session writing into `out/`: sha256 of every planted file under `<setdir>` before and
  after; a good fix run (exit 0) changes only `hidden/<id>.yaml` (now `out/<id>.yaml`'s bytes) and the archive holds
  the old bytes at `<run>/replaced-hidden/<id>.yaml`; each delivery refusal is 20 and leaves every set file
  byte-unchanged: an extra file in `out/`, a folder in `out/`, `out/<id>.yaml` absent, a link, not YAML, not a
  mapping, its `id` another id.
- **S9:** results refused 20 (no `action`, another word, `questions` 0 or 2, `by_kind` summing to 2 or 0, `by_area`
  summing to 2 or 0); a stopped result (with `out/conflicts.md`) is 21, nothing delivered; on delivery the counts'
  `fix` is `{"id": "q0N", "code": <code>, "action": <word>}` for each of `corrected` and `replaced`; a grep of stdout,
  stderr, `counts.json` and `launch.log` for every planted content marker finds 0.
- **S10 / F6:** the end-to-end run with the variant fixture committed byte for byte into the planted repository at its
  approved path (`governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md`) and approved in the planted
  APPROVED list: `--fix q02 --reason ANSWER_NOT_IN_SPANS`, the stub delivering a good `out/q02.yaml` and result: exit 0,
  the delivered file in place, `brief_sha256` in the counts equal to the approved sha256.
- **S11:** the script's docstring holds a usage line with `--fix` and `--reason` naming only `--sets-root <root>` as a
  path; and `git diff --name-only <base>...HEAD` of the branch under test names no path under
  `governance/project/indep-walls/`, `governance/project/indep-briefs/` or `governance/project/orchestration/tools/indep-schemas/`
  (take the base as `git merge-base HEAD w2/integrate` in the repository the test runs from; skip with a clear reason
  if that ref is absent).
- **S12:** a planted writer round-2 run without `--fix` still stages `input/set/` and `input/notes.md` and replaces the
  whole hidden folder as today, and its counts have no `fix` key (the existing unit suites are the main check; the lead
  runs them).

Do not assert the counts schema (`indep-counts.schema.json`) on a fix run's counts (item 6's known gap); assert keys
and values.

## Walls (hard; a breach fails the ticket)
- **Planted fixtures only.** Never open, list, grep or print anything under `/home/usain/gov-os-eval/`,
  `/home/usain/gov-os-runs/`, any folder named `hidden` outside your `tmp_path`, any `fixtures/evaluation/examin/visible`
  or `hidden` folder of any tree, EXAMIN's real repository or the owner's copy. You need none of them. Every word you
  plant is made up and carries the planted prefix `zqxw94`, as the existing W2-94 cases do.
- No GPU, model, network or installs; no real `claude` session (the stub only). One simple command per Bash call;
  longer things in a script file under your sandbox's `$TMPDIR` (`/tmp` is read-only in the sandbox). No merge inside
  the sandbox. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in different words if
  the first does not answer.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Order of work
1. Write the cases; run them against the unchanged script; every case must be red (or, for an S12 guard case, green),
   and record which and why.
2. Commit (only your new files and the README rows), every trailer in ONE final paragraph:
   `git commit -m "W2-94 (DAEO-g87r): the fix flow's acceptance cases (S6-S12, F4-F6)" --trailer "Task: DAEO-g87r" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1180, DEC-1178, DEC-820" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-94`
3. Name, for S7, S8 and S9, one planted break of a correct fix flow that a case would catch (by reading; no script
   copy needed).

Pytest, every run (if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a resource
gate's refusal is a wait, not a refusal):
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94/test_w2_94_fix_flow.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line`
Use your sandbox's own `$TMPDIR` for every temporary file.

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (the red
run's counts and the commit hash), tests, discoveries (any point where the interface is unclear or the KPI and the
interface disagree), risks, lessons, proposed_decisions, unresolved, recommended_next_action. Never quote a planted
hidden question or answer beyond its made-up marker.
