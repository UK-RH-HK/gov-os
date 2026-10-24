# W2-67 batch 7: the plants (DAEO-9nys, run 3)

Worktree `w2/W2-67`; cases as committed in `8b4fcf067410` (the plant runs ran on that content before the commit).
Every run: `PYTHONPATH=<this folder>/<fault>:/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest -p no:cacheprovider
-o tmp_path_retention_policy=failed [-n k] --junitxml=<fault>/junit.xml <node ids of tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py>`.

Each `<fault>/usercustomize.py` loads `lib/td7_plants.py`, which hooks the import of `gov.secrets` and replaces one
behaviour after the module and the case's declared figures are in place; `<fault>/ran.jsonl` logs each install and
each time the planted behaviour acted.

| Fault, in words | Planted as | Node ids | Result | Shown to have run (`ran.jsonl`) |
|---|---|---|---|---|
| fixed-limit: the limit no longer grows with the content's size | `gov.secrets.subprocess.run` given `timeout=_TIMEOUT_S` | clean, canary, pool (`-n 3`) | 3 failed in 7.96 s (`TimeoutExpired` after 4 s on the large store) | 3 installs; large store's limit 31.233 s -> 4 s on 27,232,602 bytes |
| first-half-pieces: a large store's later pieces are never scanned | `gov.secrets._pieces` keeps the first half | clean, pool (`-n 2`) | 2 failed in 44.34 s (middle word seen under 0 of 2 rule sets) | 2 installs; 567 of 1,135 pieces given, 16,777,216 bytes |
| halves-at-middle: a large text cut at its middle byte without overlap | `gov.secrets._scan` given halves | canary | 1 failed in 28.31 s (the check is green) | 1 install; cut at 8,388,608 |
| hang-green: a run past its limit taken as clean | `TimeoutExpired` returned as exit code 0 | hang | 1 failed in 9.97 s (the check is green) | 2 acts, timeout 4.012 s |
| hang-records-clean: the check fails on a hang but records the stores clean first | `stores_with_secrets` records every digest, then raises | hang | 1 failed (after-run not scanned in full) | 1 act: 3 stores recorded after `TimeoutExpired` |

A first fixed-limit run was void (`RecursionError`: the declaration's finder and the plant's asked each other without
end); both finders now step aside while they ask the others; the run is not counted and its `junit.xml` was
overwritten.

Green on the head: `../head/large-after.xml` (the 4 revised forms with `signal` and `exit-code`: 6 passed in 47.80 s)
and `../head/whole-file-after.xml` (23 passed in 71.44 s). Before: `../head/large-before.xml` (4 passed in 276.09 s)
and `../head/rest-before.xml` (19 passed in 15.37 s).
