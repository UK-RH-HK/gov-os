# ACT-OPERATOR-1: independent review, round 1

- **Reviewer:** a fresh independent session that wrote none of the drafts. Read-only except this record.
- **Date:** 2026-11-09, on `w2/integrate` at `baebd4fa5`.
- **What was reviewed:** the drafts in `.gov-runtime/scratch/orchestrator/drafts/operator-1/` as read at the end of the
  review. Their combined listing hash is `4f4fd86a6bb0` (sha256 of `sha256sum` over every file but `backup/`).
  - `apply.sh` `bc8f23b083b0`; `code/freeze_gate.py` `d21ae216a878`; `code/operator_run.py` `41271992b637`.
  - `pretooluse.pre.candidate.py` `4b528eb87118`; `pretooluse.post.candidate.py` `97a84e770058`;
    `path-map.candidate.yaml` `40085090306e`. All as pinned in `apply.sh`.
- **Governing sources:** DEC-1104 (2), DEC-1106, DEC-1107, DEC-1108 (5); `OPERATOR-AGENT-1.md`;
  `governance/project/operator/`; `tests/acceptance/W2-148/README.md`.

## What I ran
All runs were in scratch copies. No live file, no crontab, no `.git/hooks` and no `~/gov-os-operator` file was
changed (listings and reads only).
- **The new unit tests** (`code/test_act_operator_1.py`), run in a scratch layout with the merged operator code and
  the two code drafts overlaid: **14 passed**.
- **My own probes of `freeze_gate.py`**, in a scratch repository with a main tree, a worktree and a planted operator
  root. Its hook has the same `prepared` block as the candidate, pointed at a planted freeze. The cases:
  - the live branch: a commit touching control or ACT paths;
  - a worktree `update-ref` of the live branch, with GIT_DIR exported;
  - a worktree commit on another branch;
  - an ff-only merge in the main tree;
  - the main tree on a detached HEAD;
  - the operator's commit and its undo commit;
  - `pack-refs` and `gc`; `stash`;
  - timing with and without a freeze.
- **My own rule 2d probes** on the pre candidate, in a scratch git tree holding the candidate hook and map, with a
  planted HOME, under the pinned judge (the CTO's role). The forms: `mv` in and out, `ln -sf`, `touch`, `install`,
  `rsync`, `cd && >`; queue writes and moves; Write to `log/` and to `guard-calls`; reads; a sibling folder; the tree;
  timing.
- **The candidate path map through `gov.config.loader.validate`:** accepted.
- **Settings and cron:**
  - the built `operator-settings.json` through `opcommon.load_settings` under `env -i HOME PATH=/usr/bin:/bin` and
    `python3 -I`;
  - PyYAML importable under `/usr/bin/python3 -I` (system `dist-packages`);
  - `~/.local/bin/claude` is a native ELF;
  - `cron -f -P` (PATH inherited from the environment);
  - `~/gov-os-operator/log/` exists.
- **The landing check** (`landing_check.py`) run read-only on the last 300 first-parent commits.
- **The rehearsal logs, read once both runs had finished.**
  - `rehearsal-pre.log` ends `failures: 3`: guard4 before, guard4 after, `apply.sh undo`.
  - `rehearsal-post.log` ends `failures: 2`: guard4 before and after.
  - Both runs end `live: unchanged`.

## What holds (checked, no finding)
- **Rule 2d refuses only what it should.**
  - Refused, by rule 2d's own message: every write form into `~/gov-os-operator` outside `queue/`, and into
    `~/.gov-os/guard-calls`. That includes `mv` of the freeze file out, `ln -sf`, `touch`, `install`, `rsync` and
    `cd … && echo > …`.
  - Allowed: queue writes (Write, a redirect, `mkdir`/`mv` inside `queue/`), reads, `~/.gov-os/machine`, the tree.
  - Links are followed. A link in `queue/` that points into the root stays refused (op_cases R8).
  - The operator agent's walled session never meets the rule. It runs `claude --restricted` from `~/gov-os-operator/wall`
    with its own settings. The owner's operator session uses `~/gov-os-operator/.claude/settings.json`, which has no
    PreToolUse hook from the repo.
  - No CTO tool writes into `~/gov-os-operator` today (grep).
- **Rule 2d fits the hook's structure.**
  - A malformed block raises inside `main`'s fail-closed try, so every write tool and Bash call is refused, as with
    2b and 2c. Reads are untouched.
  - YAML is imported lazily; the 20-second deadline is unchanged.
  - It sits after 2c and before G-14, rm, rule 5 and rule 1. All of these are denials, so the order changes only the
    message.
  - About 64 ms per hook call in total.
- **The two candidates differ only by `answer(..., "2d")`.** Diff of diffs: one line. The bases are the live hook
  (`d5be03dbb48e`) and CALLLOG-1's candidate (`a7981319f877`); the map base is HEAD's blob (`3f7ae7f83d99`).
- **The freeze gate in my probes:**
  - refuses a commit or merge on the live branch touching the ACT's paths or the control paths;
  - judges a worktree `update-ref` of the live branch against the main tree's checked-out branch (GIT_DIR exported:
    `--git-common-dir`, then `symbolic-ref` with GIT_DIR dropped);
  - lets other branches' commits pass;
  - passes the operator's own commit and its `Undo: yes` commit;
  - refuses another ACT's trailers and a rewind;
  - passes `reset --hard` (old equal to new) and `stash`.
  - Cost: nothing when no freeze exists (one `[ -e ]`); about 5 ms per commit without a freeze and about 26 ms with
    one. No fail-open path found.
