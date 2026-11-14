# ACT-CLASS-RULES-AGENTS-1: `CLAUDE.md` and `AGENTS.md` a fixed class (b) in the operator's rule table (DEC-1173)

- **For:** the owner (one yes line), then **the owner's operator, by hand** (class (O): the operator's own rule table and install,
  OPERATOR-AGENT-1 §5, DEC-1104 (4), as ACT-W2-148-S15-1 was). About three minutes. One commit, `Role: owner`. No file under
  `tests/acceptance/` changes, so no `acceptance_exemptions` entry and no second commit.
- **By:** an ACT-preparation helper of the CTO, 2026-11-13 from about 19:40 UTC. **Nothing live was changed or started:** no write under
  `~/gov-os-operator`, no crontab write, no commit, no stage, no queue line, nothing in the main tree's tracked files. Built and rehearsed
  on planted folders (copies of the install) and fresh clones under `/tmp/claude-1000/act-class-rules-agents-1/` (section 4).
  **Not yet independently reviewed** (section 8).
- **Under:** **DEC-1173** (the owner, 2026-11-13, chat: "CLAUDE.md and AGENTS.md: (b), a row in the change-class rules, so the operator
  agent applies an approved change. Go for the class-rules ACT (the agent-instructions row), then ACT-CLAUDE-RULES-1 as class (b)");
  **DEC-1104** ((2) the rule table, (4) the operator's own install is the owner's, by hand). The manifest's `dec`: "DEC-1173, DEC-1104".
  DEC-1173 is already in `docs/DECISION_REGISTER.md` as ACCEPTED (read at 2026-11-13 ~20:30 UTC); the operator's G2 reads it when
  ACT-CLAUDE-RULES-1 runs (this ACT, applied by hand, does not go through G2).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-class-rules-agents-1/` (`build_act.py`: build, rehearse, finalize, gates;
  `part5.py`: the package's blocks in a clone; `apply.sh`; `code/`: the after file). Adapted from the precedent's
  `drafts/w2-148-s15/`. **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLASS-RULES-AGENTS-1/`.

## 1. Context
`CLAUDE.md` and `AGENTS.md` (the repository's root files, rulesync's output from `.rulesync/rules/governance.md`) are named by **no row** of
`governance/project/operator/class-rules.yaml`, so `act_class.py` sends them to the catch-all `unknown` row: class (O), not a control path.
ACT-CLAUDE-RULES-1 (the "## Guard" paragraph made true, DEC-1167 (7)) was therefore measured (O): the operator agent's G6 refuses it
("yours") and only the owner could apply it by hand (its package, section 7, set out the options). The owner chose (b) by a table row
(DEC-1173). The rule table is the owner's (§5): a change to it is this (O) ACT, applied by hand, the way ACT-W2-148-S15-1 (commit
`4be656e70`) added `home-settings`.

## 2. What changes
1. **One fixed row, `agent-instructions`, straight after `guard-hook`** (the guard and settings control rows), `class: b`, `control: true`:
```diff
   - id: guard-hook
     ...
     class: b
     control: true
+  - id: agent-instructions
+    why: "the agent instructions every session loads (CLAUDE.md, AGENTS.md): a change alters what agents are told, so it is (b): a reviewed bundle, the owner's yes, applied by the operator agent (DEC-1173)"
+    match:
+      - {root: repo, path: "CLAUDE.md"}
+      - {root: repo, path: "AGENTS.md"}
+    class: b
+    control: true
   - id: settings
```
   Rows are tried in order: the three rows above `guard-hook` (`operator-own`, `cto-scratch`, `walled-sessions`) and `guard-hook` itself
   match neither path (rehearsed, part 3), so the new row decides them. The globs are whole-path: only the root files; `docs/CLAUDE.md`,
   `template/...`, `CLAUDE.local.md` and the home `~/.claude/CLAUDE.md` (already `agents-skills-kernel`, b) keep their rows.
