---
name: check-own-tmux-before-paste
description: "before pasting into or killing a tmux session by name, run tmux display-message -p '#{session_name}' to see whether that session is this one"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-14T22:52:53.214Z
---

On 2026-11-14 the handover steps ("paste into tmux cto, watch it, then kill cto-old") reached the new CTO session itself, which runs in tmux session "cto". The paste came back into this session as a mid-turn message, and the "new session" being watched was me.

**Why:** a tmux target named in a step may be this session. Pasting into it loops back, and killing by name could end the wrong CTO.

**How to apply:** before any tmux paste-buffer, send-keys or kill-session by name, check this session's name (`tmux display-message -p -t "$TMUX_PANE" '#{session_name}'`). If it matches the target, stop and tell the owner before going on. Related: [[waits-by-pid-only]].

**tmux carries the CTO identity (11-15 17:37):** the tmux server's global environment holds GOV_ROLE=orchestrator, GOV_TICKET=DAEO-sdxk and GOV_DEV_TIERS from the session that started it. Every `tmux new` inherits them. Any session started in tmux for another repository needs `env -u GOV_TICKET -u GOV_DEV_TIERS -u GOV_ROLE` plus its own identity in the command. My EXAMIN message 4 missed it.
