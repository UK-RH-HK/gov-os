# ACT-CLAUDE-RULES-1: the "## Guard" paragraph of the governance rule, true for this repository (DEC-1167 (7)), class (b) (DEC-1173)

- **For:** the owner (one yes line), then **the operator agent** (class **(b)**, DEC-1173), **only after ACT-CLASS-RULES-AGENTS-1 is applied
  and committed** (that ACT adds the rule-table row `agent-instructions` that makes `CLAUDE.md` and `AGENTS.md` (b); before it, the table
  sends them to the (O) catch-all and the operator's G6 refuses this bundle as "yours").
- **Round b2.** The rounds: **round O** (manifest `83c5faf6c4ac…`, class O, by hand; kept at `acts/ACT-CLAUDE-RULES-1.round-O/`);
  **round b1** (manifest `199dd123fb0e…`, class b on DEC-1173, the same text; kept at `acts/ACT-CLAUDE-RULES-1.round-b1/`), which passed its
  independent review (`.gov-runtime/scratch/orchestrator/reviews/act-claude-rules-1-b.md`, copy `acts/ACT-CLAUDE-RULES-1.review-b-round-1.md`)
  with three text rows; **round b2, this bundle:** the paragraph with all three folded in, at the CTO's direction, so the text agents load is
  exact: **F1** the hook's rule 2d (no session writes into the operator agent's folder, but its queue/, or the guard's call log) and rule 4's
  sudo refusal; **F2** rule 2b's write refusal (the sets root's hidden folders) and rule 2c's wall for named sessions (the engineer on W2-56);
  **F3** the five rules cited to DEC-953 item 2 (four) and DEC-954 (the fifth). Every sentence was checked again against
  `.claude/hooks/pretooluse.py` and `.claude/hooks/bash_writes.py`; from that re-read two more exact points went in: the write rules judge
  only the writes the guard resolves from a Bash line (one it cannot work out is let through, with the landing's and the review's backstops;
  ACT-GUARD-FIX-4), and the role separation (G-14) is a read rule. The befores are round b1's (the three live files have not moved, asserted);
  the class (b), `apply.sh`, the checks and the dependency on ACT-CLASS-RULES-AGENTS-1 are unchanged. **Round b1's review does not carry over:
  this bundle needs its own** (`review.md` is the placeholder).
- **By:** an ACT-preparation helper of the CTO; round O 2026-11-13 ~14:30 UTC, round b1 ~20:00 UTC, round b2 ~21:15 UTC. **Nothing live was
  changed or started:** no commit, no stage, nothing in the main tree's tracked files, no queue line, nothing under `~/gov-os-operator` or
  `.claude/`. Rehearsed on fresh clones of `w2/integrate` (`9a467f3360a9`) under `/tmp/claude-1000/act-claude-rules-1-b2/`. **Not yet independently
  reviewed** (section 8).
- **Under:** **DEC-1167 (7)** (the owner, 2026-11-13: "The correction of CLAUDE.md's guard sentence comes by its route"); **DEC-1173** (the class);
  DEC-953 item 2 and DEC-954 (the live hook's five rules); DEC-1128 (4) and SANDBOX-1 (the OS sandbox of `gov launch`); DEC-820; CAP-33. Manifest
  `dec`: "DEC-1167 (7), DEC-1173, DEC-953 (2), DEC-1128 (4), DEC-820, CAP-33" (as round b1). All five DEC ids are ACCEPTED in the register
  (G2, read at the rehearsal, F6).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-claude-rules-1/` (`patch_source.py` makes the new source from the live one, round
  b1's text in `patch_source.round-b1.py`; `build_claude_rules_act_1c.py` builds and rehearses round b2, `_1b.py` was round b1's, `_1.py`
  round O's; `evidence-b2/`, `rehearse-b2.out`). **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1/`.

## 0. The short version, the yes line, and the steps

1. **What changes (3 files, each rewritten):** the "## Guard" paragraph of `.rulesync/rules/governance.md` (the one source of the root rule) and the
   two files rulesync 24.0.0 generates from it, `CLAUDE.md` and `AGENTS.md` (AGENTS.md also carries rulesync's two-line convention header). Every
   byte of the two copies is rulesync's output, never typed: the builder runs `rulesync generate` (portability's own GENERATE arguments) from the
   new source in an empty folder, then the held-out step (`gov.guard.heldout`) on the generated settings, as `gov.adapters.portability` does, and asserts
   that nothing else the generation writes differs from the tree (at round b2's build nothing else differed; at round O, one file in another
   ACT's window, since landed). `template/.rulesync/rules/governance.md` (the product's text, true there) is **not** changed (hash-checked, rehearsal B2).
2. **The paragraph.** Before: "The guard enforces allowed paths, tool restrictions and permission classes at runtime. It refuses writes outside a
   ticket's scope, denies installs for non-orchestrator roles, and blocks access to held-out paths. Reads are open; only secrets, ... , and writes stay
   inside the ticket's paths (DEC-820). The guard decides; role files state." After:
   > Here the live hook (`.claude/hooks/pretooluse.py`) keeps five rules (DEC-953 item 2, and DEC-954 for the fifth): only the independent test
   > designer writes acceptance tests; the held-out material is not read, nor the hidden half of an evaluation set by the sessions it measures, and the
   > sets root's hidden folders are neither read nor written by the roles the path map refuses them; independent reviewers and auditors write only their
   > own outcomes; secrets and keys are not read; and an install asks the owner in the CTO's own session and is refused in every other, while sudo is
   > refused to every session. It also refuses the catastrophic deletes; refuses every session's writes into the operator agent's folder (but its queue/)
   > and into the guard's call log; refuses named sessions reads and writes of the folders the path map walls off for them (the engineer on W2-56: the raw
   > transcripts); and applies the path map's role separation to reads. Its write rules judge a Bash line by the writes the guard resolves from it
   > (`.claude/hooks/bash_writes.py`): a write whose target it cannot work out is let through, and for the acceptance-test and reviewer rules the
   > backstops are the landing's check of acceptance-test commits and the reviewed tree's git status. It has no rule that keeps a worker's writes inside
   > its ticket's paths: a launched worker's writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4)), not by
   > the hook. In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at runtime. Reads are open; only
   > secrets, the held-out material's contents, the counterpart's work on the same ticket and the hidden half of an evaluation set are refused (DEC-820).
   > The guard decides; role files state.

   The reads sentence is kept (its closing clause "and writes stay inside the ticket's paths" dropped, its `(DEC-820)` kept), now framed as the adopted
   product's policy; the last sentence is kept; the two statements on writes are replaced.
