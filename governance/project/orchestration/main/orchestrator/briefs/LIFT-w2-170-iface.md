# W2-170's Interface block (PKG-W2-170-IFACE-1, option (a); DEC-1052)

Read `LIFT-common.md` first, **with one change: you edit one file in the main tree,
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-61vm.md`, its body only** (an `## Interface` section after the
front matter; and `DEC-1052` added to `sources`). Never change a KPI line's meaning, status or other field. You do not
commit. Report to `.gov-runtime/scratch/orchestrator/drafts/w2-170-iface/REPORT.md`. Role: product-spec helper, Sonnet high,
class C2. Never open `~/gov-os-eval/` or `~/gov-os-runs/`.

## Why
The W2-170 lead returned PACKAGES: the ticket states no interface, so the test-designer and engineer pair cannot start
(DEC-1052; the role-cto line "State the ticket's interface … before the pair starts"). Its return lists six gaps; read it:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/W2-170-A5-tests.json` (the `result`).
Read the ticket, `governance/project/orchestration/packages/MEMORY-AUDIT-1.md`, the approved briefs
`packages/MEMORY-AUDIT-1/briefs/{writer,checker,auditor}.md` (approved as written, DEC-1129 (2): **do not require any change
to them**), the `memory-verdict-2` entry of `governance/project/path-map.yaml`, the fresh-80 tools the ticket generalises
(`preflight.py` and the measure runner: find them in `governance/project/orchestration/tools/` or `tools/`), and W2-171/
W2-172's tickets (`DAEO-k1e2`, `DAEO-p8tv`) so the interface they call is the one you state.

## Write the `## Interface` section (the lead's option (a), made exact)
1. The CLI: `gov memaudit <subcommand>` or `python3 -m gov.memaudit ...` (follow how W2-171/172 call it), each flag
   (`--sets-root`, `--audit`, `--repo`, `--commit`, `--store`, `--decision`), what each defaults to, and how the gov pin and
   `retrieval.yaml` are found.
2. The layout under the sets root (the set folder, `notes.md`, `selection.json`, `dropped/`, the pool, `runs/<audit>/`
   with `PREFLIGHT.json`, `DECLARATION.json`, `USED`, the ledger), consistent with the path map's existing entry shape.
3. The ten refusal codes, one per S1 check, named and each with its condition in the KPI line's own words.
4. **Domain and subsystem by a fixed rule on the question's first source path** (a table: path prefix → domain; e.g.
   `docs/DECISION_REGISTER.md` → decisions, `.tickets/` → tickets, `src/gov/<x>/` → code:<x>, ...), derived from the
   writer brief's quota categories, so S1's spread and S2's "a drop leaves a domain at 3" are computable without a new
   question field. Say how a question whose first source matches no row is scored.
5. The declaration's keys, the exit codes (refused, void, used, ok) and the `void` cause codes.
6. The `--decision DEC-n` flag for a non-standard `retrieval.yaml` (S3).
Each item cites the KPI line it serves (S1-S5, F-lines). Checks: the front matter parses; the structural pass ok;
`gov brief lead DAEO-61vm --run tests` still builds (warnings only). Return the twelve fields, short. Estimate 45 min.
