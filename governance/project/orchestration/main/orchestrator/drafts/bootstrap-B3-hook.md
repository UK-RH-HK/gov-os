
## The pre-commit hook after B3: Wave 2 list, ranked high (2026-10-15; DEC-706, DEC-709)

- **The pre-commit tier holds only fast checks** (high). The first commit after the lefthook install was refused: `gov ci checks G1 G2` failed on index-freshness and recovery-rebuild, after 290 s, because the index was older than three tracked files. Until Wave 2 every commit runs `gov rebuild --no-embeddings` after staging (DEC-709). Fix: index-freshness and recovery-rebuild move to pre-push (G3) or CI; the commit-time re-index (CAP-17.b, a Wave 2 contract item) is built first, so no rebuild by hand is needed before a commit.
