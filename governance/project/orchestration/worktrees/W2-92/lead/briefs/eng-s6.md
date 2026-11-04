# W2-92 (DAEO-n0wb): engineer, the DEC-1065 round (D-4b; launched by the CTO, no lead)

Your worktree is `/home/usain/gov-os-worktrees/W2-92`. Read and follow
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md` (the common
rules, its "Engineer" paragraph), with ticket id `DAEO-n0wb`.

**Your KPI line this round:** S6 (a plain question costs about one second, DEC-1065 (4)), as the ticket states it.

Where it goes (from the CTO's survey): `graph_route.start_ids` (`src/gov/retrieval/graph_route.py:80-93`) parses ~840 records' front matter with the pure-Python loader (`:55`) in each process: 2.9 s; the C loader (`yaml.CSafeLoader`) 0.34 s; the store already parses each front matter at rebuild (`src/gov/store/loader.py:271`) and drops the title at `:281` (now in your paths): keep the titles in the store (a schema change: say what rebuild it needs and whether old seeds are refused, `rebuild/seed.py:67`), and use the C loader where a parse remains. Target: a cold `gov retrieve` plain question in about 1.2 s at the median (the CTO measures it on the shared servers; you time your change with stand-ins only). W2-32 is changing `semantic.py`, `rerank.py`, `fusion.py`, `ollama.py` and W2-13 `retrieve.py` in parallel: keep out of those files.