2. **Where:** the repository's source `governance/project/operator/class-rules.yaml` (231 lines to 238; sha256 `38ac2f2decce` to
   `a040a103cbda`), the install's copy `~/gov-os-operator/install/class-rules.yaml` (the one `act_class.py` reads; the same bytes), and the
   install's `APPROVED` (its one `class-rules.yaml` line). The thirteen other install files are untouched (`keep.txt`). No code changes.
3. **Effects:**
   - an ACT touching `CLAUDE.md`/`AGENTS.md` (and nothing above (b)) is **(b)**: a reviewed bundle, the owner's yes line, the operator agent
     applies it. ACT-CLAUDE-RULES-1 becomes (b) (rehearsed: rows `rulesync-other`, `agent-instructions`, `agent-instructions`, no hit).
   - `control: true`: **the landing check (S16) now reads the two files.** A commit outside a ticket (no `Task:` but `DAEO-sdxk`) that
     touches either one without `Role: owner`, or `Role: operator` with `Act:`, is one P1 inbox item (rehearsed, part 5). Before, a CTO
     commit of `CLAUDE.md` raised nothing (the catch-all is not a control path). Ticket commits (`Task: DAEO-<ticket>`) are unaffected.
   - nothing else moves (section 4, part 3).

## 3. Why
DEC-1173: the two files are what every session is told; a change to them alters agents' instructions, as `.rulesync/**` (`rulesync-other`, b)
and the role files and skills (`agents-skills-kernel`, b) already do. (b) keeps the owner's yes and an independent review, and lets the
operator agent apply it, instead of (O) by hand. Fail closed: the classes rise from "unclassifiable" (O, refused) to a governed (b); no path
falls to (a).

## 4. The rehearsal (DEC-1057): `rehearsal.log`, 91 cases, ends `failures: 0`
`python3 -B drafts/act-class-rules-agents-1/build_act.py rehearse` (planted folders and clones under `/tmp/claude-1000/act-class-rules-agents-1/work`,
never the repository or `~/gov-os-runs`). The live install (every file, hash and mode), the crontab, and the tree's `class-rules.yaml`,
path map, `CLAUDE.md` and `AGENTS.md` are checked before and after: unchanged (the last three cases).
- **Part 1, `apply.sh` on planted folders, today's install (a copy of `~/gov-os-operator/install`):** check ready; verify exit 3 before;
  undo on the before a no-op; an unknown step or none exit 2; apply (the install's own APPROVED check ok); every file the after; both install
  files 0444, the tree's file keeps its mode; no temporary file, no `__pycache__`; the thirteen other install files unchanged; `APPROVED`
  differs in the one line; verify; apply again a no-op; check "already applied"; **the manifest's five checks**; undo byte for byte (hash,
  mode, listing); **the bite: on the before all five checks are red**; a stop part way (install folder not writable: exit 5) named by check
  and finished by a second apply; **refusals that touch nothing:** the tree's file moved, another install file moved, a stray install file,
  an `APPROVED` neither base's, the install's table edited after the apply (exit 3), a tampered frozen copy of either base (exit 4), the
  operator's freeze, journal, a queued request, a launch holding `log/launch.lock` (exit 6); apply and undo from an empty folder.
- **Part 2, the ACT-LANDING-CTO-ROUTE-1 base and the order:** on an install with LANDING's `landing_check.py` and `APPROVED`: check names the
  base, apply, the five checks, verify, undo byte for byte. LANDING's own `apply.sh` then this ACT: both apply; reverse undo; this ACT first:
  LANDING's check refuses (section 6).
