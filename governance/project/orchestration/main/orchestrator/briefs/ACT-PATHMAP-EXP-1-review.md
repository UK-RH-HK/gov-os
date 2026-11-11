# The review of ACT-PATHMAP-EXP-1: `experiments/**` in one path-map namespace (W2-40's EXP-002 files)

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner for a yes and then to the
operator agent (class (b); DEC-1104 (2): rehearsal, a READY review and matching hashes). READY is computed by
`verdict.py` from your block.

## The ACT
- **The package:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/ACT-PATHMAP-EXP-1.md`.
- **The bundle:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/ACT-PATHMAP-EXP-1/`
  (`apply.sh`, `list.txt`, `manifest.json` sha256 `9a945c99201d4c2c49cbd522c38b3ebee5b2fa0c09dbb5f9e62f852721b6e93c`,
  `rehearsal.log`, `before/`, `after/`). Its form follows ACT-ACCEPTED-REDS-1 round 2
  (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/acts/ACT-ACCEPTED-REDS-1/`)
  and ACT-EXAMIN-SETS-1 round 2 (`.../drafts/examin-sets/ACT-EXAMIN-SETS-1/`); precedent for a namespace fix:
  `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-PATHMAP-NS-2.md`.
- **Why:** W2-40 (DAEO-6ox0, research: the EXP-002 hook-limit record) was ejected by the merge queue on 11-11 at
  21:38 UTC: with its head `29753c768def` merged, 16 tracked files under `experiments/EXP-002/` match no namespace, so
  `tests/unit/retrieval/test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_one_namespace` and
  `tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace` go red.
- **The chain:** this ACT's `before/` is ACCEPTED-REDS-1's `after/` (sha256 `5654eca4c139…`); the live map today is
  `f4029cfb4942…` (EXAMIN-SETS-1's before). It applies only after EXAMIN-SETS-1 and then ACCEPTED-REDS-1.

## Check
1. **The change is exactly one glob,** `"experiments/**"` added to `namespaces.doc-records.paths`, and nothing else:
   recompute `before/` against ACCEPTED-REDS-1's `after/`, `after/` against `before/` plus that line, and every hash in
   the package, `list.txt` and `manifest.json`.
2. **It fixes the fault and nothing else changes:** with W2-40 merged and the ACT applied, every tracked path matches
   exactly one namespace; no other path changes namespace. What does `doc-records` grant, refuse or leave out (read
   `src/gov/check/pathmap.py`, the retrieval code's use of namespaces, the guard's use in `.claude/hooks/pretooluse.py`)?
   Does putting `experiments/**` there widen what any role may write or read, or hide anything a check must see? The
   helper chose `doc-records` over `systems.research-and-experiments.where` because the tests read `namespaces.*.paths`:
   is that right, and is `doc-records` (not embedded) a sound home for experiment records and scripts, or should
   `run_hook_limit.py` and `results/*.json` sit elsewhere? One line each.
3. **The class and route:** `governance/project/operator/class-rules.yaml`'s `path-map` row gives (b) for a change that
   is not a refusal addition; the operator agent applies a (b) on the owner's `yes ACT-PATHMAP-EXP-1 9a945c99`. Right?
4. **apply.sh is safe:** `check` changes nothing; `apply` acts only from the frozen before state and refuses any other
   (wrong order included) touching nothing; `undo` restores byte for byte only from the after state; the temp file is
   made by `mktemp` in the map's folder; no backup file and no commit by the script.
5. **The rehearsal:** does `rehearsal.log` show red without the ACT and green with it, and the wrong order refused? It
   notes two whole `gov check` runs in a fresh clone red on index freshness, context reproducibility, rebuild and
   traceability (no store built): is that a fair reading, and does anything there bear on the path map?
You may re-run the rehearsal in a fresh `--no-hardlinks` clone under your own TMPDIR (never the main tree), with tests
through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
`-p no:cacheprovider -o tmp_path_retention_policy=failed`, `PYTHONUSERBASE=/home/usain/.local` if HOME is empty.

KPI id for the verdict block: `act-pathmap-exp-1`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT.

## Write and return
- **You write nothing** in any tree; never the live path map.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB and 2,000,000 files and folders, in your own TMPDIR; remove your clone; report `du -sh` and
  `du -s --inodes` in `evidence`.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- Refused twice for the same call: stop and say so; no third try.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields first (task, status, work_completed, files_changed, evidence, tests, discoveries, risks,
    lessons, proposed_decisions, unresolved, recommended_next_action), the sandbox and `ps` checks in `evidence`;
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - then `REVIEW_MD_BEGIN`, a review record in markdown for `review.md`, `REVIEW_MD_END`;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "act-pathmap-exp-1", "verdict": "pass|fail", "findings": [...]}]}`, each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 20 minutes.
