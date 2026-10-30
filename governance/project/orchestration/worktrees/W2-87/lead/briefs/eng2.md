## Standing rules for every worker of DAEO-s9qc (W2-87) — read first

- **Step 0, before any work: the sandbox check, reported first in your return.** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-s9qc','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
- Then run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect your role, `DAEO-s9qc`, `/home/usain/gov-os-worktrees/W2-87` and `w2/W2-87`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src` set **per command** (never in a session's `--settings` env). Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory (DEC-836, DEC-860, DEC-859):** before reading files at random, ask `gov retrieve`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used it.
- **Reads open, writes closed (DEC-820):** you read freely, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read or name the qualification oracle); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-87/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests); (d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), by anyone, in any tree. Writes stay inside the paths your brief gives.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead. Count the refusals you met and give the count in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file in your own session scratchpad (the folder your session names; the guard refuses `.gov-runtime/scratch/lead/`), written with the Write tool, and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never read the held-out material's contents; never print a secret; never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A test that needs a repository builds a temporary one from scratch. No clone or copy of a programme under `.gov-runtime/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` (and in your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Git:** no amend, no rebase, no reset, no `git checkout` of another commit, no `git clean`, no `--no-verify`, no push, merge or tag. Trailers in the final block with `git commit --trailer`. Never edit `.tickets/`, the decision register or `docs/plan/`. Never run `gov close`, `gov adopt`, `gov pause`, or `gov rebuild` (of any kind; never `--no-embeddings`). Install nothing.
- **Disk (DEC-898):** your share of the ticket's budget is 3 GB and 200,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never `--basetemp`); clean up what you make as soon as you no longer need it; measure your scratch (`du -sh`, `du -s --inodes`) at the end and give the figures.
- **Run everything in the foreground,** one command after another; return only after your commit exists. Never run a suite with `-x`. While `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run at most a single test file.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.

# Brief: engineer, DAEO-s9qc (W2-87), batch 2 of 2 — the authority order

You are a fresh engineer. Ticket: DAEO-s9qc (W2-87), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-87` on branch `w2/W2-87`. Batch 1 (the register as its entries, commit `006ad0bb36ce`) is done: `src/gov/retrieval/authority.py` holds the function that maps a register chunk to its entry. This batch adds the authority order.

## What you read

- `.tickets/DAEO-s9qc.md` (read-only): every KPI line, success and failure. The decisions DEC-952 (item 1), DEC-423, DEC-424, DEC-791 (item 1), DEC-860, DEC-866, DEC-694 and CAP-10.
- `src/gov/retrieval/retrieve.py` whole, above all `rrf` and the gathering cut (lines 135 to 151 at the base), the rerank and DEC-424's order (lines 207 to 216 at the base); `src/gov/retrieval/fusion.py` (`rrf`, read only: W2-13's) and `src/gov/retrieval/rerank.py`; `src/gov/retrieval/authority.py` as batch 1 left it.
- `src/gov/config/loader.py` (`read_yaml`, the `CONFIG_INVALID` errors) and `src/gov/config/path_map_schema.py`: read only. The path map's schema allows a new top-level key; neither the schema nor the loader changes.
- Anything else you need (DEC-820), except `tests/acceptance/W2-87/`.

## The behaviour (the lead's design; it is the specification of this batch)

**The configuration:** one top-level block of the path map, `retrieval_authority`; **nothing in the code names a path, a record type or a tier** (a failure KPI).

```yaml
retrieval_authority:
  lift:
    fused: 0.004     # added per tier step to the fused (RRF) score, before the first call's cut
    rerank: 1.0      # added per tier step to the reranker's score, after the rerank
  default: middle    # the tier of a chunk that no tier matches
  tiers:             # in order, highest authority first
    - name: governing
      records: [{type: decision, status: [ACCEPTED]}, {type: capability}]
      paths: ["docs/contract/**", "docs/charter/**", "docs/spec/**", "docs/adr/**",
              "template/governance/kernel/roles/**", "template/governance/kernel/skills/**"]
    - name: middle
    - name: reports
      paths: ["tests/**", "docs/assessment/**", "docs/audit/**", "docs/probes/**"]
