# ACT-SETS-GLOBS-1: the launch script's destinations hidden (W2-149's review F2)

- **For:** the owner's yes (a class (b) ACT: the guard changes, DEC-1112 (3)), then the owner's operator, as the
  message in §5.
- **By:** an agent for the CTO, 2026-11-09. Designed, built and rehearsed in a clone with a planted HOME. **Nothing
  live is changed** until the operator runs §5.
- **Sources:** W2-149's review rounds 1 and 2, F2 and F11 (`.gov-runtime/scratch/orchestrator/reviews/W2-149-review-r1.md`,
  `-r2.md`; ticket DAEO-52ku); the CTO's delegated decision (a tightening): the three globs; DEC-1101 (2), DEC-1112 (1)
  and (3), DEC-1082 (3), DEC-1097 (2), DEC-803 (an entry criterion of step 4); ACT-GUARD-SETS-1 and ACT-INDEP-WALLS-1
  (the models: `drafts/sets-root-guard`, `drafts/indep-walls`).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/sets-globs/` (§4).

## 1. What lands
**Two files** (`apply.sh`, §5):
1. **The path map** (`governance/project/path-map.yaml`, `40085090306e` → `7eb43071c02b`): three globs added to
   `sets_root_hidden.hidden`, and a five-line comment. Nothing else in the map changes (`path-map.patch`).
   - `fixtures/evaluation/*/hidden/**`: a writer's new set (`memory-verdict-4/hidden/`, any name).
   - `fixtures/evaluation/*/XCHECK-r*.md`: the checker's `XCHECK-r<round>.md` beside a set.
   - `runs/*/miss-classes.json`: an audit's `runs/<audit>/miss-classes.json`.
2. **The guard** (`.claude/hooks/pretooluse.py`, `97a84e770058` → `8546c73d4341`, 103 lines added and 19 changed,
   `pretooluse.diff`). Two changes, both only for a glob with a wildcard **before its end**. The live map has no such
   glob, so for today's seven globs every key and every walk is unchanged.
   - **The line rule's key** (`sets_line_keys`). Today the key is a glob's literal head. For these globs that head is
     the open folder above them (`fixtures/evaluation`, `runs`). The key is now the glob's own parts, each `*` one name
     (`<name>/hidden`, `<name>/XCHECK-r<n>.md`, `runs/<name>/miss-classes.json`), or its last name quoted.
   - **The walk and the match** (`Narrow`). The judge walks a glob from its literal head. Here that would be the
     whole `fixtures/evaluation` and `runs` folders, under the sets root and in each of the 135 trees. The walk is now
     the same walk, but it skips each folder whose name the glob's part at that depth cannot match. The judge's own
     match is asked once per path for all the parts with the same globs, behind an exact prefix filter. The file lists
     and the answers are identical (§6).

**Why the hook has to change** (the rehearsal measured both):
- **With the map alone**, the line rule's key becomes `fixtures/evaluation` and `runs`. Then 34 ordinary cases are
  refused: a Bash line naming the sets root and any open file under those folders, such as
  `cat <root>/runs/e0/counts.txt`, `ls <root>/runs`, or a set's `visible/` or `README`. That breaks DEC-1097 (2)'s
  "every other folder under runs/ stays open". At the same time `--file zz/hidden/q01.yaml` with the root passes.
- **The judge's walk and match** with these globs cost about **0.8 s** on every call that asks whether a part holds
  files (768 ms against 19 ms with `Narrow`). A revision's listing (`git grep … HEAD`) took **11.7 s**, where it took
  0.6 s before the ACT; it takes 0.2 s with `Narrow`. In runs 2 and 3 this pushed one CTO-subagent
  `git grep … HEAD -- '*.yaml'` past the guard's 20-second deadline (allow → deny). The clean run had none.
- The map alone would be class (a): an addition to a refusal list (`class-rules.yaml`, path-map). With the hook it is
  class (b).

## 2. What is hidden, and what stays open
Hidden from the six roles (orchestrator, engineer, research, product-spec, independent-test-designer,
independent-auditor), so from the CTO, the leads and their subagents too:
- reads by any tool, writes the guard resolves, listings and searches that reach the files;
- a Bash line naming the sets root together with the folder or file (`sets_line_keys`).

This applies under the sets root and in every tree, as for every `sets_root_hidden` glob.

| Path (under the sets root or a tree) | Before | After |
|---|---|---|
| `fixtures/evaluation/<set>/hidden/**` (any set, a new one included) | open (unless the set is listed) | **refused** |
| `fixtures/evaluation/<set>/XCHECK-r1.md`, `XCHECK-r12.md` | open | **refused** |
| `runs/<audit>/miss-classes.json` | open | **refused** |
| `fixtures/evaluation/<set>/visible/**`, `README.md`, `XCHECK.md` (the manual notes), `hidden-notes.md`, `<set>/sub/XCHECK-r1.md`, `XCHECK-r1.md.bak` | open | open |
| `runs/<audit>/misses.jsonl`, `classes.json`, `runs/e0/counts.txt`, `runs/<a>/<b>/miss-classes.json`, `runs/miss-classes.json` | open | open |
| `fixtures/evaluation/hidden/x` (no set level) | open | open |
| The launch script's own lines (`--sets-root <root>` only, with `--set`, `--audit`, `--round`, `--counts-only`) | allowed | allowed |

**The launch script is unaffected.** Its line names only `--sets-root <root>`. Its own code opens the files, and the
guard never sees that. Its stage-15 budget counts the hidden part by these globs from the map at `--commit`, using
`fnmatch`, where `*` crosses folders. That count is a little high, never low. In the rehearsal it delivered all three
kinds into the new globs under the applied map (§6).

**Not included** (the CTO's decision named three globs): `runs/*/misses.jsonl`, which the W2-149 reviewer said to
"also consider". It is the measure's own misses list, and the auditor reads it as input. Add it later by the same form
if wanted.

## 3. F11: the real HOME's settings in wall sessions
**Judgement: F11 does not let a wall session read outside its wall. No fix is folded into this ACT.**
- `~/.claude/settings.json` (`bc0dde042f00`) holds:
  - allow rules `Bash(*)`, `Read(*)`, `Edit(*)`, `Write(*)`, `WebFetch(*)`, `WebSearch(*)`;
  - `defaultMode: acceptEdits`, `env: CLAUDE_CODE_SUBAGENT_MODEL`;
  - no hooks, no `additionalDirectories`, no plugins enabled.

  There is no `~/.claude/CLAUDE.md`.
- In a wall session (`indep_launch.py` `session_flags`) four things stand in the way:
  - `--tools` offers only the kind's tools, so Bash, WebFetch and WebSearch are not there to allow;
  - the wall's deny rules cover Bash, the web, Agent, Skill and Read of the repository, worktrees, runs, `~/.claude`
    and the sets root's folders. A deny wins over an allow from any settings file;
  - the wall hook (`PreToolUse`, matcher `*`) refuses every path outside the wall and its tree, whatever any allow
    rule says;
  - `--restricted` confines Read, Grep and Write to the working folder and the `--add-dir`s.
- **Evidence:**
  - ACT-INDEP-WALLS-1's live session A ran exactly so: the real HOME, no `--setting-sources`, and this same user
    settings file (its hash recorded in that rehearsal's `live-before.txt`). It refused 10 of 10 outside Reads and the
    Glob.
  - W2-149's S11 live run passed (review round 2).
- **What it does let in:** the user file's allow lines, `acceptEdits` and its one environment variable load into
  every wall. A user-level hook, `CLAUDE.md`, MCP server or plugin added later would load too, though MCP is already
  shut by `--strict-mcp-config`. That is inward drift, not a read outside the wall.
- **The fix, defence in depth:** add `--setting-sources project` to `session_flags` in
  `governance/project/orchestration/tools/indep_launch.py` (`:722`), for the session and the canary alike. The wall's
  own `.claude/settings.json` is the project source and is also passed by `--settings`, so nothing the wall needs is
  lost. ACT-INDEP-WALLS-1's session B ran with exactly that flag and the real HOME's sign-in, and held.
  - This changes S10's settled flag list, so it is a DEC-105 choice for W2-149's follow-up row (or the Wave 3
    hardening pass with F13–F15). It needs one test-designer case (the flag present, the user file not loaded) and
    the live S11 re-run.
  - It is not an ACT, because the launch script is ticket code, not a control file. Recommended: apply in the
    follow-up, before the first real writer run alongside this ACT. It is not blocking.

## 4. The files (drafts, scratch; checked by hash before they apply)
| File (`drafts/sets-globs/`) | sha256 (first 12) |
|---|---|
| `path-map.candidate.yaml`: the live map plus the three globs and the comment | `7eb43071c02b` |
| `pretooluse.candidate.py`: the live hook plus `sets_line_keys` and `Narrow` | `8546c73d4341` |
| `path-map.patch`, `pretooluse.diff` (review diffs) | `f1cc9dca27b8`, `0920f599973d` |
| `apply.sh`: `check`, `apply`, `undo` (backups with sha256s; the size check; undo byte for byte) | `2a0e88638bee` |
| `sets_globs_check.py`: the guard check cases (N, L, S, O; 473) | `573dee665eb2` |
| `deliver_check.py`: the launch script delivers into the globs, then the guard refuses them (the W2-149 harness) | `c2d3303b4b0c` |
| `narrow_check.py`: `Narrow`'s file lists and matches against the judge's, every tree | `ffb59d85fd03` |
| `replay_globs.py` (on `indep-walls/replay_walls.py`), `livelog_count.py` | `c8b113db6755`, `6c72c16583da` |
| `rehearse.sh`, `rehearsal.log`, `REHEARSAL.md` (earlier runs in `old-logs/`) | `346f1f368563`, `b2ecd52002b5`, `d5a43edf5378` |

`apply.sh check` and `apply` stop in three cases:
- the live hook or map no longer hashes `97a84e770058` or `40085090306e` (checked on the main tree at head
  `260e70bd1`: "check: ready to apply");
- a candidate is not as built;
- **the size check fails.** It runs the pinned judge's own walk of the real sets root's hidden part, file names only.
  It prints two counts and two times and never a name. It refuses when the candidate globs find more than 8,000
  files (the launch script's budget; the guard fails closed past 10,000) or the walk takes more than 2,000 ms. The CTO
  never opened the real sets root, so this is its first measurement. That is why it gates.

**If the hook moves before you apply, the CTO rebuilds and re-rehearses first.** W2-141's staged hook
(`docs/changes/W2-141-hook/pretooluse.py`, READY, its ACT pending) is built on an older hook. Whichever of the two
lands second is rebuilt on the other.

## 5. The operator's steps: the message
> **ACT-SETS-GLOBS-1 (DEC-1101, DEC-1112; W2-149's review F2): the launch script's destinations hidden from every
> guarded session, before the first real writer run.** Class (b): the owner's yes first. In the main tree, about one
> minute:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/sets-globs
> bash $G/apply.sh check     # two "size" lines (counts and ms only), then "check: ready to apply" (exit 0)
> bash $G/apply.sh apply     # backup; the hook and the map; "state applied"
> git add .claude/hooks/pretooluse.py governance/project/path-map.yaml
> git diff --cached --name-status    # expect exactly: M .claude/hooks/pretooluse.py, M governance/project/path-map.yaml
> git commit -m "ACT-SETS-GLOBS-1: the launch script's destinations hidden (fixtures/evaluation/*/hidden/**, fixtures/evaluation/*/XCHECK-r*.md, runs/*/miss-classes.json); the guard's line rule keys such a glob by its own parts (W2-149 review F2)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner"
> ```
> If `check` stops on the size, send its two lines to the CTO and apply nothing.
> **Undo:** `bash $G/apply.sh undo` puts the hook and the map back byte for byte. Then commit the two files with
> `--trailer "Role: owner"`.

