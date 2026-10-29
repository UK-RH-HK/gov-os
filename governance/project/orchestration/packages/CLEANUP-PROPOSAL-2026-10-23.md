# Disk inventory and cleanup proposal, 2026-10-23 (DEC-899 item 10; nothing deleted yet)

Measured read-only between about 09:30 and 10:50 BST, with nice 10:
- the top level of `/tmp`, `~/gov-os-runs`, `~/gov-os-worktrees` and `~/.cache` (151 folders);
- then one level down in the largest.

A folder is "in use" when a running process has its working directory or an open file inside it.

**The disk (`/`, shared):** 1,007 GB, 332 GB used (35 %); 67,108,864 inodes, 30,401,984 used (46 %).

## a. The ten largest holders

| # | Folder | Inodes | Size | Newest file | In use |
|---|---|---|---|---|---|
| 1 | `/tmp/claude-1000` (Claude Code's per-session temp folders, 244 sessions) | 14,784,808 | 137.97 GiB | 10-22 21:58 | only this session's folder |
| 2 | `/tmp/pytest-of-usain` (pytest's base folders) | 10,055,692 | 88.30 GiB | 10-23 10:08 | no |
| 3 | `/tmp/gov-launch-engineer-v45jfxaw` (a launched engineer's sandbox temp) | 2,118,414 | 21.38 GiB | 10-20 22:44 | no |
| 4 | `/tmp/gov-launch-engineer-0culj3ha` (the same) | 1,951,904 | 14.40 GiB | 10-20 13:37 | no |
| 5 | `/tmp/gov-cbm-1000` (the code-graph daemon's per-run folders, 10,573) | 133,150 | 0.12 GiB | 10-23 10:25 | no |
| 6 | `/tmp/gov-os-assessment-*` (the lens folders, 12) | 97,630 | 3.56 GiB | 10-22 20:48 | no |
| 7 | `/tmp/w216probe.zM5L` | 52,785 | 0.32 GiB | 10-17 17:00 | no |
| 8 | `~/gov-os-runs/W2-00` (the nightly clone, the trials' runs) | 35,466 | 1.19 GiB | 10-22 09:40 | no |
| 9 | `~/.cache/uv` | 26,578 | 5.47 GiB | 10-05 | — |
| 10 | `~/.cache/packman`, `~/.cache/huggingface` (2.25 GiB, the embedding models), `~/.cache/pip` | 25,000 | 5.2 GiB | — | — |

The worktrees (`~/gov-os-worktrees`, 16) hold about 98,000 inodes, 3.3 GiB in all. Each belongs to a ticket that is in progress or held, or is the record worktree. W2-48's worktree is already gone.

## b. What each is

**Leftovers** (idle, from finished runs):
- **Two of W2-59's lead sessions** (`/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-59/5116ebd4…` and `…/5dfefd84…`) hold **14.0 million inodes and 132 GiB** between them: about 95 % of item 1.
  - Claude Code points `TMPDIR` at a session's folder, and every whole-tree copy those sessions' suites made stayed there.
  - The other 237 finished sessions' folders hold about 0.8 million inodes in all.
- **pytest's two `garbage-*` folders** (9.7 million inodes, 85 GiB): pytest renames old base folders this way for deletion. These two were never finished. Then 54 numbered run folders older than the newest three.
- **The two engineer sandbox temps of 2026-10-20** (4.1 million inodes, 36 GiB): the launcher left them behind when the sessions ended. Row W2-C002 recorded this as fixed at W1-28; it has recurred.
- **9,998 code-graph run folders** older than 24 hours.
- **W2-48's 44 cache folders** and **two empty `gov-check-*` folders**: about 100 inodes.

**In use, or kept on purpose:**
- this session's temp folder;
- the three running leads' sessions (all under 24 hours old, so outside every list);
- the 16 worktrees;
- `~/gov-os-runs`;
- `~/.cache` (the embedding models and the tool caches);
- the lens folders `/tmp/gov-os-assessment-*`, which the reports cite as evidence;
- `/tmp/gov-os-tooltrial`, until trial d's redo;
- `/tmp/w216probe.zM5L`, from W2-16's run of 10-17. W2-16 is held, and I cannot tell whether it is evidence, so I leave it.

## c. The proposal, for your approval

**Exact literal paths, in six list files** under `.gov-runtime/scratch/orchestrator/drafts/cleanup-2026-10-23/`, written read-only from the disk. Every path is idle, under `/tmp`, and not cited as evidence.

| List | Paths | sha256 starts | About |
|---|---|---|---|
| `1-claude-session-temp.txt` | 239 | `0203ce65700973e5` | 14.7 M inodes, 137 GiB: finished Claude Code sessions, older than 24 h, never this session's |
| `2-pytest-garbage.txt` | 2 | `880fcfec1fcecebe` | 9.7 M inodes, 85 GiB |
| `3-pytest-old-runs.txt` | 54 | `bef5869fde772988` | about 0.35 M inodes, 1 GiB: all but the newest three |
| `4-launcher-temp.txt` | 2 | `7f43334cf8149b76` | 4.1 M inodes, 36 GiB |
| `5-code-graph-runs.txt` | 9,998 | `d992822c12d91f89` | 0.12 M inodes |
| `6-testcache-and-check.txt` | 46 | `f13b1f1ef5c5f99b` | about 100 inodes |

**Together:** about 28.9 million inodes and 259 GiB. That would bring the disk to about 1.5 million inodes used (2 %) and about 73 GB (7 %).

**How it would run, on your approval only:**

`python3 .gov-runtime/scratch/orchestrator/drafts/cleanup-2026-10-23/delete.py <each list>=<its sha256 prefix>`

- In a quiet moment, never during a close.
- It refuses a list whose sha256 is not the approved one.
- It re-checks each path just before removing it, and skips anything that is gone, not a folder, outside `/tmp`, or in use.
- It prints the disk's figures before and after.

**Not proposed:**
- the lens folders, which are evidence. If you want them gone, I would first archive their small files into the record, as for lens H;
- `/tmp/gov-os-tooltrial`, which goes after trial d;
- `/tmp/w216probe.zM5L`;
- `~/.cache`;
- every worktree;
- `~/gov-os-runs`.

## The standing-rule proposal: what cleans itself up, and what a weekly sweep removes

**After each run, the run itself:**
- **every session** (lead, worker, auditor, trial, research, nightly) sets `TMPDIR` to a folder of its own, keeps pytest's retention of three base folders, and removes its clones, worktrees and temp trees before it returns (DEC-898, already in the common briefs);
- **the launcher** removes a sandboxed worker's temp folder when the worker ends: a new row reopening W2-C002, carried by W2-21, the launcher's ticket;
- **the close queue and the nightly script** remove their clones at the end, keeping only the last night's clone;
- **a lead's return** states its scratch size, and a lead that leaves more than its budget is a P1.

**A weekly sweep, by the orchestrator:** on Monday in a quiet window, never during a close, with the same re-check as `delete.py`. It removes only:
- `/tmp/pytest-of-usain/garbage-*`, and numbered run folders other than the newest three;
- Claude Code session temp folders under `/tmp/claude-1000` of sessions not running and older than 7 days;
- `/tmp/gov-launch-*` folders older than 7 days;
- code-graph run folders under `/tmp/gov-cbm-1000` older than 7 days;
- `/tmp/gov-check-*` and `/tmp/gov-testcache-*`;
- the worktrees and branches of closed tickets, after a sync.

**It never touches:**
- anything cited as evidence, until archived;
- `~/.cache`;
- `~/gov-os-runs/<a ticket in progress>`;
- the record worktree;
- the owner's EXAMIN copy;
- the workbench.

**It writes the figures before and after in the daily digest.** A sweep that finds a folder over a session's budget names the session as a P1.