```

- **Matching:** a path pattern matches the chunk's repository-relative path whole: `**` crosses folders (and matches zero or more of them), `*` stays inside one name. A record rule matches the chunk's record — for a register chunk, **its own entry** (batch 1's function), for any other file the store's record of that path — by `type`, and by `status` when it names any (absent: any status).
- **A chunk in two tiers gets the lower one** (less authority): a test or report that also carries a record is never lifted by it.
- **A chunk whose record is not current** (SUPERSEDED by status or by a SUPERSEDES edge; DEPRECATED, REJECTED, WITHDRAWN; DEC-423) **is never above the default tier**, whatever it matches: a superseded entry gets no lift.
- **The lift:** the tier at position `i`, the default at `d`; the chunk's score gains `lift × (d − i)` (+ above the default, 0 at it, − below).
  - **Before the cut:** on the fused (RRF) list, before DEC-424's move and before `(rounds + 1) × batch_size` are gathered, with the `fused` lift; a stable sort on the adjusted score (ties keep the fused order).
  - **After the rerank:** when the reranker gave scores (`rerank_score`), with the `rerank` lift, a stable sort on the adjusted score (ties keep the rerank's order); without scores the gathered (already lifted) order stands. DEC-424's failure and lesson records are then moved ahead as today.
  - The fused `score` and `rerank_score` the hits carry are not rewritten (keep the adjusted value private to the sort).
- **Bounded:** a lower-authority chunk whose score is better by more than the lift per step keeps its place.
- **With the block absent** (or no path map file), **the bundle is today's, item for item**: no re-sort at all.
- **The continuation** stays valid: the lifted order is a function of the store and the block, so a later call's offset points into the same list.
- **Fail closed:** the path map exists but cannot be parsed, or the block is no mapping, has an unknown or missing key (`lift` with `fused` and `rerank`, `default`, `tiers`; a tier's `name`, optional `paths` and `records`; a rule's `type` and optional `status`), a negative or non-numeric lift (a bool is no number), two tiers of one name, no tiers, a `default` that names no tier, a status that is no single word (letters, digits, `_`, `-`), or a pattern or type that is not a non-empty string → `GovError("CONFIG_INVALID", …)` naming the file and the key, as `gov.config.loader` does. Never read as empty or as today's order. Read the block once per call.
- **What stays exactly as today:** what the bundle keeps and leaves out (the drops, `merge.dropped`), the budget, batches, continuation, stopping reasons, parent expansion, DEC-424's records ahead of everything, the evidence fields; determinism. W2-04's packets (`src/gov/context/**`, not yours) inherit the order and must stay deterministic.

## What to build

- In `src/gov/retrieval/authority.py`: reading and validating the block, a chunk's tier, and the stable lifted sort; keep batch 1's function and its signature as they are.
- In `src/gov/retrieval/retrieve.py`: **two calls only**, one after `rrf` (before DEC-424's move and the cut), one after the rerank (before DEC-424's move); nothing in what it drops.
- In `governance/project/path-map.yaml`: **the one new top-level block above, and nothing else in the file** (append it at the end, with a two-line comment citing DEC-952 item 1 and W2-87). The lead checks `git diff` of the file adds that block alone.
- Builder tests in new `tests/unit/retrieval/test_w2_87_authority.py`: the validation refusals, the pattern matching (`**`, `*`), the lower-of-two-tiers rule, the bound. Proportion (DEC-135).
- If your code runs git, leave its environment as it stands (W2-05's).

## Your paths

Write only: `src/gov/retrieval/authority.py`, `src/gov/retrieval/retrieve.py`, `governance/project/path-map.yaml` (the one block), new `tests/unit/retrieval/test_w2_87*`. Never `tests/acceptance/**`; never `fusion*`, `lexical*`, `src/gov/retrieve/**`, `src/gov/context/**`, `src/gov/store/**`, `src/gov/records/**`, `src/gov/config/**`.

## Done when

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-87 -q -p no:cacheprovider` passes, all of it (run it; read results and failure messages, never its source).
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/unit/retrieval tests/unit/semantic tests/unit/context tests/acceptance/W1-21 tests/acceptance/W1-19 tests/unit/config -q -p no:cacheprovider -n 4 --deselect tests/acceptance/W1-19/test_w1_19_real_models.py --deselect tests/acceptance/W1-21/test_w1_21_dev_tier.py --deselect tests/acceptance/W1-21/test_w1_21_family_check.py` passes. (The sandbox cannot reach the embedder, so those three files hang or err there; the lead runs them outside it.) Your Bash calls stop at ten minutes: run a long suite in parts, each under `timeout 540`. If `gov retrieve` answers FACET_UNAVAILABLE (the index is older than the branch head), read the named files directly. A retrieval case red because the order changed is not edited and not bent to: stop and return it as a package (the case, the old and new order, the decision it rests on).
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m gov.check.pathmap` and `python3 -m gov.check.schema` (same `PYTHONPATH`) stay as they were before your change (run both first, then after).
- One commit:

      git commit -m "<subject>" --trailer "Task: DAEO-s9qc" --trailer "Implements: DEC-952, DEC-424, CAP-10" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

Your commit (12 digits) and its trailers; the lines changed in `retrieve.py`; `git diff --stat` of the path map; the suites you ran with counts; the check outputs before and after; your sandbox check; your `gov retrieve` use; read refusals met; your scratch figures.
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
