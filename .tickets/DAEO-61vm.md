---
id: DAEO-61vm
status: open
deps: []
links: [DAEO-52ku, DAEO-2bdu, DAEO-k1e2, DAEO-p8tv, DAEO-qz4p]
created: 2026-11-11T01:20:37Z
type: task
priority: 2
assignee: engineer
external-ref: W2-170
tags: [wave-2, implementation, memory, audit, full, after-the-lift]
wbs_id: W2-170
title: 'The memory audit''s set record: the checks before any search, the drop and void rule, the declaration and the use-once marker, counts only (DEC-1101 (1), DEC-1125 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/memaudit/**
- tests/unit/memaudit/**
- governance/project/test-map.yaml
- docs/changes/W2-170-evidence.md
kpis:
  success:
  - 'S1 The pre-flight checks a delivered set before any search and prints ids, counts and the codes below only. It refuses on each of: fewer than 36 files; a file not in the writer brief''s form (`id`, `question`, `gold_answer`, `sources`, `commit`, `category`, `drawn`); a `commit` other than the audit commit; a category count other than the 40-question quotas of the rubric (R5 item 6); a governing domain under 4 questions or a subsystem over 10, scaled to the kept count; a `drawn: changed` or `drawn: sample` question whose first source is not in `selection.json`''s list of that name; a source path missing at the audit commit, or a `heading` not found and `lines` outside the file; a source in an evaluation or evaluation-source namespace (R8); a gold-source set equal to a pool question''s (R9); a nonexistent-id question whose id exists at the commit. Verify: a planted set in a planted repository and sets root under TMPDIR with ten planted defects, one per check: each refused with its own code; the clean planted set ends `PRE-FLIGHT: every check as expected`; no real `~/gov-os-eval` is opened [DEC-1101 (1), DEC-1069 (5), DEC-1125 (2)]'
  - 'S2 The drop and void rule: after the checker''s second pass, every question whose verdict in the notes is not `accept` is moved to `dropped/` in the set''s folder (never deleted), the kept count and every S1 scale are recomputed from the kept questions, and a kept count under 36 or a domain under 4 makes the audit VOID: nothing is measured, no `USED` marker is written, and the counts say `void` with the cause code. Verify: planted notes with 3 drops (audit goes on, kept 37, scales recomputed), with 5 drops (VOID, no `USED`, no `DECLARATION.json`), and with a drop that leaves a domain at 3 (VOID) [DEC-1101 (1), DEC-1125 (2)]'
  - 'S3 Before any search the runner writes `runs/<audit>/DECLARATION.json` and a `USED` marker, in that order. The declaration holds: the audit commit; the store''s commit and its sha256; the gov pin; the `retrieval.yaml` digest; the standard''s four settings by name (the shared reranker, the pool on, the 6,000-token bundle, search again once); the set''s digest (`LC_ALL=C sha256sum *.yaml | sha256sum` over the kept questions); n; the bar scaled to n (at least ceil(0.85 n) right end to end, at most floor(0.05 n) wrong claims; the target ceil(0.95 n)); and how it rounds. The runner refuses to start while `USED` exists, so a set is measured once. Verify: a planted run writes both files in that order (the file times and the ledger line); a second run on the same audit exits with the refusal and writes nothing; a planted `retrieval.yaml` with the pool off is named in the declaration and the run is not ok without a decision id [DEC-1098 (1), DEC-1097 (1)(d), DEC-1101 (1)]'
  - 'S4 The set is declared in the sets root''s own path map by the runner''s code, as one `evaluation_sets` entry of the shape `memory-verdict-2`''s has (its hidden glob, the six roles measured), so `gov.retrieval.measure` accepts it, and nowhere else: the repository''s `governance/project/path-map.yaml`, the guard and the hook are never written, and no ACT is needed for a new audit''s name. Verify: a planted sets root map gains exactly one entry for `memory-audit-<date>`; `git status` in the planted repository shows no change; the measure run on the planted set accepts it [DEC-1101 (2), DEC-820]'
  - 'S5 Only counts and ids leave the tool: standard output and `runs/<audit>/PREFLIGHT.json` hold ids, counts, codes and digests, never a question, a gold answer, a source path or a heading; a line naming the sets root''s folders is refused before it is printed; the command line names only `--sets-root <root>`, never a folder under it (the guard''s line rule). Verify: a planted question with a unique word: grep of every output file and the captured stdout and stderr finds it 0 times; the printed command line holds no `fixtures/` or `runs/` [DEC-1101 (2), DEC-1097 (2)]'
  - 'S6 The package is wired in: `governance/project/test-map.yaml` places `src/gov/memaudit/**` and its tests (so a change here runs these tests and not the full suite), and the module runs as `python3 -m gov.memaudit preflight|void|declare`. Verify: `gov close`''s scoped selection for a planted change under `src/gov/memaudit/` names `tests/unit/memaudit/`; each subcommand prints its usage with `--help` and exits 0 [DEC-896]'
  failure:
  - 'A question, gold answer, answer, source path or heading of a set in any output, log or error text. Verify: S5''s planted question with a unique word, gold answer, source path and heading: grep of every output file, the captured stdout and stderr and the logs finds each 0 times'
  - 'A set measured twice, or measured without `DECLARATION.json` and `USED` written first. Verify: S3''s planted runs: the file times and the ledger line show `DECLARATION.json` before `USED` before any search, and a second run on the same audit exits with the refusal and starts no search'
  - 'The repository''s path map, the guard, the hook, `.claude/` or the walls'' template written; the real sets root or run folders opened by a test. Verify: S4''s `git status` in the planted repository shows no change, and a run of the tests with the planted roots under TMPDIR leaves no open of the real sets root or run folders in the tests'' file-access log'
  - 'A dropped question deleted; a VOID audit that wrote `USED`. Verify: S2''s planted notes with 3 drops (the 3 files are found under `dropped/`) and with 5 drops (VOID: no `USED` and no `DECLARATION.json` in the audit''s run folder)'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: FULL
sources:
- DEC-1101
- DEC-1125
- DEC-1098
- DEC-1097
- DEC-1069
- DEC-820
- DEC-896
- DEC-1050
- DEC-1073
est_loc: 450
acceptance_tests:
  path: tests/acceptance/W2-170/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines and the writer, checker and auditor briefs (`packages/MEMORY-AUDIT-1/briefs/`), before the engineer: a planted sets root, a planted repository with commits, a planted pool; never the real ~/gov-os-eval or ~/gov-os-runs'
track: B
list_rows: []
needs: []
waits_on: []
---
# W2-170 The memory audit's set record

Owner decision DEC-1125 (2): the memory audit is a scheduled practice, weekly while development is active, an
independent writer drafting fresh questions, measured once, misses classified. This ticket is the **record and the
checks** around one audit's set: what is checked before any search, what is dropped, what is declared, and the
use-once marker. The measure is W2-171's; the cycle and the schedule are W2-172's; the launch script's follow-ups are
W2-173's. The whole is described in `governance/project/orchestration/packages/MEMORY-AUDIT-1.md`.

- **Home:** a new package `src/gov/memaudit/`, so that the tool ships with Gov OS and with every adopted repository
  (W2-88 reuses it: its `memory_sets.py` calls this core and carries no second copy). **After the lift; usage (A)
  keeps it waiting until the weekly reset (DEC-1122 (2)).**
- **Built on:** the independent sessions' launch script, merged (`2f98aecbc`, W2-149), the walls (`147706ae`), the
  install ACT (`baac0b2c2`), and the fresh 80's tools (`.gov-runtime/scratch/orchestrator/drafts/fresh80/`:
  `preflight.py`, `f80lib.py`), which are generalised here: they pin one set name and one run folder. The CTO copies the
  fresh-80 tools to `.gov-runtime/scratch/ref/fresh80/` in the worktree when the ticket starts.
- **Alternatives (one line each):** carry the checks in the launch script (rejected: it decides what a session sees,
  not whether a set is fit to measure); keep the fresh-80 scripts per set (rejected: pinned to one set, no tests for
  a second).
- **Not here:** the measure, the reader run, the pool's re-run (W2-171); the cycle, the schedule, the digest (W2-172);
  `--effort`, the stop word, the notes' form (W2-173).

[DEC-1101 (1)-(2); DEC-1125 (2)]