- **Part 3, the rule's effect** (the live `act_class.py`, the old table against the new): the rows are the old ones in order plus
  `agent-instructions` straight after `guard-hook`, every old row, the hits and the version equal; no earlier row matches the two paths,
  which fall to `unknown` (O) under the old table. **Over 226 (root, path) pairs** (every row's globs instantiated, edge names such as
  `docs/CLAUDE.md`, `CLAUDE.local.md`, `claude.md`, the home `CLAUDE.md`, and every path any bundle on the machine names) **exactly two
  change: the repository's `CLAUDE.md` and `AGENTS.md`, unknown (O) to agent-instructions (b).** `classify_manifest`: CLAUDE.md alone,
  AGENTS.md alone, and the RULES-1 shape (O) to (b); CLAUDE.md with a `src/` file stays (O); `docs/CLAUDE.md` stays (O); the home
  `~/.claude/CLAUDE.md` stays (b). **W2-148's trial (S23), its 57 ACT file lists made manifests its own way: none changes class** (6 a, 19 b, 32 O under both tables). Every ACT file in
  the packages folder (94): none changes class (10 a, 51 b, 33 O under both). Every bundle under `acts/` (44): one changes, ACT-CLAUDE-RULES-1, (O) to (b). ACT-CLAUDE-RULES-1's bundle: (O) under the old table, **(b)** under the new.
- **Part 4, the operator's own tests** on a `git clone --no-hardlinks` of `w2/integrate` with the after file, through `heavy_slot.sh` (TMPDIR
  outside the repository, `-p no:cacheprovider`): **`tests/unit/operator` and `tests/acceptance/W2-148`: 654 passed, 0 failed.** The clone's only change is the table.
- **Part 5, the package's blocks as printed** (cut from this file, the repository root replaced by a clone with a planted HOME): section 5's
  block exit 0; one commit, exactly `class-rules.yaml`, its blob the after, the subject and three trailers; the install the after, the tree
  clean; the landing check: no item (control: without `Role: owner` it is a P1 on `operator-own`); **a planted CTO commit of `CLAUDE.md`
  is now a P1 on `agent-instructions`** (and none with the before table back); the undo after the commit; the undo before the commit, with
  and without `git add`.

The operator's own code on the bundle (`build_act.py gates`, read only): `validate_manifest` pass; 18 files hash as the
manifest says, none unlisted, no `__pycache__`; the path rule passes on `apply.sh` and all five checks; `act_class.classify`: class O (three
rows `operator-own`), no hit, also on the LANDING base's rows and under its own after table. Clone head: `8801ffd17df9`.

