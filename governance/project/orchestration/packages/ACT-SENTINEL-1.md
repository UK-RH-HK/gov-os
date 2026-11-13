# ACT-SENTINEL-1 — the dead-man's switch through the Claude app alone: a sentinel session (DEC-998)

## 1. Context
You ruled: Claude only (no ntfy, no other app, no email); "Push when actions required" on (yours, in `/config`);
every fresh CTO session confirms its Remote Control link and sends one test push at its start; the dead-man's switch
must reach your phone through the Claude app. Cron cannot: a headless `claude -p` has no Remote Control link (tests
1 to 3 today: "Not sent — this terminal is active", every time). Test 4, from a live interactive session with Remote
Control, reached your phone; today's earlier misses were the presence rule (pushes are skipped while you are focused
on the connected terminal), not a broken link.

## 2. The option: a sentinel session
A second, small interactive Claude Code session, started with Remote Control (`claude --remote-control "CTO
sentinel"`) inside `tmux` so it keeps running with no window open. Its brief
(`governance/project/orchestration/tools/sentinel-brief.md`) gives it one loop:
- it runs `deadman.py --watch` in a background Bash run; that script looks at the CTO's session every 2 minutes
  (entry types and times only, never their text) and exits only (a) on a stall, printing the alert line, or (b)
  after 110 minutes, printing a heartbeat (the Bash tool's background runs end at 2 hours);
- on a stall it calls PushNotification with the alert line, e.g. "P1 DEADMAN | the CTO session is waiting on a tool
  (Bash; likely a permission prompt) since 01:46, 133 min | approve or restart it"; on a heartbeat it re-arms silently;
- the stall rule is as tested today: over 60 minutes since the CTO's last action (inside 02:00 to 07:30, over 2
  hours); one alert per stall, a reminder every 2 hours while it lasts.
- **Which session it watches:** the one named in `log/cto-session.txt`; each fresh CTO session writes its own id there
  at its start (so the sentinel never watches itself or a throwaway session). Tested: 7 unit tests, the watch's
  stall and heartbeat exits included.
- **Why its pushes arrive:** its "connected terminal" is the tmux pane nobody looks at, so the presence rule does not
  hold its pushes back (unlike the CTO's own, which are skipped while you are at that panel).

## 3. Cost
- No model use while it waits (a background run costs nothing). One short turn per heartbeat (about 13 a day) and
  one per alert. Each turn re-reads its cached context (Claude Code's own system prompt and tools, roughly 100 to 130
  thousand tokens, mostly cache reads) plus a few hundred new tokens.
- **Estimate:** on Sonnet 5.5, about 1 to 2 USD a day; on Haiku 5.5, well under 1 USD a day (the headless Haiku calls
  today cost 0.11 USD each including the cache's first write). Measured in the first day, and reported in the
  morning package. It counts against your plan's usage like any session.

## 4. Risks
- **The sentinel itself stops** (a crash, WSL restart, the PC asleep): no alert comes. Mitigation: the CTO checks the
  sentinel's last heartbeat (`log/deadman.log`, under 2 hours old) at every resume and in the morning package, and
  pings you by day if it is gone. If both stop at once (the PC down), nothing can alert: there is no cloud side.
- **Its Remote Control link drops** (after about 30 minutes without the server, e.g. a network change): its pushes
  then go nowhere and it cannot tell. Mitigation: it sends one push a day at 09:05 ("CTO sentinel alive"), so a missing
  one tells you; a dropped link is restored by typing `/remote-control` in its tmux pane (`tmux attach -t cto-sentinel`).
- **A false alert when the CTO is idle by design** (e.g. standing by for you, or tonight between the handover and the
  fresh session): the CTO writes `log/cto-standby.txt` with its reason while it stands by, and the switch stays quiet
  while that file exists (added before it starts).
- **It could freeze on a prompt:** it runs one allowed command and PushNotification only; started in the main tree, it
  is covered by the quiet-hours hook at night.
- **It is a second session on your account** and appears in the Claude app's session list ("CTO sentinel").
- Threat model: honest stalls, not an adversary (ADR-0001). It reads the CTO's transcript for times and entry types only.

## 5. Recommendation (confidence medium-high)
Start it tonight with the fresh session: Haiku 5.5 (cheap, the job is mechanical), the daily 09:05 alive push, the
standby file, the CTO's heartbeat check. Trial for two days, then I report its cost and any false alerts.

## 6. What it blocks
Nothing. Until it runs, the quiet-hours hook and "Push when actions required" cover the freeze case; a hang without a
prompt is caught only when you next look.

## The commands (a plain WSL terminal, or your operator)
```
tmux new -d -s cto-sentinel 'cd /home/usain/Dynamic-Agentic-Engineering-OS && ~/.local/bin/claude --remote-control "CTO sentinel" --model claude-haiku-5-5 --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"DAEO-sdxk\"}}" "$(cat governance/project/orchestration/tools/sentinel-brief.md)"'
tmux ls                               # shows cto-sentinel
tmux attach -t cto-sentinel           # to look (Ctrl-b then d to leave it running)
```
Stop it: `tmux kill-session -t cto-sentinel`.
