# Brief: independent test designer, DAEO-qzrq (W2-123) run 2, STANDARD — revise the query server's GPU cases (DEC-1033)

You are a fresh independent test designer (MR-3). Ticket: DAEO-qzrq (W2-123), profile STANDARD, run 2. You work only
in the worktree `/home/usain/gov-os-worktrees/W2-123-tests` on branch `w2/W2-123-tests` (DEC-963). You never read or
write the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-123`. The owner's DEC-1033 (an emergency decision)
replaces DEC-798: the query embedder may run on the GPU, and the Gov OS starts the query server with the GPU visible.
Run 1's acceptance tests still enforce the hidden GPU. You revise exactly those expectations, lowering nothing else,
and map them to the ticket's KPI lines as they now stand. Keep it small.