**Then the CTO**, the same day:
- merge `w2/integrate` into the live worktrees, since each runs its own copy of the hook;
- run `sets_globs_check.py <main tree>` with the real HOME, which runs its L, S and O cases on the live tree (names
  only; the R cases need the planted root);
- file the F11 follow-up row (§3).

## 6. The rehearsal (DEC-1057): `REHEARSAL.md` and `rehearsal.log`
There was one clean run, 21:48–22:04 GMT, from a fresh `env -i` shell, with **0 failures**. It used a
`--no-hardlinks` clone at the main tree's head with a worktree and a planted HOME. The planted sets root held dummy
lines, including the three destinations and their open neighbours. Every hook run logged into the rehearsal's own
folder; the live call log got 0 lines from it. The real sets root was never opened.

| Step | Result |
|---|---|
| **Guard check cases** (`sets_globs_check.py`, 473): N (each destination: Read, Bash, Grep, Glob, Write, a Bash write; under the root and in two trees), L (the line rule), S (the launch script's lines), O (nothing else) | **before: 473 run, 0 failed** (every N and L case allowed: the gap). **After: 473 run, 0 failed**. Refused to the six roles, the CTO, a lead, the CTO's subagents and the tuner; the sessions no rule names and prose without the root untouched |
| The map alone, with the live hook | 40 answers wrong: **34 open forms refused**, 6 line-rule forms allowed (§1) |
| **The launch script delivers** (`deliver_check.py`: the real script, the W2-149 harness, the applied map) | writer (a new set's `hidden/`), checker (`XCHECK-r1.md`), auditor (`runs/audit-1/miss-classes.json`): **delivered**. The hook before: each file open; after: each refused to Read, `cat` and Grep, the script's own line allowed (48 of 48) |
| `walls_check.py repo <clone>` before / after | 331, 0 failed / 331, 0 failed |
| `guard4_check.py --settings <clone>` before / after | 501, 0 failed / 501, 0 failed |
| Suites before / after | `test_guard_fix_4` 467 / 467; `test_g14` 150 passed, 1 skipped, 1 failed / the same (a check of today's tree that fails at this head without the ACT); live hook, reads 85 / 85; W2-149's unit and acceptance suites 128 passed, 3 skipped / the same |
| `Narrow` against the judge (`narrow_check.py`) | file lists equal on 135 trees, the planted root and a synthetic tree; `match` equal on 3,730 paths × 135 parts |
| **Replay**, 48 hours, 11,885 unique calls | before → after **0 changed** (11,808 allow, 77 deny); 65 calls name the new globs |
| Latency (real HOME, 135 trees) | median 133.3 → 136.4 ms (noise); `git grep … HEAD` 604 → 212 ms |
| `apply.sh` | check ready (size 7 → 10, 1 ms on the planted root); applied; a second apply refused; the commit: exactly the two files, the trailers as the message; undo byte for byte, then "ready to apply" |
| Live files (the hook and modules, the map, `held-out.yaml`, the settings, the launch script, the walls' template, the checks, `~/.claude/settings.json`, `~/gov-os-operator`, the real sets root's entry) | **unchanged** |

Runs 1–3 (`old-logs/`) found the walk and match costs and the deadline refusal (§1), a harness location rule and a
masked exit code. All were fixed before the clean run (`REHEARSAL.md`).

## 7. For your decision
1. **Yes to this ACT** (class (b)): the three globs as the CTO decided, and the two hook changes that keep everything
   else as it is. Recommended: yes, before step 4 (the first real writer run, DEC-803).
2. **F11:** the `--setting-sources project` follow-up row for the launch script (§3). Recommended: yes, as a row, not
   blocking.

**Residuals:**
1. The glob does not catch a hidden folder copied under another name, or one more than one level below a set. The
   older literal globs and the briefs cover those cases.
2. The size check meets the real sets root for the first time at `check`. If it stops, the CTO measures the count
   and decides whether the globs should be narrowed or the budget raised.
3. As for every guard ACT: calls in a worktree are judged by that worktree's own hook until it is merged.

**What it costs:** no measurable change on ordinary calls (§6, latency); a revision's listing gets faster. Three
globs in the map, about 100 lines of hook.
No install, no GPU.

**Basis:** question 2 (a hidden set stays hidden from the sessions it measures, the CTO included, from its first
real run).
