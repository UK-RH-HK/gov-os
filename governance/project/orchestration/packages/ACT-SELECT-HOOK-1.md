# ACT-SELECT-HOOK-1: one line in the reference-transaction hook starts a scoped selection after every landing outside a ticket on the settings, the tool registry or the test map (DEC-1100 (2)-(4))

- **For:** the owner's operator (a git hook is configuration: DEC-1100 (3)).
- **By:** the CTO, 2026-11-09. The tool and this line built and rehearsed in clones; nothing live is changed until the
  operator runs §3. **Nothing to commit:** the hook is not tracked; the CTO records the ACT.
- **Under:** DEC-1100 (2) trigger (a), (3) mechanism (a), (4) the CTO's tools first (its product line goes into W2-115
  only once it has proven itself in use); P-SELECT-FIXES-1 §3 (iii), S7 and S8.

## 1. What changes
- **The hook:** `.git/hooks/reference-transaction` (W2-116's, installed at re-pin window 4, DEC-1087 (3)) gains one
  line, after its store refresh and before its final `exit 0`:
  ```
  setsid -f env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/landing_select.sh --hook >> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/landing-select.log 2>&1 </dev/null  # DEC-1100 (2)-(3), ACT-SELECT-HOOK-1: the scoped selection after a landing outside a ticket
  ```
  It runs only where the hook's own two guards let it: the `committed` state, and a transaction that moved
  `refs/heads/w2/integrate`. It is detached (`setsid -f`, every stream redirected), so the hook returns at once and
  still ends with `exit 0`. It reads no standard input (the hook's `grep -q` has taken it): the tool finds the range
  itself.
- **The tool it calls:** `.gov-runtime/scratch/orchestrator/tools/landing_select.sh` (the CTO's tools; tests
  `tools/test_landing_select.sh`, 45 of 45 pass). With `--hook` it:
  1. drops every `GIT_*` variable (git exports `GIT_DIR=<repo>/.git/worktrees/<name>` to the hook for a landing made
     from a worktree; rehearsed), takes the state lock, and reads the range from the last head it examined
     (`log/landing-select.head`; the first time, the branch's previous reflog value) to `w2/integrate`'s head;
  2. **during a FRESH-80 or E4 hold** (`log/act-in-progress.txt` naming FRESH-80 or E4) logs the landing DEFERRED and
     does not advance the state, so the next landing's range holds it; any other hold does not stop it;
  3. picks the first-parent commits **outside a ticket** (`Role: owner`, or no `Task: DAEO-<ticket>` other than
     DAEO-sdxk) whose own change touches `.claude/settings*.json`, `.rulesync/**` (the settings' source, P-SELECT-FIXES-1
     S7), `governance/project/tool-registry.yaml` or `governance/project/test-map.yaml`;
  4. if there are any, starts the run detached: a `git clone --shared` at the new head, its store seeded and rebuilt
     as a close's clone is (`seed_store.py rebuild`, DEC-1032), then `lead_verify.sh --fg` on it with the selection
     `select_tests.py --merge <those commits>` (their own changes, the tree at the new head): the parallel run and the
     serial phase, each pytest in `heavy_slot.sh`, the hold checked again inside the slot. **Never the full suite**
     (DEC-968); a refused selection is REFUSED, never green;
  5. writes the verdict (GREEN, RED, REFUSED, INCOMPLETE, HELD) to `log/landing-select.log` and one item to the
     dispatcher's inbox; a RED keeps its clone for the CTO, who fixes or reverts at once (DEC-968).
- **The cost (P-SELECT-FIXES-1 §3):** about 0.85 runs a day in the window (17 commits in 20 days); one scoped
  selection each, 10 to 20 minutes of wall time in one heavy slot. The hook itself adds no measurable time (§4).
- **Widened if an emergency merge reds again** (DEC-1100 (2)): the trigger is the one `TRIGGER` line of the tool.

## 2. The files (scratch; checked by hash before they apply)
| File | sha256 (first 12) | What |
|---|---|---|
| `.git/hooks/reference-transaction` (live) | `7a21de6dfc51` | as re-pin window 4 installed it, mode 755 |
| `drafts/select-hook/reference-transaction.candidate` | `6fbbf312bacd` | the live hook plus the one line |
| `drafts/select-hook/apply.sh` | `eceff00ebdeb` | check, apply, undo; refuses unless the candidate is the hook plus exactly that line |
| `drafts/select-hook/rehearse.sh`, `rehearsal.log` | `4064b37bfd26`, `18fac9de5f1e` | the rehearsal (§4) and its record |
| `tools/landing_select.sh` | `18c454cf6681` | the tool (`apply.sh check` prints its hash; it is the CTO's to change) |
| `tools/test_landing_select.sh` | `aa0e9fdce1e4` | the tool's tests on planted ranges |

## 3. The operator's steps (main tree, under a minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
H=.gov-runtime/scratch/orchestrator/drafts/select-hook
bash $H/apply.sh check     # the hook as built, the candidate = the hook plus one line, the tool present (exit 0)
bash $H/apply.sh apply     # backup with its sha256 and mode, the candidate put in place (755), the hash after
```
Nothing to commit. **Then the CTO:** after the next landing on `w2/integrate`, `log/landing-select.log` has one line
for it (the first one says "landing <old>..<new>: …"). **Undo:** `bash $H/apply.sh undo` restores the hook byte for
byte, its mode too (rehearsed). **Order with ACT-SELECT-FIXES-1:** either first; if this one is applied first, the
operator's commit of ACT-SELECT-FIXES-1 (an owner commit on the test map) starts the first run, as designed.

## 4. The rehearsal (`drafts/select-hook/rehearsal.log`, 2026-11-09 01:27:54–01:28:04, 0 failures)
In a `--shared` clone at the main tree's head with a worktree; `apply.sh` on the live hook's exact bytes. For the
landings, the installed hook is the same file with three substitutions only (shown by `diff` in the log): the main
tree's path → the clone's, `~/.local/bin/gov` → a stub that records its call (no rebuild runs), the store's refresh
lock → a private one; heavy-slot locks private; the tool's verifier a stub (no pytest), passed through git's
environment as the hook inherits it.

| Step | Result |
|---|---|
| `apply.sh check`, `apply` | the hook as built (`7a21de6dfc51`); applied (`6fbbf312bacd`, 755); the diff is the one line |
| `apply.sh undo` | byte for byte, mode 755; applied again for the landings |
| The store refresh | still starts on every landing: 10 of 10 landings without the line, 10 of 10 with it, and on the settings landing |
| Commit time, median of 10 | 14 ms without the line, 14 ms with it (max 15 and 15) |
| Records-only landings (CTO) | 10 logged "none outside a ticket on the trigger paths"; no run |
| A settings commit with `Role: owner` | a run on that commit (the stub saw `--merge <it>`), GREEN, one inbox item |
| A ticket's merge touching settings | "none outside a ticket"; no run |
| A commit on another branch | neither line runs |
| A landing made from a worktree (`update-ref` there) | the run's clone at the new commit; the worktree's HEAD untouched |
| A FRESH-80 hold | DEFERRED, state not advanced; the next landing ran the deferred commit |
| The tool sleeping 30 s / exiting 1 / missing | commit rc 0 in 12–13 ms each time |
| The hook by hand | exit 0 for `prepared`, `aborted`, `committed`, another ref, empty input |
| Live files | the hook, the tool, the test map and the settings hashed unchanged before and after; the live tool log not written |

**The tool's tests** (`bash tools/test_landing_select.sh`): **45 of 45 pass** on planted ranges. They cover the
trailers and paths (the CTO's, a ticket's, `Role: owner`, `decision-record`, none; settings, `settings.local.json`,
`.rulesync`, the registry, the map, a look-alike path, records only, code); merges (a ticket's, the CTO's emergency
merge); a range of three; a `GIT_DIR` from elsewhere ignored; the run's verdicts GREEN, RED (clone kept), REFUSED,
INCOMPLETE (a failed rebuild, a shut disk gate), nothing to run; FRESH-80 and E4 holds deferring, another ACT's hold
not; the slot form and a hold beginning inside the slot (exit 75); the hook form's state, detachment (under 2 s while
the run goes on), the lock not kept by the run, an unchanged head, a branch moved back, no repository (exit 0); and
the real `select_tests.py` through the tool's generated selection on a `--shared` clone of this repository with a
planted owner settings commit (scoped, the commit's own change, 142 targets).

## 5. For the owner
- **Proven in use first** (DEC-1100 (4)): after a fortnight of landings the CTO reports the runs (how many, wall time,
  reds caught at the landing, any false start) and only then proposes S9's product line for W2-115.
- **A note on W2-116's own line, not changed here:** for a landing made from a worktree, git exports that worktree's
  `GIT_DIR` to the hook, and the existing refresh line passes it on to `gov rebuild` (the rehearsal's stub recorded
  `GIT_DIR=<clone>/.git/worktrees/wt`). The CTO's landings run in the main tree, where this does not arise. If a
  landing from a worktree is ever made, the refresh may read that worktree's state. A one-word fix (`-u GIT_DIR` on that
  line) would be a W2-116 change. Options: (a) add it to this ACT now (a second line changed; about 15 minutes with a
  new rehearsal); (b) defer it to W2-116's own ticket; (c) leave it (main-tree landings only). Recommended: (b).

[DEC-1100 (2)-(4), DEC-1098 (2)(b), DEC-968, DEC-1087 (3)]
