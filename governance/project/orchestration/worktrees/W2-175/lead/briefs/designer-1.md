# Brief: independent test designer for DAEO-wahn (W2-175), round 1

You are a fresh **independent-test-designer** session (template `role-test-designer` 1.0.0, in your system prompt). This brief was written by hand by the ticket lead: `gov context DAEO-wahn --role independent-test-designer` refused (`CONTEXT_OVER_CEILING`, 21044 of 6000 tokens). Where this brief and the copied `EMG-common.md` / `EMG-d4b-launched.md` beside it differ, **this brief holds** (in particular: your `Implements:` trailer is the list below, not `DEC-1065`; a lead does run for this ticket).

## Identity and where you work
- Role `independent-test-designer`, ticket `DAEO-wahn` (W2-175). Check: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-wahn`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-175-tests` and `w2/W2-175-tests`). Different: stop and say so.
- **Step 0, before any work, the sandbox check, reported first in your return:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wahn','w').write('x')"` must FAIL; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop and return.
- The one folder you may write: `tests/acceptance/W2-175/` in `/home/usain/gov-os-worktrees/W2-175-tests` (a `README.md`, a support module, one or more test files). Nothing else, anywhere.

## What you test: the ticket's KPI lines, word for word (`.tickets/DAEO-wahn.md` in your tree; read it whole)
Each line's `verify:` text is the design's measure.

**S1** line: "Each of the seven role templates (role-cto, role-engineer, role-lead, role-product-spec, role-research, role-reviewer, role-test-designer) states, in one statement, that reads are open and that only four things are refused, in DEC-820 item 2's words: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); (c) the counterpart's work on the same ticket; (d) the hidden half of an evaluation set; the statement ends with [DEC-820]"
verify: "tests/acceptance/W2-175/: for each of the seven files, one statement (a paragraph, a list item or a table row, whitespace collapsed) carries `read` with `open`, `secret`, `held-out`, `counterpart` and `hidden half` and ends with `[DEC-820]`; red on the base (no template cites DEC-820 for it)"

**S2** line: "The counterpart refusal (c) is stated in each role's own half: role-engineer says the engineer never reads this ticket's acceptance-test code and may run its cases and see names, pass or fail and failure messages; role-test-designer says the designer never reads this ticket's implementation (the branch's changes other than its own tests) and works from the specification, the KPI lines and the existing code; role-reviewer says a reviewer reads everything, tests and code alike [DEC-820 item 2 (c) and item 3, DEC-957, DEC-963]"
verify: "tests/acceptance/W2-175/: three string tests, one per file, each on one statement carrying a negation (`never`, `not`) for the engineer's and the designer's, and `everything` with `tests` and `code` for the reviewer's; and tests/acceptance/W2-128/test_w2_128_templates.py::test_s3_engineer_template_holds_no_instruction_to_read_the_acceptance_tests still passes"

**S3** line: "Each of the six templates role-engineer, role-test-designer, role-product-spec, role-research, role-reviewer and role-lead states that the owner's decisions are recorded by the orchestrator's decision-record commits and that no worker or lead puts `Role: owner` or `Decided-by:` on a commit; role-cto keeps its decision-record commit line (`Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (chat, {DATE})`) unchanged [DEC-861]"
verify: "tests/acceptance/W2-175/: for each of the six, one statement carries `decision-record`, `owner` and `Role: owner`, and ends with `[DEC-861]`; for role-cto, the line of the base is still there byte for byte (a test reads it from `git show` of the base commit)"

**S4** line: "Each of the seven role templates carries, word for word, the stop sentence of the brief envelope's return section: \"Refused twice for the same call: stop and say so. Never work around a refusal: report it.\" [DEC-1137 (2)]"
verify: "tests/acceptance/W2-175/: each of the seven files holds that sentence, and the sentence is a substring of brief.md too (one source of wording, so TPL-6 F1's conflict cannot arise)"

**S5** line: "Each changed role template's `version` goes from 1.0.0 to 1.0.1 (DEC-1121's step for a template delta); no other front matter key changes, and the prose of each stays within its budget in `governance/project/facts.yaml` (3500 characters, role-lead 8000, role-cto 6000) with every placeholder a key of `keys.yaml` [DEC-1050, DEC-1116, DEC-1121]"
verify: "tests/acceptance/W2-175/: the front matter of each changed file parses with `version: 1.0.1` and the other keys equal the base's; tests/acceptance/W2-128/test_w2_128_templates.py::test_s2_prose_is_within_r3_budget and ::test_s5_every_key_placeholder_is_in_keys_yaml pass for all seven"

