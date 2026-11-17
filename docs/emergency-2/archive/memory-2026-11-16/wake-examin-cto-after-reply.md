---
name: wake-examin-cto-after-reply
description: after every REPLIES.md edit, wake the EXAMIN CTO with tmux send-keys -t examin-cto 'Read the replies file and continue.' Enter (owner 11-15)
metadata:
  type: feedback
---

The EXAMIN CTO, in tmux session `examin-cto`, does not wake on its own when the replies file changes. The owner's rule (2026-11-15 21:5x): after every reply I write, wake it with one line, and tell the owner if anything refuses it:
`tmux send-keys -t examin-cto 'Read the replies file and continue.' Enter`

**Why:** it sat idle after the F-011 interim, waiting for a replies file it never re-read.

**How to apply:** edit REPLIES.md with the Edit tool, then send that line. Check first that my own session is not `examin-cto` (mine is `cto`). Related: [[check-own-tmux-before-paste]].

**Before a send-keys wake (11-15 23:00):** capture the pane first (`tmux capture-pane -p -t <s> | tail -4`). If it shows a trust screen ("Yes, I trust this folder") or a permission question (numbered options, "Esc to cancel"), do not send. Enter would pick the highlighted option, and on a trust screen that is "No, exit". Tell the owner it is waiting instead. The same rule covers the w281-* sessions.

**A wake sent while the session was busy may be lost (11-15 23:3x).** Afterwards the input box can show `❯ Read the replies file and continue.` in grey. That is Claude Code's suggestion, not typed text, so Enter or C-m on it does nothing. Send the full line again once the session is idle, then confirm that the pane shows the session working (or an empty `❯`).

**Headless resume (11-16 00:32):** the adopters read only the part of the replies file they have not seen, often the end (`sed -n 36,300p`). A section I insert near the top is missed: legacy-docs and secret-history replied "nothing new". Resume with `adopter.sh resume <name> "<message naming the new section and its line>"`. Never `mv` a glob of inbox items: file only the items I have read, by name. My 00:31 glob swept rust-workspace's unread item.

**CHANGED 11-16 15:2x (DEC-1200 (b)):** EXAMIN's CTO is now an INTERACTIVE session in tmux `examin-cto` with Remote Control ("EXAMIN CTO", visible in the owner's app), resumed from the headless session 9d3404b0. Its cross-session name is in `.gov-runtime/scratch/orchestrator/examin/cto-name.txt` (today `examin-5b`). Wake it after each REPLIES.md section with SendMessage to that name, naming the section; fallback `tmux send-keys -t examin-cto '<text>' Enter` then a second `Enter` (the first is swallowed), and check the pane. Do NOT use tools/adopter.sh resume for it any more (one session per CTO).
