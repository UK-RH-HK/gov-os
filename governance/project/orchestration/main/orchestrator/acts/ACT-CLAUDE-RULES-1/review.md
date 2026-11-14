# ACT-CLAUDE-RULES-1 (round b2): the independent ACT review

task: ACT-CLAUDE-RULES-1
decisions: DEC-1104 (2), DEC-1173 (2), DEC-1167 (7), DEC-953 (item 2), DEC-954, DEC-957, DEC-820, DEC-1082 (3), DEC-1128 (4), DEC-1010, DEC-801, DEC-808
reviewer: a read-only reviewer session, not the ACT's author (cto). Disclosure: round b1's record names session f3886235-4854-4c91-9cf3-1a1dd009cb50, and that is also this session's id. This session holds no context from round b1 and re-derived every result below from the files. The brief's bar ("never the ACT's author") holds. If the owner reads "fresh" more strictly, that is a reason to relaunch.
brief: ~/gov-os-operator/install/reviewer-brief.md, sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (computed)
bundle: .gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1/, manifest.json sha256 38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea (computed; equals the one handed over)
integration head read: 9a467f336 (w2/integrate; the main tree is clean; the three files are at their before hashes)

Classification of the findings: F1 and F2 are in scope and reachable in ordinary work, but neither fails open nor loses work. F3 is out of scope. All three are rows; none blocks; this record proposes no round.

## What I did

