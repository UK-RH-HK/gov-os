# P-PING-1: a ping that does not stop the CTO's work while it waits for you (P1, it changes DEC-855)

For the owner (DEC-971, "bring me a way to ping me that doesn't stop your work").

## 1. Context
- Today a ping is `~/.local/bin/owner-ping "<line>"`. The script only appends the line to `~/.config/gov-os-notify/pings.log`.
- Your user settings (`~/.claude/settings.json`, the `ask` list, lines 19 to 22) make every call of it a permission request. That request is what reaches your phone. DEC-855 made this the way, and DEC-945 forbids a paid notifier or an app install.
- A permission request stops the session that asked until you answer it.

## 2. What happened
- The ping of 04:05 waited until 11:46.
- In that time, the 05:37 investigation, the 07:30 morning package and thirteen lead returns waited too.
- Leads and closes kept running, because they are other processes. Only the CTO stopped.

## 3. Why it matters
Every ping stops the CTO until you answer, at night most of all, and the cost grows with each lead running.

## 4. Options
- **(a) Recommended: Claude Code's own notification, which does not wait.**
  - This session has a built-in `PushNotification` tool. It sends a desktop notification and, when Remote Control is connected, a push to your phone. It returns at once, needs no answer, and costs nothing (no install, no service).
  - The ping becomes: write the line to `pings.log` with a plain logging command that is not on your `ask` list, then send `PushNotification` with the same line.
  - **Two limits:**
    - It skips the notification when you are at the terminal, since you then see the message anyway.
    - It reaches your phone only while Remote Control is connected.

    So the tool's answer ("sent" or "not sent") is written beside each line in `pings.log`. A P1 whose notification was "not sent" while you are away is repeated at your next active moment, and always appears in the next morning package.
  - **The change:** DEC-855's ping step in the prompt §7, the RESUME HERE notes and `owner-ping` (it keeps writing the log; the ask rule stays on your side, unused, so you can switch back at once).
  - **First, a test while you are away from the terminal:** one notification ("test: a non-blocking ping"), to confirm it reaches your phone.
- **(b) Keep `owner-ping` with its ask rule, but call it from a helper session,** so only the helper waits. This is cheaper to change, but a helper's permission request may still hold the parent session until it is answered (not measured), and it adds a session per ping.
- **(c) An outside push service** (for example ntfy.sh, free). It needs an app on your phone, so it is an install under DEC-945, and it sends the ping's text to a third party.
- **(d) No pings at night:** P1s wait for the 07:30 package (already my rule since this morning), and daytime pings stay blocking. This fixes the night but not the day.

## 5. Recommendation
**(a), plus (d) at night, confidence medium-high.** The one unknown is whether Remote Control is connected when you are away; the test answers it.

## 6. What it blocks, and what waiting costs
- **Blocks:** nothing.
- **Waiting costs:** each daytime ping stops the CTO until you answer, typically minutes, and at night hours (now avoided by (d)).
- **Until you decide:** I use `owner-ping` by day only when the item needs you that day, and hold night P1s for the morning package.
