---
name: rename-defeats-link-checks
description: "a same-user mv brings a secret into a sandbox's read set with nlink 1; name/link-count checks don't cover it; judge by content index or freeze+show (job runner r9, 11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T05:39:53.779Z
---

Job runner round 9 (11-16 05:4x): I decided Option A (freeze yes-gated may_read) plus B3 (refuse nlink>1) and thought in-reach leaks were closed. The fresh review showed a plain `mv ~/.ssh/key ~/notes/readme.txt` keeps nlink 1, so a routine job with live may_read returned the key (and held-out text), before or during the run. Symlink checks done on the target text (lexical) were also beaten by `a -> .` chains. The builder's own test copied opcommon.py from the LIVE operator folder (a DEC-1196 (5) breach in a test).

**Why:** the CTO and the runner are the same Unix user; only the guard separates them, and it lets through writes it cannot resolve. Any check on names, paths or link counts can be renamed around.

**How to apply:** for any sandbox/allowlist design I decide, ask "what if the queueing agent mv's a protected file into reach first, or mid-run?" Require a rename-proof test (a cumulative content-hash index of protected bytes + inode match) and show the owner the frozen file list behind a yes. Resolve symlinks step by step against the recorded tree, never lexically. Check every test file for live-path reads before it runs. Related: [[no-rehearsal-against-live]].

**Session sandbox (B), 11-16:** the same lesson the other way round: what a sandboxed agent may WRITE that an outside same-user process later RUNS is an escape (.git/config core.fsmonitor and hooks, ~/.claude/settings.json), and shared ~/.claude transcripts and /tmp task folders leak held-out text. A wall must cover reads of everything mounted AND writes that outside processes execute; mask folders, not files (an outside mv over a masked file is seen).
