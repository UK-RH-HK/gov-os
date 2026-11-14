# ACT-CLAUDE-RULES-1 (class b rebuild): the independent ACT review

task: ACT-CLAUDE-RULES-1
decisions: DEC-1104 (2), DEC-1173 (2), DEC-1167 (7), DEC-953 (item 2), DEC-954, DEC-957, DEC-820, DEC-1128 (4), DEC-1174 (2), DEC-1010, DEC-801, DEC-808
reviewer: a fresh read-only reviewer session (f3886235-4854-4c91-9cf3-1a1dd009cb50), not the ACT's author (cto)
brief: ~/gov-os-operator/install/reviewer-brief.md, sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a (computed)
bundle: .gov-runtime/scratch/orchestrator/acts/ACT-CLAUDE-RULES-1/, manifest.json sha256 199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26 (computed; equals the one handed over)
integration head read: abadad60e (w2/integrate; the session started at e437c799c, two commits since, none touching the three files, the hook or the operator's tables)

Classification of the findings: F1, F2, F3 are rows (in scope, none fails open or loses work); no finding blocks; no round proposed.

## What I did

- Read the brief, the package, the manifest, apply.sh, list.txt, the rehearsal log, before/ and after/ of the three files, the
  author's builder (drafts/act-claude-rules-1/build_claude_rules_act_1b.py), ACT-CLASS-RULES-AGENTS-1's after table, the
  operator's classifier (read only), the live hook `.claude/hooks/pretooluse.py` in full, the path map's role_paths,
  sets_root_hidden, session_hidden and write_refused blocks, the launcher's sandbox and settings code, the product's write rule
  (decide.py `_path_allowed`), and the register entries DEC-820, DEC-953, DEC-954, DEC-1128, DEC-1167 (7), DEC-1173, DEC-1174.
- My own rehearsal (/tmp/claude-1000/acr1b/rehearse.sh, output rehearse.out beside it): a fresh clone of w2/integrate at
  abadad60e, HOME planted at an empty folder, the bundle's own apply.sh run in place with the clone as cwd. Then
  tests/unit/adapters through heavy_slot.sh with TMPDIR under /tmp/claude-1000/acr1b (tests.sh). Nothing in any tree or in the
  live HOME was written; the main tree's status is clean.

## The six checks

1. **Touched list and path rule: pass.** list.txt equals the manifest's touched list; every file in `files` hashes as stated.
   In the clone the apply changes exactly CLAUDE.md, AGENTS.md and .rulesync/rules/governance.md, each byte for byte the
   bundle's after; nothing in the planted HOME, no crontab entry, the template's rule source untouched. apply.sh is byte for
   byte the copies ACTs' apply.sh (ACT-CLAUDE-COPIES-7, 84f6f595...): it reaches the bundle through its own folder (a
   subshell `cd` to the script's dirname, not to the repository or HOME), writes only `$PWD/<path>` for `repo` rows and exits
   9 on any other root. No live path, `~/`, `$HOME/` or bare `cd` in it or in the four checks; `commands` is empty.
2. **Undo tested: pass.** The log shows B13 and D4-D6; I reproduced it: undo exit 0, the clone's tree clean, `check` exit 0
   again; a moved AGENTS.md makes `check` exit 3 before any write.
3. **Rehearsal real: pass.** rehearsal.log hashes as the manifest says, equals the author's rehearse-b.out, ran this apply.sh
   (the builder copies and executes the bundle's own) in a fresh clone with a planted HOME, and ends with `failures: 0`
   (49 ok). Its clone was at 8801ffd17; the three files are still at their before hashes on today's head, and my rehearsal on
   abadad60e gives the same results. tests/unit/adapters after the apply: 102 passed, 40 deselected, as the log's E line.
4. **Checks right: pass.** Run from the clone after the apply: the two hash checks exit 0; the gone-sentence count is 0; the
   new-sentence count is 3; exits and counts as the manifest states. Before the apply the first and fourth refuse (log B4).
5. **Class: b, as claimed, only under ACT-CLASS-RULES-AGENTS-1's table.** The operator's act_class.py (a copy in my scratch)
   with today's table: O (CLAUDE.md and AGENTS.md match no row: `unknown`). With the after table of
   ACT-CLASS-RULES-AGENTS-1 (a040a103...): b; CLAUDE.md and AGENTS.md by `agent-instructions`, the rule source by
   `rulesync-other`; no script hits. The ACT must therefore be queued only after ACT-CLASS-RULES-AGENTS-1 is applied (its own
   review.md is still "not written yet"); queued earlier, G6 refuses it as O, which fails closed. By the brief's table the
   change alters what every session is told about a control, so (b) is right on the merits too (DEC-1173 (2)).
6. **Guard replay: pass, not applicable.** No path-map or deny-list addition; replay_refused is empty.

## The new text against the hook and the register, sentence by sentence

- "only the independent test designer writes acceptance tests": rule 1 (MR-3, DEC-906). Sound.
- "the held-out material and the hidden half of an evaluation set are not read": rules 2 and 2b (reads). Sound as far as it
  goes; see F2 for what rule 2's family also does.
- "independent reviewers and auditors write only their own outcomes": rule 5 (DEC-954). Sound.
- "secrets and keys are not read": rule 3 (DEC-820 (a)). Sound.
- "an install asks the owner in the CTO's own session and is refused in every other": rule 4 (DEC-957), the orchestrator on
  W2-00 alone asks. Sound; it omits rule 4's sudo refusal (F1).
- "It also refuses the catastrophic deletes and applies the path map's role separation": the rm rule (DEC-1050 (8)) and G-14
  (role_paths: the engineer the ticket's tests, the test designer the ticket's new code). Sound.
- "It has no rule that keeps a worker's writes inside its ticket's paths": true; the hook holds no allowed_paths rule. This is
  the sentence the ACT exists for: the old text told agents of a write wall the hook does not keep (DEC-1167 (7)).
- "a launched worker's writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4))":
  sound in substance: a worker's settings carry the strict sandbox (writes: the worktree, its temp folder, its run folder,
  the reranker's log) and no bypass mode or added directory (DEC-313); DEC-1128 (4) keeps it, leads unsandboxed. Observation,
  not a finding: for the file tools the wall is the CLI's permission checks under those settings, not the OS sandbox, which
  binds commands.
- "In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at runtime":
  matches the product guard (decide.py `_get_allowed_paths`, `_path_allowed`; DEC-1174 (2) names the latter). Sound.
- "Reads are open; only secrets, the held-out material's contents, the counterpart's work on the same ticket and the hidden
  half of an evaluation set are refused (DEC-820)": DEC-820 item 2 word for word; in this repository rule 2c adds one narrow
  read refusal (F2).

## Findings

**F1. The paragraph omits two refusals the hook applies to every session.** What was done: the new paragraph lists five
rules, then "also" the catastrophic deletes and role separation, which reads as the whole list. What happens: the hook also
refuses (a) every write, by any session, into the operator agent's folder (~/gov-os-operator, but its queue/) and into the
guard's call log (~/.gov-os/guard-calls) (rule 2d, ACT-OPERATOR-1, path map write_refused), and (b) sudo, to every session
(rule 4). What should have happened: one clause naming both, e.g. "no session writes the operator's folder (but its queue)
or the guard's call log; sudo is refused to every session".
- Ordinary work: yes, because an honest CTO or lead may write into the operator's folder (a fix to an install file) or try
  sudo, and meet a refusal the paragraph did not foretell.
- Consequence: other (the hook still refuses: the omission fails closed and loses no work).
- Scope: in. Reverses it: a reading of the hook in which 2d or the sudo refusal is not live (the path map without
  write_refused, or has_sudo not reached), or an owner reading that the paragraph names only DEC-953's rules by design.

**F2. Rule 2's family is described as reads only, and the "only four refusals" sentence ignores rule 2c.** What was done: rule
2 is summarised as "not read". What happens: rule 2b also refuses the writes the guard resolves into the sets root's hidden
folders, and rule 2c refuses reads and writes of ~/.claude/projects to the engineer on W2-56 (session_hidden), a refusal
beyond DEC-820's four. What should have happened: "not read or written" for 2b, and a half-clause for named sessions'
walls; or the DEC-820 sentence framed as the policy, not as the hook's full list.
- Ordinary work: no for 2c (one named session on one ticket); yes for 2b, but an honest agent has no reason to write into a
  hidden folder.
- Consequence: other (both fail closed).
- Scope: in. Reverses it: the session_hidden block removed from the path map, or an owner reading that DEC-820's sentence is
  meant as policy only.

**F3. "Since DEC-953 item 2 ... five rules" cites the item that set four.** What was done: the five rules are attributed to
DEC-953 item 2 alone. What happens: DEC-953 item 2 states four rules; the fifth (reviewers and auditors write only their own
outcomes) is DEC-954's, which changes DEC-953 item 2 (DEC-953's "Changed by" line). The hook's own docstring cites "DEC-953
item 2, DEC-954". Both ids: DEC-953 (item 2, amended) and DEC-954. What should have happened: "since DEC-953 item 2 and
DEC-954".
- Ordinary work: yes, because a reader tracing the rule set to its decision finds four rules and no reviewer rule.
- Consequence: other.
- Scope: in. Reverses it: an owner reading that DEC-953 item 2 as amended is the conventional citation for the five-rule set.

Disposition: none blocks (DEC-1010: none fails open or loses work). F1 to F3 are recorded rows; they may ride along in the
next CLAUDE.md or rule-source ACT, or the CTO may rebuild this one with the clauses if the owner prefers (that would need a
new bundle and a new review).

## Notes for the CTO (not findings)

- The brief says the verdict block is appended to the bundle's review.md; my launch confined my writes to this record. The
  bundle's review.md still reads "Review: not written yet": the block below must be carried into it before queueing, or G4
  refuses (review.md is not hashed in the manifest, so this does not move the manifest's sha256).
- Queue order: ACT-CLASS-RULES-AGENTS-1 (class O, the owner's operator by hand) first; it has no review yet.
- Probed and found sound: the three files are generated consistently (rulesync 24 from the applied source into an empty
  folder gives CLAUDE.md and AGENTS.md byte for byte the bundle's after); the template's rule source is deliberately left as
  is (an adopted product keeps the kernel guard's sentence); no test names the replaced sentence (log C5); the old text's
  fail-open claim (a write wall per ticket) is gone from all three files.
- No guard refusal met in this session.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "pass", "findings": []},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
                                                       {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"},
                                                       {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "199dd123fb0edf3ab699c476d6fb2cc2280a1ecfd966ae21e599be7f2328ed26",
 "class": "b",
 "reviewer": "act-claude-rules-1-b reviewer, session f3886235-4854-4c91-9cf3-1a1dd009cb50",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T20:53:13+00:00",
 "replay_refused": []}
```
