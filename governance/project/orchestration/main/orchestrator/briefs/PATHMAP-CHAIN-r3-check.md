# The narrow check of the path-map chain's round 3 (the owner's P1-D (a), 2026-11-12: a third round, limited)

You are a fresh, read-only independent reviewer. This is not a design review: the owner allowed one narrow check of a rebuild
(beyond DEC-1010's two rounds). READY is computed by `verdict.py` from your block.

## What was rebuilt, and why
The owner's operator applied ACT-OPERATOR-HOURS-2 this morning; its second commit (6b8634d2c) added one `acceptance_exemptions`
entry to `governance/project/path-map.yaml`, so the live map moved from `f4029cfb4942` to `30233a092a4b` and the three queued
path-map ACTs (fixed before hashes) refused. A helper rebuilt them as round 3 with the same builders:

| ACT | Round 2 (reviewed READY) | Round 3 | Before -> after |
|---|---|---|---|
| ACT-EXAMIN-SETS-1 | `acts/ACT-EXAMIN-SETS-1.r2-e8020292/` | `acts/ACT-EXAMIN-SETS-1/` (manifest sha8 `2f814211`) | `30233a092a4b` -> `1fe00f43d8ab` |
| ACT-ACCEPTED-REDS-1 | `acts/ACT-ACCEPTED-REDS-1.r2-b8df21d8/` | `acts/ACT-ACCEPTED-REDS-1/` (`9c20e5e3`) | `1fe00f43d8ab` -> `e4281125cf0e` |
| ACT-PATHMAP-EXP-1 | `acts/ACT-PATHMAP-EXP-1.r2-9a945c99/` | `acts/ACT-PATHMAP-EXP-1/` (`b26fe623`) | `e4281125cf0e` -> `805bd918d467` |

All under `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/`. The drafts and packages are in
`drafts/examin-sets/`, `drafts/accepted-reds-1/`, `drafts/pathmap-exp-1/` (each package's "Round 3" note); the chain's rehearsal is
`drafts/examin-sets/rehearsal.r3.log`.

## Check exactly this, nothing more
1. **Entries byte-identical:** for each ACT, the lines its after copy adds to its before copy equal, byte for byte, the lines round 2's
   after added to round 2's before; only the hunk's line numbers moved. (`diff` the before/after copies of each round.)
2. **The chain:** round 3's EXAMIN before equals the live `governance/project/path-map.yaml` on `w2/integrate` today (sha256
   `30233a092a4b...`); each next ACT's before equals the previous ACT's after.
3. **Nothing else changed:** each round 3 `apply.sh`, `list.txt` and manifest differ from round 2's only in hashes, the before/after
   names, comments and (EXP) a rebuild hint naming `insert_exp.py`; the manifest's checks are the same checks; every hash recomputed.
4. **The rehearsal:** `rehearsal.r3.log` ends `failures: 0`; run the chain once yourself in a `--no-hardlinks` clone of `w2/integrate`
   (each bundle's own `apply.sh check`, `apply`, `verify` in order; `PYTHONPATH=src python3 -m gov.check.pathmap` exit 0 after each).
Never touch the main tree, `~/gov-os-operator` or the sets root's map; never run a real Claude session.

KPI id for the verdict block: `pathmap-chain-r3`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this rebuild.

## Write and return
- You write nothing in any tree. Single simple Bash commands. Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
- Read-only probes in your own TMPDIR are allowed in the quiet hours (the owner, P1-G (a)). Every pytest through heavy_slot.sh.
- The hidden-half rule holds: never open anything under the evaluation sets' root or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder. A session refused twice for an action stops and says so; it never reaches the same effect by another form.
- Scratch: your own TMPDIR outside the repository and outside ~/gov-os-runs' other folders; remove your clone (`chmod -R u+w` first).
- **Your record is your final message**: the twelve labelled fields; your answers to checks 1-4; every finding with its two lines and
  scope; `REVIEW_MD_BEGIN` ... `REVIEW_MD_END`; then the fenced `verdict` block
  `{"kpis": [{"kpi": "pathmap-chain-r3", "verdict": "pass|fail", "findings": [...]}]}` (ids from F1).
- Estimate: 15 minutes.