3. **Each clause against the hook** (`.claude/hooks/pretooluse.py`'s docstring and code; `bash_writes.py`'s docstring):
   - "five rules (DEC-953 item 2, and DEC-954 for the fifth)": the docstring "It keeps exactly five rules ... (DEC-953 item 2, DEC-954, DEC-1050
     (8))"; the register: DEC-953 item 2 states four rules, DEC-954 "Changes: DEC-953 item 2 (a fifth rule ...)" (**F3**).
   - acceptance tests: rule 1 (MR-3, DEC-906). Held-out material, every role (DEC-820 (b)); the hidden half by the sessions it measures (DEC-820 (d)):
     rule 2. The sets root's hidden folders, no reads and no resolved writes, for the roles `sets_root_hidden.refused_roles` names and the roles a set
     measures: rule 2b (DEC-1082 (3)) (**F2**).
   - reviewers and auditors write only their own outcomes: rule 5 (DEC-954). Secrets and keys: rule 3 (DEC-820 (a)).
   - installs ask only in the CTO's own session (the orchestrator on W2-00), refused in every other: rule 4 (DEC-957); `has_sudo` refuses sudo to every
     session, code `4-sudo` (**F1**).
   - the catastrophic deletes: the rm rule (DEC-1050 (8)). The operator agent's folder but `queue/`, and `~/.gov-os/guard-calls`: rule 2d, path map
     `write_refused` (ACT-OPERATOR-1, DEC-1106 (3), DEC-1108 (5)), "no writes, by any session this guard judges" (**F1**).
   - named sessions' walls: rule 2c, path map `session_hidden` (ACT-INDEP-WALLS-1): reads and writes of `~/.claude/projects` refused to the engineer
     on W2-56; every other session untouched (**F2**).
   - role separation to reads: G-14 (DEC-1052), applied only to Read, NotebookRead, Grep and Bash (`role_paths` reads_denied).
   - the write rules judge only resolved writes: the docstring (ACT-GUARD-FIX-4, DEC-1050 (12)) and `bash_writes.py` ("the hook's rules 1 and 5 use
     only the targets this module resolves (an unresolvable one is let through)"); 2b and 2d say the same; the backstops G-1 (the landing's check
     that a commit touching `tests/acceptance/` carries `Role: independent-test-designer`) and G-2 (the reviewed tree's git status).
   - no rule keeps a worker's writes inside its ticket's paths: no allowed-paths rule in the hook (the review's check, round b1).
   The brief's example list ("the frozen paths") is not in the hook, so it is not in the text; the counterpart's work stays in the kept reads sentence.
4. **Class (b), measured, after ACT-CLASS-RULES-AGENTS-1.** `act_class.classify` on this bundle: with **ACT-CLASS-RULES-AGENTS-1's after
   table**, class **(b)**: `.rulesync/rules/governance.md` row `rulesync-other` (b), `CLAUDE.md` and `AGENTS.md` row `agent-instructions` (b),
   no script hit (rehearsal F4b). With **today's live table** it is still (O) (`CLAUDE.md`, `AGENTS.md` on the catch-all `unknown`, F4a): so the
   request is written only after that ACT's apply and commit. The manifest claims `b`; the reviewer's vote makes the third.

**The order:** (1) ACT-CLASS-RULES-AGENTS-1 reviewed, the owner's yes, applied by hand and committed (its package); (2) this ACT's review
(`review.md`, the operator's fixed reviewer brief, the fenced verdict block G4 reads); (3) the owner's yes line below in the CTO session;
(4) the CTO writes the request line; the operator agent runs it.

## 1. The yes line (the owner's line, on its own line)

yes ACT-CLAUDE-RULES-1 38d4a2df

(the first 8 digits of the manifest's sha256 `38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea`.) **Round O's line
`yes ACT-CLAUDE-RULES-1 83c5faf6` and round b1's `yes ACT-CLAUDE-RULES-1 199dd123` are void**: those manifests are no longer the bundle's.

## 2. The operator's steps

**By the operator agent** (the route): after ACT-CLASS-RULES-AGENTS-1's commit, this ACT's review and the owner's yes, the CTO writes the
request line in `~/gov-os-operator/queue/` (manifest sha256 `38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea`). The agent
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
sha256sum $G/manifest.json      # expect 38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea
bash $G/apply.sh check && bash $G/apply.sh apply    # check prints nothing and exits 0; if a file moved: "moved: <path>", exit 3
F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 3
git commit -m "ACT-CLAUDE-RULES-1: the Guard paragraph of the governance rule is true for this repository (DEC-1167 (7))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1167, DEC-1173" --trailer "Role: owner" -- $F
```
After the commit, `python3 -m gov.adapters.portability` (PYTHONPATH `src`, `RULESYNC_BIN`) reads the same findings as before (none at
round b2's build) and none on the three files. `.claude/settings.json` is **not regenerated**: the generation with the held-out
step reproduces the live file byte for byte before and after (rehearsal B10), so there is nothing to write.

## 3. The files

| file | old sha256 | new sha256 |
|---|---|---|
| `.rulesync/rules/governance.md` | `aab9e7c05dd61f6fb734cc8973e0489c5f176362971c7b4b869c8b016a5155d7` | `52fd435b377679ba9625970c8808d1b88dd6aa4ed7ccde8b67b690c71df5ed97` |
| `CLAUDE.md` | `f672e46802d34c2fbc6340b97b06336c0f93119785572f45a67a49e13d258249` | `c14dfa51ebb6dfa87c8409080109c6d2011ae61b194b499f5a40c59af7c58629` |
| `AGENTS.md` | `18e826269b0a0cdc02883c206162d7694b2a9fecc8ce43a578b4c94013eae7d0` | `8dcc416e220e8e37ec5214f504d062e61095ec2f75c8c1018ce0728e76c8c51a` |

`template/.rulesync/rules/governance.md` stays at `b7ff8b723440819e64ef527ffd40cf667b3230cb10d8c695938f66282254ee9f`. The befores are round O's and round b1's; the afters are new in round b2.

## 4. Why the three go together

The source alone (the copies not yet written) is a drift: portability reads `GENERATED_DIFFERS` for `CLAUDE.md` and `AGENTS.md` (rehearsal C1). The copies
without the source are drift the other way. So one apply writes all three, and `check` refuses unless all three are at their before hash (C2 to C4).

## 5. The rehearsal (`rehearsal.log`, 49 cases, last line `failures: 0`)

Fresh `--no-hardlinks` clone of `w2/integrate` (`9a467f3360a9`), HOME planted at an empty folder, `apply.sh` run from the bundle, every pytest
through `heavy_slot.sh` with `TMPDIR` under `/tmp/claude-1000/act-claude-rules-1-b2/`. A: the bundle (hashes, list, the live files at the before,
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

By the operator: `undo ACT-CLAUDE-RULES-1 38d4a2df` (its own undo and commit). By hand: `bash $G/apply.sh undo` (the three put back byte for
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
| `list.txt` | `e21de3fcb0bc3b8abbe081ed892d7089a34ed84cd675a7f0d03899911e2e2307` |
| `rehearsal.log` | `5ff53157ff95a9959ffea20ba7a2c44c4535fb09cfc7be6ba6fb1d01f82f1d77` |
| `manifest.json` | `38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea` |

- One independent review (the operator's fixed reviewer brief; verdict block in `review.md`). **Review: not written yet.** (Round b1's review, of manifest `199dd123`, does not carry over.)
- ACT-CLASS-RULES-AGENTS-1 applied and committed first.
- The CTO tells the owner when the review is in; the owner sends the yes line (section 1).
