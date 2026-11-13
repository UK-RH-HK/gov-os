# Brief rev-1: independent auditor (FULL review, round 1) for DAEO-k1e2 (W2-171), class C2

You are the independent auditor for ticket DAEO-k1e2 (W2-171): the memory audit's measure (`python3 -m gov.memaudit
measure|judge|classes|pool|pool-import`: the control, the retrieval figures, the judged reader run, the fault rule, the
misses file, FIGURES.json, the regression pool, the spend brake). Read-only: you write nothing in the repository; your
verdict is your return. Probe head `1ba9203a94fe` of branch `w2/W2-171` (check it is unchanged when you start:
`git -C /home/usain/gov-os-worktrees/W2-171 rev-parse HEAD`). The code head is `c103e26be`; `1ba9203a9` only merges
w2/integrate's ticket files in.

## What to read
| what | path |
|---|---|
| ticket (KPI lines S1-S8, F1-F5 are the spec; `## Interface` items 1-12; the CTO's ten rulings; the PKG-W2-171-F5-1 ruling at its end) | /home/usain/gov-os-worktrees/W2-171/.tickets/DAEO-k1e2.md |
| the code | src/gov/memaudit/ (matcher.py is the one adapter onto `gov.retrieval.measure`'s private names, ruling 3) |
| W2-170 (the layer underneath: DECLARATION.json, USED, the preflight; read, not under review) | the code W2-171 calls in src/gov/memaudit/ that predates the branch, and tests/acceptance/W2-170/ |
| the fresh 80's reference tools (what S3's pins and the printed forms generalise) | /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/ref/fresh80/ (f80lib.py, run_measure.sh, fresh80_reader.py, fresh80_figures.py) |
| the ticket's base (F5) | `git -C /home/usain/gov-os-worktrees/W2-171 merge-base HEAD w2/integrate` (= `03393ee51`) |
| the engineers' evidence (claims to check, not to trust) | docs/changes/W2-171-evidence.md |
| tests | tests/acceptance/W2-171/ (README.md first; the test designer's, td-1, `439806e0f`), tests/unit/memaudit/ |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073, DEC-1052, DEC-1129 |

Implementers: td-1 (test designer, session 96589783), eng-1 (engineer, session ba9dbbb3: `5f72ee4b6`, `90f61e006`,
`386a93faa`, `5710c100d`), eng-2 (engineer, fix round 1, session d1f3d78d: `c103e26be`).

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer from
both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

## What to probe (at least these; find more)
1. Each of S1-S8: does the code do what the line and its Interface item say, including each Verify's planted cases, and
   fail closed? In particular:
   - S1: the control after DECLARATION.json and USED (ruling 1); 34 and 33 proceed, 31 stops before the audit set's first
     search; `control out of range` in the counts; USED untouched.
   - S2: the figures from the matcher and families of `gov.retrieval.measure`; every ranked output kept; `--kept`
     re-scores to the same figures without a search.
   - S3: the reader's and graders' prompts pinned by hash to the fresh 80's (`READER_SYS`, the schemas, the cut); the
     verdict line's r, w, exact 95 % interval, bar ceil(0.85 n) / floor(0.05 n), target ceil(0.95 n); the beside figures
     (exact McNemar) printed, never judged.
   - S4: a degraded search (not reranked, a route missing, rerank fallen back) or a store sha256 change makes the attempt
     not whole; one restart only while no attempt has counted; a second fault stops and goes to the owner; a store change
     stops with no restart; the reranker checked ready before each attempt.
   - S5/F2: misses.jsonl's exact form and outcomes; empty file when no miss; a second run refused by USED with
     misses.jsonl byte-identical; a verdict below the bar stays recorded.
   - S6/F1: FIGURES.json counts only; no question, gold answer, answer or source path in stdout, stderr, any log or
     FIGURES.json, including error texts and tracebacks.
   - S7: the pool whole at 400 or fewer, else a seeded draw of 400 with the seed recorded first; same seed, same draw;
     a fall of 3 points or more named a regression; `pool-import`'s count guard (79, 138) refuses with nothing written.
   - S8: each call's `total_cost_usd` in the ledger; stop at twice the projection; resume asks only the unfinished.
2. F3: no search entry in the ledger earlier than DECLARATION.json's and USED's file times; no rebuild call ever.
3. F4: the Ollama servers and the reranker touched only by query calls; no stop, restart, load, unload; no signal to
   their processes (look for any `kill`, `os.kill`, `/api/pull`, `keep_alive: 0`, `systemctl`, etc.).
4. F5: `git diff --name-only 03393ee51 1ba9203a94fe` lists only paths matched by the ticket's allowed_paths, plus the
   test designer's `tests/acceptance/W2-171/**`.
5. The tests: would they catch a wrong implementation of each line (one planted mutation per line, reasoned or run on a
   `git archive` copy under /tmp/W2-171-rev1/, never in the tree)?
6. Spend safety and the real world: could any path of the code, run as the CTO will run it, open the real sets root,
   a hidden half or the held-out material other than through W2-170's declared path, or spend model tokens beyond the
   brake?

Runs: planted folders only (pytest's tmp_path), never the real ~/gov-os-eval, ~/gov-os-runs, ~/.claude, a hidden folder,
a live Ollama or reranker, or a real model call. Every pytest goes through the heavy-slot gate (the CTO's order), one
folder or file per run, TMPDIR outside the repository and outside ~/gov-os-runs:
`TMPDIR=/tmp/W2-171-rev1 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
(make /tmp/W2-171-rev1 first with `mkdir -p`).

Known and not this ticket's (do not count them as findings):
- the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py (shared base reds, the CTO's
  ruling P-W2-121-5; W2-177 fixes them);
- `tests/acceptance/W2-170/test_w2_170_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows`: it judges
  any branch against W2-170's paths, so it is red on W2-171's branch by construction (the CTO's ruling, the ticket's last
  section; W2-180 fixes it before this ticket lands);
- one W2-171 case skips in the sandbox (the AF_UNIX reranker stand-in).

## Severity
A finding is blocking when an honest operator running the tool as the ticket says can hit it and it fails open (a figure
or verdict that is wrong and looks right, a content leak, a search before USED, a server touched, spend past the brake)
or loses work (a finished question re-asked, a recorded verdict overwritten). Major: a KPI line or Interface item not
met but failing closed. Minor: everything else (a test gap, wording, an unstated edge that fails closed).
The verdict is FAIL if any finding is blocking or major; else PASS.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

The ticket's context packet (`gov context DAEO-k1e2 --role independent-auditor`, built by your lead) follows.

