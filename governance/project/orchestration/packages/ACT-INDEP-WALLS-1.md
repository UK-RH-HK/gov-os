# ACT-INDEP-WALLS-1: the independent sessions' walls in the path map, the guard and their folders' settings (DEC-1101 (2)-(3) step 1; the sandbox seal folded in, DEC-1099 (1) Q6)

- **For:** the owner, to decide §7, then the owner's operator (a guard change: P-ACT-SPLIT). One ACT: it carries
  ACT-SANDBOX-SEAL-1's patch unchanged, so that package has no operator step of its own.
- **By:** a research agent for the CTO, 2026-11-09. Designed, built and rehearsed in a clone. **Nothing live is
  changed** until the operator runs §4.
- **Sources:** DEC-1101 (1)-(3), DEC-1099 (1) Q5/Q6 and (2) (4), DEC-1098 (4), DEC-820, DEC-1078, DEC-1082 (3),
  DEC-1097 (2); ACT-GUARD-SETS-1 (applied, `15952bbf`); ACT-SANDBOX-SEAL-1 and its requirements (§3); ACT-MSET-3/4 (the
  operator's writer and checker folders); SANDBOX-GUARD-EXP-1 §2 (b), §4; the CTO's decision on the tuner's transcripts.
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/indep-walls/` (the files in §3, `REHEARSAL.md`,
  `rehearsal.log`, and `LAUNCH-SPEC.md` for step 2).

## 1. What lands, and the layout
**Four changes** (`apply.sh`, §4):
1. **The path map** (`a9d8b97267c4` → `622b0c5b1a77`):
   - **the seal**: ACT-SANDBOX-SEAL-1's `path-map.patch` applied byte for byte (`906544ac4afb`; its own after-hash
     `ef9952e9ea4f` is the first step of this map). It adds the evaluation set `sandbox-guard-exp-1`, with its hidden
     glob, measuring the five roles, and the same glob in `sets_root_hidden`;
   - **`indep-walls/**` in `sets_root_hidden`**: the walls are refused to the six roles under the sets root, by the rules
     already live (2b and its line rule);
   - **a new block `session_hidden`**: `~/.claude/projects` refused to the engineer on W2-56 only (the sandbox
     experiment's tuner).
2. **The guard** (`.claude/hooks/pretooluse.py`, `bd545af83198` → `d5be03dbb48e`): rule **2c**, which reads
   `session_hidden` (about 120 lines, no other change; `pretooluse.diff`).
3. **The walls' template**, six new files in `governance/project/indep-walls/`: `settings.json.tmpl`,
   `wall_hook.py`, `CLAUDE.md.tmpl`, `kinds.yaml`, `tree-exclude.txt` and `README.md`.
4. **The approved list**: `<sets root>/indep-walls/APPROVED` (folder 0700, file 0400), holding the template files' sha256s.
   The briefs' lines are added at step 3, when the owner approves the briefs.

**The layout:**
```
~/gov-os-eval/indep-walls/               hidden to the six roles (rule 2b, the line rule)
  APPROVED                               the owner's list: template and brief sha256s (operator-written)
  <kind>/<run>/                          one wall per job kind and run: writer, checker, auditor, labeller
    WALL.json seed.txt brief.md CLAUDE.md    the manifest, the seed (written first), the approved brief, the note
    .claude/settings.json .claude/wall_hook.py
    input/                               the content chosen by rule (selection.json) and staged read-only copies
    out/                                 the only writable folder
  <kind>/<run>.tar                       a finished wall, packed into one file (step 2)
~/gov-os-wall-trees/<kind>-<run>/        the wall's plain tree of the repository at the pinned commit (read-only)
~/gov-os-runs/indep/                     what the CTO reads: counts.json per run, SEEDS.log, AUDITS.log
```

**Why this layout:**
- **The walls go under the sets root.** It is the one root outside every tree that the live guard already refuses to
  the six roles, the CTO and leads included, for reads, resolved writes and the line rule. One glob seals the walls
  with no new guard code. The sets root is outside every worktree and every run clone, so no branch can carry a wall.
- **One wall per kind and run.** Nothing is shared, so a wall has nothing of another's to read. A wall is created
  empty and never reused. The checker gets the writer's set as a read-only copy staged by the launch script, never
  through the writer's wall.
- **The trees go outside the sets root.** The rehearsal found this the hard way. The guard walks the hidden part of
  the sets root for file names and refuses everything once that part passes **10,000 files**
  (`reads._MOST_FILES`). Four walls holding their own trees (3,364 files each) made it refuse plain `ls`, `grep -r`
  and `git diff | xargs` lines for every refused role (26 guard4 cases and 4 seal cases red). A tree is only the
  repository's own content at a commit, less the exclusions. It is nothing a measured role cannot read in git, so it
  needs no hiding. A wall now holds about 7 files (43 for six walls in the rehearsal), and a finished one is packed into one file
  (LAUNCH-SPEC S17/S18).
- **The folder is `indep-walls/`, not `walls/`.** The glob holds in every tree too, so with `walls/**` a bare word
  `walls` read from a tree root (a CTO heredoc drafting DEC-1101's text) was refused. That was the replay's one
  allow→deny in run 3. `indep-walls` is rare as a bare word; case W5c pins the prose as allowed. Its price: a line
  naming the sets root together with a path holding `/indep-walls/` (for example `drafts/indep-walls/`) is refused
  to the six roles by the line rule.
- **The writes go to `out/` only.** The writers' and labellers' products reach the set's folder and the sealed folder
  through the launch script's code, after the output schema checks. The session itself never writes there
  (ACT-SANDBOX-SEAL-1 §3 (2), met through the script).

## 2. The decisions taken in the design
**(a) The repository's guard does not run in the walls; each wall runs its own wall hook. Three layers, each tested
alone:**
1. **Claude Code's restricted mode** (`claude -p --restricted --settings <wall's> --add-dir <tree>`). It ignores
   user, project and local settings, so the user's `Bash(*)`/`Read(*)` allow list, plugins and hooks do not load. It
   confines the file tools to the wall and its tree.
2. **The wall's settings.** They allow the wall (writes `out/` only) and the tree. They deny the shell, the web,
   subagents, notebooks, skills, memory's search (`gov retrieve`, `gov context`, `gov.cli.main`, the measure), git,
   ollama, the live repository, the worktrees, `~/gov-os-runs`, `~/.claude`, the pin, the rest of the sets root
   (fixtures, runs, transcripts, its map), `APPROVED`, the other kinds' walls and the walls of the same kind present at
   build time. They block edits to the wall's own `.claude/`, input, brief, seed, manifest and tree.
3. **The wall hook.** Reads and writes are closed to the wall and its tree, links followed and `..` resolved. Writes
   go only into `out/`, never through a link. Only Read, Grep, Glob, Write, Edit, MultiEdit and TodoWrite are allowed;
   everything else is refused (Bash, WebFetch, Task, MCP, ToolSearch, an unknown name). It fails closed.

**Why not the repository's hook:** its policy is DEC-820's, reads open and writes closed, keyed on `GOV_ROLE` and the
repository's tickets. A wall needs the inverse, reads closed too. Giving a wall one of the six roles would refuse it
its own folder (`indep-walls/**`). A seventh role in the hook would be a kernel change for something a 120-line,
deny-by-default hook does better. The repository's guard still guards the walls from the outside (b). **The sandbox**
becomes a fourth layer once W2-56 proves it (the slot is the launch line). Until then, the walls stand on (1) to (3).

**(b) The six refused roles cannot read the walls:** `indep-walls/**` in `sets_root_hidden`. The CTO's launch script names
only `--sets-root <root>` on its line and opens the walls in its own code, as the measure and the fresh-80 scripts do.
The sessions no rule names (no `GOV_ROLE`, `ticket-lead`) stay allowed, as for every hidden set: the operator's sessions
run outside the guard.

**(c) The tuner's transcripts rule (the CTO's decision, ACT-SANDBOX-SEAL-1 §3 (1)):** rule 2c refuses
`~/.claude/projects` to `engineer` sessions whose ticket goes by `W2-56` (its id `DAEO-wnnz`, its file name or its WBS
id, read from `.tickets/`), the tuner's subagents included, and to no one else. The CTO's `tools/guard_refusals.py`,
the replays, other engineers, a lead on W2-56 and the auditor are untouched (cases T7). It needs a hook change because
`role_paths` globs are tree-relative. The guard's walk (`_Part`) is not used for it either: `~/.claude/projects`
holds thousands of transcripts and would pass the 10,000-file cap. Rule 2c instead checks the path a file tool names
(and a Grep or Glob starting at or above the folder), and applies 2b's line rule to Bash with `~/.claude` as the root
and `projects` as the hidden folder. The sealed folder is refused to the tuner by the seal (the engineer is a measured
role; cases T5). **The settings layer for the tuner** is the CTO's launch line, not a live file:
`--settings '{"permissions":{"deny":["Read(//home/usain/.claude/projects/**)","Read(//home/usain/gov-os-eval/fixtures/evaluation/sandbox-guard-exp-1/hidden/**)"]}}'`.
**Its wall** is set-up B's sandbox, once proven (§7 residual 1).

**(d) Content by rule, the seed first, only counts out** are the launch script's job (LAUNCH-SPEC §2-§4). This ACT
gives it the template, the approved list and the walls' places.

## 3. The files (drafts, scratch; checked by hash before they apply)
| File (`drafts/indep-walls/`) | sha256 (first 12) |
|---|---|
| `path-map.candidate.yaml`: the live map `a9d8b97267c4` plus the seal, `indep-walls/**` and `session_hidden` | `622b0c5b1a77` |
| `path-map.patch` (review diff, 51 lines; the seal's lines inside it unchanged) | `5c27871be57a` |
| `pretooluse.candidate.py`: the live hook `bd545af83198` plus rule 2c | `d5be03dbb48e` |
| `pretooluse.diff` (review diff, 139 lines) | `3ef4745e45f8` |
| `template/settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl` | `9b85b9a604d0`, `95638d7d9edb`, `aee245ce7a80` |
| `template/kinds.yaml`, `tree-exclude.txt`, `README.md` | `8b50a78f01b3`, `21660e1ee5ad`, `65298d346848` |
| `apply.sh`: `check`, `apply`, `undo` (backups, sha256s; `undo` refuses while a wall run exists) | `a17b78553d21` |
| `walls_check.py` (the guard cases, §5), `build_wall.py` (the reference builder), `replay_walls.py` | `15d405ce1595`, `05b95cad7c69`, `d8522a06728a` |
| `rehearse.sh`, `freeze.py` (writes the built hashes into `apply.sh`), `rehearsal.log` | `8c06042d7d1d`, `d067f21f902f`, `8b8716fd089c` |
| `LAUNCH-SPEC.md` (step 2), `REHEARSAL.md` (the record) | `666b76a36cd1` |

`apply.sh check` and `apply` stop unless the live hook and map still hash as before (`bd545af83198`,
`a9d8b97267c4`, checked on the main tree at 2026-11-09), every draft hashes as built, the template folder does not
exist and `<sets root>/walls` does not exist. **If the map or the hook moves before you apply, the CTO rebuilds
(`freeze.py`) and re-runs the rehearsal first.**

## 4. The operator's steps (main tree, about 1 minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/drafts/indep-walls
bash $G/apply.sh check     # every hash as built; "check: ready to apply" (exit 0)
bash $G/apply.sh apply     # backups, the map, the hook, governance/project/indep-walls/, ~/gov-os-eval/indep-walls/APPROVED
git add .claude/hooks/pretooluse.py governance/project/path-map.yaml governance/project/indep-walls
git diff --cached --name-status    # expect 2 M and 6 A, nothing else
git commit -m "ACT-INDEP-WALLS-1: the independent sessions' walls (indep-walls/** hidden, the walls' template, the approved list), the sandbox experiment's sealed folder (ACT-SANDBOX-SEAL-1), and the W2-56 tuner refused ~/.claude/projects (rule 2c)" --trailer "Implements: DEC-1101, DEC-1099" --trailer "Role: owner"
```
**Then the CTO**, the same day: merge `w2/integrate` into the live worktrees with measured roles (each runs its own
copy of the hook), **W2-56's first** (rule 2c lives in the hook copy, so the tuner's tree must have it before the
tuner starts). Then run `walls_check.py repo` on the live tree (expected §6 r1 counts, the `~` forms included).
**Undo:** `bash $G/apply.sh undo` restores the hook and the map byte for byte and removes the template and `indep-walls/`
(rehearsed). It refuses while any wall run exists.

**Order (ACT-SANDBOX-SEAL-1 §3 (4)):** apply before the experiment's second writer writes and before the extractor
writes the held-out half.

## 5. The guard check cases (`walls_check.py`, by class of action; no worked bypass)
- **repo (the repository's guard), 331 cases over the roles:**
  - **W1-W4, refused:** reads of a wall's files (brief, seed, manifest, settings, input, out, `APPROVED`) by Read,
    `cat`, `head`, `ls`, `wc`, `grep -rn`, inline code, Grep and Glob, and writes into a wall (Write, `echo >`, `cp`),
    to the six roles, the CTO's subagents, a lead and the tuner.
  - **W5, refused:** the line rule, the root named with `indep-walls/` in the `~`, `$HOME` and absolute spellings, or with a
    variable or a `cd`. **W5c, allowed:** prose naming walls (a heredoc body, `echo walls`,
    `grep -rn walls`).
  - **W6-W8, allowed:** the launch script's own lines (`--sets-root <root>` only), the sessions no rule names,
    `~/gov-os-runs/indep/`, an open run folder, a repository path holding `walls` deeper down, and the walls' trees.
  - **T1-T5, refused to the tuner** (by its id, by its WBS id, its subagent): Read, Grep, Glob and Bash reaching
    `~/.claude/projects` (the folder, a file, a search from `~/.claude`, `cd`, a variable, a glob, inline code, an
    append), and the sealed folder.
  - **T6, allowed to the tuner:** its tree, the tuning folder, `~/.claude/settings.json`, `ls ~/.claude/skills`, and a
    script that opens the transcripts in its own code (a known limit, stated as a case).
  - **T7, allowed to everyone else:** the CTO, a lead on W2-56, research and the test designer on W2-56, an engineer on
    another ticket, the CTO's engineer subagent, the auditor, the sessions no rule names; `guard_refusals.py`,
    `ls ~/.claude/projects`, a transcript's tail.
- **wall (the wall hook), 83 cases:** reads in its wall and tree (allowed); reads of another wall of the same or another
  kind, another tree, the sets root's sets, runs and transcripts, `APPROVED`, the repository, the CTO's scratch, the
  worktrees, `~/gov-os-runs`, `~/.claude/projects`, `/etc` (refused); climbing out with `..` in a path, a Grep start,
  a Glob head or after a wildcard (refused); links out of the wall (refused) and in (allowed to read, refused to write
  through); writes only into `out/` (the tree, `.claude/`, brief, seed, manifest, input, the root, another wall,
  `/tmp`: refused); every tool but the seven (refused); fail closed (a bad path, the wrong folder, malformed input,
  a missing argument).
- **F (the built walls), 15 checks per wall:** hashes (settings, hook, brief, seed), the allow list, every required
  deny class, the one hook, no link, no excluded path and nothing writable in the tree, the tree outside the sets root,
  a small wall, the seed before the content, the read-only root.
- **The seal's 179 cases and guard4's 527 sets cases** re-run unchanged on the combined map.

## 6. The rehearsal (DEC-1057): `REHEARSAL.md` and `rehearsal.log`
One clean run, 02:01–02:13 GMT, from a fresh `env -i` shell, **0 failures**, in a `--no-hardlinks` clone at the main
tree's head with a worktree, a planted sets root (the seal's layout, with markers) and a planted CTO scratch marker.

| Step | Result |
|---|---|
| Gap (before the ACT) | repo cases **245 run, 0 failed**; 234 cases deny after and allow before |
| Suites before / after | `test_guard_fix_4` 467 passed; `test_g14` 151 passed, 1 skipped; W2-58 sets, launcher, live hook, reads 105 passed: the same |
| `apply.sh check`, `apply` | every hash as built; a second `apply` refused; the map loads (`load_config`, `check_sets`, schema 0 errors) |
| Build | six walls from the installed template; **43 files under `indep-walls/`** (the trees outside); a build into a wall that is not empty refused; the same seed, the same sample |
| **R2** (HOME planted) | repo **331, 0 failed**; seal **179, 0 failed**; guard4 sets **527, 0 failed** |
| **wall** | wall hook **83, 0 failed**; built-wall checks **84, 0 failed** |
| **R1** (real HOME, root planted, the registered line) | repo **321, 0 failed**; seal **165, 0 failed**; guard4 **501, 0 failed** |
| Replay (6,434 unique calls, 48 hours) | before → after **0 changed** (6,379 allow, 55 deny); after → every call as W2-56 **0 changed** |
| Live session A (as the launch script runs it) | **10 of 10** outside reads attempted and refused (another wall, another tree, `APPROVED`, a hidden set, the sealed folder, a run folder, the transcripts, the seed ledger, the CTO's scratch, the repository); 0 markers out; 0 writes outside `out/`; 0 traces under `~/.claude` |
| Live session B (the wall's settings only, no `--restricted`: as if opened by hand) | **10 of 10** refused by the settings and the wall hook alone; Bash and WebFetch not offered; 0 markers, 0 writes, 0 traces |
| `apply.sh undo` | refused while wall runs exist; then byte for byte; `git status` clean; `indep-walls/` gone |
| Live files (the hook, the map, the settings, the operator's two folders, `~/.claude/settings.json`, the real root's entry) | **unchanged** |

The earlier runs found the two design changes in §1: the trees outside the sets root (the 10,000-file walk) and
`indep-walls/` (one false refusal). They also found one probe-model decline, now retried and counted (REHEARSAL.md).
`apply.sh check` on the live main tree passes (state before, every draft as built).

## 7. For your decision
1. **Approve the layout and the three layers** (§1, §2 (a)): walls under the sets root, trees outside it, the wall
   hook rather than the repository's guard, the sandbox added when proven. Recommended: yes.
2. **Rule 2c for the tuner** (§2 (c)): a hook change, scoped to the engineer on W2-56. Recommended: yes. Its limits:
   - a script that opens the transcripts in its own code, and a recursive search from `~` or `/`, are let through
     (2b's limits); the tuner's brief forbids both, and set-up B's sandbox closes them;
   - the tuner's settings layer is its launch line (§2 (c)).
3. **The operator's two folders** (`~/gov-os-writer`, `~/gov-os-checker`) are left as they are until the launch
   script is the default (DEC-1101 (3)). Found while reading them, for your note:
   - they load your user settings (`Bash(*)`, `Read(*)`, `WebFetch(*)` allowed; only their deny lists stop reads);
   - the writer's deny list has no git commands;
   - both read the live repository (its scratch and worktrees denied by name), not a pinned tree.
   Recommended: retire them at the default; no change before.
4. **The budgets and timeouts** in `kinds.yaml` are placeholders, decided with the briefs (step 3).

**Residuals:**
1. The tuner's "wall" is the sandbox, not yet proven.
2. Claude Code ignores a settings file that fails validation in `-p` mode, without a word. The launch script's canary
   (LAUNCH-SPEC S9) is the guard against it.
3. The deny list names the walls of the same kind present at build time; later walls are kept out by layers (1) and
   (3), which the rehearsal shows hold alone.
4. The guard's 10,000-file walk caps the sets root's whole hidden part: the launch script keeps a budget of 8,000
   (S18). Today's real count under the hidden globs was not taken (the sets root is never opened here); the CTO
   counts it in the script's code before the first launch.

**What it costs:** rule 2c reads the ticket only for an engineer session (one `.tickets` read). Every other session
pays one more map block parse (the map is already read). A wall run costs a canary of about $0.005, plus the job.

**Basis:** question 2 (the sets' independence enforced by walls, not by trust; the held-out halves sealed) and
question 1 (the periodic audits' fresh questions written blind).