## 5. The operator's exact steps
**By hand, the owner's operator,** in the main tree, not at a :x0 minute (the cron's launch), with nothing queued for the operator, and
after ACT-LANDING-CTO-ROUTE-1 if that is applied today (its `verify` run first; section 7). Before you start, tell the CTO "starting
CLASS-RULES-AGENTS-1"; the CTO writes `log/act-in-progress.txt` (it holds the operator at G9 and the CTO's lands) and removes it when you send
the commit id.
```bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLASS-RULES-AGENTS-1
bash $G/apply.sh check     # exit 0: "check: ready to apply on the install as built ..." (or "... on the install after ACT-LANDING-CTO-ROUTE-1 ...")
bash $G/apply.sh apply     # exit 0: "apply: repo/...class-rules.yaml", "apply: home/.../class-rules.yaml", "apply: home/.../APPROVED", "the install's own APPROVED check: ok", "APPROVED <sha256>", "state applied (...)"
bash $G/apply.sh verify    # exit 0: "verify: every listed file is the after (...); the install's other files as built"
git status --short -- governance/project/operator/class-rules.yaml    # one line: " M governance/project/operator/class-rules.yaml"
git add governance/project/operator/class-rules.yaml
git commit -m "ACT-CLASS-RULES-AGENTS-1: CLAUDE.md and AGENTS.md a fixed class (b) in the operator's rule table, row agent-instructions (DEC-1173)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1173" --trailer "Role: owner" -- governance/project/operator/class-rules.yaml
git log -1 --format='%h %s'
```
`APPROVED` after the apply is `af28cefe7b99c91d3bf780639746deef71f25e56e101f5ac796b06a2922417d7` (today's install) or
`4209aac246a9765962b5c612289deb5bb585724d553a10935f237508421a8f3a` (after ACT-LANDING-CTO-ROUTE-1). Send the CTO the commit id (12 digits)
and the `APPROVED` line. If `check` stops (exit 3: a file moved; exit 4: a frozen copy altered; exit 6: the operator is busy), send its line
to the CTO and apply nothing (exit 6: wait and run it again). If `apply` stops part way (a full disk, a kill), run it again: it finishes.

**The check line after it:** `apply.sh verify` exits 0; the manifest's five checks pass: the install's table and `APPROVED` hash as the
after; `APPROVED` names the new table; the install's own `act_class` routes `CLAUDE.md` and `AGENTS.md` to `agent-instructions` (b), the home
`~/.claude/CLAUDE.md` to `agents-skills-kernel` (b) and `docs/CLAUDE.md` to `unknown` (O); the tree's file is the after.

**Undo before the commit** (after an apply, with or without the `git add`):
```bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLASS-RULES-AGENTS-1
bash $G/apply.sh undo      # exit 0: "undo: ..." three lines, "the install's own APPROVED check: ok", "state before (undone) (...)"
git restore --staged -- governance/project/operator/class-rules.yaml   # takes back a git add, if one was run (no output)
bash $G/apply.sh check     # exit 0: ready to apply again
git status --short -- governance/project/operator/class-rules.yaml    # no output
```
**Undo after the commit** (whatever landed on top, as long as nobody changed `class-rules.yaml` since; with the CTO holding, as for the
apply; **not after ACT-CLAUDE-RULES-1 is queued or applied as (b)**: undo that one first, or its class goes back to (O)):
```bash
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLASS-RULES-AGENTS-1
git diff --quiet HEAD -- governance/project/operator/class-rules.yaml   # exit 0: the tree's file is as committed (otherwise stop: tell the CTO)
bash $G/apply.sh undo      # exit 0: the tree's class-rules.yaml and the install's two files back to the before
bash $G/apply.sh check     # exit 0: ready to apply again
git add governance/project/operator/class-rules.yaml
git commit -m "ACT-CLASS-RULES-AGENTS-1 undone: CLAUDE.md and AGENTS.md back to the catch-all (the owner's undo of DEC-1173)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1173" --trailer "Role: owner" -- governance/project/operator/class-rules.yaml
git log -1 --format='%h %s'
```
No reset and no revert: the undo is a second `Role: owner` commit of the before bytes. **By hand** (only if `apply.sh` cannot run):
`before/home/gov-os-operator/install/class-rules.yaml` then `.../APPROVED` over the install's two files (mode 0444; nothing queued, no launch
running; on the LANDING base the copies under `alt/landing/before/`), and `before/repo/...` over the tree's file.

## 6. The yes line
**After the independent review is in `review.md`** (its fenced verdict block), the owner sends, on its own line:

yes ACT-CLASS-RULES-AGENTS-1 244d5a39

(the first 8 digits of the manifest's sha256 `244d5a399df53418f02e93f97b44222605645260dea20ffe7bc17f1734aadc09`, section 9). Then the owner's operator runs section 5.

## 7. The order with ACT-LANDING-CTO-ROUTE-1 and ACT-CLAUDE-RULES-1
| Applied | Result |
|---|---|
| **ACT-LANDING-CTO-ROUTE-1, then this ACT** (if both are approved today) | both apply; this ACT verifies; LANDING's own `verify` then exits 3 (its `keep.txt` pins today's `class-rules.yaml`), so run LANDING's verify **before** this ACT. Undo in reverse order: both exit 0 (rehearsed). |
| **this ACT alone** (LANDING not applied today) | applies on today's install; LANDING would then refuse at `check` (exit 3, "moved: home/gov-os-operator/install/APPROVED"; its `keep.txt` also pins today's table), nothing touched, and need a rebuild by the CTO and a new yes. |
| **this ACT, then ACT-CLAUDE-RULES-1** | RULES-1 (rebuilt as (b), its own package) is queued for the operator agent only after this ACT's commit, its review and DEC-1173 in the register. |

