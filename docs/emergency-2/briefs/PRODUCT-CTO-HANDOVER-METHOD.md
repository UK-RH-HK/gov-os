# The handover method for a product's CTO (DEC-1253; from 26 November 2026)

For the EXAMIN and ASMO OS CTOs. It is the Gov OS CTO's method (`template/governance/kernel/templates/role-cto.md`,
"Take over" and "Hand over"), adapted to your own repository. Paths below are relative to **your** repository; "your
coordination ticket" is the ticket your checkpoints are recorded under (the one your `gov checkpoint` calls use today).

## Each evening, or before a restart: hand over
1. Write `docs/CTO-HANDOVER.md` in your repository (or the path your CTO notes already use; keep it one file):
   - the state: HEAD, the live gov (`gov --version`), date and time;
   - your progress (what is done, what is in flight, what waits);
   - what runs: leads, background runs, cron lines, your watcher, tmux sessions, and how to check each;
   - held branches with what each owes;
   - what waits on the owner, with links to the pages;
   - the next actions in order, with exact commands;
   - the traps of the day.
2. Record it: `gov checkpoint --ticket <your coordination ticket> --trigger stop --next "<first action>" --input docs/CTO-HANDOVER.md`, then commit both.
3. Start the fresh CTO in a new tmux session (Opus, high effort, `--remote-control`, `--permission-mode bypassPermissions`,
   `GOV_ROLE=orchestrator`), with a prompt that tells it to read your role card and the handover whole and take over by
   the checks below. The Gov OS start script is the model: `governance/project/orchestration/tools/start_cto.sh` in the
   Gov OS repository (change the repository path, the session name prefix and the files it reads).
4. Wait for its takeover message, then stop.

## Each morning, as the fresh CTO: take over before anything else
1. `gov checkpoint --resume --ticket <your coordination ticket>`: the handover's recorded sha256 equals the file's (`sha256sum`).
2. `git log -1` equals the handover's commit, or only commits it names came after.
3. `readlink -f ~/.local/bin/gov` and `gov --version` equal the live release the handover names (today 0.1.7).
4. `tmux ls` works; address every session by its exact name: `tmux send-keys -t "=<name>:0.0" -l "<text>"`, then `Enter`.
5. If you run a watcher, start it as a tracked background command (never `&`) and restart it after every event it reports; no heartbeat.
6. Every running item the handover lists exists (`ps`, the leads' `.exit` files, `crontab -l`), and nothing unlisted runs.
7. Read your inbox and your `REQUESTS.md` FINDINGS LOG; write your session id and your tmux name where your notes keep them.
8. Send the owner one takeover message: your progress, what you checked and its result, your first action. The outgoing
   CTO stops only after it. Tell the Gov OS CTO your new tmux session name (type it into `cto-<mmdd-hhmm>`, the name in
   Gov OS's `.gov-runtime/scratch/orchestrator/log/cto-tmux.txt`), so findings reach the right session.

## What you read first, every morning (whole, never cut: long files in consecutive pages with the Read tool, never `head`, `tail` or a pipe)
Your CLAUDE.md and AGENTS.md (the golden rules at their head); your role card or brief; your handover; the decisions it
names; your Contract and plan where the handover says; then memory for your first action: `gov retrieve "<question>"`,
read every item, then search again once in your own words.
