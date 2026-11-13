# The sweep for the two ejection defects (DEC-1155 (2); the helper, 2026-11-12 ~21:50) — for the 09:00 package

**Defect A (a path case judging any branch), live:**
| File:line | Why it fails in the queue's merged clone | Fix | Owner |
|---|---|---|---|
| tests/acceptance/W2-171/test_w2_171_f5_paths.py:27 | diffs merge-base(HEAD, w2/integrate)..HEAD on any branch | skip unless HEAD is refs/heads/w2/W2-171, naming why | W2-171 closed; the fix is in W2-172's paths (DEC-1155 (1)), running now |
| tests/acceptance/W2-157/test_w2_157_nothing_else.py:97 | the same | the same, for W2-157 | W2-157 closed; the fix is written on w2/W2-181 (open, parked, not merged) |
| tests/acceptance/W2-159/test_f4_scope.py:37 | the same | the same, for W2-159 | W2-159 closed; no ticket covers it |
| tests/acceptance/W2-178/test_w2_178_unchanged.py:133 | the same | the same, for W2-178 | W2-178 closed; no ticket covers it |
**Defect A, failing only for some lands:** tests/acceptance/W2-55/test_w2_55_backfill.py:145 (fails when a land changes docs/DECISION_REGISTER.md); tests/acceptance/W2-71/test_w2_71_nothing_printed_or_written.py:239 (fails when a land changes .gitleaks.toml); both owners closed.
**Defect B (a hygiene check tripped by the clone's folder):** tests/acceptance/W2-172/conftest.py:49 (checks W.SRC and sys.executable for runs/; fix: check only the planted paths; W2-172 running now); tests/unit/launch/test_runs.py:150 (searches a temp path's text for gov-os-runs: fails when TMPDIR is under ~/gov-os-runs; fix: compare with Path.is_relative_to; owners W2-153, W2-60a, W2-56, in progress). Latent: W2-170's test_w2_170_s5_counts_only.py:47, :120-122 and test_w2_170_s1_s3_preflighted_set.py:327 pass today but would fail with TMPDIR under ~/gov-os-runs.
**Safe (with reasons):** W2-170 F5 and W2-173 F3/F4 skip off their own branch; W2-170 S4 fixed by W2-179; W2-66, W2-71 keywords, W2-91, W2-145, W2-69 look at the ticket's own commits; W2-153, W2-54, W2-49, W2-105, W2-58, W1-11, W1-28, W1-42, W1-50, W2-72, W2-149, W2-97 use fixed commits or planted repositories; W2-50's conftest checks only the real runs folder unchanged; W2-61h skips without GOV_EVAL_SETS_ROOT; W2-121 S6, W2-159 S5 and the dispatch unit check scan source text.
**The queue's environment:** /usr/bin/python3, TMPDIR inherited (empty: /tmp), no --basetemp; so the only ~/gov-os-runs paths a test sees are the repository's own.
**Options for the owner:** (a) unpark W2-181 and land it (W2-157's F4); (b) one gap ticket in W2-181's form for W2-159 F4 and W2-178 F3 (and W2-55, W2-71's conditional cases), the owner's decision (DEC-974); (c) test_runs.py:150 fixed under W2-153 or W2-56 (a widening or their own scope); (d) optionally a fixed queue TMPDIR outside ~/gov-os-runs (a control-path ACT).
