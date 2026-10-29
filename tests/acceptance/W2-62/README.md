# W2-62 acceptance tests (DAEO-juee)

W2-62: resume in full. The session-start hook delivers the whole RESUME HERE section and names the prompt in
force (rows W2-M372, W2-M373; DEC-837, DEC-792, DEC-838). Profile STANDARD. The independent test designer
(MR-3) wrote these tests from the ticket's KPI lines and their sources, before the implementation. The designer
read the existing hook only as it stands on `w2/integrate`.

## How they run

```
PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src \
python3 -m pytest tests/acceptance/W2-62 -q -p no:cacheprovider -rs -m "not local_only"
```

The live case (`local_only`) is run by the lead, on a machine with the network and the caller's own Claude Code
credentials: the same command with `-m local_only`. It needs `~/.local/bin/claude` (2.1.292) and is skipped with
that reason when the CLI is absent. Run it once and expect one to five minutes. A run in which the model gives no
answer fails with that reason and is repeated (DEC-232). Such a run is not a finding against the hook.

- **Which code runs (DEC-732).** `w2_62_support.py` derives `REPO_ROOT` from its own location
  (`Path(__file__).resolve().parents[3]`). Every hook run is `python3 REPO_ROOT/template/governance/kernel/hooks/sessionstart.py`,
  started as a process with `PYTHONPATH=REPO_ROOT/src`, so the tests always run the hook of the checkout they
  are in, never an installed copy, a registered command or `.claude/hooks/`. The fixture `code_under_test`
  asserts that the hook and `src/gov/__init__.py` exist. The staleness cases also run `precompact.py` from the
  same folder, to put a real generated state block at the end of a checkpoint.
- **The projects.** Every test builds its own git repository from scratch under pytest's `tmp_path`: a README,
  a `.gitignore`, stand-in prompts (always including `governance/project/prompts/w1-orchestrator.md` as a
  file, so a hook that falls back to it would find it), and, as the test needs, a roster at
  `governance/project/roster.yaml` and the checkpoint. The worktree cases add a real linked worktree of that
  temporary repository. Nothing of this repository is copied or read as fixture data. Nothing is written under
  a `.gov-runtime/` folder of this repository.
- **`tk`.** A stand-in `tk` comes first on the hook's `PATH`. It prints a ready list the test chooses (empty by
  default, 30,000 characters for the trimming cases). The real `tk` is never called.
- **Deterministic, no network**, apart from the one `local_only` case. Each hook run must end within 15 s.

## The interface these tests fix

| What | Fixed by these tests |
|---|---|
| The bound | `hookSpecificOutput.additionalContext` is never longer than 10,000 characters. This is the size up to which Claude Code 2.1.292 delivers a SessionStart hook's context whole; the orchestrator measured it on 2026-10-19. |
| The instruction (orchestrator, a section exists) | The checkpoint's path relative to the project; the words "read", "RESUME HERE", one of "in full / whole / entire / complete / every line", and one of "before anything else / before doing anything / first"; the range as `lines <first>-<last>`; the size as `<n> characters` (thousands separators allowed). |
| The range | 1-based line numbers of the checkpoint file, inclusive: from the heading line to the section's last line that is not empty. Trailing empty lines are excluded. A generated state block is never part of it. A `#` line inside a fenced block neither starts nor ends the section. |
| The size | The number of characters of those lines joined by newlines (no final newline). |
| Whole when it fits | When the instruction, the staleness warning (if any) and the whole section fit within 10,000 characters together, the section is in the injection character for character. A total of exactly 10,000 counts as fitting. |
| Never a cut | A section that does not fit: never its first 9,000 characters as a cut, and never the word "truncated". The tests neither require nor forbid a short opening part. |
| Optional parts | The `gov context --brief` summary, the `tk ready` output and the checkpoint brief are the parts trimmed. The instruction, the warning and a section that fits never are. |
| No section | The checkpoint's path, and one of "missing / can't be read / cannot be read / could not be read / unreadable / no RESUME HERE / not found / does not exist". No line range. Exit 0. |
| The prompt in force | `governance/project/roster.yaml` → `roles:` → `orchestrator:` → `prompt: <path relative to the project>`. When it is set, the injection names that path: in the main tree with "read" and "now", in a linked worktree with "ticket lead for <GOV_TICKET>" and "appendix A5". When it is absent (no roster, no key, the key only under another role, a roster that is not valid YAML), the injection holds nothing under `governance/project/prompts/` and names none of the test's other prompt paths. The checkpoint and its instruction are still there. |
| Unreadable input | Empty stdin, text that is not JSON, a JSON array, a JSON string, or a checkpoint that is not UTF-8: exit 0, and stdout is either nothing or one `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": <str>}}` within the bound. |
| Other roles | `engineer`, `independent-test-designer` or no `GOV_ROLE`, in the main tree and in a worktree: none of the section's text, no "RESUME HERE", no line range. |
| The skill | In the Markdown section(s) of `template/governance/kernel/skills/checkpoint/SKILL.md` that name RESUME HERE: "session state" with one of full/whole/complete/entire; terms for what is happening, what was decided, what is next and where; "knowledge", "retriev…", "context packet". In the section(s) that speak of the handover: every/each handover, a worker's return, merge, package, compaction. Any mention of 8,000 must say that the limit is lifted, no longer applies or was removed. |
| The CIT-P | `docs/changes/W2-62-CIT-P.md` records 2.1.292, headless (or `claude -p`), SessionStart, additionalContext, 9,500 (whole), 12,000 and 60,000, "saved to a file", "preview", the bound of 10,000, and the route (instruction or read, the file, the line range, the size). |

