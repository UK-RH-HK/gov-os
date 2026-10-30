## Standing rules for every worker of DAEO-s9qc (W2-87) — read first

- **Step 0, before any work: the sandbox check, reported first in your return.** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-s9qc','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
- Then run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect your role, `DAEO-s9qc`, `/home/usain/gov-os-worktrees/W2-87` and `w2/W2-87`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src` set **per command** (never in a session's `--settings` env). Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory (DEC-836, DEC-860, DEC-859):** before reading files at random, ask `gov retrieve`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used it.
- **Reads open, writes closed (DEC-820):** you read freely, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-87/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests); (d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), by anyone, in any tree. Writes stay inside the paths your brief gives.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you met and give the count in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-87/.gov-runtime/scratch/lead/work/` written with the Write tool, and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never read the held-out material's contents; never print a secret; never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A test that needs a repository builds a temporary one from scratch. No clone or copy of a programme under `.gov-runtime/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (and in your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Git:** no amend, no rebase, no reset, no `git checkout` of another commit, no `git clean`, no `--no-verify`, no push, merge or tag. Trailers in the final block with `git commit --trailer`. Never edit `.tickets/`, the decision register or `docs/plan/`. Never run `gov close`, `gov adopt`, `gov pause`, or `gov rebuild` (of any kind; never `--no-embeddings`). Install nothing.
- **Disk (DEC-898):** your share of the ticket's budget is 3 GB and 200,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never `--basetemp`); clean up what you make as soon as you no longer need it; measure your scratch (`du -sh`, `du -s --inodes`) at the end and give the figures.
- **Run everything in the foreground,** one command after another; return only after your commit exists. Never run a suite with `-x`. While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run at most a single test file.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.

# Brief: independent test designer, DAEO-s9qc (W2-87), profile STANDARD

You are a fresh independent test designer (MR-3). Ticket: DAEO-s9qc (W2-87), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-87` on branch `w2/W2-87`. You write the ticket's acceptance tests from its KPI lines, its sources and the behaviour below, before the implementation exists, and you show them red. No implementation exists yet; the code you work with is the code as it stands on `w2/integrate` (read it with `git show w2/integrate:<path>` if in doubt).

**Policy P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/retrieval/authority.py`, `src/gov/retrieval/retrieve.py` as changed on this branch, `tests/unit/retrieval/test_w2_87*`, `docs/research/W2-87-memory-measure.md`, and this branch's change to `governance/project/path-map.yaml`), and name in your return any such result you were served. `retrieve.py` as it stands on `w2/integrate` is existing code you may read.

## What you read

- `.tickets/DAEO-s9qc.md` (read-only): its KPI lines (success and failure), its `allowed_paths`, its sources.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-952 (item 1), DEC-423, DEC-424, DEC-791 (item 1), DEC-860, DEC-866, DEC-694, DEC-951 (item 5: tests minimal and in proportion); CAP-10 in `docs/contract/contract.yaml`.
- The public interfaces: `gov retrieve` (the CLI) and `gov.retrieval.retrieve.retrieve(root, query, *, ids=(), ticket=None, radius=0, batch_size=None, bundle_budget=None, continuation=None, reranker=None)` as it stands on `w2/integrate`, with the bundle it returns (`evidence` in rank order, each with `path`, `start_line`, `end_line`, `chunk_id`, `routes`, `batch`; `merge.dropped`; `gaps` with `NOT_GATHERED`; `continuation`; `stopping_reason`). A reranker is passed as its loader: a function without arguments that returns `score(query, texts)`, one number per text, higher is better (`gov.retrieval.rerank`). Fusion is reciprocal rank fusion (`gov.retrieval.fusion.rrf`, k = 60: each route adds `1 / (60 + rank)`), and the first call gathers the first `(rounds + 1) × batch_size` fused chunks (2 × batch size at radius 0).
- How the existing acceptance suites plant a repository and its store: `tests/acceptance/W1-21/w1_21_support.py` and `conftest.py`, and W1-19's. Build the store the way they do, **without embeddings** (the semantic route unavailable or stubbed as they do it), never this repository's store, and never by running `gov rebuild`.

## The behaviour to test

Two parts, in **two commits**: part 1 first (its own batch), then part 2.

### Part 1 — the register is its entries (the owner's defect, DEC-952 item 1)

