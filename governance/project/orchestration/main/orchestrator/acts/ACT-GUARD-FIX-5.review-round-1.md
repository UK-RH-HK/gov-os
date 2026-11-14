# ACT-GUARD-FIX-5: the ACT review, round 1 (FAIL) — placed by the CTO

The reviewer (a fresh independent auditor, Opus high, read-only, not the author; the operator's reviewer brief sha256
e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a) could not write this record itself (its role writes
reviews only under docs/probes, docs/audit, docs/assessment or the CTO's reviews folder); the CTO places its return here,
2026-11-13 16:40. Kept as round 1; round 2's review is written to review.md. This file is not the G4 record.

Classification: 1 blocking finding, F1 (in scope, ordinary work yes, fails open). F2 fails check 1 (other: G1 refuses).
F3 to F6 are rows.

- F1 (check 6): ten commands refused before are allowed after: unquoted heredocs read by a shell with options or a stdin
  word whose body's command substitution writes into tests/acceptance/ (or rm -rf's it), or whose body goes to a file the
  command then runs (bash -o pipefail > s.sh <<EOF; tee s.sh <<EOF | bash -o pipefail, then bash s.sh). Before, these
  shells were read as data and the unquoted body's substitutions were judged; after, an unquoted shell body is one
  "unresolvable" finding that rule 1 drops under G-1 (DEC-1050 (12)). 16 calls in 48 hours used the spelling, none writing
  into the tests. Fix (a): judge an unquoted body's substitutions for every kind, as the data path does (optionally read an
  expansion-free unquoted body as the quoted one, closing W2-42a's 15th spelling); re-run the replay.
- F2 (check 1): before/ and after/ hold __pycache__/bash_writes.cpython-312.pyc, unlisted; G1 refuses. Remove both folders
  (the manifest's bytes do not change).
- F3 (check 4): check 3 tests only the _kind mapping, so "never less strict" cannot see F1.
- F4 (out of scope): the unquoted delimiter stays open as today under G-1; F1 (a)'s option would close it.
- F5: check 3's python3 -I writes bytecode beside the hook (use -B).
- F6: the package names a stale head and W2-42a ref (now a7b36bcfd, a4afc4166136); nothing relevant changed.
- Sound: the _kind mapping never turns shell into data (10.5 M argument lists); fails closed on an exception; 14 of 15
  F1 spellings refused after; replay 697 calls, 24 refused before and after, none loosened in the logs.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}],
 "manifest_sha256": "d2903e7dd2988bc427e1c4620efcf79aff4ac2b8354deb71145c4eadd7f72d44",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T16:06:23+00:00",
 "replay_refused": []}
```
