# Emergency task: gitleaks scanning switched off in the CTO's tools; the real-gitleaks tests in the nightly only (engineer)

Read `briefs/EMG-common.md` beside this file first; its rules hold (ignore its lines that say to gitleaks a fixture:
DEC-1045 lifted that here).

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/EMG-noscan-tools`, branch `emg/noscan-tools` (from
`w2/integrate`), for the committed scripts; and the CTO's scratch tools in
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/` as candidates (`<name>.candidate.py`,
backups `<name>.pre-dec1045`; the CTO switches them on). `Task: DAEO-sdxk`, `Implements: DEC-1045`. TMPDIR
`/tmp/gov-os-emg-noscan-tools`. Lighter lane (DEC-979 item 2): your own tests before use.

## The owner's decision (DEC-1045, read it in `docs/DECISION_REGISTER.md`)
All gitleaks scanning is lifted on this repository: the landing's pre-check, the scans in the closes, the nightly's,
and the record branch's sync. The tests that run the real gitleaks run only in the nightly full suite; between
tickets only the scoped tests and the acceptance tests (DEC-968).

## The switch (shared with the product)
`governance/project/secrets.yaml`, key `scan: on|off` (absent file or key = on; anything else: stop with an error,
fail closed). Another engineer adds it to the product; this repository's copy says `off`. Your tools read the same
file (a few lines of YAML reading; no product import needed), so one setting governs both.

## Where it acts
1. `tools/land.py` (about line 122: `gitleaks detect` on each ticket's change before it is queued): off -> skipped,
   the landing's record line says "gitleaks: off by configuration (DEC-1045)".
2. `tools/close_build.py` (about line 515): the same, and its close record's line.
3. `governance/project/orchestration/sync_context.py` (about lines 116-135: `gitleaks dir` over the record, and over
   the staged set): off -> skipped, named on stderr. Its tests, if any, in that folder.
4. `tools/select_tests.py`: the suites whose subject is the real gitleaks binary are left out of every scoped
   selection (leads, landings, closes) and named in its JSON (`left_out_nightly_only`); the nightly runs everything,
   unchanged. Find them by a static scan of `tests/` for tests that run the gitleaks binary or `gov ci staged-secrets`
   or the secrets filter on real content (for example `tests/acceptance/W2-69/`, `tests/acceptance/W2-107/`,
   `tests/unit/secrets_check/`, W1-15's secret-filter cases); write the list into one file the tool reads
   (`tools/nightly_only.txt`, one path or node id per line, each with a comment saying why), so it is one place to
   change. Never drop a suite that does not run gitleaks.
5. `governance/project/orchestration/nightly/`: confirm nothing in it runs a gitleaks scan of its own (the suites
   that test gitleaks stay in the nightly); if one does, switch it off the same way, with `test_nightly.sh` passing.
For each: a test (switch on: today's behaviour; off: no gitleaks call, named; bad value: refuses). Return DONE with
the head, each candidate's path, the nightly-only list with its reasons, and the tests' results. Estimate: 1.5 hours.