- **`apply.sh` ordering and safety.**
  - Order: the map before the hook (and the hook before the map on undo); the crontab last on apply and first on undo.
  - The hook base: pre or post; any other hash makes the state `other` and apply refuses.
  - APPROVED is generated in `sha256sum` form and validated by the install's own `opcommon.approved_state` before
    apply goes on. The freeze file and `__pycache__` are excluded on both sides.
  - Undo restores a file only when it is at the ACT's after-hash. It refuses a file at third bytes, a changed crontab
    table and a busy operator.
  - The owner's files (`CLAUDE.md`, `.claude/`, `hooks/`, `log/*.log`) are never written. The rehearsal's
    `owner_files` step: unchanged.
- **The crontab line works under cron.**
  - `/usr/bin/python3 -I` adds no script folder, but the launcher puts its own folder on `sys.path`. PyYAML is
    system-wide.
  - The install's own `operator-settings.json` is found next to the code, and it gives claude's absolute path.
  - The quiet hours are left out (`0-1,8-23`); F9 is a refinement.
- **F26's list and justification.**
  - Keeping `.claude/settings.local.json` as a control file is right. It holds `permissions.allow` and hooks, and
    Claude Code's own "don't ask again" write to it *is* a loosening of a control.
  - Skipping `.claude/scheduled_tasks.lock` is safe: it is a scheduler lock (session id, pid, time) and governs no
    agent. It is git-ignored (`.git/info/exclude`), so the operator's git-status checks (`tree_state(ignored=False)`)
    never saw it. The snapshot was the only place it bit, so F26 covers it.
  - The one gap is F6.

## Findings

