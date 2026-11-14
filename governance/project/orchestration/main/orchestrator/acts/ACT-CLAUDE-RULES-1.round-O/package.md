# ACT-CLAUDE-RULES-1: the "## Guard" paragraph of the governance rule, true for this repository (DEC-1167 (7))

- **For:** the owner (one yes line), then **the owner, by hand** (class **(O)**, measured; section 0.4). About three minutes.
- **By:** an ACT-preparation helper of the CTO, 2026-11-13 from about 14:30 UTC. **Nothing live was changed or started:** no commit, no stage,
  nothing in the main tree's tracked files, no queue line, nothing under `~/gov-os-operator` or `.claude/`. Built and rehearsed on fresh clones of
  `w2/integrate` (`79159cd44c5b`) under `/tmp/claude-1000/acts-landing-rules/`. **Not yet independently reviewed** (section 8).
- **Under:** **DEC-1167 (7)** (the owner, 2026-11-13: "The correction of CLAUDE.md's guard sentence comes by its route"); DEC-953 item 2 (the live
  hook keeps its own rules); DEC-1128 (4) and SANDBOX-1 (the OS sandbox of `gov launch`); DEC-820; CAP-33. Manifest `dec`: "DEC-1167 (7), DEC-953
  (2), DEC-1128 (4), DEC-820, CAP-33".
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-claude-rules-1/` (`patch_source.py` makes the new source from the live one;
  `build_claude_rules_act_1.py` builds and rehearses; `evidence/`). **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1/`.

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
   sessions it measures) or of the held-out material (every role), with 2b to 2d (the sets root's hidden folders, the session-hidden folders, writes into
   the operator's folder and the call log); 5 independent reviewers and auditors write only their own outcomes; 3 no reads of secrets or keys; 4 no
   installs without the owner (asked only in the CTO's own session, refused in every other, `sudo` refused). Then `rm` is free but for the catastrophic,
   and the path map's role separation (`role_paths`) applies. **The brief's example list differs** ("the counterpart's work" and "the frozen paths" are
   not among the header's five; the counterpart's work is the path map's role separation, and no "frozen paths" rule is in the file), so the text above
   follows the header; the counterpart's work stays in the kept reads sentence. And since rules 1, 5 and 2d do limit some writes, the text says there
   is no rule that keeps a worker's writes **inside its ticket's paths**, not that the hook has no write rule.
4. **Class (O), measured, not (b).** `act_class.classify` gives **(O)**: `.rulesync/rules/governance.md` is the `rulesync-other` row (b, control), but
   `CLAUDE.md` and `AGENTS.md` are named by **no row** of `class-rules.yaml`, so they fall to the catch-all (O, not a control path): "a path no rule
   names". The manifest claims `O` (the three votes agree); the operator agent's G6 would refuse it ("yours"), and the CTO's route (ACT-LANDING-CTO-ROUTE-1)
   needs (b), so **the owner applies it by hand with `Role: owner`**. Options if the owner wants (b): section 7.

**The owner's line, on its own line:**

yes ACT-CLAUDE-RULES-1 83c5faf6

(the first 8 digits of the manifest's sha256 `83c5faf6c4ac2ff3267d7c58fdb830afb8ce44494b061a877c683c72620e074f`, section 6.)

**The steps** (the owner, in the main tree; nothing queued for the operator; tell the CTO "starting RULES-1" so it lands nothing until the commit):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
test -z "$(git status --short --untracked-files=no -- .rulesync/rules/governance.md CLAUDE.md AGENTS.md)" && echo clean
G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1
sha256sum $G/manifest.json      # expect 83c5faf6c4ac2ff3267d7c58fdb830afb8ce44494b061a877c683c72620e074f
bash $G/apply.sh check && bash $G/apply.sh apply    # check prints nothing and exits 0; if a file moved: "moved: <path>", exit 3
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 3
git commit -m "ACT-CLAUDE-RULES-1: the Guard paragraph of the governance rule is true for this repository (DEC-1167 (7))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1167" --trailer "Role: owner" -- $F
```
**The check that each of the three is at its before hash** is `apply.sh check` (it hashes the live files against `list.txt`) and the rehearsal's B1;
`.rulesync/**` is a landing-select trigger, so the landing runs the scoped suites for the commit (a `Role: owner` commit is not a P1). After the
commit, `python3 -m gov.adapters.portability` (PYTHONPATH `src`, `RULESYNC_BIN`) reads the same findings as before (one, `.claude/skills/adopt/SKILL.md`) and
none on the three files. `.claude/settings.json` is **not regenerated**: the generation with the held-out step reproduces the live file byte for
byte before and after (rehearsal B10), so there is nothing to write.

## 1. The files

| file | old sha256 | new sha256 |
|---|---|---|
| `.rulesync/rules/governance.md` | `aab9e7c05dd61f6fb734cc8973e0489c5f176362971c7b4b869c8b016a5155d7` | `3b141726f84a87317c6a745193f8fe671da66208ca0e1f35ec63f9e5b8daabc7` |
| `CLAUDE.md` | `f672e46802d34c2fbc6340b97b06336c0f93119785572f45a67a49e13d258249` | `65e244836adf4ed79a158b144e5b80bfd022d17b414991e19c3530ef6c2639f2` |
| `AGENTS.md` | `18e826269b0a0cdc02883c206162d7694b2a9fecc8ce43a578b4c94013eae7d0` | `931f1fe2014e52c7e899dd0589b6f78b308d16fce778c3b2eb4f13aa6527faa1` |

`template/.rulesync/rules/governance.md` stays at `b7ff8b723440819e64ef527ffd40cf667b3230cb10d8c695938f66282254ee9f`. The manifest's four checks, run after the apply: the three after hashes (`sha256sum -c`),
the template's hash, none of the replaced sentences in the three files, and the new sentence in all three.

## 2. Why the three go together

The source alone (the copies not yet written) is a drift: portability reads `GENERATED_DIFFERS` for `CLAUDE.md` and `AGENTS.md` (rehearsal C1). The copies
without the source are drift the other way. So one apply writes all three, and `check` refuses unless all three are at their before hash (C2 to C4).

## 3. The rehearsal (`rehearsal.log`, last line `failures: 0`)

Fresh `--no-hardlinks` clone of `w2/integrate` (`79159cd44c5b`), HOME planted at an empty folder, `apply.sh` run from the bundle as the owner will, every pytest
through `heavy_slot.sh` with `TMPDIR` under `/tmp/claude-1000/`. A: the bundle. B: the three at their before hashes, the template unchanged, `apply.sh
check` (exit 0, silent), the manifest's checks before (refuse) and after (pass), apply, the changed set is the three files, `.claude/settings.json` and
the template untouched, **an independent rulesync generation** from the applied source gives the two copies byte for byte and the held-out step gives the
settings byte for byte, portability after equals before, `check` after refuses, undo byte for byte with the tree clean, apply again. C: the source
alone reads as drift; each of the three changed refuses `check` by name; no test names the replaced sentences. D: the owner's steps literally (stage,
commit with `Role: owner`, the operator's landing check raises nothing, undo, undo commit, empty diff, again). E: the suites that read the rules, the
copies, portability or the rulesync sources, each before and after on the same base: `tests/unit/adapters` 102 passed; `W1-38` 42; `W2-23` 32 passed and 1 failed (`test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir`, red before and after: not this ACT's); `W2-153` 66; `W2-98` 502; `W2-106` 26; `W1-33` 112; new red brought by the ACT: none. F: the operator's `validate_manifest`, `check_act`,
`path_rule` pass; `act_class` gives (O). G: the main tree's files and the planted HOME unchanged.

## 4. Risks

- **The text is the CTO's reading of the hook, checked against its header.** If the owner prefers the brief's list, the source text changes and the ACT is
  rebuilt (the builder takes `patch_source.py`).
- **The window:** none inside the apply; the three files change together. A concurrent landing between the apply and the commit would carry them: the
  CTO holds landings for the three minutes.
- **`gov adapters generate` in an adopted product** merges its generated block into a programme's own `CLAUDE.md`; this repository's `CLAUDE.md` is rulesync's
  output byte for byte (portability compares it so). Nothing here changes how the product generates.

## 5. Undo

`bash $G/apply.sh undo` (the three put back byte for byte; the tree is clean, rehearsal B13), then `git add -A $F` and a commit with `Role: owner`.

## 6. Hashes

| file | sha256 |
|---|---|
| `apply.sh` (the copies ACTs' own) | `84f6f595968947de01022ba7561961648b58db9df1a6e808242948259072a231` |
| `list.txt` | `a9b3b90cd70817375c52fee7d50205b48385bdd18b3b331e57ff9bbb7f87672e` |
| `rehearsal.log` | `242634a23d37aede94ad739a5ad29985d948fe87c003c17f6fb0ba9582a6965e` |
| `manifest.json` | `83c5faf6c4ac2ff3267d7c58fdb830afb8ce44494b061a877c683c72620e074f` |

## 7. Options for the owner (proposed decisions, none taken here)

- **(O) by hand, as built** (the owner's three minutes, no rule-table change).
- **(b) by the CTO's route:** add one row to `class-rules.yaml` (the operator's install, an (O) ACT of its own): `root-instructions`, match `CLAUDE.md` and
  `AGENTS.md`, class b, control true. Cost: another install file and APPROVED line (a second bundle or an added file in ACT-LANDING-CTO-ROUTE-1, rebuilt and
  re-reviewed); effect: edits to the two root files by anyone outside a ticket become landing-check items, and this ACT would be (b) for the CTO after
  ACT-LANDING-CTO-ROUTE-1.
- **A different text** (the brief's list, or shorter): the source is changed and the bundle rebuilt.

## 8. Before the yes

- One independent review (verdict block in `review.md`). **Review: not written yet.**
- The CTO tells the owner when the review is in; the owner sends the yes line.
