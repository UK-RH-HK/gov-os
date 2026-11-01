# ACT-PUSH-INPUT-1 — turn on "Push when actions required" (DEC-998 item 2)

**Where it is:** not in the VS Code panel. The menu item is in the command-line Claude Code's `/config` (in a
terminal: `claude`, then `/config`), shown only while Remote Control is on and only where Anthropic has switched the
item on for the account; that is why you do not see it. Its value is a key in the user settings file,
`~/.claude/settings.json`, beside `agentPushNotifEnabled` ("Push when Claude decides", already `true` there):

- **Key:** `inputNeededNotifEnabled`
- **Value:** `true`
- **What it does** (Claude Code's own description of the key): "Push to mobile when a permission prompt or question is
  waiting". When a Remote Control session connects, Claude Code sends it to Anthropic's notification preferences
  (as "code requires action: enable push"); from then on a waiting permission prompt or question in that session
  pushes to your phone, where you can answer it.
- **Found in:** Claude Code 2.1.314's own code (its settings schema and its `/config` menu); the documentation names
  the menu item but not the key.

## The change (your operator; a plain terminal or a Claude session; my session may not edit a `.claude/` path)
```
python3 - <<'EOF'
import json, pathlib
p = pathlib.Path.home() / ".claude/settings.json"
d = json.loads(p.read_text())
d["inputNeededNotifEnabled"] = True
p.write_text(json.dumps(d, indent=2) + "\n")
EOF
```
## The check
```
python3 -c "import json,pathlib; d=json.loads((pathlib.Path.home()/'.claude/settings.json').read_text()); print(d.get('inputNeededNotifEnabled'), d.get('agentPushNotifEnabled'), d.get('remoteControlAtStartup'))"
```
It prints `True True True`. It takes effect in sessions started after the change (tonight's fresh session and the
sentinel). **The live check:** the fresh session, at its start, runs one command that needs your approval (I ping
first, DEC-991), so a permission prompt waits; you should get a push for it on your phone, and you can approve it
there. I will tell you just before.

## Risk
A push for every prompt by day, from any of your Claude sessions with Remote Control (the leads run headless and
have no prompts). At night, the quiet-hours hook refuses a prompt before it shows, so no night pushes from it.
Undo: set it to `false`.