| id | area | finding | blocking | one-line fix |
|---|---|---|---|---|
| F1 | apply.sh | Undo after real use exits 1 with "the tree after the undo is not as before". `queue/` keeps `taken/` and `done/`, so `state` reads `queue: present` and gives `other`. This is the rehearsal-pre `REHEARSAL FAIL: apply.sh undo`. Every part was in fact restored. A re-apply later also refuses while that `queue/` exists. | no (other; a false failure code, no loss) | In the after-undo check (and the before-apply state), treat `queue/` holding only `taken/ done/ rejected/` as `absent`, or leave it out of `state` and report it separately |
| F2 | rehearsal | Both rehearsals end non-zero (pre 3, post 2) on guard4's 5 cases (`sets F5`/`F7`: grep/Grep of `<planted sets root>/runs`, want deny, got allow). The failures are identical before and after the apply, so not the ACT's. Together with F1, DEC-1057's rehearsal is not clean. | no (other) | Have guard4 compare before against after (same failures: not an ACT failure), or plant the root's hidden files; re-run until both logs end `failures: 0` |
| F3 | freeze gate | While a freeze holds, `git pack-refs` and `git gc` (auto-gc too) are refused. So is `git update-ref <live> <new>` given no old value. In git 2.43's prepared state these report `old` as zeros, and the gate reads that as "created". The paths do not matter. A failed auto-gc writes `.git/gc.log`, and auto-gc then stops for a day with a warning on every command. The repository holds 5,069 loose objects against the 6,700 auto-gc threshold. | no (fails closed; other) | When `old` is zeros and the ref exists, take its current value (`rev-parse -q --verify <ref>`) as `old`; skip a line whose `old` equals `new` |
| F4 | freeze gate | With the main tree on a detached HEAD, `symbolic-ref` fails and `live` is None. While the freeze holds, every ref update in the repository is then refused (proven: a worktree commit on another branch). That contradicts "other refs are never judged". | no (rare; fails closed) | Without a symbolic HEAD, judge nothing (or the configured `refs/heads/w2/integrate`) rather than everything |
| F5 | freeze gate / CTO tools | The gate refuses at the prepared state, *after* `git merge` has written the main tree's index and work tree. The merge queue lands with `git merge --ff-only` in the main tree (`merge_queue.py advance`). If that landing touches the ACT's or the control paths during an apply, it is refused and leaves the index and work tree at the landed tree, with HEAD unmoved (proven). The operator's apply then sees unlisted changes, undoes, leaves the foreign files, holds the lock and sends a P1. The main tree needs a hand reset. `merge_queue.py` does not read the freeze, though DEC-1106 (3) says "the CTO's tools … read it". | no (fails closed; nothing lost; P1) | `merge_queue.advance()`, and any CTO landing in the main tree, waits for or defers on the freeze as `landing_select.sh` does (a follow-up ticket before the first live run); the gate stays the backstop |
| F6 | F26 | `.claude/hooks/__pycache__/*.pyc` (git-ignored) is rewritten by Python on the guard's first run after `bash_writes.py` or `role_reads.py` changes. On a guard-code (b) ACT whose check goes red, or that the owner undoes, the `.pyc` shows as a foreign control change. The result is "refused", the lock held and a P1 naming the `.pyc`. F26's justification does not mention it. | no (failure paths only; fails closed) | Either skip `.claude/**/__pycache__/*.pyc` (derived from the hashed sources) or state in F26's note that it stays deliberately, and that such a P1 is expected |
| F7 | apply.sh / ACT order | ACT-GUARD-CALLLOG-1's `apply.sh` accepts only `d5be03` as its base. If OPERATOR-1 is applied first (hook `4b528e`), CALLLOG-1 refuses and must be rebuilt. If both are applied, CALLLOG-1's undo refuses until OPERATOR-1's undo has run. | no (fails closed) | The package message states the order (CALLLOG-1 first, then OPERATOR-1) and the undo order (reverse) |
| F8 | apply.sh | **Install sources:** the tree's `governance/project/operator/*` files are checked only as each is copied (step 2), after the code is already in the tree. If the tree moved since the build, apply dies mid-install with "run undo". Undo cannot clean that: with no `APPROVED.sha256` it dies "install/APPROVED has changed", leaving the partial install and the code parts. **Undo order:** undo checks each part only when it reaches it, so the crontab and the tools are restored before a moved hook stops it. | no (fails closed; hand clean-up) | Check every `install.sums` source in the tree (and every part's state) before the first write, in apply and in undo; let undo remove a partial install whose files hash as in `install.sums` |
| F9 | crontab | Hours `0-1` allow a launch at 01:50. The session (45 minutes) then runs into the quiet hours. G9 waits inside the session until the launcher's timeout stops it, and the request has already been moved to `done/`. | no (other) | Hours `8-23,0` (last launch 00:50), or `8-23` |
| F10 | first live use | The owner's undo has no queue form. The launcher reads only `ACT-<id> <sha>` and runs `run`, yet each notice says "to undo, say `undo ACT-x <sha8>`". Nothing runs `operator_run.py undo` on that line. | no (other; not ordinary) | The message names who runs `python3 ~/gov-os-operator/install/operator_run.py undo <ACT> <sha>` (the owner's operator) until a queue form exists |
| F11 | first live use | `calls` defaults to `~/gov-os-operator/log/calls.jsonl`, which rule 2d closes. Until DEC-1108 (2) is built, an (a) ACT that adds to the path map or a deny list is applied, committed, then undone by the after-check ("call log cannot be read"): fails closed, with a P1. DEC-1108 (2)'s builder must not write into `log/`; by script it would also slip past 2d's intent. | no (other) | The message says such ACTs wait for DEC-1108 (2); that build puts its corpus where the operator reads it and sets `calls` in the install's settings |
| F12 | landing check | Run on the last 300 first-parent commits (since 11-04), the new P1 items would have been 4: CTO merges without a `Task:` trailer, and decision records touching `path-map.yaml`. That is about one P1 a day, each a true "control path outside an ACT". | no (other) | The message gives the owner the expected rate |

