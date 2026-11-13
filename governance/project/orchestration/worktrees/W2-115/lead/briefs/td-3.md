# Brief: independent test designer, DAEO-emq1 (W2-115), FULL, class C3 — two decided revisions (build run 3, td-3)

Budget: projection 3 USD. Keep your context short: read only what these two revisions need.

You are a fresh independent test designer (MR-3) for ticket DAEO-emq1 (W2-115), in
`/home/usain/gov-os-worktrees/W2-115-tests` on `w2/W2-115-tests` (DEC-963). You revise two existing acceptance suites
of other tickets that the smart close's built change (S8's nightly key, the template's `close.yaml`) now turns red.
Both revisions are decided (the ticket, section "PK-1 and PK-2 (2026-11-12 ~09:55)"); you do not re-open them.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-emq1`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-emq1','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it (its test-designer
paragraph applies).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-emq1`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-115-tests`, `w2/W2-115-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md` (its `allowed_paths:` names the six
  files below, for this revision only; its "PK-1 and PK-2" section). The register (`docs/DECISION_REGISTER.md`,
  1.6 MB): grep only by id (`### DEC-1142`, `### DEC-866`, `### DEC-903`, `### DEC-966`). No context packet: `gov
  context` refuses this ticket (CONTEXT_OVER_CEILING); this brief and the ticket are your inputs.
- **Writes:** only these six files:
  `tests/acceptance/W1-39/test_w1_39_copy.py`, `tests/acceptance/W1-39/README.md`,
  `tests/acceptance/W2-77/w2_77_support.py`, `tests/acceptance/W2-77/test_w2_77_unchanged.py`,
  `tests/acceptance/W2-77/test_w2_77_failed_removal.py`, `tests/acceptance/W2-77/README.md`.
  Scripts, if any, as files under your sandbox `TMPDIR`. Do not read `src/gov/close/` beyond what a failure message
  already tells you (independence, MR-3): the behaviour is stated below.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). No `$(…)` or variable as a write target, no here-document, no `bash -c`.
  Foreground only. No reset, checkout, clean, amend, rebase, push, merge or install.
- **Every pytest run goes through the heavy-job slot**, with a TMPDIR outside the repository and outside
  `~/gov-os-runs` (your sandbox TMPDIR is fine), `PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`:

      env HOME=/home/usain/gov-os-worktrees/W2-115-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-115-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

  If the slot script is refused by the sandbox, say so and run the same pytest line without it, once.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file
  (DEC-1142 (9)). On an authentication error return `AUTH_REQUIRED`.

## Revision 1 (PK-1 (a)+(c), the owner, DEC-1142 (3)): W1-39's overlay case

`tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay` now fails on the built code:

    AssertionError: `copier copy` created more in the overlay than the path map and the test map DEC-903 names:
    ['governance/project/close.yaml', 'governance/project/path-map.yaml', 'governance/project/test-map.yaml']

The template now carries `template/governance/project/close.yaml` (holding `close: scoped`, W2-115's S1: a new
project's config chooses the scoped close). DEC-1142 (3) changes DEC-903's overlay list to name `close.yaml`. Revise
the case so the overlay is exactly the path map, the test map **and** `governance/project/close.yaml`, nothing else;
keep it as strict as today (an exact list, each file named in its own message). If you can do so without widening,
also check the created `close.yaml` reads `close: scoped`. Put a line in the test's docstring:
`Rewrite-Reason: DEC-1142 (3) (DEC-903's overlay list names close.yaml), DEC-866.` and update the README's line for
this case to say the same. Touch no other W1-39 case.

## Revision 2 (PK-2 (a), the CTO, delegated): W2-77's four key-set cases

The nightly's record now carries one more key, `secrets_full_scan` (W2-115's S8: the nightly rebuilds its stores with
the full secrets scan and its record says so, DEC-966 item 4). Four W2-77 cases fail with "Extra items in the left
set: 'secrets_full_scan'":
- `test_w2_77_failed_removal.py::test_a_failed_clean_up_does_not_change_the_verdict` (line ~120)
- `test_w2_77_unchanged.py::test_a_green_night_s_envelope_exit_code_and_verdict_are_as_today` (line ~37)
- `test_w2_77_unchanged.py::test_a_green_night_s_record_has_exactly_today_s_keys_and_no_cleanup_key` (line ~49)
- `test_w2_77_unchanged.py::test_a_red_night_s_envelope_exit_code_and_verdict_are_as_today` (lines ~69 and ~73)

Revise the key set (`RECORD_KEYS` in `w2_77_support.py`, and its comment "the night's record as it is today") so it
names `secrets_full_scan` as one of the record's keys; the sets stay exact (no subset or "at least" checks). Keep W2-77's
own point intact: `cleanup` appears only on a failed removal. Put `Rewrite-Reason: DEC-966 item 4 (W2-115 S8: the
nightly's record names the full secrets scan); PK-2 (a).` in the support file's comment and in each of the four cases'
docstrings, and update the README's lines for these cases. Touch no other W2-77 case.

## Check and commit

1. Run both suites' files on this branch (it holds the built smart close, so they should now pass):
   `tests/acceptance/W1-39/test_w1_39_copy.py tests/acceptance/W2-77` with the slot line above. Quote the last line
   and any failure's one-line reason. A failure outside the six cases: say so; do not fix it.
2. Commit only your paths:

       git commit -m "W1-39, W2-77 acceptance: the overlay names close.yaml (DEC-1142 (3)); the nightly record's key set names secrets_full_scan (PK-2 (a)) (td-3)" --trailer "Task: DAEO-emq1" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-966, DEC-983, DEC-953" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W1-39 tests/acceptance/W2-77

   (DEC-1142 and DEC-866 are not in the ticket's `sources:`: they go in the Rewrite-Reason lines and in your
   `discoveries`, never in `Implements:`, DEC-1073.) Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `ps` check (EMG-d4b-launched.md), the run's last line, the commit hash with its
trailers, `du -sh` of your TMPDIR. In `tests`: the cases revised per file and the run's counts. Also the refusals met.
