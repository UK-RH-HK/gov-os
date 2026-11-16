# P-EXAMIN-LEAD-1: the EXAMIN CTO leads EXAMIN's Wave 0; reachable from your app; the channel between the CTOs and the operator

Drafted 2026-11-16 14:0x for the owner (to be recorded with DEC-1199 once the 0.1.1 hold ends). It follows your
message of ~13:4x: the EXAMIN CTO leads EXAMIN's Wave 0 (the audit, the specs, the refactor) governed by Gov OS; the
Gov OS CTO works on Gov OS only; the CTOs talk to each other and to the operator, where every CTO's action runs; you
talk to each CTO directly in the app. P-EXAMIN-WAVE0-1 is withdrawn.

## (a) The EXAMIN CTO's new brief
File: `drafts/examin-lead/EXAMIN-CTO-wave0-brief.md`, sha256 `0d96110c5d76f775d555f7a59e0ac12de0ce3b5d5016b354ce6278c0d38fd9b0`.
In short (the file is the brief, word for word):
- **Role:** leads EXAMIN's Wave 0 in the copy, owns EXAMIN's specs, tickets and escalations to you, governed by Gov OS
  (the product only, its guard, walls and close rules). The freeze is lifted for this work.
- **Order:** (1) the target layout under the path map (test folders under `tests/`, product docs indexed), approved by
  you; (2) the full audit: every file and folder, alive or not (imported, called, referenced, read; last change;
  superseded by what), working or not (tests per module, code with no tests, core flows end to end), a disposition
  (keep, rename, relocate, merge, archive, delete) with its destination; (3) the spec audit: specs built, partly built
  or not, tickets done or not by wave, specs without code, code without spec; every gap asked of you; (4) an
  independent auditor checks the dispositions, you approve them by group, nothing moves before; (5) the refactor
  tickets: characterization tests first, the restructure, the code in slices behind tests, the memory build, a fresh
  question set after it, 95 % or better on the hidden half run by your operator; W2-28's verdict after the refactor.
  0.1.1 is re-installed in the copy before step 5, on your line.
- **Asks you:** every spec gap, the layout, the dispositions by group, costs and installs. **Asks the Gov OS CTO:** a
  product defect or gap as a finding with evidence, never a workaround. **Asks the operator:** anything needing your
  permissions (ticket fields `tk` cannot write, installs, commits outside its rights), each order naming it, run after
  your yes typed in the operator's session where a yes is needed (FREE-HAND D1).
- **Hard rules:** held-out and hidden material never read; walled writer and hidden half as W2-94 and W2-15a; customer
  data never copied (synthetic fixtures); no install or apply against a live path while rehearsing; the first brief's
  walls (held-out.yaml, settings, hooks; no push, tag or sudo).
- **Stops** at each step for its check, on your word, or after two refusals of the same action.
- It takes effect once W2-27's run is closed (the LITE ticket, items 13, 14, 16 reported).

## (b) Reachable from your app, still woken automatically
Today the EXAMIN CTO runs headless (`claude -p --resume` through `tools/adopter.sh`), so the app cannot see it.
Proposed: one long-lived interactive session in tmux with Remote Control, started as the Gov OS CTO and its sentinel
are (their live start lines: `claude --remote-control CTO --add-dir … --settings {"env":{"GOV_ROLE":…}}`):
```
tmux new -d -s examin-cto 'cd /home/usain/gov-os-runs/W2-27/examin && env -u GOV_DEV_TIERS ~/.local/bin/claude --remote-control "EXAMIN CTO" --resume 9d3404b0-5a77-4cb2-8941-3562eb4d934e --settings "{\"env\":{\"GOV_ROLE\":\"orchestrator\",\"GOV_TICKET\":\"exa-dt1z\"}}"'
```
- It keeps today's session and context (`--resume` of the headless session id); it compacts as any long session does,
  and its checkpoint is its reports plus `REPLIES.md`/`REQUESTS.md`.
- **Woken automatically** by a cross-session message naming the new section to read, sent the way the dead-man watch
  wakes the Gov OS CTO (`governance/project/orchestration/tools/deadman.py`: a headless `claude -p` limited to
  `ToolSearch,SendMessage`, `--setting-sources user`, from a private folder, to the session's name); tmux `send-keys`
  stays the fallback. Its name goes in a file like the Gov OS CTO's `log/cto-name.txt`.
- The headless runs stop (`adopter.sh` keeps its registry for the record); one session per CTO.
- **Inside the box (B), when it is live:** started by `session_start.sh --scope tree` with the copy as its writable
  root. The box masks `/run/user/<uid>`, where the cross-session sockets live (`/run/user/1000/cc-socks/`), so the
  wake is not proven there: the box must bind `cc-socks` (or a per-session socket folder) for SendMessage to reach the
  session, and the review of (B) must check that a boxed session cannot use those sockets to drive an unboxed one.
  Until that is proven, tmux `send-keys` from outside is the wake (the box has no tmux control from inside; the outside
  can still type into it).

## (c) The minimal channel
The same for every repository (DEC-1195's row: one operator, one CTO per product).
| From → to | Durable text (append only, dated sections) | Wake |
|---|---|---|
| Gov OS CTO → product CTO | `<orchestrator>/<product>/REPLIES.md` (today `examin/REPLIES.md`) | SendMessage to the product CTO's name, naming the section; tmux fallback |
| product CTO → Gov OS CTO | `<product copy>/.gov-runtime/scratch/govos/REQUESTS.md` (new) | SendMessage to `log/cto-name.txt`'s name |
| any CTO → operator | an order in the operator's `queue/` naming the requester; an order needing your yes waits for it, typed in the operator's session (D1) | the operator's own tick |
| operator → CTO | the order's result file and an inbox line | the CTO's inbox waiter |
| you → any CTO | the app, in that CTO's session | — |
- Who asks whom: a product CTO asks you (product decisions, spec gaps), the Gov OS CTO (product findings) and the
  operator (permissioned actions); the Gov OS CTO asks a product CTO to act or answers its findings, and asks the
  operator; the operator acts only on orders and your yes.
- How you see it all: each CTO in the app; the morning digest lists every request and order of the day by CTO.

## Your lines
- `P-EXAMIN-LEAD-1 (a) yes EXAMIN-CTO-wave0-brief 0d96110c` (or name changes).
- `(b) yes` (the tmux Remote Control session; the headless runs stop) or `(b) keep headless`.
- `(c) yes` (REPLIES/REQUESTS files, wakes, the operator's queue with your yes) or name changes.
