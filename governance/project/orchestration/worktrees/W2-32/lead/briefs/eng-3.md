# W2-32 engineer, round 2: gov accept, then S10 (the CTO)

The CTO merged into `w2/W2-32` outside the sandbox: the designer's round-2 tests (`35b0fb74`: the map in full node ids,
S3's hidden-miss rule, S10's cases; other tickets' cases pinning their stand-in's digest) and today's integration head
(`2bc918f1`: the ticket's S10 line, DEC-1065). Do not merge yourself. Same rules as before (no `gov retrieve`, no real
model, no scoped set).
1. Run `gov accept W2-32 --json`. S1 to S5, S9 and F1 should now pass; S10 is red until built. **The CTO's ruling
   P-W2-32-5:** a hidden-half miss is recorded by its **id only**, strictly: no root cause, no repair, no free text either
   (free text about a hidden miss could carry its gold path or wording); keep your strict refusal as it is.
2. Build **S10** (the ticket's line and the CTO's notes in your earlier message: `ensure_*` a health check only with a
   named unavailable; only an explicit restart of the shared servers starts one; the GPU the only device; a CPU vector
   refused, never cached or stored; a rebuild refuses to embed on the CPU), with unit tests (stand-ins), in its own
   commit. Expect other tickets' stand-ins that report the CPU (`size_vram: 0`, e.g. W2-123's and W2-122's) to fail: name
   them; a test designer revises them (P-W2-32-4).
3. Run `gov accept W2-32` again; update the evidence file (S10's row); commit; return the twelve fields with the `ps` check.
