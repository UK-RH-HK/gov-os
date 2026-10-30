---
id: DAEO-e8f0
status: in_progress
deps: []
links: []
created: 2026-10-24T14:15:22Z
type: task
priority: 1
assignee: engineer
external-ref: W2-71
tags: [wave-2, secrets, check, full]
wbs_id: W2-71
title: 'The secrets check passes a real commit hash of this repository for row W2-L423''s rule only'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-rmbe]
allowed_paths:
- src/gov/secrets/**
- tests/unit/secrets_check/**
kpis:
  success:
  - 'A match of row W2-L423''s rule (the gitleaks default rule that takes a bare 40-hex string for a token beside its keyword) that is exactly 40 hex digits naming a commit object of this repository (git cat-file -e <sha>^{commit} in the project being scanned) is no finding: a full commit hash beside the rule''s keyword, in a file under .gov-runtime/ and in a stored value, leaves the secrets-indexing check and the pre-index filter clean [DEC-911 item 4]'
  - 'A real token of that vendor still fails: a token in each of the rule''s forms (its prefixed form, and a 40-hex token that names no commit object here), built at test time beside the keyword, is a finding of the check and of the pre-index filter [DEC-911 item 4]'
  - 'Only that rule and only that match: a finding of any other rule whose match is a commit hash of this repository stays a finding, and so do a match of 39 or 41 hex digits, a shortened hash, a commit of another repository, a tree or blob id, and a match whose verification cannot run (no git, not a repository, an error, a timeout): it fails closed [DEC-911 item 4, DEC-298]'
  - 'The matches are held in memory only: no report file is written, no match is printed, logged or recorded, and the clean-result record (DEC-853) never records a finding; every file the check scans today is still scanned with every rule set, with no allowlist added [DEC-853, DEC-290, DEC-298, DEC-347]'
  - 'The rule''s id and keywords are written only in parts in every tracked file this ticket writes (code, tests, records), so no index store holds one whole and row W2-L423''s early warning stays quiet; under .gov-runtime/, commit hashes in its records and returns are 12 digits [DEC-911 items 1 and 2]'
  failure:
  - A real token of any rule let through.
  - A match let through that names no commit object of this repository.
  - A match or a finding printed, logged or written to a file.
  - A file the check scanned before no longer scanned, or a scan that cannot finish passing as clean.
profile: FULL
sources:
- DEC-911
- DEC-298
- DEC-347
- DEC-853
- DEC-290
- DEC-909
est_loc: 50
acceptance_tests:
  path: tests/acceptance/W2-71/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows:
- W2-L423
---
# W2-71 The secrets check passes a real commit hash of this repository for row W2-L423's rule only

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-71), from P-W2-L423-A (a) (owner, DEC-911 item 4).

- **Why:** a full commit hash beside the rule's keyword in a log under `.gov-runtime/` turns the hard-block check red (W2-69's run 2 met it on three of its own review logs). The check strips every allowlist (DEC-298, DEC-347), so the exemption is written in the check itself.
- **Place:** starts in a free slot after the first re-pin, when no ticket in flight holds `src/gov/secrets/`; merges before the second re-pin, which carries it with W2-68.
- **The test designer's files** (MR-3: named here, not in the engineer's paths): `tests/acceptance/W2-71/**`. The vendor token is built at test time from parts, never written whole in a tracked file (only two tracked credential fixtures stand, W2-M398).
- **Until it lands:** DEC-911 items 1 to 3 hold (12-digit hashes and no keyword under `.gov-runtime/`, the paths-only early warning, gate (b) failing closed).
