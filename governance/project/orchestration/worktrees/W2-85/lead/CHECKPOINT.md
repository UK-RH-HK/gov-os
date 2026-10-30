# Lead checkpoint — DAEO-gdzh (W2-85), run 1 — FINAL (returned PACKAGES, partial)

## State
- Branch `w2/W2-85`, head `d113ff5ea045`; tree clean. Commits since claim `403d70b396ff`:
  - `1a682b6a45eb` test designer (Task DAEO-gdzh, Role independent-test-designer, Implements DEC-951 + DEC-889, Rewrite-Reason DEC-951 item 3, Co-Authored-By): serial-only.txt +4 (2 comments, 2 `nightly: real-model` entries), W2-54 README +15, green_here docstring +4/−1.
  - `d113ff5ea045` lead: gov checkpoint record CP-DAEO-gdzh-0002 (Task, Implements DEC-951, Role orchestrator).
- trailer_gate: "DAEO-gdzh: 4 commits, 4 judged, 0 lacking, 0 Implements item(s) not a decision or Contract id that resolves".
- Loop: no implementer (test-revision ticket); converged in one designer pass.

## Verification (logs under log/)
- gov.__file__ = /home/usain/gov-os-worktrees/W2-85/src/gov/__init__.py
- rebuild 1 (at 403d70b3) ok, rebuild 2 (at 1a682b6a) ok, digest eeb6bcf41b3e.
- selection_check.py OK: 65 entries, 17 nightly, 48 serial phase; both cases routed, neither in the phase.
- collect W2-54: plain 101/103 (2 desel), plugin 97/103 (6 desel): plugin removes exactly the two + the two already-listed W2-54 entries.
- w2-54 parallel with plugin: 97 passed, rc 0 (the two not in junit).
- readers (W2-57 serial_list + nightly_route, W1-30 r11): 55 passed.
- select_tests.py: scoped, why_full [], 32 targets; sel-parallel 3525 passed 1 skipped (govbridge); sel-serial 1 entry, 9 passed.
- collect over tests: 17271/17273 (2 deselected), no error.
- two cases alone: RED. time-limit 71 s at load 13 (content: 11 tickets' mandatory inputs superseded); green-here 332 s (context-reproducibility RED, same). Rerun of time-limit at head under load 87–48: past 630 s (load).
- gov check 1 (stale store): RED context-repro (superseded), product-traceability-trailers (DEC-891 superseded), index-freshness + recovery-rebuild (my order). gov check 2 (fresh head, load ~60): index-freshness + recovery-rebuild GREEN; context-repro + retrieval-regression timeout 600 s; trailers RED.

## Package P-W2-85-1 (partial)
Cause: commit 3f28e09c (DEC-953 item 7, 42 status lines SUPERSEDED). 11 tickets (W2-80, W2-68*, W2-79, W2-66*, W2-65*, W2-12, W2-19, W2-20, W2-07*, W2-69*, W2-78; * closed) cite them as sources -> context check errors. Recommend re-marking the lifted entries so the context check takes them as current (orchestrator; owner if it alters DEC-953 item 7's application); merge W2-85 meanwhile.

## Resume
Nothing to resume in this worktree unless the orchestrator asks for a re-run of the two cases alone after the fix (each alone, no plugin, quiet machine).

## Brief gaps
- context check red on content on w2/integrate since 3f28e09c, not in brief | this ticket's part | ~15 min
- select_tests.py --ignores the own suite (by design); brief does not say to run it separately | common brief / tool | ~10 min
- rebuild before first worker + test designer's commit after it -> index-freshness/recovery-rebuild red; no rule to rebuild again before verification | common brief | ~70 min (lock wait 22 + rebuild 30 + check)
- gov retrieve in a sandboxed worker tries ollama.com:443, times out at 120 s | tool | ~3 min (designer)
- "under the load gate" for the alone runs vs DEC-953 lifting the load wait | this ticket's part | ~2 min

## Guard read refusals: lead 0, designer 0 (one command form refused for approval in the designer: a pipeline writing /tmp into comm).
