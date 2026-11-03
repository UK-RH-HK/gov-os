# Emergency task: gitleaks scanning switched off on this repository by configuration (the product's switch) (engineer)

Read `briefs/EMG-common.md` beside this file first; its rules hold (ignore its lines that say to gitleaks a fixture:
DEC-1045 lifted that here).

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/EMG-noscan`, branch `emg/noscan` (from `w2/integrate`).
`Task: DAEO-sdxk`, `Implements: DEC-1045,DEC-953`. TMPDIR `/tmp/gov-os-emg-noscan`.

## The owner's decision (DEC-1045, read it in `docs/DECISION_REGISTER.md`)
All gitleaks scanning is lifted on this repository (private, never shared): the memory-indexing scan in rebuilds, the
scans in closes, the nightly's. **The feature stays built in the Gov OS and is switched off on this repository by
configuration, as DEC-953 did for the other lifted gates: every other repository keeps it ON by default, and the
switch is named wherever it acts, never silent.**

## The switch (fixed by the CTO; another engineer's tools read the same file)
A new known file of the project's configuration, `governance/project/secrets.yaml`, read by `gov.config.loader`
(add it to `KNOWN_FILES` with a schema: one key `scan`, values `on` or `off`; anything else `CONFIG_INVALID`). **Absent
file or absent key = on.** This repository gets the file with `scan: off` and a comment naming DEC-1045.

## Where it acts (find every product call site of the gitleaks binary: `grep -rn gitleaks src/gov`)
- `gov.secrets.indexable`: with scan off, the governance-namespace filter still applies; no content is given to
  gitleaks; the rebuild's report (and `scan_counts`) names "secrets scan: off by configuration (DEC-1045)".
- `path_holds_secret`: off -> False, no scan. `stores_with_secrets`: off -> no scan; the secrets-indexing family check
  in `gov check` reports its own state for "off by configuration" (not RED, not a silent GREEN: name it as the other
  lifted checks are named; look at how `gov check` reports a check that does not apply), and `gov doctor` says so.
- `gov ci staged-secrets`: off -> exit 0 with the line "secrets scan: off by configuration (DEC-1045)".
- `retrieval/retrieve_check.py`, `retrieval/lexical.py`, `doctor`: whatever they call follows the switch.
- **Never fail open elsewhere:** on (the default), every behaviour is byte-for-byte today's; a configuration that
  cannot be read is `CONFIG_INVALID` (fails closed), not "off".

## Tests
Your unit tests in `tests/unit/secrets_check/test_dec1045_switch.py` (and `tests/unit/config/` if the loader has its
tests there): absent file -> on (gitleaks called); `scan: off` -> not called, named in each output; `scan: maybe` ->
CONFIG_INVALID; `gov check` on a temp repo with off names it. Then the scoped set through the gate, every red named
against the base: an acceptance test that reads THIS repository's real check output and needs the secrets check GREEN
would go red: name it (a test designer revises it; never you). Never run the suites whose subject is gitleaks more
than once (they are nightly-only now).

Return DONE with the head, where the switch is read and named, the scoped results, and any acceptance case needing a
designer. One review follows; it goes live with re-pin window 2. Estimate: about 100 lines, 1.5 hours.
