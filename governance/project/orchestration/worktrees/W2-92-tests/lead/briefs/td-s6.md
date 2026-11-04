# W2-92 (DAEO-n0wb): independent-test-designer, the DEC-1065 round (D-4b; launched by the CTO, no lead)

Your worktree is `/home/usain/gov-os-worktrees/W2-92-tests`. Read and follow
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md` (the common
rules, its "Test designer" paragraph), with ticket id `DAEO-n0wb`.

**Your KPI line this round:** S6 (a plain question costs about one second, DEC-1065 (4)), as the ticket states it.

Facts for your cases (from the integrated code): `graph_route.start_ids` (`src/gov/retrieval/graph_route.py:80-93`) parses the front matter of ~840 records with the pure-Python YAML loader (`:55`) in every process (2.9 s here; the C loader 0.34 s); the store drops the title it parses at rebuild (`store/loader.py:281`). S6's time figure is the CTO's (measured on the shared servers); your cases test what a test can: in a planted project with many records, the record route does not read every record's front matter per process (count the reads, or time it against a bound that the old code fails), the titles come from the store after a rebuild, and S1's record route answers as before (S4: nothing else changes in the bundle).
