# ACT-QUIET-DENY-1 — refuse at once, never ask, in the quiet hours (DEC-991 item 4)

**Owner act:** add one `hooks` block to your local settings file, `.claude/settings.local.json` (untracked, yours;
the guard's tracked settings and their tests are untouched). Claude Code's own safety check asks before any edit of
a `.claude/` file, so this is yours to make.

## 1. Context
DEC-991: in the quiet hours the CTO never runs a command that could need your approval. The rule depends on the CTO
judging every command right; one misjudged call froze the session for 9 hours last night. You asked whether Claude
Code can refuse an unapproved command at once instead of asking.

## 2. What exists (checked in Claude Code's documentation and tested here)
- **The `PermissionRequest` hook** runs at the moment Claude Code is about to show a permission prompt, for ask-rule
  prompts (our `rm` and `owner-ping`) and the built-in safety checks, in the VS Code panel and headless. Its answer can
  be "deny, with a message the model reads", "allow", or nothing (the normal prompt appears). It runs before the
  prompt, so it never waits for you.
- **The hook:** `governance/project/orchestration/tools/permission_request.py` (standard library, about 50 lines).
  Between 02:00 and 07:30 it refuses with: "Quiet hours (02:00 to 07:30): this call needs the owner's approval, so it
  was refused at once and queued for the 09:00 morning package (DEC-991). Do not retry it or try another form of it;
  carry on with other work". It appends the call to `log/approval-queue.jsonl` for the morning package. By day it says
  nothing, so you get the normal prompt (after the CTO's ping, DEC-991 item 2). It logs every prompt it sees, by day
  too, so we learn which calls prompt. Any error inside the quiet hours still refuses. Local time (Europe/London, so
  BST is followed).
- **Tested:** at 01:59, 07:30 and 12:00: no answer (prompt as usual); at 02:00, 03:00 and 07:29: refused; bad input
  at 03:00 and an unwritable queue: still refused. **Live:** a throwaway headless Claude session with the clock forced
  to 03:00 ran `rm -rf <scratch>/nothing-here`; Claude Code called the hook, the call was refused with the message
  above, the model reported it and did not retry, and the queue file got the entry.
- **Other options considered:** the `dontAsk` permission mode refuses everything that would prompt, all day: it would
  also refuse what you approve by day through Remote Control (against DEC-991 item 2), and a mode cannot follow the
  clock. A PreToolUse rule in the guard's hook: it would need the guard's tracked settings and their tests changed.

## 3. Why it matters
It turns a 9-hour freeze into one refused call and a line in the morning package. The CTO's judgement becomes the
first line, not the only one.

## 4. Risks
- **If the hook itself cannot run** (python missing, a crash before it prints): with no answer, Claude Code shows the
  prompt, so the freeze could come back. The line below sets `"onFailure": "block"` (documented from Claude Code
  2.1.295; this machine runs 2.1.314) so a failed hook refuses instead; the cost is that by day a broken hook would
  also refuse what you would have approved (you would see refusals in the chat; no freeze). The dead-man's switch
  (ACT-DEADMAN-1) catches the rest.
- **A timeout:** set to 10 seconds; the hook takes about 50 ms.
- **Scope:** your local settings file applies to sessions started in the main tree, which is the CTO's session (and
  any session you start there). Leads run headless in their worktrees, where a call that needs approval is refused
  anyway; they are not affected.
- **What it does not cover:** a command that hangs without a prompt, or a session that stops for another reason (the
  dead-man's switch covers those); the AskUserQuestion box (forbidden to the CTO already).
- **A refused call is not lost:** it is in the queue with its command, for the 09:00 package.
- Threat model: honest mistakes in ordinary work (ADR-0001); the hook fails closed.

## 5. Recommendation (confidence: high)
Add it now. Undo is deleting the block.

## 6. What it blocks, and what waiting costs
Nothing waits on it; until it is in, a misjudged call in the quiet hours can still freeze the session.

## The change (merge the `hooks` key into the existing JSON of `.claude/settings.local.json`; keep `env` and `permissions` as they are)
```json
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/permission_request.py",
            "timeout": 10,
            "onFailure": "block"
          }
        ]
      }
    ]
  }
```
Check it: `python3 -c "import json; d=json.load(open('/home/usain/Dynamic-Agentic-Engineering-OS/.claude/settings.local.json')); print(list(d['hooks']))"` prints `['PermissionRequest']`. It takes effect in sessions started after the change (tell me and I will check it in a throwaway session with the clock forced to 03:00).
