# ACT-PUSHOVER-1 — Emergency pushes to the owner's phone through Pushover (DEC-939 item 7)

From: the W2 orchestrator, 2026-10-29. Your acts: the account, the application and its token (on the Pushover site and your phone), and one file on this machine. No install: `curl` is already here.

## What it is for

Only DEC-938 item 6's emergencies:
- a secret exposed;
- a risk of losing data or history;
- the disk below its floor;
- the guard failing open.

Everything else stays in the morning package and its one 07:30 ping. Today the nightly pushes when the disk gate shuts at night; my session pushes for the others when it finds one and you are not active.

**Each message** is one status line of at most 120 characters (for example "Gov OS emergency: the disk is below its floor; the nightly did not start"):
- no code, no path, no secret;
- the script replaces any other line with "Gov OS emergency: see the morning package";
- every attempt is logged to `~/.config/gov-os-notify/pings.log` as an `EMERGENCY` line, never with the token.

**The sender** (`governance/project/orchestration/nightly/push_emergency.sh`):
- it is committed and reviewed with its tests (`test_nightly.sh` P1 to P6);
- two mutation checks show the tests catch a removed file-mode check and a removed message filter;
- it hands the token to curl on standard input, never on a command line.

## Your acts

1. On pushover.net: an account (or your existing one); install the Pushover app on your phone and log in. Note your **user key**.
2. On pushover.net, "Create an Application/API Token": name it "Gov OS"; note its **API token**.
3. On this machine, in a plain terminal (not a Claude session: the token must not pass through a session):
   ```
   mkdir -p ~/.config/gov-os-notify && chmod 700 ~/.config/gov-os-notify
   umask 077 && printf 'PUSHOVER_TOKEN=%s\nPUSHOVER_USER=%s\n' 'YOUR-API-TOKEN' 'YOUR-USER-KEY' > ~/.config/gov-os-notify/pushover.env
   chmod 600 ~/.config/gov-os-notify/pushover.env && stat -c '%a %n' ~/.config/gov-os-notify/pushover.env
   bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/push_emergency.sh "Gov OS test push: please ignore"
   tail -1 ~/.config/gov-os-notify/pings.log
   ```
   Replace the two quoted values with yours. Before running it, clear the line holding them from your shell history (for example, start the line with a space if your shell ignores such lines, or run `history -d` afterwards).

## What to see

- `stat` prints `600 /home/usain/.config/gov-os-notify/pushover.env`.
- Your phone shows "Gov OS test push: please ignore".
- The last line of `pings.log` reads `... EMERGENCY pushed: Gov OS test push: please ignore`.

## Where the token lives

`~/.config/gov-os-notify/pushover.env`, outside every repository and every worktree, beside `pings.log`:
- only the sender script reads it, to send; I never read it, print it or copy it, and no brief names its contents;
- it is not in the index's namespaces, and the secrets check never scans it (it is outside the tree).

## Rollback

`rm ~/.config/gov-os-notify/pushover.env`: the script then sends nothing and logs "not pushed".

## Then

Tell me the test push arrived. I record it in the register; from then on the emergencies are pushed at once.
