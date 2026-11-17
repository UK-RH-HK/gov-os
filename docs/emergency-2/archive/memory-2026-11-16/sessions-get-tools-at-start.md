---
name: sessions-get-tools-at-start
description: CORRECTED 11-15 22:58: user-level ~/.claude/settings.json already allows Bash(*)/Read(*)/Edit/Write/Web* in acceptEdits; only reads OUTSIDE the session's folder ask; pre-allow one folder with --allowedTools 'Read(//abs/folder/**)' (tested)
metadata:
  type: feedback
---

**Corrected 2026-11-15 22:58.** I first claimed that a session started with plain `claude` in a kit-adopted repository asks on every Bash call. That was wrong. The user-level `~/.claude/settings.json` allows `Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`, `WebFetch(*)` and `WebSearch(*)`, with `defaultMode: acceptEdits`, for every session on the machine.

`Read(*)` and `Write(*)` cover the working directories only. So the one question an operator-started session meets is a read outside its own folder, such as the CTO's replies file. That is what stalled the W2-81 adopters.

**Fix (tested headless, 11-15):** add `--allowedTools 'Read(//<absolute folder>/**)'` to the start line. It is read-only, so it is narrower than `--add-dir`, which in acceptEdits mode would also open writes there. `operator_setup.py` prints these start lines.

**Why:** a session that stops on a permission question overnight loses the night, and my wrong claim caused needless restart advice.

**How to apply:** check `~/.claude/settings.json` before claiming what a session will ask. Give every interactive governed session's start line the scoped read allow for its replies folder. Related: [[w2-81-run-needs-session-and-kit]], [[wake-examin-cto-after-reply]].
