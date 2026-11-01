# Lead checkpoint, DAEO-zpdj (W2-105), run 1, at return (04:55, 2026-10-31)

## State
- Branch w2/W2-105, head 381e1187 (clean). Base 1f0bf2836dc2.
- Commits: 94aab25d56a8 (test designer, W2-105 tests), 67af427b08c0 (test designer, W1-38 revision,
  Rewrite-Reason DEC-966 item 1), b868b60a2a56 (product-spec, the two deny rules removed), be944228 (lead, merge of
  w2/W2-105-tests), 381e1187 (lead, gov checkpoint record CP-DAEO-zpdj-0002).
- Tests worktree and branch w2/W2-105-tests removed (merged).
- Red check done (tests worktree = base + tests): 22 failed / 25 passed, all for the stated reason (log/red.txt).
- Collection check: "17498/17500 tests collected (2 deselected) in 39.23s", exit 0.
- trailer_gate: 6 commits judged, 0 lacking, 0 bad Implements (run before 381e1187; re-run on resume).
- keyword_warn: 0 files.

## Not done (what held it)
- The machine's load gate (DEC-847) held from 03:20 to 04:51 (load 40-150 on 20 CPUs; other leads' runs) and the
  machine rebuild lock was held 60+ min by the nightly's rebuild. Per DEC-943, returned PACKAGES at 90 min.
- ps-2 (fresh product-spec to run the acceptance tests once) never ran its tests: stopped by me at 04:51 (exit 130),
  no commit, no output.
- Rebuild of this worktree's store: never ran (rebuild-1 stopped while queued behind the nightly).
- Scoped verification (select_tests.py + parallel run in the close's form; 0 serial cases in the preview), W1-39 for
  KPI 4 (not selected by select_tests.py), gov check: not run.

## What a resume must do
1. Wait for the load gate (background script), disk gate, then
   `flock /tmp/gov-os-rebuild.lock` full rebuild of this worktree (rebuild.sh 2).
2. select_tests.py (after the last commit), plan_run.py to make parallel.args / serial.args, the parallel run in the
   close's form with --junitxml log/parallel.xml (serial phase only if serial.args non-empty), plus W1-39 run alone
   as the KPI-4 evidence (labelled as outside the selection).
3. gov check --json; trailer_gate again; keyword_warn again.
4. Optionally a fresh product-spec to run the acceptance tests once (the loop's step), or count the lead's scoped run.
5. Return DONE with package P-W2-105-1 (KPI 2 scope) still open.

## Package P-W2-105-1 (not blocking the change)
KPI 2's "leads included" and "every other session": the kernel's install rule
(template/governance/kernel/hooks/pretooluse.py, install branch) asks any orchestrator-role session (leads too) and
lets research install inside its experiment folder (DEC-163). The CTO-only rule exists only in this repository's
.claude/hooks/pretooluse.py (CTO_WBS = "W2-00"). Out of this ticket's one path. Recommend (a): re-baseline KPI 2 for
this ticket to what the tests cover; file a new ticket for a product notion of the coordination ticket in the kernel
guard (P1, installs).

## Loop
- Iteration 1; not yet verified.

## Brief gaps (running list)
- KPI 2's second half needs code outside the ticket's path | the ticket file | ~10 min
- The implementer's sandbox mounts tests/ and .gov-runtime/scratch/ read-only, so the TESTS-READY merge step cannot
  run in an implementer session | common brief | ~5 min
- git merge has no --trailer; the merge form (--no-commit then commit --trailer) is not given | common brief | ~2 min (est.)
- W1-39 (named by KPI 4) is not selected by select_tests.py | this ticket's part / tool | ~5 min
- The nightly holds the machine rebuild lock (60+ min), though DEC-961 says the nightly takes no lock | common brief | ~40 min
- gov retrieve on W2-00-store hangs inside the sandbox (ollama.com blocked) | tool / common brief | ~3 min (worker)
- The hook refuses read-only commands that name tests/acceptance/... in a grep or wc | tool (guard) | ~3 min

## Guard refusals
- ~03:31 | pgrep/grep pipeline naming the tests/acceptance/W2-105 path in a grep pattern | "a command that may write the acceptance tests ..." | false-positive | 1 min; pgrep without the path
- ~03:45 | grep/wc/python3 -c reading tests/acceptance/serial-only.txt | same reason | false-positive | 2 min; Read tool and a script file
- td-1: 2 (TMPDIR variable write target; rm cleanup x2); ps-1: 2 (Write to .gov-runtime/scratch/ps/ denied; merge read-only fs)

## Left files
- .gov-runtime/scratch/lead/briefs/ps-2-head.md (rm refused by a permission prompt)
- /tmp/gov-os-lead-W2-105: 14M, 2809 files and folders (pytest base folders of the red check and collection)
