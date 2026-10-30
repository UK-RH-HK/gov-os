# W2-87 design note (lead, 2026-10-30): retrieval ranks by authority; the register as its entries

Behaviour, not code. Sources: DEC-952 item 1, DEC-423, DEC-424, DEC-791 item 1, DEC-860, DEC-866, DEC-694, CAP-10.

## Part 1 — the register defect (its own test batch and engineer batch, first)

- **A chunk of the register** (the file the path map's `decision_register` names) **is the entry whose span holds it**, never the register as a whole. The entries, their ids, types and statuses come from the store's register records (W2-03: each decision its own record, with its heading and span); the entry's lines are where its stored span stands in the register file. A chunk belongs to the entry whose span holds the chunk's first line; a chunk before the first entry belongs to no entry.
- **An entry is not current** when its status is SUPERSEDED, it is the target of a SUPERSEDES edge, or its status is must-not-cite (DEPRECATED, REJECTED, WITHDRAWN; DEC-423).
- **The closure route:** a register chunk joins it when *its own* entry is in the closure, not when the register's last entry is.
- **The drops:** a register chunk is never dropped for another entry's status (today a register whose last entry by id is superseded loses every chunk). Leaving out superseded and done entries, with their count, is W2-55's (DEC-791 item 1); this ticket drops nothing new. Every other file's drops are today's.
- **One function** maps a register chunk to its entry; W2-55 reuses it.

## Part 2 — the authority order

**The configuration:** one top-level block of the path map; nothing in the code names a path, a record type or a tier.

```yaml
retrieval_authority:
  lift:
    fused: 0.004     # added per tier step to the fused (RRF) score, before the first call's cut
    rerank: 1.0      # added per tier step to the reranker's score, after the rerank
  default: middle    # the tier of a chunk no tier matches
  tiers:             # in order, highest authority first
    - name: governing
      records: [{type: decision, status: [ACCEPTED]}, {type: capability}]
      paths: ["docs/contract/**", "docs/charter/**", "docs/spec/**", "docs/adr/**",
              "template/governance/kernel/roles/**", "template/governance/kernel/skills/**"]
    - name: middle
    - name: reports
      paths: ["tests/**", "docs/assessment/**", "docs/audit/**", "docs/probes/**"]
```

- **Matching:** a path pattern is matched against the chunk's repository-relative path, whole: `**` crosses folders, `*` stays inside one name. A record rule matches the chunk's record (for the register, its entry; for any other file, the store's record of that path) by `type`, and by `status` when it names any (absent: any status).
- **A chunk in two tiers gets the lower one** (the less authority): a test or a report that also carries a record is never lifted by it.
- **A chunk whose record is not current is never above the default tier,** whatever it matches: a superseded entry gets no lift.
- **The lift:** tier at position `i`, default at `d`; the chunk's score gains `lift × (d − i)`: +lift above the default, nothing at it, −lift below. Before the cut, on the fused score; after the rerank, on the reranker's score (when the reranker gave scores; without them the gathered, already lifted, order stands). Both sorts are stable, so equal scores keep the order they came in (the fused order, then the rerank's), and two runs on one store give one bundle.
- **Bounded:** a lower-authority chunk whose score is better by more than the lift per step between them keeps its place.
- **The values proposed:** `fused: 0.004` is about the gap between a route's 1st place (1/61) and its 21st (1/81): a governing chunk just past a first call of 20 can enter it over a middle chunk, and against a report (two steps, 0.008) a governing chunk at a route's 21st place passes any report that route alone found; a chunk that both routes found (about +0.015) still keeps its place over one only a single route found. `rerank: 1.0` is one logit of the pinned reranker (its scores run from about −10 to +5; probed by the lead), close matches only.

**What stays:** what the bundle keeps and leaves out (W2-55's); the budget, batches, continuation, stopping reasons, parent expansion; DEC-424's failure and lesson records ahead of everything (moved after each lift); determinism. **With the block absent, the bundle is today's, item for item.**

**Fail closed:** the path map cannot be parsed, or the block is no mapping, has an unknown or missing key (`lift`, `default`, `tiers`, a tier's `name`, `paths`, `records`; a rule's `type`, `status`), a negative or non-numeric lift, two tiers of one name, no tiers, a `default` naming no tier, a status that is no single word (letters, digits, `_`, `-`; the store holds `ACCEPTED` and `closed` alike), or a pattern that is not a non-empty string: `CONFIG_INVALID`, naming the key. Never read as empty or as today's order. A path map that is absent: the block is absent.