**S6** line: "The cases of W2-128, W2-152 and W2-153 that read the role templates still pass with the new text (the gov brief golden files, the template tests, the launch delivery) [DEC-1050, DEC-1116]"
verify: "`PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-128 tests/acceptance/W2-152 tests/acceptance/W2-153 -q -p no:cacheprovider` exits 0 in the ticket's worktree, run through the heavy-job gate"

**S7** line: "The change goes through DEC-1116's route, recorded in docs/changes/W2-175-CIT-P.md: the template delta (each changed file, its base and new sha256, the lines added), the independent review's READY, and the owner's approval of the new bytes; the record's `status` is ACCEPTED only after that approval, and the kernel set is promoted at the approved bytes [CAP-33, DEC-1116, DEC-1137 (2)]"
verify: "docs/changes/W2-175-CIT-P.md has a section per CAP-33 step (evidence, proposal, independent review, owner's approval, versioned promotion); the sha256 column equals `sha256sum` of each file at the ticket's head; the file's `decisions_read` and `decisions_carried` cite DEC-1137, DEC-820 and DEC-861"

**F1** line: "A role template line that states a rule cites a PROPOSED or superseded decision for it, or states a stop rule that differs from brief.md's [DEC-1073, TPL-6 F1]"
verify: "tests/acceptance/W2-128/test_w2_128_templates.py::test_f7_every_bracketed_decision_id_in_a_template_is_accepted passes for the seven files; the substring test of the stop sentence (success line 4) fails when one file's sentence is changed by a letter"

**F2** line: "The ticket's diff names any file beyond the seven role templates and docs/changes/W2-175-CIT-P.md: not brief.md, a `brief-*.md` pointer, keys.yaml, facts.yaml, a skill, a file under `roles/`, any `.claude/` or `.rulesync/` path [DEC-1137, DEC-315]"
verify: "`git diff --name-only <base>..HEAD` of the ticket's branch lists only those paths (a close-time check; the guard refuses the rest at write time)"

