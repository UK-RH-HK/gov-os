# W2-13 (DAEO-zqvn): engineer, the DEC-1065 round (D-4b; launched by the CTO, no lead)

Your worktree is `/home/usain/gov-os-worktrees/W2-13`. Read and follow
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md` (the common
rules, its "Engineer" paragraph), with ticket id `DAEO-zqvn`.

**Your KPI line this round:** S5 (search respects role separation, DEC-1065 (2)), as the ticket states it.

Where it goes (from the CTO's survey): the filter at `src/gov/retrieval/retrieve.py:159`, where the chunk list is built (every route funnels through it: `:169`, `:175`, `:227`), and in `src/gov/context/supplementary.py:55`; the matcher as a product module `src/gov/guard/role_paths.py` built from `.claude/hooks/role_reads.py`'s logic (`section`, `expand`, `Judge`, `judges`, lines ~95-137, ~395+, ~439-490, ~843-891; it uses `gov.guard.reads`), keyed on `GOV_ROLE` (or `--role`) and `GOV_TICKET` (as `measure.py:70-73` reads them); `--role` is parsed at `src/gov/cli/main.py:130` and unused today. Do not change the hook (`.claude/hooks/` is the owner's, an ACT): the product module is new and the hook may reuse it later. What is filtered is named in the bundle (count and rule), never dropped silently. W2-32 is changing `semantic.py`, `rerank.py`, `fusion.py` and `ollama.py` in parallel: keep out of those files.
