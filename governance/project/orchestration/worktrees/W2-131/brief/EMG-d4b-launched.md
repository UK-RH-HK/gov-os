# D-4b's launched workers: the common rules (CTO session 33b3628c, 2026-11-03; DEC-1055, DEC-1064, DEC-1065)

You run in the launch sandbox under your own ticket's id (`GOV_TICKET`), so the guard keeps the test designer and the
engineer apart (DEC-1056, DEC-1063). No lead runs (DEC-1051): the CTO acts as your ticket's lead from its session.

**Step 0, the sandbox check, reported first in your return:** (a)
`python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-<ticket id>','w').write('x')"` must fail; (b)
`echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or
(b) failed, stop and return.

Read first, whole: `/home/usain/gov-os-worktrees/W2-131/.gov-runtime/scratch/brief/EMG-common.md`
(where it names a TMPDIR or the heavy slot, use the sandbox's own TMPDIR; the heavy slot only if the sandbox allows it),
`governance/project/orchestration/INTENT-DEC-1052.md`, your ticket (`.tickets/<id>.md`, its KPI lines, `allowed_paths`
and the notes at its end), and the register's `### DEC-1065` (grep; the register is 1.6 MB).

**No private embedder, no real model (DEC-1064, DEC-1065 (1)):** never run `gov retrieve` or `gov context` in the sandbox
(read the code with grep and the Read tool); no test of yours starts a real embedder, reranker or model (stand-ins only);
no scoped set from `select_tests.py` (the CTO runs it outside the sandbox). Before you return: `ps -eo pid,args | grep -iE
"[o]llama|[l]lama-server"` must show nothing of yours: report it. Never the hidden half (`~/gov-os-eval`), held-out
material or secrets.

**Every pytest run excludes the real-model cases (DEC-1012: broken twice on 2026-11-03):** add
`-m "not local_only" -k "not real and not green_here and not time_limit"` to every run of a whole folder, and set
`HOME` to an empty scratch folder so no reranker environment exists; name in your return what the exclusion left out.
The CTO runs those cases outside the sandbox, between measures.

**Do not merge `w2/integrate` yourself:** the sandbox keeps `.claude/`, `.tickets/` and `tests/acceptance/` read-only, so
a merge fails part-way. The CTO merges `w2/integrate` (and the designer's tests) into your branch outside the sandbox before
you start or when you ask; if your branch lacks something you need from integrate, say so and stop.

**Commits:** `Task: <your ticket id>`, `Implements: DEC-1065`, `Role: <your role>`, `Co-Authored-By: Claude Opus 5.5
<noreply@anthropic.com>`. **Return:** the twelve fields as labelled lines (task, status, work_completed, files_changed,
evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox check
and the `ps` check first.

**Test designer:** write only `tests/acceptance/<W2>/**` in your tests worktree; tests from the new KPI line only, in the
README map **with full node ids** (`test_<file>.py::test_<name>`, every item; the runner fails a line whose map names a
test it cannot collect); show each red on today's integrated code; write `TESTS-READY` text in your return (the CTO
writes the marker). **Engineer:** build to the KPI line and the ticket's notes, never to the tests (you never read your
ticket's acceptance tests); your own unit tests (stand-ins); `docs/changes/<W2>-evidence.md` (one row per KPI line);
stop when your unit tests pass; the CTO merges the designer's tests and you run `gov accept <W2>` after.