## The ticket's Interface section, word for word (stated before the pair starts, DEC-1109 (2))
**Interface (the lines, stated before the pair starts).** A template may shorten a line; it may not drop an idea.
- Policy 2, all seven: "Reads are open: the whole repository, other worktrees, git history and what your searches return. Refuse only four things: secrets and keys (never printed); the held-out qualification material's contents (its file names may be seen); the counterpart's work on the same ticket; the hidden half of an evaluation set [DEC-820]."
- (c), the engineer: "Never read this ticket's acceptance-test code; run its cases and read their names, pass or fail and failure messages [DEC-820, DEC-957]." The sentence must carry a negation: W2-128's TPL-1 S3 case refuses an engineer sentence that names the acceptance tests with a reading verb and no `never`, `not` or `no`.
- (c), the designer: "Never read this ticket's implementation (what its branch changes other than your own tests); work from the specification, the KPI lines and the existing code [DEC-820, DEC-963]." Line 4 of the base already says the first half; keep it and add what is missing.
- The reviewer: "You read everything, tests and code alike [DEC-820]."
- The record rule, the six non-CTO templates: "The owner's decisions are recorded by the orchestrator's decision-record commits; never put `Role: owner` or `Decided-by:` on a commit of yours [DEC-861]."
- The stop, all seven: "Refused twice for the same call: stop and say so. Never work around a refusal: report it." (the sentence of `brief.md`'s return section, copied, then `[DEC-1137]`).
- The base for the sha256 and the diff checks is the commit the ticket's branch starts from; the record names it.

Design from these lines (a template may shorten a line but not drop an idea: test the KPI's needles, not the Interface's exact wording, except the stop sentence, which is byte-exact).

## What you read, and what you never read
- Read: the ticket; the **base** templates as integrate has them (`git show w2/integrate:template/governance/kernel/templates/<name>.md`; your own tree holds the same bytes at the base); `tests/acceptance/W2-128/` and its support module `tests/acceptance/W2-128/w2_128_support.py` (reuse `units`, `prose`, `NEGATION`, `ENDS_CITED`, `BUDGET`, `split`, `fold` by import or by the same reading, so your cases judge a statement the way W2-128's do); `governance/project/facts.yaml`; `template/governance/kernel/templates/keys.yaml`; `docs/changes/W2-128-CIT-P.md` (the form of a CIT-P record); the decisions by id in `docs/DECISION_REGISTER.md` (grep `### DEC-820`, `### DEC-861`, `### DEC-1137`, `### DEC-1116`, `### DEC-1121`; the register is large: read by line range).
- **Never read this ticket's implementation (DEC-820 (c), DEC-963):** the worktree `/home/usain/gov-os-worktrees/W2-175` and the branch `w2/W2-175` (the product-spec worker's), and nothing `git diff --name-only w2/integrate...w2/W2-175` names. Drop unread any search or retrieval result from there and name it in your return (P-R1).
- Memory: `gov retrieve` is not available in your sandbox (DEC-1065): use the Read and Grep tools on your own tree (it is the base) and `git show w2/integrate:<path>`. When a search does not answer, or your answer may be incomplete, search once more in different words, then answer from both with path and lines, or say "not found"; two searches in all (DEC-1092 (1)). Never one giant query (DEC-860).
- DEC-849: the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, search named folders instead, count the refusals in your return.
- Protected material (DEC-820): never read the held-out material's contents or the hidden half of any evaluation set (`~/gov-os-eval`), never print a secret; never write in `~/gov-os-workbench`.

## The cases (pytest; the tests read files from the repository root they sit in: `REPO_ROOT = Path(__file__).resolve().parents[3]`)
- **S1:** one case per template, seven (parametrised): one statement (W2-128's `units`, whitespace collapsed) carries `read` with `open`, `secret`, `held-out`, `counterpart` and `hidden half` and ends with `[DEC-820]`.
- **S2:** three string cases, one per file (role-engineer, role-test-designer: one statement with a negation `never`/`not` and the KPI's needles; role-reviewer: one statement with `everything`, `tests` and `code`). Name W2-128's `test_s3_engineer_template_holds_no_instruction_to_read_the_acceptance_tests` in the README as the guard case (not re-written).
- **S3:** six cases (one per non-CTO template): one statement carries `decision-record`, `owner` and `Role: owner` and ends with `[DEC-861]`; and the role-cto case: the decision-record line of the base is still in the file byte for byte, read with `git show a6c83d497035:template/governance/kernel/templates/role-cto.md` (a6c83d497035 is the last commit that changed role-cto.md before this ticket; say why in a comment: a base is the last commit to change the file before the ticket, never an old one).
- **S4:** seven cases (each file holds the exact sentence `Refused twice for the same call: stop and say so. Never work around a refusal: report it.`) plus one case that the sentence is a substring of `template/governance/kernel/templates/brief.md`. Put the check in one helper the F1 case reuses.
- **S5:** the front-matter case per template: parses, `version` is `1.0.1`, every other key equals the base's (read the base with `git show a6c83d497035:<path>`-style from the last commit that changed each file before this ticket; find each with `git log -1 --format=%h w2/integrate -- <path>`, or read the base front matter from `w2/integrate` since the templates are unchanged there; say which and why in a comment, and that the reading stays right after this ticket merges). The placeholder and budget checks are W2-128's own tests (`test_s2_prose_is_within_r3_budget`, `test_s5_every_key_placeholder_is_in_keys_yaml`): named in the README, not re-written.
- **S6:** README note: the ticket's own command over W2-128, W2-152 and W2-153 (no new case).
- **S7:** structure cases of `docs/changes/W2-175-CIT-P.md`: front matter with `decisions_read` and `decisions_carried` each citing DEC-1137, DEC-820 and DEC-861; a section per CAP-33 step (evidence, proposal, independent review, owner's approval, versioned promotion); a table whose sha256 column for each of the seven files equals `sha256` of that file at the head; `status` is PROPOSED or ACCEPTED, and ACCEPTED only with a non-empty owner's-approval section. **It never requires ACCEPTED**: the owner's approval follows the review, after the lead returns. Judge the headings loosely enough that an honest writer following the five step names passes (state your reading in the README).
- **F1:** the mutation case: a planted copy (in `tmp_path`) of one template with the stop sentence changed by one letter makes the S4 helper fail; and name W2-128's `test_f7_every_bracketed_decision_id_in_a_template_is_accepted` in the README.
- **F2:** a README note only (a close-time check over the branch's diff against a base the tests cannot name stably; the lead checks it with `git diff --name-only <BASE>..HEAD -- . ':!tests/acceptance/W2-175'`).
Deterministic, no network, no real model, no store; a case that needs a repository builds one in `tmp_path`.

## The red on the base is the design's proof
Run your folder on your own worktree (the base templates): every S1 to S5 and S7 case must be red there for the reason the README states (S7: the record does not exist yet). A case green on the base pins nothing: rewrite or drop it, and name it. The expected greens on the base: the F1 mutation case, the role-cto byte-for-byte case of S3 (the line is there at the base: name it as a guard case, green by design), the `brief.md` substring case of S4, and any W2-128 guard case. Name each expected green.

## The README map, in the form `gov accept` reads (DEC-959 item 6)
One heading per KPI line (`### Success 1: ...` to `### Success 7: ...`, `### Failure 1: ...`, `### Failure 2: ...`, as in `tests/acceptance/W2-105/README.md` and `tests/acceptance/W2-128/README.md`), each with a table whose `Test` column holds **real case ids** in code spans (`test_<file>.py::test_<name>` or `test_<file>.py::test_<name>[param]`), and the expected red reason. **No placeholder in angle brackets, no bare `name[param]` without its file.** Read `src/gov/accept/runner.py` (`parse_map`, `matches`) in your tree to check your map, then run once at the end, outside pytest:
`env PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-175-tests/src gov accept DAEO-wahn --root /home/usain/gov-os-worktrees/W2-175-tests --json`
Every mapped line must read pass (expected greens) or fail for its stated reason, none "fail with 0 cases". S6 and F2 lines, which have no case of yours, are mapped to the W2-128/W2-152/W2-153 cases if `gov accept` can collect them from another folder, otherwise stated in the README as notes; say in your return how `gov accept` read them.

## Running tests
- `PYTHONPATH` is always your tree's own `src` (DEC-732, word for word: **every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-175-tests/src` set per command**).
- Your folder: `env HOME=/home/usain/gov-os-worktrees/W2-175-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-175-tests/src python3 -m pytest tests/acceptance/W2-175 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"` (one small folder: no heavy slot needed; anything larger goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>` if your sandbox allows it, else say so). Never the full suite; never `-x`.
- Scratch budget (DEC-898): your share 2 GB and 100,000 files outside the tracked tree; the sandbox's own TMPDIR; clean as you go; give `du -sh` of what you leave.

## Commit
`git commit -m "W2-175: acceptance tests for the role templates' Policy 2, record rule and stop lines" --trailer "Task: DAEO-wahn" --trailer "Implements: DEC-1137, DEC-820, DEC-861, DEC-1116, DEC-1050, DEC-1121, DEC-957, DEC-963, DEC-1073, DEC-315, CAP-33" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-175`
New files: no `Rewrite-Reason`. Never amend, rebase, merge or push. Before committing check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit`; never `--no-verify`.

## Rules
- Command forms the guard reads: one simple command per Bash call; no `cd ... &&`; no here-documents, backticks, `$(...)` or shell variables as a write target; no long inline `python3 -c` with braces; anything longer goes in a script file under `/home/usain/gov-os-worktrees/W2-175-tests/.gov-runtime/scratch/` (Write tool), run with `python3 <file>`. A refused form is not retried in another disguise.
- Row W2-L423's rule (DEC-911): under `.gov-runtime/`, commit hashes as 12 digits, never 40; never write the keywords of the secrets rule that takes a bare 40-hex string. In committed tests, compute hashes at run time rather than writing them.
- No installs (P1 in your return). No copy of the tree (`cp -r`, `rsync`, `git worktree`, `git clone`).
- An ambiguous KPI line is never guessed: return it in `proposed_decisions` with options, recommendation and confidence.
- **Refused twice for the same call: stop and say so. Never work around a refusal: report it.**

## Return (your last message; nothing else is read)
Add to the fields: the case ids per KPI line, the red and green counts on the base with each green named, the exact pytest line, `gov accept`'s per-line reading, your commit (12 digits), the sandbox check result, and the retrieval/refusal counts.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

The twelve fields come first, each as a labelled line, any payload after them. Refused twice for the same call: stop and say so.
