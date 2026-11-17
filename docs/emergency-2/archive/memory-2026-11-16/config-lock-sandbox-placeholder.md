---
name: config-lock-sandbox-placeholder
description: "a zero-byte read-only .git/config.lock is gov launch's sandbox placeholder while sandboxed workers run; never remove it live; \"could not lock config file\" on branch -d is then harmless"
metadata:
  node_type: memory
  type: reference
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-14T23:35:04.044Z
---

`gov launch`'s sandbox mounts a zero-byte, mode 0444 `.git/config.lock` in the main repository while sandboxed workers run, so they cannot write `.git/config`. While it is there, `git branch -d` and `git worktree remove` print "could not lock config file .git/config", but the branch and worktree are still removed; only the config write is skipped. Check with `grep <branch> .git/config`.

Never `rm` it while workers run: the guard refuses the rm anyway (catastrophic-delete rule). If one stays with no workers running (as on 11-14 at 14:08), it goes to the owner's operator as a one-line rm. Seen again 2026-11-14 23:33 when W2-111's workers started. Related: [[waits-by-pid-only]].
