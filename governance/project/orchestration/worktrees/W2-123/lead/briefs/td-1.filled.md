# Brief: independent test designer, DAEO-qzrq (W2-123), STANDARD

You are a fresh independent test designer (MR-3). Ticket: DAEO-qzrq (W2-123), profile STANDARD. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-123-tests` on branch `w2/W2-123-tests` (DEC-963). You never read or write
the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-123`. You write the ticket's acceptance tests from its KPI
lines and its sources, in parallel with the engineer, and you show them red.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-qzrq','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-qzrq`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-123-tests` and
  `w2/W2-123-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing
  started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for
  verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src` set
  **per command** (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in
  your return; it must point into this worktree. Your tests must exercise whatever `gov` the pytest process imports
  (import `gov.retrieval.ollama` from the pytest process; any child process runs `sys.executable` with the pytest
  process's own `PYTHONPATH` inherited), so that, once merged into the ticket's worktree and run there with that
  worktree's `PYTHONPATH`, they exercise the ticket's code. Your README says so.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`
  (a read). Never the ticket worktree's store. **Never one giant query (DEC-860):** a large question is taken in
  batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question
  (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and
  targeted, never a load of the whole graph. What changed on `w2/integrate` since that store's refresh, read with
  `git show w2/integrate:<path>`.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`src/gov/retrieval/ollama.py`, `tests/unit/retrieval/test_w2_123*`, `docs/changes/W2-123-evidence.md`), and name in
  your return each such result you were served (DEC-820 (c)). You may read `src/gov/retrieval/ollama.py` as it stands
  on `w2/integrate` (`git show w2/integrate:src/gov/retrieval/ollama.py`) to learn today's public behaviour, never the
  ticket branch's.
- **Policy 2 (DEC-820):** reads are open, with four refusals: (a) secrets and keys, never printed; (b) the contents of
  the held-out qualification material (its file names may be seen); never read or name the qualification oracle;
  (c) the counterpart's work on this ticket: you never read this ticket's implementation, the files
  `git -C /home/usain/gov-os-worktrees/W2-123 diff --name-only w2/integrate...HEAD` names (other than your own
  tests), and never anything in `/home/usain/gov-os-worktrees/W2-123`; (d) the hidden half of any evaluation set, by
  whoever is measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the
  repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named
  folders instead, and count the refusals in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces; anything longer goes in a script file under
  `/home/usain/gov-os-worktrees/W2-123-tests/.gov-runtime/scratch/td/` written with the Write tool, then run. A refused
  form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of
  this repository). A test that needs a repository builds a temporary one from scratch, under pytest's `tmp_path`. No
  clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Never write in `~/gov-os-workbench`; never
  list, glob or search it; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a session `.gov-runtime/freeze` may
  show as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your budget (DEC-898):** 4 GB and 200,000 files and folders outside the tracked tree (your share of the ticket's
  20 GB and 1,000,000). Set `TMPDIR=/tmp/gov-os-lead-W2-123` on every test run (where `gov launch`'s sandbox sets its
  own temp folder, keep that one and count it). Keep pytest's own temp retention; never `--basetemp`. Clean what you
  make as soon as it is no longer needed. Measure (`du -sh` and `du -s --inodes`) before your red run and at the end;
  give the figures in `evidence`.
- **Heavy steps (DEC-979 D1, DEC-1008):** one test file is not heavy. If your red run covers more than one file, run it
  as `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh <the pytest command>`.
  You need no rebuild. Never run `gov rebuild --no-embeddings` on any real worktree.
- **Never the real embedding servers:** no test sends a request to, stops, or starts anything at 127.0.0.1:11434 or
  127.0.0.1:11435, and no test runs the real `ollama`. Every test sets `HOME`, `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST` in the `env=` it passes (free ports on 127.0.0.1 your test picks), `GOV_OLLAMA_BIN` to a
  planted executable under `tmp_path`, and stands up its own stand-in endpoint. A safe-restart test stops only a
  process your test started. Existing tests on `w2/integrate` that plant an Ollama executable or a stand-in endpoint
  (for example under `tests/unit/ollama/`, `tests/acceptance/W1-18/`, `tests/acceptance/W2-54/`) show how: find them
  and reuse their way.
- Install nothing (a tool you need is a package, P1). No push, merge, rebase or tag. Never write `.gov-runtime/**`
  outside `.gov-runtime/scratch/`. No subagents that write. Never ask or notify the owner; never `owner-ping`.
- On an authentication or access error, stop and return `AUTH_REQUIRED`. On ESCALATION_BLOCKED from any command,
  stop and return it.

## What you read

- The ticket file `.tickets/DAEO-qzrq.md` (read-only): its KPI lines, its `allowed_paths` and its sources.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1014 (items 4 and 6), DEC-1015 (item 2), DEC-1017, DEC-1010
  item 7, DEC-1011, DEC-982, DEC-996 item 3, DEC-260, DEC-261, DEC-798, DEC-135, DEC-221.
- The package `governance/project/orchestration/packages/ACT-OLLAMA-CAP-1.md` (what the cap is and why).
- W2-20's ticket `.tickets/DAEO-r30l.md` (its KPI line on the durable cap of both servers, which this ticket's start
  reads).
- The WBS rules, `docs/plan/WAVE_2_WBS.md` section 0, and the W2-123 card in section 2.
- The code it works with, as it stands on `w2/integrate`: `src/gov/retrieval/ollama.py` and how
  `src/gov/retrieval/semantic.py` embeds and keeps vectors (its model, its `/api/embed` requests, float32 BLOBs).

## The behaviour to test

The ticket's KPI lines, as they stand in its file, and this interface, which the lead fixes so that you and the
engineer build to the same outside:

## The outside of W2-123 (the lead's interface spec: the same text in both workers' briefs)

The ticket's KPI lines say what must be true; they do not say where the configuration lives, what the start's
result names, or how the health probe, the safe restart and the determinism check are called. So that the test
designer and the engineer, working in parallel and never reading each other's work, meet on the same behaviour, the
lead fixes these public forms for this run (a P3 reading of the lead, inside the ticket's paths, reversible; logged
for the CTO). Everything not fixed here is the implementer's choice, and the tests do not depend on it. Every name
below is in the module `gov.retrieval.ollama`, which today holds `ensure_available`, `ensure_query_available`,
`query_host`, `DEFAULT_HOST`, `QUERY_DEFAULT_HOST`, `NO_GPU` and `WARNING` (read it on `w2/integrate`).

### S1. The configuration (KPIs 1, 4 and 6)

- **The file** is the resource gate's one configuration file (W2-20): `<HOME>/.gov-os/machine/gate.json`, where
  `<HOME>` is the `HOME` of the environment the call is given (`env=`, default the process's own). A test plants it
  under a temporary `HOME`. Other keys of that file are W2-20's and are not read here.
- **The section** is the key `embedding_servers`: an object with up to two entries, `shared` (the server at
  `OLLAMA_HOST`, which `ensure_available` starts) and `query` (the CPU-only one at `GOV_QUERY_OLLAMA_HOST`, which
  `ensure_query_available` starts). Each entry is an object; every key in it is optional:
  - `parallel`: an integer of at least 1, the number of requests the server answers at once. It reaches
    `ollama serve` as Ollama's own setting `OLLAMA_NUM_PARALLEL` in the daemon's environment (the configured value
    wins over any inherited one).
  - `cpus`: the logical CPUs the server and every process it starts may run on, as a string in the CPU-list form of
    `taskset -c` and of `Cpus_allowed_list` in `/proc/<pid>/status` (for example `"2-5,8"`).
  - `nice`: an integer from 0 to 19, the lower priority the server and every process it starts run at (the started
    process's niceness is at least this value).
  - `probe_slow_s` and `probe_hung_s`: positive numbers of seconds, `probe_slow_s` below `probe_hung_s`, used by the
    health probe (S3).
- **Defaults** (no file, no section, no entry, or a key left out): the product's measured defaults, the same on
  every machine; the CPU default is a count, resolved at start to the highest-numbered that many of the CPUs the
  calling process may run on (all of them if it has fewer); nothing of this machine (its CPU numbers) is written in
  the code. The ports stay as today (`OLLAMA_HOST` / `GOV_QUERY_OLLAMA_HOST`, else Ollama's own default and DEC-798's
  product default): they are product defaults, not this machine's. The query server keeps its GPU hidden (`NO_GPU`)
  whatever the configuration says.
- **An unreadable value** (the file not JSON or not an object, `embedding_servers` or an entry not an object, a key
  of the wrong type or out of range, a `cpus` list that cannot be parsed or names no CPU the calling process may run
  on, `probe_slow_s` not below `probe_hung_s`): **the server is not started**. The start's result is
  `available: False`, `started: False`, `state: "CONFIG_INVALID"`, and its `warning` names the file and the key
  (for example `embedding_servers.shared.parallel`); the warning is written once to standard error. Never an
  uncapped start. If the server already answers, it is used as today (`available: True`, `started: False`), and the
  `warning` still names the unreadable value.

### S2. The start and its result (KPIs 1 and 6)

- `ensure_available(*, timeout_s=20.0, env=None)` and `ensure_query_available(*, timeout_s=20.0, env=None)` keep
  their signatures and their present behaviour (the daemon is started as `<executable> serve` with the executable
  found as today, `GOV_OLLAMA_BIN` first, detached, never stopped by them), and **every start of either server is
  capped**: the started process runs on the configured (or default) CPUs at the configured (or default) niceness,
  with its configured (or default) `OLLAMA_NUM_PARALLEL`, and every process it starts inherits the cap. A planted
  executable (`GOV_OLLAMA_BIN` pointing to a script) sees this from inside: its `Cpus_allowed_list`, its niceness,
  its environment, and those of a child it starts.
- **The result** keeps its keys (`available`, `started`, `facet`, `state`, `warning`) and gains `settings`: an object
  with `parallel` (integer), `cpus` (the CPU list applied or to be applied, in the CPU-list form, concrete, e.g.
  `"12-19"`), `nice` (integer) and `source` (the configuration file's path when the values came from it, else
  `"default"`). When the server was already answering, `settings` states the values a start would use. With an
  unreadable value, `settings` is `None`.

### S3. The health probe (KPI 5)

- `probe(server, *, env=None)`, `server` either `"shared"` or `"query"`, sends one fixed text to the server's
  `/api/embed` (the semantic store's model) and returns an object with at least `server`, `host`, `state` and
  `seconds` (the time to the answer, or `None`):
  - `state` `"healthy"`: a vector came back within `probe_slow_s`;
  - `"slow"`: a vector came back after `probe_slow_s` but within `probe_hung_s`;
  - `"hung"`: no vector within `probe_hung_s` (no answer in time, or an answer without a vector);
  - `"down"`: nothing listens at the server's address.
  A probe never starts, stops or restarts anything. An unreadable configuration value: `state` `"CONFIG_INVALID"`,
  naming it, and nothing is sent.

### S4. The safe restart (KPIs 5 and 6)

- `safe_restart(server, *, env=None)`, `server` either `"shared"` or `"query"`, returns an object with at least
  `server`, `host`, `restarted` (bool), `reason` (a string), `probe` (the probe's result it acted on), `settings`
  (as S2), `old_pid` and `new_pid` (integers or `None`):
  - **answering** (`healthy` or `slow`, re-checked immediately before any stop): nothing is stopped or started;
    `restarted` false, `reason` names that it is answering. **A restart never happens while the server answers.**
  - **hung:** the process that listens on the server's port is stopped, together with the processes it started,
    only when its command line is `<executable> serve` for the executable the Gov OS would start (resolved paths
    compared); then the server is started again exactly as S2 starts it (its configured cap and parallel requests),
    and its health is awaited. `restarted` true, `old_pid` and `new_pid` named. A port held by any other process is
    never stopped: `restarted` false, `reason` names the process that holds it.
  - **down:** the server is started as S2 starts it; `restarted` true, `reason` names `down`, `old_pid` `None`.
  - **an unreadable configuration value:** nothing is stopped or started; `restarted` false, `reason` names it.
- **The record:** every call that stops or starts a server appends one JSON line to
  `<HOME>/.gov-os/machine/embedding-restarts.jsonl` (the same `HOME` as S1), with at least `time`, `server`, `host`,
  `probe_state`, `old_pid`, `new_pid`, `restarted` and `settings`. A call that finds the server answering records
  nothing.

### S5. The determinism check (KPI 2 and the failure line)

- `check_determinism(host, references, parallel)`: `host` an endpoint in `OLLAMA_HOST`'s form; `references` a list of
  pairs `(text, expected)`, `expected` the text's vector as the semantic store keeps it (float32, native byte order,
  `struct.pack(f"{n}f", *vector)`); `parallel` an integer of at least 1. It embeds every text in a request of its own
  (the semantic store's model, `{"model": …, "input": [text]}` to `/api/embed`), with `parallel` requests in flight at
  once, packs each answer to float32 the same way, and compares it with `expected` byte for byte (the stored
  precision). It returns an object with `parallel`, `checked` (how many texts), `differing` (the indices whose vector
  differed or was not returned) and `verdict`: `"accepted"` only when every vector came back equal, otherwise
  `"refused"` (a missing answer refuses too).
- A parallel setting is only chosen, or made a default, when this check accepted it on the real embedder against
  vectors made at one request at a time; the evidence file records the check.

### S6. The evidence file (KPI 3)

- `docs/changes/W2-123-evidence.md` holds a table of the 16 measured cases (parallel requests 1, 2, 4 and 8; under
  the configured CPU cap and without it; alone and with three rebuilds' embedding at once), each row with its chunks
  per second and its semantic stage in seconds, and a line beginning `Chosen setting:` that names the parallel
  requests and the CPU cap chosen and why. The lead measures; a later engineer batch writes the file from the lead's
  figures. No test runs the measurement.

## What you write

- Only inside `tests/acceptance/W2-123/` in your worktree. No throwaway implementation is left in the tree.
- STANDARD (DEC-221): every KPI line's success and failure plus the key edge cases (an unreadable value of each
  kind S1 names, the query server's cap and hidden GPU, a cap inherited by a child, a restart refused while the
  server answers and for a foreign process on the port). No combinatorial expansion. Behaviour through the public
  interface above, never internals. Deterministic, no network beyond stand-in endpoints on 127.0.0.1 that your tests
  start and stop. Tests that need a CPU list pick CPUs from `os.sched_getaffinity(0)` at run time, so they pass on
  any machine; nothing of this machine in the tests either.
- KPI 3 (the measure) gets at most one test: the evidence file exists and has S6's table and `Chosen setting:` line.
- A `README.md` there that maps each KPI line (KPIs 1 to 6 and the failure line) to its tests, gives the expected red
  reason of each, and says how the tests exercise the code under test (above).
- Red first: run your tests to the end, never with `-x`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123-tests/src TMPDIR=/tmp/gov-os-lead-W2-123 python3 -m pytest tests/acceptance/W2-123 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (through `verify_lock.sh` if more than one file); they fail for the reason the README states (the base code reads
  no configuration, starts uncapped, states no settings, and has no probe, restart or determinism check). Collection
  must succeed. Report the counts.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact,
  reversibility, cost, recommendation, confidence). If the KPIs require revising an earlier ticket's acceptance test,
  name it and do not edit it.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only your test paths, in one commit, with the trailers in
the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-qzrq" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014, DEC-1017" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your sandbox check (first); your commit's hash (12 digits); the test count; the KPI lines with their tests; the red
reason as you saw it; the `gov.__file__` line; every earlier test you rewrote, with its reason (none expected); the
`gov retrieve` queries you ran and any result under the implementation paths you were served; the read refusals you
met; any package.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so.
