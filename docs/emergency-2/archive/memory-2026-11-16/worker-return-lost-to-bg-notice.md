---
name: worker-return-lost-to-bg-notice
description: "a launched worker's background Bash job can end after its return, so its last message (the log's result) answers the notice; recover the return from its transcript jsonl"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d6bb0738-e41f-4fde-b443-dfe5667b507a
  modified: 2026-11-16T06:28:49.509Z
---

W2-189 td-1 (2026-11-16): the test designer started a background pytest that timed out at the heavy-slot gate after it returned. The session's final `result` in td-1.json was its answer to that notice, not the twelve-field return. The full return was the last long assistant text in `~/.claude/projects/-home-usain-gov-os-worktrees-<W2>-tests/<session id>.jsonl`.

**Why:** only the last message is read, so the return looked missing although the worker had finished.

**How to apply:** when a worker's log result is short or off-topic, pull the last long assistant text from its transcript before resuming the worker. Briefs should say: no `run_in_background` for pytest, or stop every background job before returning. Related: [[copy-td-logs-before-worktree-remove]], [[pytest-through-heavy-slot]].

Recurred W2-189 en-1 (11-16) although the brief said "never a background pytest": the heavy slot queued past the 10-min foreground limit, so the engineer backgrounded its suites and its last message answered a stale waiter's notice. Transcript path for a lead-tree worker: ~/.claude/projects/-home-usain-gov-os-worktrees-<W2>/<session>.jsonl. Briefs: "a background job must be stopped or awaited before your return; your return is your last message".
