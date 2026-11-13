# ACT-CLAUDE-COPIES-5: the six generated `.claude/skills` copies that W2-11's round 2 left stale

- **For:** the owner's yes, then the operator agent, as ACT-CLAUDE-COPIES-1 to -4 ran; it goes beside the owner's approval
  of W2-11's CIT-P (CAP-33). Class **(b)**: it changes generated skill bodies, which instruct agents (OPERATOR-AGENT-1 §2
  row `agents-skills-kernel`). The operator's own `act_class.py` gives (b) for all 6 files, with no hits.
- **By:** the CTO (orchestrator `DAEO-sdxk`), 2026-11-12, built and rehearsed by
  `.gov-runtime/scratch/orchestrator/drafts/claude-copies-5/build_claude_copies_act_5.py` (a copy of
  `drafts/claude-copies-4/build_claude_copies_act_4.py`, which is not edited; its changes are in its docstring). The six
  copies are written by the clone's own rulesync 24.0.0 from the root `.rulesync/skills/` sources, never by hand.
  **Nothing live changes until it runs.**
- **Under:** DEC-315 (a launched session cannot edit `.claude/`; generated copies only by an ACT); DEC-992 P-W2-11-5 and
  DEC-1112 (3) (W2-11's copies are the CTO's step, after the lead's DONE, with no worker writing `.claude/**`); DEC-1057
  (every ACT rehearsed as the operator runs it). CAP-33.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-5/`, built from integrate `0206c0f7c691` with
  `w2/W2-11` `58ac442d6820` (the reviewed head `646850506819` plus the CIT-P review record) merged in a clone (a clean
  merge; the merge is only for the generation, integrate itself does not change). `w2/W2-11` has since moved to
  `dca382f3069f` by one docs-only commit (the CIT-P's figures): no `.claude`, `.rulesync` or kernel file changed, so the bytes stand.
  **Manifest sha256 `e602d5960dccf62100cb8bc151ae3363fe3e8eb4d96ed8c9e29fe045450f0c91`.**
- **Review:** the operator's fixed reviewer brief applies, as for ACT-4 (`ACT-CLAUDE-COPIES-5/review.md`); it is not
  written yet. The CTO starts the reviewer on this bundle before the owner's line is asked for.

## 0. What the owner says
The line the operator agent reads, on its own line:

yes ACT-CLAUDE-COPIES-5 e602d596

## 1. What it does (6 files; each one's old and new sha256 is in `manifest.json` and `list.txt`)

| file | what changes | why |
|---|---|---|
| `.claude/skills/discovery/SKILL.md` | the version line `1.0.0` to `1.1.0` (1 line) | W2-11's one-version rule: the kernel skill, its two `.rulesync` copies and the generated copy carry the same version (the case `test_the_skill_carries_one_version_in_all_four_places`) |
| `.claude/skills/retrieval/SKILL.md` | the same, `1.0.0` to `1.1.0` (1 line) | the same |
| `.claude/skills/test-design/test-kinds.md` | the same, `1.0.0` to `1.1.0` (1 line) | the same (round 1's copy carried the file at 1.0.0) |
| `.claude/skills/orchestration/SKILL.md` | the round-2 skill: `metadata.version 1.4.0`, the resource gate in place of a fixed ceiling (DEC-847), the exit audit and close lines (DEC-733, DEC-968, DEC-536), and the detail pointer to `briefs-and-returns.md` (+25, -20 lines) | the kernel source changed in round 2; this copy was never regenerated (integrate's 1.0.0 body) |
| `.claude/skills/orchestration/briefs-and-returns.md` | round 2's additions to the brief detail: the anti-drift kit, scope control, the approvals method (DEC-952, DEC-974, DEC-991; +52 lines, none removed) | the kernel source grew after round 1's copy |
| `.claude/skills/test-design/SKILL.md` | the round-2 skill: the work order, the black-box techniques, proportion, test kinds and the README map (+40, -13 lines) | the kernel source changed in round 2; this copy was never regenerated |

**Why exactly these six.** `python3 -m gov.adapters.portability`, run on integrate with `w2/W2-11` merged, reports
`GENERATED_DIFFERS` for exactly these six files and for nothing else (exit 1, 6 findings). Rulesync 24.0.0, run over
the merged root `.rulesync/`, differs from the tree in exactly these six files under `.claude/agents`, `.claude/skills`
and `.claude/commands` (the one other difference, `.claude/settings.json`, is the held-out step's deny, DEC-616, which
no ACT regenerates). The other generated copies W2-11 changes (audit, change, checkpoint, planning, qa-review and its
scenarios, incident-response, integration-queue, nightly-sheriff, and the orchestrator agent) were generated in round 1
and come in with the merge already equal to rulesync's output. Of the six, two (`discovery/SKILL.md`,
`retrieval/SKILL.md`) differ from integrate's own files, two (`briefs-and-returns.md`, `test-kinds.md`) are new on
integrate, and two (`orchestration/SKILL.md`, `test-design/SKILL.md`) equal integrate's: the old values below are the
bytes at `w2/W2-11` `58ac442d6820`, not integrate's.

**What stays.** The kernel skills, the root and `template/.rulesync` sources (byte-equal to the kernel, checked by the
builder), `.claude/agents`, `.claude/templates`, `.rulesync/subagents`, `.claude/settings.json`, hooks and
permissions. Nothing outside the 6 files is written. **Disjoint from ACT-CLAUDE-COPIES-4:** its 19 files are
`.claude/templates`, `.rulesync/subagents` and `.claude/agents`; the builder asserts that the two sets share no file.

| file | old sha256 | new sha256 |
|---|---|---|
| `.claude/skills/discovery/SKILL.md` | `55800596536681e740e25d74f839083f54a5acf4dfac04cb1683904464b99120` | `82d847fa6ff478136ba36a915945d409b69a03a730426071c3d69f68b1a53306` |
| `.claude/skills/orchestration/SKILL.md` | `4f25cf7468d9bcab01fb1422b626af107ab369d32967da3b006c9848dd2514cc` | `d240afca997bb4e4bae09e95c3907cb7588b10fb4647827c56afd7a24354f651` |
| `.claude/skills/orchestration/briefs-and-returns.md` | `5e4eb4e15520c8600ca18d049a10b8c4675ff37803e3759357f3f2194a682760` | `4b26908111e1808e9972024c125b9616f17d30a9e9ad7a1bbe99c2c1913664a1` |
| `.claude/skills/retrieval/SKILL.md` | `dc745ec3e5e8ba0cfd85f48959ecb53bd09085b74d2ec0b7083f6fc3dfd92c1b` | `c5779db4841ef8ff1ca5274d68128ae4d580153d9bf2b48bca69042b87d217f4` |
| `.claude/skills/test-design/SKILL.md` | `97d434e36f6ac8ae4232359b59c9ab61322a0ed7d66b27a008bf8df809cca630` | `47509c207a02e0a54b80c3895f04ad29fe38a7ebb6e01764e945362922f07cad` |
| `.claude/skills/test-design/test-kinds.md` | `8b17d7413061f1134c8614c4c11921b7a674d2526846802780e2fa5b1bb8edaa` | `a1da42e665b425adbb5cfb06f2f02d22789f2bd2e36b932ac0a26c1e70d7bf01` |

**The approved bytes.** The new bytes are rulesync 24.0.0's output over the root `.rulesync/skills/` sources at
`w2/W2-11` `58ac442d6820`: the six sources are the CIT-P's reviewed text (the kernel, `template/.rulesync` and root copies are byte-equal, which the builder checks before generating). The
manifest's two checks are sha256 checks, not comparisons with `template/`: check 1 is the six new copies, check 2 is the
six root sources they were generated from (`.rulesync/skills/**`, new sha256 `224b4d0b33aa1661…`, `eae3cb7d0f4e7139…`,
`4b26908111e1808e…`, `7a191d5b972529b2…`, `e2a467de0722b16b…`, `a1da42e665b425ad…`, in the manifest's order), so a source
that moves before the apply shows red instead of letting stale bytes in.

## 2. The order, and what the main tree reads in between

**The operator applies this ACT after `w2/W2-11` has landed on integrate.** Three facts fix that order (all measured in
clones):
1. **ACT first, then merging integrate into `w2/W2-11` conflicts.** Four of the six files (`discovery/SKILL.md`,
   `retrieval/SKILL.md`, and the two add-add files `briefs-and-returns.md` and `test-kinds.md`) were also written by
   W2-11's round-1 CTO generation; the merge stops with 4 conflicts, all in `.claude/skills`, and resolving them means
   writing `.claude/` from the ticket's worktree (DEC-315). ACT-4's order (ACT, then merge integrate into the ticket) is
   therefore not this ACT's order. With the ACT after the landing the merge is clean.
2. **The bundle's `before` is W2-11's bytes**, so `apply.sh check` (and the operator's G7) refuses on integrate until
   W2-11 has merged (`moved: .claude/skills/discovery/SKILL.md`, exit 3, measured; the builder's negative control). The
   request line is therefore written after the landing, not before.
3. **ACT-4 cannot follow W2-11.** W2-11 changes `.claude/agents/orchestrator.md` and `.rulesync/subagents/orchestrator.md`,
   two of ACT-4's 19 files; with W2-11 merged, ACT-4's `apply.sh check` exits 3 (`moved: .claude/agents/orchestrator.md`,
   measured). The two ACTs touch no common file, but in time ACT-4 goes first, then W2-11 lands (a clean merge, measured),
   then this ACT; with W2-175 merged as well, portability reads exit 0 after this ACT (measured on that sequence).

**The four states** (measured in fresh clones; each folder one pytest run through the heavy-job gate, real HOME;
portability from the clone's root; logs in `drafts/claude-copies-5/evidence/`):

| state | portability | red cases |
|---|---|---|
| (i) integrate | exit 0, no findings | none (W2-11's folder is not on integrate; the 11 other folders pass, `W2-142` at its older 9 cases) |
| (ii) integrate + this ACT (applied by force; `check` refuses here) | exit 1, 6 findings: `GENERATED_DIFFERS` 4, `GENERATED_WITHOUT_SOURCE` 2 (the two new files) | none in the 11 folders on integrate (W2-11's folder is absent); only portability reads it |
| (iii) integrate + W2-11 merged, no ACT (**the window**) | exit 1, 6 findings: `GENERATED_DIFFERS` for the six files | **7, all in `tests/acceptance/W2-11`:** `test_w2_11_skills.py::test_every_copy_carries_the_kernel_skills_body[test-design]` and `[orchestration]`; `::test_the_skill_carries_one_version_in_all_four_places[discovery]`, `[orchestration]`, `[retrieval]`, `[test-design]`; `test_w2_11_supersession.py::test_the_file_teaches_no_superseded_rule[.claude/skills/orchestration/SKILL.md]` |
| (iv) integrate + W2-11 + this ACT | exit 0, no findings | none: W2-11 193 passed, 1 skipped |

In (iii), the other eleven folders read as on integrate: `tests/acceptance/W2-128` 121 passed, `W2-142` 13, `W1-35` 124,
`W2-153` 66, `tests/unit/adapters` 94, `W1-30` 7, `W1-38` 42, `W2-57` 20, `tests/unit/gitenv` 61, `W1-33` 112, `W1-40` 38
(counts as the folders select them; none fails in any of the four states).

**The window cannot be avoided, only shortened, and it is the CTO's to hold.** From W2-11's merge to this ACT's commit:
- Portability reads exit 1 with exactly the six findings, and W2-11's seven copy cases are red. Any landing or nightly
  run that collects `tests/acceptance/W2-11` in the window is red on those seven, and nothing else is.
- **Hold other landings and the nightly run from the merge to the ACT's commit** (the CTO's merge queue), so no run meets
  the seven. A landing that cannot be held sees exactly those seven and no other new red.
- The CTO writes the request line as soon as W2-11 has merged; the operator's G7 and G8 run against the merged head.
- **The abort.** If `apply.sh check`, the two checks or portability do not read as in §4, or the sitting breaks off,
  the operator's `undo ACT-CLAUDE-COPIES-5 e602d596` restores the six files to W2-11's round-1 bytes (the window state,
  byte for byte, measured) and the window is open until a rebuilt ACT lands; the other abort is W2-11's own rollback
  (revert the merge; CIT-P §7.4). Neither changes `w2/W2-11`.
- Why two commits, stated plainly: the ACT is the only route that writes generated `.claude/` copies (DEC-315), and its
  `before` hashes are W2-11's bytes, so it can only run on a tree that already holds W2-11. One commit carrying both would
  need a ticket session or the CTO to write `.claude/` outside an ACT; the window is the price of keeping DEC-315.

**The sequence this gives** (the CTO's, without a pause once the owner has said yes to the CIT-P and to §0):
1. hold the queue and the nightly; ACT-CLAUDE-COPIES-4 first if it is still to run (it must precede W2-11's merge);
2. merge integrate into `w2/W2-11` (clean), re-run its suite there: **7 failed (the copy cases), the rest passes** (measured);
3. CIT-P ACCEPTED; merge `w2/W2-11` into integrate;
4. write the request line; the operator applies this ACT and commits it;
5. re-run `tests/acceptance/W2-11`, `W2-128`, `W2-142` and portability on integrate (§3: 193 passed 1 skipped, 121, 13, exit 0);
6. close W2-11, release the queue and the nightly.

## 3. Rehearsals (DEC-1057; 0 failures)
- **The bundle's own** (`rehearsal.log`, hashed in the manifest; HOME planted at an empty folder; the log carries no
  integrate head, pid, date, timing or live-tree count, so a re-run is byte-equal), on fresh `--no-hardlinks` clones:
  1. **plain integrate** (W2-11 not merged): `apply.sh check` exits 3 and names the first moved file, and changes nothing;
  2. **integrate with W2-11 merged**: `apply.sh check` exit 0; check 1 red before the apply (6 `FAILED`), check 2 green;
     `apply`; both checks green; the changed set equals the 6 files; every target at its stated new sha256; portability
     exit 0, no findings; `undo` byte for byte with the tree clean, portability back to the window's reading (exit 1, 6
     `GENERATED_DIFFERS`); `check` again; `apply` again, the same bytes;
  3. **the gated runs on that clone with the ACT applied**, one folder per run through the heavy-job gate, each read from
     pytest's own summary line and required to show passed > 0: `W2-11` 193 passed 1 skipped, `W2-128` 121, `W2-142` 13,
     `W1-35` 124, `W2-153` 66, `tests/unit/adapters` 94, all 0 failed; `python3 -m gov.adapters.portability` exit 0;
  4. **§4 literally**: stage the 6 paths (6 staged), commit with the trailers, portability after the commit exit 0,
     `undo`, stage, commit, an empty diff over the 6 paths against the start;
  5. **ACT-CLAUDE-COPIES-4 applied first, then W2-11 merged** (the order of §2): this ACT's `check` and `apply` run on
     that tree, both checks green, no `GENERATED_DIFFERS` left; the remaining 13 findings are ACT-4's own window until
     W2-175 merges (measured separately: with W2-175 merged too, exit 0);
  6. the live main tree's 6 files unchanged by the rehearsal, nothing written to the planted HOME.
- **The operator's gates on the bundle** (its own `operator_run.validate_manifest` and `path_rule`, its own
  `act_class.py`, and its install `class-rules.yaml`, which equals the committed one): `validate_manifest` passes; all
  15 files named in the manifest hash as stated and no file on disk is unnamed; `path_rule` passes; `act_class` gives (b)
  with no hits.
- **Logs of all the measurements:** `drafts/claude-copies-5/evidence/` (`window-*.log`, one pytest run per folder, four
  trees; `portability-four-states.txt`; `portability-full-sequence.txt`; `act_class.json`; `operator_gates.txt`).
- **Where the rehearsal differs from the real run:** the real run applies in the main tree, whose HEAD will be later than
  `0206c0f7c691`; the six before hashes are the blobs at `w2/W2-11` `58ac442d6820` (the builder asserts it), and the
  operator's G7 and `apply.sh check` compare them with the live files again. HOME for pytest is the real HOME (pytest is
  in the user site); HOME for every apply step is planted.

## 4. The operator's steps
**By the operator agent:** after the owner's yes (§0) and W2-11's landing, the CTO writes the request line in
`~/gov-os-operator/queue/`, and the agent runs the bundle through its gates.

**Or by hand**, in the main tree (as rehearsed in §3 item 4):
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> test -z "$(git status --short --untracked-files=no)" && test ! -e .git/MERGE_HEAD && echo clean
> G=.gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-COPIES-5
> sha256sum $G/manifest.json      # expect e602d5960dccf62100cb8bc151ae3363fe3e8eb4d96ed8c9e29fe045450f0c91
> bash $G/apply.sh check && bash $G/apply.sh apply
> F=$(cut -d'|' -f2 $G/list.txt); git add $F; git diff --cached --name-only | wc -l    # expect 6
> git commit -m "ACT-CLAUDE-COPIES-5: the six .claude/skills copies for W2-11's round-2 kernel skills (6 files)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-315, DEC-992" --trailer "Role: owner"
> ```
> **Undo (the abort):** `bash $G/apply.sh undo`, `git add $F`, commit with `--trailer "Role: owner"`.

**The lines it must print.**
- `apply.sh check` prints nothing and exits 0 when all 6 files are at their old sha256 (it prints `moved: <path>` and
  exits 3 for the first file that is not; on a tree without W2-11 that is `moved: .claude/skills/discovery/SKILL.md`).
- The manifest's two checks (run after the apply) print `<path>: OK` for each file, 6 lines and then 6, and exit 0. Run
  on the tree before the apply, check 1 prints 6 `FAILED` lines and exits 1 (that is what it is for); check 2 prints 6
  `OK` lines.
- The staged count line prints `6`. After the commit `python3 -m gov.adapters.portability` exits 0 with no findings.

## 5. After it
- The CTO re-runs `tests/acceptance/W2-11` (193 passed, 1 skipped), `W2-128` (121) and `W2-142` (13), one folder per run, on
  integrate, then closes W2-11 and releases the queue and the nightly.
- The structural pass on integrate reads portability exit 0 with no findings (with ACT-CLAUDE-COPIES-4 and W2-175 as in
  their own packages); the CTO merges integrate into the live worktrees.
- W2-11's close no longer names the seven copy cases: they are green on the landed tree.

## 6. Not in this ACT
`.claude/templates`, `.rulesync/subagents` and `.claude/agents` (ACT-CLAUDE-COPIES-4's); any change to the kernel, the
sources or the policy (CAP-33: they follow W2-11's CIT-P and the owner's approval); `.claude/settings.json`; the
rows W2-11's CIT-P §7.2 leaves open (the validator's refusal of a brief without the twelve-field rule, the vendored
skills' versions, `allowed-tools` in the copies of the existing skills).
