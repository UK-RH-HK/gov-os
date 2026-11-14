# ACT-CLAUDE-RULES-1: the "## Guard" paragraph of the governance rule, true for this repository (DEC-1167 (7)), class (b) (DEC-1173)

- **For:** the owner (one yes line), then **the operator agent** (class **(b)**, DEC-1173), **only after ACT-CLASS-RULES-AGENTS-1 is applied
  and committed** (that ACT adds the rule-table row `agent-instructions` that makes `CLAUDE.md` and `AGENTS.md` (b); before it, the table
  sends them to the (O) catch-all and the operator's G6 refuses this bundle as "yours").
- **Round b.** This is the bundle rebuilt from round O (manifest `83c5faf6c4ac…`, class O, by hand), on the owner's decision (DEC-1173,
  2026-11-13: "Go for the class-rules ACT (the agent-instructions row), then ACT-CLAUDE-RULES-1 as class (b)"). **The content is unchanged:**
  the three files' before and after bytes, `list.txt` and `apply.sh` are byte for byte round O's (asserted by the builder); `CLAUDE.md`,
  `AGENTS.md` and `.rulesync/rules/governance.md` have not moved since round O was built (the live files are at the before hashes). What
  changed: the manifest's `claimed_class` (`O` to `b`), its `dec` (DEC-1173 added), the rehearsal (re-run), the manifest sha256. Round O's
  files, with its package, are kept at `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1.round-O/`.
- **By:** an ACT-preparation helper of the CTO; round O 2026-11-13 ~14:30 UTC, round b ~20:00 UTC. **Nothing live was changed or started:**
  no commit, no stage, nothing in the main tree's tracked files, no queue line, nothing under `~/gov-os-operator` or `.claude/`. Rehearsed
  on fresh clones of `w2/integrate` (`8801ffd17df9`) under `/tmp/claude-1000/act-claude-rules-1-b/`. **Not yet independently reviewed** (section 8).
- **Under:** **DEC-1167 (7)** (the owner, 2026-11-13: "The correction of CLAUDE.md's guard sentence comes by its route"); **DEC-1173** (the class);
  DEC-953 item 2 (the live hook keeps its own rules); DEC-1128 (4) and SANDBOX-1 (the OS sandbox of `gov launch`); DEC-820; CAP-33. Manifest
  `dec`: "DEC-1167 (7), DEC-1173, DEC-953 (2), DEC-1128 (4), DEC-820, CAP-33". All five DEC ids are ACCEPTED in the register (G2, read at the
  rehearsal, F6).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-claude-rules-1/` (`patch_source.py` makes the new source from the live one;
  `build_claude_rules_act_1b.py` builds and rehearses round b, `build_claude_rules_act_1.py` was round O's; `evidence-b/`, `rehearse-b.out`).
  **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1/`.

## 0. The short version, the yes line, and the steps

1. **What changes (3 files, each rewritten):** the "## Guard" paragraph of `.rulesync/rules/governance.md` (the one source of the root rule) and the
   two files rulesync 24.0.0 generates from it, `CLAUDE.md` and `AGENTS.md` (AGENTS.md also carries rulesync's two-line convention header). Every
   byte of the two copies is rulesync's output, never typed: the builder runs `rulesync generate` (portability's own GENERATE arguments) from the
   new source in an empty folder, then the held-out step (`gov.guard.heldout`) on the generated settings, as `gov.adapters.portability` does, and asserts
   that nothing else the generation writes differs from the tree except the one file that already differed before (`.claude/skills/adopt/SKILL.md`,
   another ACT's window). `template/.rulesync/rules/governance.md` (the product's text, true there) is **not** changed (hash-checked, rehearsal B2).
2. **The paragraph.** Before: "The guard enforces allowed paths, tool restrictions and permission classes at runtime. It refuses writes outside a
   ticket's scope, denies installs for non-orchestrator roles, and blocks access to held-out paths. Reads are open; only secrets, ... , and writes stay
   inside the ticket's paths (DEC-820). The guard decides; role files state." After:
   > Here, since DEC-953 item 2, the live hook (`.claude/hooks/pretooluse.py`) keeps five rules: only the independent test designer writes acceptance
   > tests; the held-out material and the hidden half of an evaluation set are not read; independent reviewers and auditors write only their own
   > outcomes; secrets and keys are not read; and an install asks the owner in the CTO's own session and is refused in every other. It also refuses the
   > catastrophic deletes and applies the path map's role separation. It has no rule that keeps a worker's writes inside its ticket's paths: a launched
   > worker's writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4)), not by the hook. In an adopted product
   > the kernel guard enforces allowed paths, tool restrictions and permission classes at runtime. Reads are open; only secrets, the held-out material's
   > contents, the counterpart's work on the same ticket and the hidden half of an evaluation set are refused (DEC-820). The guard decides; role files state.

   The reads sentence is kept (its closing clause "and writes stay inside the ticket's paths" dropped, its `(DEC-820)` kept) and so is the last sentence; the two statements on writes are replaced.