## KPI lines, their tests and the red reason

Red, observed on 2026-10-19 against the base (`162f17ea`, the hook as on `w2/integrate`): **35 failed, 22 passed**
of the 57 deterministic tests. The 1 `local_only` test was deselected and not run (no network here).

| KPI line | Tests | Red reason on the base |
|---|---|---|
| Success 1: the whole section, never a 9,000-character cut, no "[truncated]" | `test_w2_62_resume_in_full.py`: `test_a_section_that_fits_is_injected_whole_with_the_instruction` ×4 sources, `test_the_fit_edge_whole_at_the_bound_and_never_cut_one_character_over`, `test_a_section_of_50000_characters_is_named_by_its_lines_never_cut` ×2, `..._in_a_worktree`, `..._after_a_compaction` | No `lines a-b` range in the injection. Past that point the base would also fail on the 9,000-character cut and the word "truncated", and in the edge test on a section of about 9,700 characters cut at 9,000. |
| Success 2: research first; the route that arrives whole; a live resumed session reads the whole section | `test_w2_62_documents.py`: `test_the_research_record_exists_and_names_the_measured_harness`, `..._gives_the_measured_sizes_and_what_happened`, `..._gives_the_conclusion_the_bound_and_the_route`. `test_w2_62_resume_in_full.py`: every test that calls `assert_instruction` (section ends at the end of the file, empty lines before the next heading, a level-1 heading with more text, a fenced `#` line, a section followed by the generated state block, the lead's section in a worktree). `test_w2_62_live_resume.py` (`local_only`) | `docs/changes/W2-62-CIT-P.md` does not exist; the injection gives no line range or size. The live case is not run here. On the base it would fail: the session is given the first 9,000 characters and no route to the token at the end. |
| Success 3: the cap never cuts the section or the instruction; the optional parts are trimmed | `test_a_long_ready_list_is_trimmed_not_the_section_or_the_warning`, `test_a_long_ready_list_with_a_50000_character_section_stays_within_the_bound`, `test_a_section_followed_by_a_generated_state_block`, `test_a_section_of_50000_characters_after_a_compaction` | No line range (the base keeps the warning and trims the ready list, but has no instruction with a range). |
| Success 4: the prompt of the wave in progress, from the configuration; none when there is no setting | `test_w2_62_prompt_in_force.py`: `test_the_main_tree_names_the_rosters_prompt` ×3, `test_in_a_worktree_the_lead_is_sent_to_appendix_a5_of_the_rosters_prompt` ×2, `test_two_projects_with_two_prompts_get_two_paths`, `test_with_no_setting_the_main_tree_names_no_prompt` ×4, `test_with_no_setting_the_worktree_names_no_prompt`, `test_with_no_setting_and_no_checkpoint_the_path_and_the_gap_are_still_named` | The base names the constant `governance/project/prompts/w1-orchestrator.md` whatever the roster says, and names it when there is no roster. |
| Success 5: the checkpoint skill states the resume rule | `test_the_skill_says_resume_here_holds_the_full_session_state`, `test_the_skill_says_repository_knowledge_comes_from_retrieval_and_the_context_packets`, `test_the_skill_says_a_checkpoint_is_written_at_every_handover`, `test_the_skill_does_not_limit_resume_here_to_8000_characters` | The skill on the base does not mention RESUME HERE, retrieval, context packets or a handover. **Passes on the base:** the 8,000 test, because the skill on the base states no 8,000-character limit. It guards against one being written. |
| Failure: 50,000 characters with no character lost; no section still says so; unreadable input exits 0; another role gets no injection | 50,000: the four tests under success 1, and the live case. No section: `test_no_section_still_says_so` ×5 (no checkpoint, no section, a directory, an unreadable file, a RESUME HERE heading only inside a fence) and `test_in_a_worktree_without_a_lead_checkpoint_the_lead_path_is_named`. Unreadable input: `test_unreadable_input_exits_0` ×8 (4 kinds of stdin × orchestrator and engineer), `test_a_checkpoint_that_cannot_be_decoded_exits_0`. Other roles: `test_another_role_gets_no_resume_here_injection` ×6 | 50,000: no line range. **Pass on the base** (behaviour the base already has): the 6 no-section tests, the 9 unreadable-input tests and the 6 other-role tests. |

The 22 tests that pass on the base: the 21 failure-line tests just named and the 8,000 test.

**The tests checked against a reference.** Before committing, the designer ran the 57 deterministic tests
against a throwaway reference hook, skill and CIT-P written only in the session's temporary scratch folder
(never in this tree, and gone with the session). All 57 passed. With the fit check made strict (`<` in place
of `<=`), only the edge test failed. With trailing empty lines kept in the range, the 27 range tests failed.
So the tests can be met as written, and they catch an off-by-one at the edge and in the range.

## Earlier tests revised (rewrites, with their reasons)

This ticket's KPI lines contradict three assertions of the earlier suites that run the same hook. Each is
revised by the least change that makes it agree. No other earlier test was touched.

| File | Change | Reason |
|---|---|---|
| `tests/acceptance/W1-49/w1_49_support.py` | `make_project` also writes `governance/project/roster.yaml` with `roles: orchestrator: prompt: governance/project/prompts/w1-orchestrator.md` (new constants `ROSTER_REL`, `STAND_IN_ROSTER`). | Success 4 (W2-M373): the hook names the prompt the roster names, and none without a roster. Every W1-49 and W1-29 assertion that expects `PROMPT_REL` (the fixture's stand-in prompt) to be named now holds because the fixture's roster names it. Those assertions are unchanged. This covers W1-29 too, whose `combined_base` is built by this `make_project`. |
| `tests/acceptance/W1-49/test_w1_49_sessionstart.py::test_a_resume_here_section_larger_than_the_cap_is_cut_and_said_so` | Renamed `..._is_named_by_its_lines_not_cut`. The assertion that the section's head is injected is replaced by one that a `lines a-b` range is given, and "`truncated` in the injection" becomes "`truncated` not in it". | Success 1 and failure line (W2-M372, DEC-837 item 1): a section over the cap is never cut and never said to be truncated. Whether its opening part is shown is the implementer's choice, so the head assertion cannot stay. |
| `tests/acceptance/W1-49/test_w1_49_sessionstart.py::test_a_section_over_the_cap_with_the_warning_stays_inside_the_cap` | The same two assertions are changed in the same way (docstring updated). | The same. |
| `tests/acceptance/W1-49/README.md` | A history row (batch 6) points here. | So that its section 1 rows "The cap" and "SessionStart in the main tree" are not read as current. |

On the base, the revised W1-49 suite gives 92 passed and 2 failed: the two rewritten tests, red because there is
no line range. The other 11 tests are `local_only` and were deselected. W1-29 gives 45 passed.

## Files

| File | What |
|---|---|
| `w2_62_support.py` | Project and checkpoint builders, the hook runner, the shared assertions, the regular expressions of the range and size forms |
| `conftest.py` | Fixtures (`code_under_test`, `sandbox`, `project`, `worktree`) and the `local_only` marker |
| `test_w2_62_resume_in_full.py` | Items 1–6, 8, 9 (success 1–3, failure line) |
| `test_w2_62_prompt_in_force.py` | Item 7 (success 4) |
| `test_w2_62_documents.py` | Items 10, 11 (success 5; success 2, first half) |
| `test_w2_62_live_resume.py` | Item 12, `local_only` (success 2, second half; failure line) |
