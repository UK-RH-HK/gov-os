# W2-56 — the independent review, round 1 (DAEO-wnnz)

You are a fresh, read-only independent reviewer. Review **W2-56** (`.tickets/DAEO-wnnz.md`: read it in full, with
"The first half's points settled", "The guard-alone outcome (DEC-1112 (1))" and "The second half's points settled").
The owner's decision is DEC-1112 (1) in `docs/DECISION_REGISTER.md` (with DEC-1098 (4), DEC-1099 (1), DEC-1035): W2-56
builds on the path-map guard alone, with today's launcher sandbox for workers unchanged (not generated from the path
map). The acceptance cases' README (`tests/acceptance/W2-56/README.md`) states the interface they assume.

## What to review
- **The branch:** `w2/W2-56` in `/home/usain/gov-os-worktrees/W2-56` at `befa57695 (the engineer's round 2 at 466e279fb, integrate merged in)`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-56`): `src/gov/launch/` (`launcher.py`, `sandbox.py`, `environ.py`),
  `src/gov/codeintel/__init__.py`, `tests/conftest.py`, `template/governance/kernel/settings.json`, the unit tests,
  `docs/changes/W2-56-CIT-E.md`; and the designer's cases `tests/acceptance/W2-56/` with W1-27's revised W2-67 cases.
- **The runs (the CTO's, outside the sandbox):** on `466e279fb`: `gov accept W2-56` with `GOV_W2_56_REAL=1` (the four real sandboxed
  sessions included) 260 passed, 0 failed, 0 skipped; on an earlier run the S7 real case was red once on the CLI's own
  `.git/config.lock` placeholder (P-S7, settled: S7 changed, the rest a Wave 3 row); `gov accept W1-20` 35/35; W1-27's
  revised W2-67 cases and `tests/unit/resources/test_w2_20_round3.py` 41/41 (`--optin=lifted,breadth`);
  `tests/unit/retrieval/test_w2_112_shared_reranker.py` green; `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`
  red on integrate too (not W2-56's). The CTO's D-13 probe: on Linux a one-path `allowUnixSockets` leaves a sandboxed
  connect refused (EPERM); `allowAllUnixSockets` connects.
- **The engineer's return:** round 1 `/home/usain/gov-os-worktrees/W2-56/.gov-runtime/scratch/lead/log/W2-56-engineer.json`
  and round 2 `…/W2-56-engineer-r2.json` (each file's last JSON object, its `result`); the designer's records
  `/home/usain/gov-os-worktrees/W2-56-tests/.gov-runtime/scratch/lead/log/W2-56-designer-r2.json` to `-r4.json`.

## Check
- Each KPI line S1 to S15 and F1 to F6 against the code, not only against the tests: do the cases prove the line, or
  could a launcher pass them and still miss it? Profile FULL: a mistake here fails open in ordinary work (DEC-801).
- **Fails open:** a worker launched with a wider sandbox than today's (any write entry beyond the temp folder, the run
  folder and S11's one log file; any socket or port beyond S8's one path; `allowAllUnixSockets`); a refusal the
  launcher made before no longer refusing (F2); a parent CLAUDE*, GOV* or PYTHONPATH value reaching the session; a link
  followed onto the write list; a temp folder or daemon folder left behind; a signal that leaves the session's group
  running.
- **The changed lines:** S2, S3 and F1 (write scope the guard's, the script-write gap named in the CIT-E), S11 and F5
  (W2-145's form). Does anything in the branch assume set-up B, or widen the sandbox by more than the ticket allows?
- **Known, decided, not findings against the engineer:** D-13 (on Linux the one-path socket allow is inert; S8's reach
  and S10 are the owner's DEC-105 choice); D-14 waits with it; S10 is the CTO's measurement. Name anything the engineer
  reported as a conflict (S13 against S2's deny rules) and judge whether its handling fails open.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- **You write nothing** in any tree; run nothing that writes outside your own temp folder (tests read-only with
  `-p no:cacheprovider`, only `tests/acceptance/W2-56` or a single file of it, through the heavy slot that
  `EMG-common.md` names, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56/src`). Single simple Bash commands (DEC-1080).
  Never the full suite. The real cases need a session outside your sandbox: read the CTO's results instead.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, network or installs.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your verdict per KPI line, every finding with its lines and `scope: in|out`, and at the end the
  fenced `verdict` block in DEC-1010's form:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`
  with one entry per KPI line (S1-S15, F1-F6).