No other bundle on the machine touches the install or the table with a live before (every `manifest.json` under `acts/`: only S15-1 (applied),
OPERATOR-HOURS-2/3 (applied) and LANDING-CTO-ROUTE-1 (pending)).

## 8. Risks, and what I did not do
1. **Not independently reviewed.** The CTO's ordinary review round before the owner's yes; `review.md` needs the reviewer's fenced verdict
   block (the operator's G4 reads it even for a hand-applied ACT's record). **Review: not written yet.**
2. **New landing-check items.** After this ACT, a CTO commit (`Task: DAEO-sdxk`) that touches `CLAUDE.md` or `AGENTS.md` without
   `Role: owner` or `Role: operator` with `Act:` is a P1 inbox item (the intent of `control: true`). No such commit is planned; RULES-1 goes
   through the operator (`Role: operator`, `Act:`).
3. **A session already running** reads the table at G6 and at the recompute, from the install; `APPROVED` is checked by the launcher (a launch
   in the instant between the table and `APPROVED` refuses "APPROVED mismatch" once; hence "not at a :x0 minute" and the CTO's hold).
4. **Not rehearsed:** the owner's commit under the main tree's hooks (the `reference-transaction` freeze gate, the landing and trailer checks;
   the clones have git's defaults); a real cron launch.

## 9. Files and hashes
| File (`acts/ACT-CLASS-RULES-AGENTS-1/`) | sha256 |
|---|---|
| `before/{repo/governance/project/operator,home/gov-os-operator/install}/class-rules.yaml` (the live bytes, both; also under `alt/landing/`) | `38ac2f2decce660a9e190c85038b7175dcbae0e0c0ce79acc0597df17d0e79a4` |
| `after/.../class-rules.yaml` (both; also under `alt/landing/`) | `a040a103cbda4f6fb28a0060464c43689b780bd83cdee591a76a60f23b68b2eb` |
| `before/home/gov-os-operator/install/APPROVED` (the live one) | `3744df3a637feadc26c673b88a10cbc757e8c8746aced078d700300906962815` |
| `after/home/gov-os-operator/install/APPROVED` | `af28cefe7b99c91d3bf780639746deef71f25e56e101f5ac796b06a2922417d7` |
| `alt/landing/before/home/gov-os-operator/install/APPROVED` (LANDING-CTO-ROUTE-1's after) | `ef5afbac78f3fce16ab7551ef88987a6898acd8f9a7a18439bf83aeb9216c157` |
| `alt/landing/after/home/gov-os-operator/install/APPROVED` | `4209aac246a9765962b5c612289deb5bb585724d553a10935f237508421a8f3a` |
| `apply.sh` | `41a83378d91e01cb2804462c5497fa5a70a51ee55877063304c082c0c3b54725` |
| `list.txt`, `alt/landing/list.txt` (root, path, before, after; in apply order, `APPROVED` last) | `ed75287458d9`, `0145aa1a068d` |
| `keep.txt`, `alt/landing/keep.txt` (the thirteen install files the ACT leaves, per base) | `2ed5eb2bcaad`, `d926966c02db` |
| `rehearsal.log` | `e3652b6668bf3494f933e8bf116277bbf729ffd582a2cf6c23f786e4f88b6ddc` |
| **`manifest.json`** | **`244d5a399df53418f02e93f97b44222605645260dea20ffe7bc17f1734aadc09`** |

The bundle depends on the live install, the tree's `class-rules.yaml` (committed at `4be656e70`) and LANDING-CTO-ROUTE-1's bundle as they
are now: if any moves before the apply, `check` says so and the CTO rebuilds (`build_act.py all`).
