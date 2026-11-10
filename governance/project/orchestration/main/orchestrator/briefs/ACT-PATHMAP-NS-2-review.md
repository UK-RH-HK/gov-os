# The review of ACT-PATHMAP-NS-2: the path-map namespace for governance/project/indep-briefs/** (a fault after ACT-W2-149-INSTALL-1)

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner for a yes and then to the
owner's operator by hand (class (b); DEC-1104 (2): rehearsal, a READY review and matching hashes). READY is computed
by `verdict.py` from your block.

## The ACT
- **The package:** `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/packages/ACT-PATHMAP-NS-2.md`.
- **The bundle:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-PATHMAP-NS-2/`
  (`apply.sh`, `list.txt`, `path-map.patch`, `manifest.json` sha256 `b19855849e1e5af58e20dee37145eb14c752b43a12a036d3c88eef1f23678c10`,
  `rehearsal.log`, `before/`, `after/`). Precedent: `packages/ACT-PATHMAP-NS-1.md`.
- **Why:** ACT-W2-149-INSTALL-1 (applied `baac0b2c2`) added five tracked briefs under
  `governance/project/indep-briefs/sgx1/`; no namespace in `governance/project/path-map.yaml` matches them, so
  `python3 -m gov.check.pathmap` reports 5 PATH_NO_NAMESPACE and
  `tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace` is red, which
  makes `gov check` red for every close and the re-pin.

## Check
1. **The change is exactly one path (and its comment)** in `project-overlay`; `before/` equals the live map (sha256
   `44f99ea563cb…`), `after/` equals before plus the patch; recompute the hashes against the package and manifest.
2. **It fixes the fault and nothing else changes:** after it, each tracked path matches exactly one namespace (no
   overlap); what does the namespace grant or refuse (read `src/gov/check/pathmap.py` and the guard's use of
   namespaces in `.claude/hooks/pretooluse.py`)? Does putting fixed briefs of walled sessions under `project-overlay`
   widen what any role may write or read? Compare with how `governance/project/indep-walls/**` is held, and with
   `class-rules.yaml`'s `walled-sessions` row naming `indep-briefs/**` as (O).
3. **The class and route:** `class-rules.yaml`'s `path-map` row gives (b); the agent takes no path-map ACT before
   2026-11-11 20:02Z (DECIDED-NOT-DONE rows 76, 87), so by hand. Right?
4. **apply.sh is safe:** `check` changes nothing; `apply` refuses an unknown map state; `undo` restores byte for byte;
   the backup lands under `.gov-runtime/` only; the commit line commits only the map with `Role: owner`.
5. **The package's two questions** (refusals for the briefs folder; adding `gov.check.pathmap` to every ACT's
   rehearsal): give your view on each in one line.
You may re-run the rehearsal in a fresh clone under your own TMPDIR (never the main tree), with tests through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
`-p no:cacheprovider -o tmp_path_retention_policy=failed`, `PYTHONUSERBASE=/home/usain/.local` if HOME is empty.

KPI id for the verdict block: `act-pathmap-ns-2`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree; never the live path map.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080). Row W2-L423's rule: under
  `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