Today every chunk of the decision register (the file the path map's `decision_register` key names) takes the identity and status of the register's *last* entry by id, because each decision is its own store record but all share the register's path. The required behaviour:

- A chunk of the register is the entry whose span holds it (the store's register records: each entry from its heading to the line before the next heading). A chunk belongs to the entry whose span holds the chunk's first line.
- **Closure:** with `ids=[<an older entry's id>]` (or a ticket whose closure reaches it), the chunk of that entry's span joins the bundle through the closure route (`"closure"` in its `routes`) — today it does not, unless the register's last entry is reached.
- **Drops:** a register whose last entry by id is SUPERSEDED (by its status line, or as the target of a SUPERSEDES edge from another entry) keeps its other entries' chunks in the bundle — today every register chunk is dropped and `merge.dropped` names the register with the last entry's id. This ticket drops nothing new: a superseded entry's own chunk that today's code keeps stays kept (leaving it out is W2-55's, DEC-791 item 1).

### Part 2 — the authority order (DEC-952 item 1; the KPI lines)

The order is configuration: one top-level block of the path map (`governance/project/path-map.yaml` of the planted repository), `retrieval_authority`, in this form (the form is the interface; plant your own values):

```yaml
retrieval_authority:
  lift:
    fused: 0.004     # added per tier step to the fused (RRF) score, before the first call's cut
    rerank: 1.0      # added per tier step to the reranker's score, after the rerank
  default: middle    # the tier of a chunk that no tier matches
  tiers:             # in order, highest authority first
    - name: governing
      records: [{type: decision, status: [ACCEPTED]}, {type: capability}]
      paths: ["docs/contract/**", "docs/charter/**", "docs/spec/**", "docs/adr/**"]
    - name: middle
    - name: reports
      paths: ["tests/**", "docs/assessment/**", "docs/audit/**", "docs/probes/**"]
```

- Path patterns match the chunk's repository-relative path whole: `**` crosses folders, `*` stays inside one name. A record rule matches the chunk's store record (for the register, its own entry; for another file, the store's record of that path) by `type`, and by `status` when it names any.
- A chunk in two tiers gets the lower one. A chunk whose record is not current (SUPERSEDED by status or edge; DEPRECATED, REJECTED, WITHDRAWN) is never above the default tier: a superseded entry gets no lift.
- The lift: the tier at position `i`, the default at `d`, adds `lift × (d − i)` (+ above the default, 0 at it, − below): to the fused score before the cut, and to the reranker's score after the rerank (when the reranker gave scores). Both sorts are stable: equal adjusted scores keep the order they came in. A lower-authority chunk whose score is better by more than the lift per step keeps its place.
- With the block absent, the bundle is today's, item for item.
- Fail closed: a path map that cannot be parsed, a block that is no mapping, an unknown key, a `default` that names no tier, or a status that is no single word (letters, digits, `_`, `-`; e.g. `ACCEPTED, SUPERSEDED` as one string) → the call refuses with error code `CONFIG_INVALID` (a `GovError` whose code is that; the CLI's JSON error carries it). Never read as empty or as today's order.
- What stays: what the bundle keeps and leaves out (`merge.dropped`, the set of evidence when everything is gathered), the budget, batches, continuation, stopping reasons, parent expansion, DEC-424's failure and lesson records ahead of everything; two runs on one store give one bundle.

## The cases (about six, a few hundred lines at most; STANDARD, DEC-951 item 5)

Everything planted in a temporary repository built from scratch: a register with a superseding pair (a newer entry whose status line supersedes an older one), a capability, a spec, an ADR, a test and an assessment report, all carrying the same matching text. A stub reranker passed in.

- Part 1, in its own file (e.g. `test_w2_87_register.py`): (R1) the closure route takes an older entry's chunk by its own id; (R2) a register whose last entry by id is superseded keeps its other entries' chunks; and the superseded entry's own chunk is still kept when the last entry is accepted (nothing newly dropped).
- Part 2 (e.g. `test_w2_87_authority.py`):
  1. For the same match, every governing chunk ranks above every test and report chunk, without a reranker and with a stub that scores them alike.
  2. A governing chunk that the plain order leaves just past a small first call (a small `batch_size`) enters it; a lower-authority chunk scored better by more than the lift keeps its place (plant a small lift).
  3. Configuration decides: a planted path map that puts tests above decisions flips the order; with the block absent, the order is the plain fused one.
  4. An unreadable block, and a block naming an unknown tier (as its `default`), each refuse with `CONFIG_INVALID`.
  5. The superseded entry ranks below its successor (same match).
  6. Two runs on one store give the same bundle; with and without the block, when everything is gathered, the same chunks are kept and the same left out.

Cases R1, R2 (its first half), 1, 2, 3 and 5 must be red on today's code; say for each why.

## What you write

- Only under `tests/acceptance/W2-87/`: the tests and a `README.md` mapping each KPI line (success and failure) to its tests and its expected red reason, and saying how the tests run this worktree's `src/` (DEC-732) — e.g. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-87 -q -p no:cacheprovider`.
- Behaviour through the public interfaces, never internals. Deterministic, no network, no embedder, no real reranker.
- Red first: run your tests to the end (DEC-732's form above); they fail for the reasons your README states. Also run them with `-p no:randomly` if the project uses it, and confirm collection of `tests` is clean: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-87 --collect-only -q -p no:cacheprovider`.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commits

Two commits, only your test paths: first part 1 (the register file and the README's part-1 lines), then part 2 (the authority file and the rest of the README):

    git commit -m "<subject>" --trailer "Task: DAEO-s9qc" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-952, CAP-10"

## Return

Your two commits' hashes (12 digits); the test count; the KPI lines with their tests; the red reason of each as you saw it; any package; your sandbox check; your `gov retrieve` use; read refusals met; P-R1 results served; your scratch figures.

Your final message is your return. It starts with these twelve labelled lines, then any payload:

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

The twelve fields come first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