3. **The five rules, checked against the hook's own header** (`.claude/hooks/pretooluse.py`, docstring: "It keeps exactly five rules, and the
   catastrophic deletes"): 1 only the independent test designer writes `tests/acceptance/**`; 2 no reads of the hidden half of an evaluation set (by the
   sessions it measures) or of the held-out material (every role), with 2b to 2d; 5 independent reviewers and auditors write only their own outcomes;
   3 no reads of secrets or keys; 4 no installs without the owner (asked only in the CTO's own session, refused in every other, `sudo` refused). Then
   `rm` is free but for the catastrophic, and the path map's role separation (`role_paths`) applies. The brief's example list differs ("the
   counterpart's work" and "the frozen paths" are not among the header's five), so the text follows the header; the counterpart's work stays in the
   kept reads sentence. Since rules 1, 5 and 2d do limit some writes, the text says there is no rule that keeps a worker's writes **inside its
   ticket's paths**, not that the hook has no write rule.
4. **Class (b), measured, after ACT-CLASS-RULES-AGENTS-1.** `act_class.classify` on this bundle: with **ACT-CLASS-RULES-AGENTS-1's after
   table**, class **(b)**: `.rulesync/rules/governance.md` row `rulesync-other` (b), `CLAUDE.md` and `AGENTS.md` row `agent-instructions` (b),
   no script hit (rehearsal F4b). With **today's live table** it is still (O) (`CLAUDE.md`, `AGENTS.md` on the catch-all `unknown`, F4a): so the
   request is written only after that ACT's apply and commit. The manifest claims `b`; the reviewer's vote makes the third.

**The order:** (1) ACT-CLASS-RULES-AGENTS-1 reviewed, the owner's yes, applied by hand and committed (its package); (2) this ACT's review
(`review.md`, the operator's fixed reviewer brief, the fenced verdict block G4 reads); (3) the owner's yes line below in the CTO session;
(4) the CTO writes the request line; the operator agent runs it.

## 1. The yes line (the owner's line, on its own line)

yes ACT-CLAUDE-RULES-1 199dd123

(the first 8 digits of the manifest's sha256 `199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26`.) **Round O's line
`yes ACT-CLAUDE-RULES-1 83c5faf6` is void**: that manifest is no longer the bundle's.

## 2. The operator's steps

**By the operator agent** (the route): after ACT-CLASS-RULES-AGENTS-1's commit, this ACT's review and the owner's yes, the CTO writes the
request line in `~/gov-os-operator/queue/` (manifest sha256 `199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26`). The agent
runs its gates: G2 (all five DEC ids ACCEPTED), G4 (the verdict block), G6 (code b, claim b, review), G7 (the dry run: `apply.sh check` exits 0
and prints nothing; `apply`), G8 (the manifest's four checks: the three after hashes, the template's hash, none of the replaced sentences, the
new sentence in all three), then `git add` of the three paths and its own commit (`Role: operator`, `Act: ACT-CLAUDE-RULES-1`, `Act-sha:`,
`Class: b`, `Review:`, `Approved-by:`). The landing check raises nothing for that commit under the new table (rehearsal D3b); the same tree as
a plain CTO commit would be one P1 on `agent-instructions` and `rulesync-other` (D3c). The CTO tells the owner nothing more is needed unless the
agent's notice says otherwise. `.rulesync/**` is a landing-select trigger, so the landing runs the scoped suites for the commit.

**Or by hand, by the owner** (the fallback, as round O; `Role: owner`; tell the CTO "starting RULES-1" so it lands nothing until the commit):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no -- .rulesync/rules/governance.md CLAUDE.md AGENTS.md)" && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1
sha256sum $G/manifest.json      # expect 199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26
bash $G/apply.sh check && bash $G/apply.sh apply    # check prints nothing and exits 0; if a file moved: "moved: <path>", exit 3
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 3
git commit -m "ACT-CLAUDE-RULES-1: the Guard paragraph of the governance rule is true for this repository (DEC-1167 (7))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1167, DEC-1173" --trailer "Role: owner" -- $F
```
After the commit, `python3 -m gov.adapters.portability` (PYTHONPATH `src`, `RULESYNC_BIN`) reads the same findings as before (one,
`.claude/skills/adopt/SKILL.md`) and none on the three files. `.claude/settings.json` is **not regenerated**: the generation with the held-out
step reproduces the live file byte for byte before and after (rehearsal B10), so there is nothing to write.

## 3. The files

| file | old sha256 | new sha256 |
|---|---|---|
| `.rulesync/rules/governance.md` | `aab9e7c05dd61f6fb734cc8973e0489c5f176362971c7b4b869c8b016a5155d7` | `3b141726f84a87317c6a745193f8fe671da66208ca0e1f35ec63f9e5b8daabc7` |
| `CLAUDE.md` | `f672e46802d34c2fbc6340b97b06336c0f93119785572f45a67a49e13d258249` | `65e244836adf4ed79a158b144e5b80bfd022d17b414991e19c3530ef6c2639f2` |
| `AGENTS.md` | `18e826269b0a0cdc02883c206162d7694b2a9fecc8ce43a578b4c94013eae7d0` | `931f1fe2014e52c7e899dd0589b6f78b308d16fce778c3b2eb4f13aa6527faa1` |

`template/.rulesync/rules/governance.md` stays at `b7ff8b723440819e64ef527ffd40cf667b3230cb10d8c695938f66282254ee9f`. All as round O.

## 4. Why the three go together

The source alone (the copies not yet written) is a drift: portability reads `GENERATED_DIFFERS` for `CLAUDE.md` and `AGENTS.md` (rehearsal C1). The copies
without the source are drift the other way. So one apply writes all three, and `check` refuses unless all three are at their before hash (C2 to C4).

## 5. The rehearsal (`rehearsal.log`, 49 cases, last line `failures: 0`)

Fresh `--no-hardlinks` clone of `w2/integrate` (`8801ffd17df9`), HOME planted at an empty folder, `apply.sh` run from the bundle, every pytest
through `heavy_slot.sh` with `TMPDIR` under `/tmp/claude-1000/act-claude-rules-1-b/`. A: the bundle (hashes, list, the live files at the before,
`apply.sh` the copies ACTs' own, no `__pycache__`). B: the three at their before hashes, the template unchanged, `apply.sh check` (exit 0, silent),
the manifest's checks before (refuse) and after (pass), apply, the changed set is the three files, `.claude/settings.json` and the template untouched,
**an independent rulesync generation** from the applied source gives the two copies byte for byte and the held-out step gives the settings byte for
byte, portability after equals before, `check` after refuses, undo byte for byte with the tree clean, apply again. C: the source alone reads as
drift; each of the three changed refuses `check` by name; no test names the replaced sentences. D: the hand steps literally (stage, commit with
`Role: owner`, the landing check raises nothing, undo, undo commit, empty diff, again); **D3b the operator agent's commit form under
ACT-CLASS-RULES-AGENTS-1's table: no landing item; D3c the same tree as a CTO commit: one P1 (rows `agent-instructions`, `rulesync-other`).**
E: the suites, each before and after on the same base: `tests/unit/adapters` 102 passed; `W1-38` 42; `W2-23` 32 passed and 1 failed
(`test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`, red before and after: not this ACT's); `W2-153`
137 passed, 18 skipped; `W2-98` 502; `W2-106` 26; `W1-33` 112; new red brought by the ACT: none. F: the operator's `validate_manifest`,
`check_act`, `path_rule` pass; **F4a `act_class` with the live table (O); F4b with ACT-CLASS-RULES-AGENTS-1's after table (b), the claim's**;
F5 no unlisted file; F6 the register: DEC-1167, DEC-1173, DEC-953, DEC-1128, DEC-820 all ACCEPTED. G: the main tree's files and the planted HOME
unchanged.

## 6. Undo

By the operator: `undo ACT-CLAUDE-RULES-1 199dd123` (its own undo and commit). By hand: `bash $G/apply.sh undo` (the three put back byte for
byte; the tree is clean, rehearsal B13), then `git add -A $F` and a commit with `Role: owner`. Undo this ACT **before** any undo of
ACT-CLASS-RULES-AGENTS-1 (without that row, this bundle classes (O) again and the operator would refuse its own undo's class check).

## 7. Risks

- **The text is the CTO's reading of the hook, checked against its header.** If the owner prefers the brief's list, the source text changes and the
  ACT is rebuilt (the builder takes `patch_source.py`).
- **The order.** Queued before ACT-CLASS-RULES-AGENTS-1 is applied, the operator's G6 refuses it ("class (O): yours"); nothing is changed, the
  request is written again after.
- **The window:** none inside the apply; the three files change together.
- **`gov adapters generate` in an adopted product** merges its generated block into a programme's own `CLAUDE.md`; this repository's `CLAUDE.md` is
  rulesync's output byte for byte (portability compares it so). Nothing here changes how the product generates.
- **Not rehearsed:** the operator agent's real run (its walled session, the cron launch) on this bundle; the rehearsal ran its gate functions
  read-only, its commit form against the landing check, and the apply and checks it runs.

## 8. Hashes, and before the yes

| file | sha256 |
|---|---|
| `apply.sh` (the copies ACTs' own) | `84f6f595968947de01022ba7561961648b58db9df1a6e808242948259072a231` |
| `list.txt` | `a9b3b90cd70817375c52fee7d50205b48385bdd18b3b331e57ff9bbb7f87672e` |
| `rehearsal.log` | `3c9ba3cf9a0283ce157480360b4549be9476ab37bccd23470c2aa7bb8a233e0d` |
| `manifest.json` | `199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26` |

- One independent review (the operator's fixed reviewer brief; verdict block in `review.md`). **Review: not written yet.** (Round O had none either.)
- ACT-CLASS-RULES-AGENTS-1 applied and committed first.
- The CTO tells the owner when the review is in; the owner sends the yes line (section 1).
