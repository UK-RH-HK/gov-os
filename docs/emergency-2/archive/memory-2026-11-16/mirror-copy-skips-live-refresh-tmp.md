---
name: mirror-copy-skips-live-refresh-tmp
description: "copying a live store half for a rehearsal mirror races the live hook's refresh (rebuild/seed.tmp vanishes under cp -a); exclude it (11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T05:45:57.119Z
---

On 2026-11-16 05:43 the 0.1.1 re-pin rehearsal (drafts/repin-rel-0.1.1/rehearse_rel.sh, copied from 0.1.0's) stopped in the mirror step: `cp -a W2-00-store-b/.gov-runtime/rebuild` failed because the live reference-transaction hook was rebuilding that half after a commit, and `rebuild/seed.tmp/store.db-journal` vanished mid-copy.

**Why:** the halves are live; any commit on w2/integrate (the CTO's, a fork's, a land) starts a refresh of the spare half. 0.1.0's rehearsals ran in quiet hours and never hit it.

**How to apply:** when mirroring a live store half, copy `codeintel`/`rebuild` with `tar --exclude=rebuild/seed.tmp` (the SQLite DBs by `.backup`), or wait out the refresh lock. Related: [[no-rehearsal-against-live]].
