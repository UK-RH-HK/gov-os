**Sandbox check (step 0):** (a) the write of `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-lrre` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` worked (blob `1ae28402a`, exit 0), and so did `git update-index --refresh` (exit 0). GOV_TICKET=DAEO-lrre. The check passes.
**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

- **task:** DAEO-lrre (W2-33), rv-3: narrow independent check of commit `4452d6b8c` (`git diff 707d23b82 4452d6b8c`)
- **status:** done. The check passes with two recorded rows; nothing blocks.
- **work_completed:** HEAD is the expected `9ace61e8ce72e7371b88be5c6a65abfd9baaa1fd`. I read the diff, the ticket's `## Interface` and its KPI lines, the helpers in `w1_33_support.py`, and DEC-163 and DEC-1156 (3) and (7). I recomputed the pinned hash from the git object. I ran 19 changes to copies of research.md in my sandbox's TMPDIR, using the case's own logic. I ran the W1-33 folder through the heavy slot twice and got the same result both times.
- **files_changed:** none. `git status --porcelain` was empty at the end. The only writes were the blob from the step-0 check and scratch files in `$TMPDIR/rv3`.
- **evidence:**
  - Recomputed body hash of `c70bbb69d:template/governance/kernel/roles/research.md`, using the case's filter: `4793c8eba118c7e39acb9211a60b802b73c101f2c28348e69b11593b476d3596`. It equals the pin.
  - The whole file at `c70bbb69d` hashes to `60f9092f…`, which equals the old `RESEARCH_ROLE_FILE_SHA256`, so the source commit is the right one.
  - HEAD's research.md gives the same body hash. Its only differences from W1-46's file are the six added Interface lines and the old `- **Model tier:** standard; …` line, which is removed.
- **tests:** `6 failed, 105 passed, 1 skipped, 2 deselected`.
  - Case 1 passes.
  - Case 2 fails as the brief expects: `missing ['qa-engineer', 'senior-engineer', 'ticket-lead'], extra []`, with six agents found.
  - The five `test_the_definition_agrees_with_its_kernel_role_file[*]` cases fail; these belong to the copies ACT.
  - The exclusion (`-m "not local_only" -k "not real and not green_here and not time_limit"`) deselected two cases. I did not find their names: no test function name contains those words, so they are probably parameter ids.
- **discoveries:** W2-33's own test `test_w2_33_lines` already checks each head once, whole and at column 0. It also checks that `Launch by criticality` is absent where the model rubric does not vary. This covers the blind spot in N1.
- **risks:** none beyond N1 and N2
- **lessons:** none
- **proposed_decisions:** none
- **unresolved:** the names of the two cases the exclusion deselected
- **recommended_next_action:** land the revision. N1 and N2 are recorded rows only.

## Findings

**N1. Lines starting with one of the seven heads are invisible to case 1.**
- **Behaviour:** the body hash skips every line that starts with one of the seven heads, and case 1 asserts only four whole lines. So these changes to research.md all leave case 1 passing:
  - a second, conflicting `- **Launch default:** model claude-opus-5-5, effort high` line added
  - a `Launch by criticality` line added for research
  - the `Version` or `Skills` line dropped
  - any new line beginning `- **Version:** …`
- **Where:** `tests/acceptance/W1-33/test_w1_33_kernel_role_files.py:182-184` (the filter) and `:187` (the case).
- **Severity:** low.
- **Ordinary work:** yes, because a duplicated or stray line during an edit is easy to make.
- **Consequence:** other. It does not fail open, because W2-33's `test_w2_33_lines` turns red on each of these.
- **Status:** row, in scope, not blocking.
- **What would reverse it:** a change that passes case 1 and also passes W2-33's line tests.

**N2. Line endings and the final newline are normalised.**
- **Behaviour:** `splitlines` followed by `"\n".join(...) + "\n"` means converting research.md to CRLF, or removing its final newline, leaves case 1 passing.
- **Where:** `test_w1_33_kernel_role_files.py:182-184`.
- **Severity:** negligible.
- **Ordinary work:** yes, because an editor can convert line endings.
- **Consequence:** other. The text of the body does not change.
- **Status:** row, not blocking.
- **What would reverse it:** DEC-163 being read as pinning the bytes rather than the text.

## Answers

**1. Case 1 keeps the point of DEC-163.**
- The glob still checks that `research*` gives exactly `["research.md"]`.
- The pin matches my recomputation, and it is computed from W1-46's git object, not from HEAD.
- Changing research.md's own body turns the case red. Each of these did: a line removed, a line added, a word changed, a trailing space added, a blank line added, and a body line replaced by a line under a head.
- Changing any of the four asserted lines turns it red. Each of these did: Launch default dropped, Launch default changed to Opus, Model tier changed, a word of Work order changed, One writer dropped, Work order duplicated.
- The filter matches only exact column-0 prefixes like `- **Version:**`, and W1-46's body has no line like that except the old Model tier line. So the filter hides no existing body text. The gap is only in lines added under a head (N1), and W2-33's own tests cover it.

**2. Case 2 is correct.**
- It wants exactly nine definitions: the five of `support.ROLES`, `research`, `ticket-lead`, `qa-engineer` and `senior-engineer`. It asserts the roster is nine, that `independent-reviewer` is not defined, and that each name is defined once.
- Its docstring says it is red until the copies ACT generates the three agents (DEC-315).
- Today it is red only because those three are missing: nothing is extra, nothing is duplicated, and there is no `independent-reviewer`. It brings no other red in W1-33.

**3. The Rewrite-Reasons, the scope and the trailers are in order.**
- Each case carries a `Rewrite-Reason:` naming DEC-1156 (3), (7) and saying what changed and why: `test_w1_33_kernel_role_files.py:151` and `test_w1_33_agent_definitions.py:86`.
- The diff touches nothing else in the two files beyond `import hashlib`, the module constants (`_INTERFACE_LINE_HEADS`, the pin, `_RESEARCH_INTERFACE_LINES`, `_ADDED_ROLES`, `_NOT_A_ROLE`) and the helper `_without_interface_lines`.
- The trailers are `Task: DAEO-lrre`, `Role: independent-test-designer` and `Implements: DEC-957, DEC-959, DEC-1120`. All three ids are in the ticket's `sources:`. The commit also carries a `Rewrite-Reason:` trailer.
- The commit has no `Role: owner` and no `Decided-by:`.

**4. No assertion is fitted to HEAD's file.**
- I compared programmatically: the Work order and One writer strings equal the ticket's `## Interface` word for word.
- `Model tier: see Launch default` comes from the Interface. `model claude-sonnet-5-5, effort high` comes from S7 ("product-spec and research Sonnet high") and the Interface's statement that "Sonnet" means claude-sonnet-5-5.
- The values that exist only in HEAD's file are not asserted: `Version: 1.1.0` and `Skills: discovery, retrieval`.
- The pin is computed from `c70bbb69d`. It happens to equal HEAD's body hash, which is the expected outcome, not a sign of fitting.

```verdict
verdict: PASS
probed_commit: 9ace61e8ce72e7371b88be5c6a65abfd9baaa1fd
findings: 2
```
guard_refusals: none. One first test run was lost in a background timeout; I reran it. One heavy-slot wait ("all 3 slots taken") was a wait, not a refusal. A Monitor call needed approval and was not used.