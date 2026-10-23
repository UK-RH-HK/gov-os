---
id: DAEO-rmbe
status: open
deps: []
links: []
created: 2026-10-22T15:54:42Z
type: task
priority: 1
assignee: engineer
external-ref: W2-69
tags: [wave-2, secrets, check, full]
wbs_id: W2-69
title: 'The secrets check reads what the stores hold: no chance red from where a scan begins'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-kl5e]
allowed_paths:
- src/gov/secrets/**
- src/gov/rebuild/command.py
- tests/unit/secrets/**
- tests/unit/secrets_check/**
- tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py
- tests/acceptance/W2-50/w2_50_scan_support.py
- tests/acceptance/W2-50/test_w2_50_never_indexed.py
- tests/acceptance/W2-50/test_w2_50_last_review.py
- tests/unit/rebuild/test_compaction*
- docs/research/W2-69-secrets-scan.md
kpis:
  success:
  - 'A real token is found at every offset and in every form the derived stores hold it: in a stored value, in a SQLite row read as text, in UTF-16 text, and across every boundary where the check splits or reads its input, at a word boundary as the rule defines it [DEC-897 item 1, W2-M404]'
  - 'An embedded fragment of a longer identifier is not flagged: a token-shaped string inside a word, placed at every offset relative to wherever the check or gitleaks begins a read, is not a finding, for every rule with a leading word boundary [DEC-897 item 1, W2-M404]'
  - 'Deleted text does not survive a rebuild: after a full rebuild, text deleted from a SQLite store is in neither its rows nor its free pages, so a secret removed from the sources leaves no residue the check would find, or miss [DEC-897 item 1]'
  - 'The design question is answered with evidence in docs/research/W2-69-secrets-scan.md before the code: scan the indexed text (rows as text) with each store compacted (VACUUM) after each rebuild and a boundary-aware raw scan kept only as a backstop, against boundary-aware raw reads alone; the choice is the one whose tests above pass, and row W2-M395 (the byte join) is settled by it or left to W2-45 with a reason [DEC-897 item 1]'
  - 'Every file under .gov-runtime/ the check scans today is still scanned, with every rule set; a scan that cannot finish still fails closed; the reuse of a clean result keyed on the store''s hash (DEC-853) stays, and a finding is never reused [DEC-853, DEC-290]'
  - 'The earlier tests this change affects are named for the test designer and revised only where scanning the rows as text or compacting the stores changes what they expect, each with Rewrite-Reason: DEC-897: W2-50''s secrets-scan scale cases (test_w2_50_secrets_scan_scale.py, w2_50_scan_support.py) and the secrets cases of test_w2_50_never_indexed.py and test_w2_50_last_review.py [DEC-899, P-IS-5 (a), P-I1-7]'
  - 'tests/unit/secrets/ is renamed tests/unit/secrets_check/, so it no longer shadows the standard library''s secrets module under plugins that import it first; collection is clean with pytest-rerunfailures and pytest-randomly loaded [W2-L373, I2 F8, DEC-899]'
  failure:
  - A real token at a word boundary that the check misses, at any offset or in any stored form.
  - A word-internal fragment flagged at a read edge (the chance red of W2-62's queue, 2026-10-22).
  - Deleted text left in a store's free pages after a rebuild.
  - A store or file the check scanned before and no longer scans; a scan that cannot finish passing as clean.
profile: FULL
sources:
- DEC-897
- DEC-853
- DEC-290
- DEC-899
- DEC-868
- DEC-896
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-69/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- P-W2-62-G1
list_rows:
- W2-M404
- W2-L373
---
# W2-69 The secrets check reads what the stores hold: no chance red from where a scan begins

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-69), from DEC-897 (owner, 2026-10-22, P-W2-62-G1 (a)).

- **Why:**
  - The secrets-indexing check is a hard-block check. It feeds a store's content to `gitleaks stdin` as one input.
  - When one of gitleaks' reads begins inside a word, a rule's leading word boundary matches there, so a fragment of a longer identifier is taken for a token.
  - Where the reads begin moves with every rebuild, so any rebuild can turn `gov check` and a close RED by chance. W2-62's queue of 2026-10-22 stopped this way: a `gov-token-lower` hit, 62 bytes inside an 84-character identifier.
  - It fails closed, but it stops closes at random. Row W2-M404.
- **The design question (DEC-897):** should the check scan the indexed text (each SQLite store's rows, as text) instead of the database's raw bytes? That option comes with:
  - each store compacted (`VACUUM`) after each rebuild, so no deleted text survives in free pages;
  - a boundary-aware raw scan kept only as a backstop.
  The KPIs' tests decide. The answer, with its evidence, goes in `docs/research/W2-69-secrets-scan.md` before the code.
- **Place:**
  - Rides in the first re-pin, with W2-58, W2-59, W2-65, W2-66 and W2-07 (DEC-896, DEC-897).
  - Until then, the pin's check decides closes, under DEC-897 (b)'s one proven re-run per close.
  - Starts in a free slot after W2-50's run 9 returns: W2-50 shares `src/gov/secrets/__init__.py`, and two tickets with overlapping paths are never in flight together.
  - W2-43 (`src/gov/secrets/**`) and W2-06 (`src/gov/rebuild/**`) are open and start after it.
- **Allowed paths:**
  - `src/gov/secrets/**`;
  - `src/gov/rebuild/command.py`: the compaction step after each store's build only;
  - `tests/unit/secrets/**`, `tests/unit/rebuild/test_compaction*`;
  - `docs/research/W2-69-secrets-scan.md`.
- **KPIs, success:**
  - A real token is found at every offset and in every form the stores hold it.
  - An embedded fragment of a longer identifier is not flagged.
  - Deleted text does not survive a rebuild.
  - The design question is answered with evidence.
  - Every file scanned today is still scanned, with every rule set. A scan that cannot finish fails closed. DEC-853's clean-result reuse stays.
- **KPIs, failure:**
  - a missed real token;
  - a word-internal fragment flagged;
  - deleted text left in free pages;
  - a file no longer scanned;
  - an unfinished scan passing as clean.
