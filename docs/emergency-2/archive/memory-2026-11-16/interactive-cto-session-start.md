---
name: interactive-cto-session-start
description: starting a product CTO as a tmux --remote-control --resume session: trust prompt first time, tmux wake needs a 2nd Enter, the SendMessage name is folder-derived (rehearsed 11-16)
metadata:
  type: reference
---

Rehearsed 11-16 for P-EXAMIN-LEAD-1 (b) on a scratch session (drafts/examin-lead/REHEARSAL-b.md): `tmux new -d -s <name> 'cd <repo> && claude --remote-control "<label>" --resume <headless session id> --settings ...'` resumes with context and shows in the app. Three things to handle: (1) the first interactive start in a folder shows the workspace-trust prompt (default "No, exit"): capture the pane and accept once (Down, Enter); (2) a tmux `send-keys "<text>" Enter` wake types the text but the first Enter is swallowed: send Enter again and check the pane; (3) ListAgents shows the session under a folder-derived name (e.g. repo-e9), not the --remote-control label: read it after the start and write it to a name file the waking side uses. Related: [[wake-examin-cto-after-reply]].