- Read the brief, the package, the manifest, apply.sh, list.txt, the rehearsal log, and before/ and after/ of the three files.
- Read round b1's review, the builder (`drafts/act-claude-rules-1/build_claude_rules_act_1c.py`) and ACT-CLASS-RULES-AGENTS-1's after table.
- Read the live hook in full: `.claude/hooks/pretooluse.py`, plus `role_reads.py` and the docstrings of `bash_writes.py`.
- Read the pinned judge's `names_held_out`, `has_sudo` and `reads._hidden` (`~/.local/share/gov-os/pin-797495bdfc70`), and the path map's `role_paths`, `sets_root_hidden`, `session_hidden` and `write_refused` blocks.
- Read the launcher's sandbox and settings code, and the register entries DEC-820, DEC-953, DEC-954 (and its owner text), DEC-1128 (4), DEC-1167 (7) and DEC-1173.
- My own rehearsal (`/tmp/claude-1000/acr1b2/rehearse.sh`, output `rehearse.out`): a fresh `--no-hardlinks` clone of w2/integrate at 9a467f336, with HOME planted at an empty folder. The bundle's own apply.sh was run with the clone as cwd. Result: `failures: 0`.
- A fresh `rulesync generate` (24.0.0, the builder's arguments) from the applied source into an empty folder, under a planted HOME.
- The operator's `act_class.py`, copied to my folder, run under the live table and under the after table.
- Hook probes (`/tmp/claude-1000/acr1b2/probe.py`, output `probe.out`): the clone's hook run by the pinned interpreter, with a planted HOME, planted worktrees, a planted held-out path in the clone's own config and a planted call log.
- I re-ran no suite: the rehearsal's E lines are the builder's, and the change is text only (log C5: no test names either sentence).
- Nothing was written in any tree or in the live HOME. No guard refusal was met.

## The six checks

1. **Touched list and path rule: pass.**
   - list.txt equals the manifest's `touched`, and every file in `files` hashes as stated.
   - In the clone, the apply changes exactly `.rulesync/rules/governance.md`, `CLAUDE.md` and `AGENTS.md`, each byte for byte the bundle's after.
   - Nothing else changed: the planted HOME stays empty, `crontab -l` is unchanged, the operator folder's listing is unchanged, and the live tree's three files, the template's source and `.claude/settings.json` are unchanged.
   - apply.sh is byte for byte the copies ACTs' script (84f6f595...). It reaches the bundle through its own folder (a subshell `cd` to its dirname) and writes only `$PWD/<path>` for `repo` rows. It names no live path, `~/`, `$HOME` or bare `cd`; neither do the four checks; `commands` is empty.
2. **Undo tested: pass.**
   - The log shows B13 and D4 to D6.
   - Reproduced: undo exits 0, the three files are byte for byte the before, the tree is clean, and `check` exits 0 again.
   - With AGENTS.md moved, `check` exits 3 ("moved: AGENTS.md") before any write.
3. **Rehearsal real: pass.**
   - rehearsal.log hashes as the manifest says (5ff53157...) and equals the builder's `rehearse-b2.out`.
   - The builder copies the copies ACTs' apply.sh into the bundle (A4) and runs the bundle's own copy in a fresh clone of 9a467f336 with a planted HOME.
   - It ends with `failures: 0` (49 ok).
4. **Checks right: pass.** Run from the clone:
   - After the apply: check 1 exits 0 and check 2 exits 0; check 3 counts 0 and check 4 counts 3. Each exit and count is as the manifest states.
   - Before the apply: checks 1, 3 and 4 refuse (exit 1; count 3; count 0), as the log's B4 says.
5. **Class: b, as claimed, valid only after ACT-CLASS-RULES-AGENTS-1.**
   - `act_class.py` under today's live table (38ac2f2d...) gives O: CLAUDE.md and AGENTS.md fall to `unknown`.
   - Under ACT-CLASS-RULES-AGENTS-1's after table (a040a103...) it gives b: the two copies by `agent-instructions`, the source by `rulesync-other`, and no script hits.
   - The live table is not yet the after table, so this ACT must be queued only after that ACT's apply and commit. Queued earlier, G6 refuses it as O, which fails closed.
   - On the merits, the change alters what every session is told about a control, so (b) is right (DEC-1173 (2)).
6. **Guard replay: pass, not applicable.** The ACT adds nothing to the path map or the deny list, so `replay_refused` is empty.

## Round b1's findings: each now right

- **F1 (rule 2d, sudo): fixed.**
  - "refuses every session's writes into the operator agent's folder (but its queue/) and into the guard's call log" matches the path map's `write_refused`: `~/gov-os-operator` with `except: [queue]`, and `~/.gov-os/guard-calls` with no exceptions. It is applied to every role for a file tool or Bash.
  - "sudo is refused to every session" matches `has_sudo`, rule `4-sudo`, before the install branch.
- **F2 (rules 2b, 2c): fixed.**
  - "the sets root's hidden folders are neither read nor written by the roles the path map refuses them" matches 2b: the reads judge, plus `2b-write` on resolved writes, for `refused_roles` and for each role a set measures.
  - "refuses named sessions reads and writes of the folders the path map walls off for them (the engineer on W2-56: the raw transcripts)" matches `session_hidden` (`~/.claude/projects`, roles `[engineer]`, tickets `[W2-56]`).
  - The DEC-820 sentence now follows "In an adopted product", so it reads as the policy, not the hook's full list.
- **F3 (citation): fixed.** "(DEC-953 item 2, and DEC-954 for the fifth)" is right. DEC-953 item 2 states four rules. DEC-954 says: "The guard's fifth rule (standing, added to DEC-953 item 2): independent reviewers and auditors write only their own outcomes". The hook's docstring cites the same pair.

## The new text against the hook and the register, sentence by sentence

- **"five rules (DEC-953 item 2, and DEC-954 for the fifth)":** sound (above).
- **"only the independent test designer writes acceptance tests":** this is rule 1, but stated wider than the hook keeps it (F2).
- **"the held-out material is not read":** this is rule `2-heldout`, but stated narrower than the hook keeps it (F1).
- **"nor the hidden half of an evaluation set by the sessions it measures":** sound. This is rule 2 via `reads._hidden`, which takes the hidden globs of the sets whose `measures` name the role or ticket, in every tree.
- **"the sets root's hidden folders are neither read nor written by the roles the path map refuses them":** sound (2b, as above).
- **"independent reviewers and auditors write only their own outcomes":** sound (rule 5; REVIEWERS and REVIEW_PATHS, plus their own scratch and /tmp).
- **"secrets and keys are not read":** sound (rule 3, via the reads judge's SECRET_REFUSAL).
- **"an install asks the owner in the CTO's own session and is refused in every other, while sudo is refused to every session":** sound. Only orchestrator plus acting orchestrator on W2-00 gets the ask (DEC-957).
- **"It also refuses the catastrophic deletes":** sound (the rm rule, DEC-1050 (8)).
- **2d and 2c:** sound (above).
- **"applies the path map's role separation to reads":** sound. G-14 runs only for Read, NotebookRead, Grep and Bash, and `role_reads` judges only reads.
- **"Its write rules judge a Bash line by the writes the guard resolves ... let through ... backstops":** sound for rules 1, 5, 2b-write, 2c's write half and 2d (all use `bash_writes_of`). G-1 and G-2 match the docstring.
- **"It has no rule that keeps a worker's writes inside its ticket's paths":** true. The hook has no allowed-paths rule.
- **"a launched worker's writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4))":** sound in substance. DEC-1128 (4) keeps the workers' sandbox; leads are unsandboxed. See note N1.
- **"In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at runtime":** sound (decide.py `_path_allowed`, DEC-1174 (2)).
- **"Reads are open; only ... (DEC-820)":** this is DEC-820 item 2 word for word, now framed as policy. Sound.

## Findings

**F1. The held-out rule is described as "not read"; the hook refuses every call that names or reaches the held-out material.**
- What was done: the paragraph says the held-out material "is not read". With the kept DEC-820 sentence ("the held-out material's contents"), a reader infers that its names can be listed and that its path can be written in a record.
- What happens: the hook's first check refuses any call, by any tool, whose input holds a held-out path anywhere or reaches one. That covers writes into it, a listing of it, and a Write or Edit whose text merely names the path.
- Reproduced with a planted held-out path in my clone's own config, as the orchestrator:
  - `ls <path>`: refused.
  - A Write into `<path>/x.txt`: refused.
  - A Write of `docs/notes.md` whose content names the path: refused ("the call names or reaches the held-out material").
  - The same Write with plain text: allowed.
- What should have happened: "no call names, reads or writes the held-out material".
- Ordinary work: yes, because an honest CTO or product-spec session writing a record that cites the held-out folder's path, or listing it, is refused although the paragraph said only reads are.
- Consequence: other (the hook refuses; the omission fails closed and loses no work).
- Scope: in.
- What reverses it: the pinned judge's `names_held_out` refusing only reads (my P6 to P8 then allowed), or an owner reading that the paragraph names each rule by its purpose only.

**F2. "Only the independent test designer writes acceptance tests" is wider than the hook's rule 1.**
- What was done: the rule is stated without its reach.
- What happens: for file tools and the shell's own writes, rule 1 refuses only paths in the acceptance tests of the session's own tree. Another tree of the same repository is refused only for the writes of code run inline.
- Reproduced in my clone with planted worktrees under the planted HOME:
  - The orchestrator in the main tree writing its own `tests/acceptance/...`: refused.
  - The same session writing a ticket's tests worktree (`~/gov-os-worktrees/W2-ZZ-tests/tests/acceptance/...`) by Write: allowed.
  - An engineer in its own worktree editing that file by Edit: allowed.
  - The same engineer with `cp` to it: allowed.
  - The same engineer with `python3 -c "open(...,'w')"`: refused.
- What should have happened: "only the independent test designer writes the acceptance tests of the tree it runs in (and code's writes into any tree's)". Alternatively, the backstop sentence could name this case with the G-1 landing check.
- Ordinary work: yes, because a lead (unsandboxed, DEC-1128 (4)) or the CTO may fix a file in a ticket's tests worktree by its path from its own tree, and the paragraph says it would be refused. A launched engineer is held instead by its sandbox and settings.
- Consequence: other. The landing's G-1 check refuses a commit touching `tests/acceptance/` without `Role: independent-test-designer`, so the write cannot land unseen, and no work is lost.
- Scope: in.
- What reverses it: rule 1 judging file-tool and shell targets against every tree (`tree_roots`), as it already does for code's writes (P2 to P4 then refused).

**F3. The hook's rule 1 does not cover another tree's acceptance tests for file tools and shell writes (the guard gap behind F2).**
- What was done: rule 1 checks `under_acceptance` against the session's own root for those targets. `in_a_trees_tests` is used only for code's writes.
- What happens: see F2's probes.
- What should have happened: one test, `in_a_trees_tests`, for every target kind.
- Ordinary work: yes (as F2).
- Consequence: other, because G-1 closes it at the landing. The hook alone fails open for this path.
- Scope: out. It is the hook's code, not this ACT, and the ACT does not touch or widen it. It is a row for the guard's hardening list.
- What reverses it: an existing row or decision that already records this reach as intended.

Disposition (DEC-1010): no finding fails open or loses work within this ACT's scope, so none blocks. F1 and F2 are text rows that can ride in the next rule-source ACT. A rebuild of this bundle would be its third round, which by the brief goes to the owner. F3 goes to the hardening list.

## Notes (not findings)

- **N1 (as round b1's observation):** for the file tools, the wall a launched worker meets outside its worktree is the CLI's permission checks under the launcher's settings (no bypass mode, no added directories), not the OS sandbox, which binds commands. The sandbox's `allowWrite` also opens the session's temp folder, its run folder and the reranker's log, so "outside its worktree" is slightly broad.
- **N2:** "named sessions reads" lacks its apostrophe ("named sessions' reads").
- **N3:** the paragraph does not say that the hook fails closed: an error or its 20-second deadline refuses the call. This is behaviour any session can meet, but it is not a rule.
- **N4:** for the roles they apply to, the 2b and 2c line rules refuse some lines whose writes the guard cannot resolve (the sets root named with a variable, glob or cd after it). That is stricter than "let through", and it fails closed.
- **N5:** the brief appends the verdict block to the bundle's `review.md`. My launch confines my writes to this record, so the block below must be carried into `review.md` before queueing, or G4 refuses. `review.md` is not hashed in the manifest.
- **Queue order:** ACT-CLASS-RULES-AGENTS-1 (class O, by hand) is applied and committed first; its review.md now carries a verdict.
- **Probed and found sound:**
  - The two copies are rulesync's output byte for byte from the applied source.
  - The template's rule source is deliberately unchanged (check 2: b7ff8b72..., exit 0 before and after).
  - The old text's fail-open claim (a per-ticket write wall) is gone from all three files.
  - Every round b1 finding is folded in correctly.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                                                       {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                                                       {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "38d4a2df4399bdcddc25d661b997314ccc3345897eedb3e96928056d0a49ffea",
 "class": "b",
 "reviewer": "act-claude-rules-1-b2 reviewer, session f3886235-4854-4c91-9cf3-1a1dd009cb50 (not the ACT's author)",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T21:15:18+00:00",
 "replay_refused": []}
```