Out of scope (noted, not this ACT's):
- **O1:** guard4's five baseline failures (F2) may be an artefact of the planted root, which has no hidden files for
  the recursive grep to find. The CTO should confirm them against the live sets root before relying on the
  registered line.
- **O2:** `tests/acceptance/W2-148/test_w2_148_trial.py` and `tests/unit/operator/test_w2_148_trial.py` share a
  basename. Run together, pytest reports "import file mismatch"; this is the rehearsal's "1 error" in units, before
  and after.

## Verdict
No finding fails open or loses work. Rule 2d, the freeze gate's refusals, F26 and the install's own checks all do
what DEC-1106 (3) and DEC-1108 (5) ask, and every flaw found fails closed. The verdict below is **READY**, worked out
by `verdict.py`.

Before the ACT goes to the owner:
- **F1 and F2** must be fixed so that both rehearsal logs end `failures: 0` (DEC-1057). That changes `apply.sh`, so
  the manifest changes and needs a narrow re-check of `apply.sh`'s undo tail and the new rehearsal logs.
- **F3, F5 and F7** should be in the package message or fixed before the first live run.

```verdict
{"manifest": "ACT-OPERATOR-1 drafts as of your read (drafts/operator-1 listing 4f4fd86a6bb0; apply.sh bc8f23b083b0, freeze_gate.py d21ae216a878, operator_run.py 41271992b637, pre 4b528eb87118, post 97a84e770058, map 40085090306e)",
 "kpis": [
  {"kpi": "rule 2d (refuses only what it should; fail-closed; structure; candidates differ only by the rule id)", "verdict": "pass", "findings": []},
  {"kpi": "freeze_gate.py (live branch from a hook, merges, rewinds, the operator's commit and undo, cost, unrelated work, fail open)", "verdict": "fail", "findings": [
    {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "apply.sh (order, hook base, APPROVED, undo safety, crontab, the owner's files)", "verdict": "fail", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "crontab line (python3 -I, the install's settings, PATH under cron, quiet hours)", "verdict": "pass", "findings": [
    {"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "F26 (the list and its justification)", "verdict": "pass", "findings": [
    {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "first live use (claude under cron, settings defaults, undo path, replay corpus, landing check)", "verdict": "pass", "findings": [
    {"id": "F10", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F11", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "rehearsal (DEC-1057: 0 failures)", "verdict": "fail", "findings": [
    {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "outside this ACT", "verdict": "pass", "findings": [
    {"id": "O1", "scope": "out", "ordinary_work": "no", "consequence": "other"},
    {"id": "O2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}
 ]}
```
