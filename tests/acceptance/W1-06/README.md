# W1-06 — Wave 1 tool prerequisites: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-ipqy` (W1-06), CAP-25 / CAP-25.a
and CAP-40 of Contract v4, DEC-074, DEC-083, DEC-086, DEC-121, DEC-127, DEC-141, DEC-191, ADR-0002 §2 and the "Interim
install rule" of `governance/project/bootstrap.md`. Written before implementation. No earlier ticket's test was
rewritten.

**Second batch (2026-10-03, a fresh designer, still before implementation).** The owner answered the four packages
below (DEC-192 … DEC-197). This batch adds 49 cases in three files for those answers and revises two cases of this
suite; see "Second batch" below.

**Third batch (2026-10-03, a fresh designer, after implementation).** The owner answered DP-5 (DEC-199). This batch
adds 2 cases in one file and changes no existing test; see "Third batch" below.

## Run

```sh
python3 -m pytest tests/acceptance/W1-06 -q -p no:cacheprovider
```

`pytest`, the standard library and PyYAML (the project's declared dependency, used only to parse the registry). No
network. **No test installs, downloads, uninstalls or runs an install command.** The tests read the committed registry,
its schema, the decision register and the vendor folder, and ask git what it tracks.

Eleven cases are marked `local_only`; they fail, not skip, when the tool is absent, because on this machine it must be
there. Deselect them elsewhere with `-m "not local_only"`.

- 2 (ccusage): they look for the ccusage package under `~/.nvm/versions/node/v22.23.3` (DEC-192) and read the version
  from its own `package.json`. Nothing is run.
- 7 (DEC-196): they hash a single-file binary that is already on this machine and compare it with the registry.
- 1 (DEC-195): it runs `gitleaks version`, which prints the version and touches nothing.
- 1 (DEC-194): it asks whether the scratch clone's folder still exists. It reads nothing in it.

## KPI → tests → red reason today

First red run on `w1/integrate` at `175c5ef3`: 45 errors (45 cases, 27 test functions). Second batch, at `42acf806`:
**94 errors, 0 passed, 0 failed** (94 cases, 51 test functions).

- 80 cases error in the `registry` fixture: **`governance/project/tool-registry.yaml does not exist: W1-06 has not
  created the tool registry`**.
- 14 cases (`test_w1_06_vendor.py`) error in the `vendor` fixture: **`template/governance/kernel/vendor/superpowers/
  does not exist: W1-06 has not committed the Superpowers source`**.

The last column gives what each group fails on first once the file exists.

| KPI line | Test file | Test functions | Red reason after the file exists |
|---|---|---|---|
| **Success 1.** ccusage installed and pinned through a DEC-083 decision package and recorded in the registry | `test_w1_06_ccusage.py` | `test_ccusage_is_recorded_in_the_registry` · `test_ccusage_is_pinned_to_one_exact_version` · `test_the_recorded_install_command_installs_the_pinned_version` · `test_the_recorded_uninstall_command_removes_ccusage` · `test_ccusage_carries_a_sha256_digest` · `test_ccusage_was_approved_by_an_owner_decision_of_the_register` · `test_ccusage_was_not_installed_before_its_approval` · `test_ccusage_is_installed_on_this_machine` (`local_only`) · `test_the_installed_ccusage_is_the_pinned_version` (`local_only`) | No ccusage entry; there is no `ccusage` on `PATH` today |
| **Success 2, second half.** Every DEC-074 pin is recorded in the registry with sha256 **[CAP-25.a]** | `test_w1_06_pins.py` | `test_a_dec_074_pin_is_recorded_at_its_pinned_version[10]` · `test_a_dec_074_pin_is_recorded_with_the_sha256_of_the_stack_table[10]` · `test_pyyaml_is_recorded_at_6_0_1` (DEC-191) | No entry for the pin |
| **Success 2, first half.** The Superpowers v6.4.2 source is available for vendoring | `test_w1_06_pins.py` | `test_superpowers_is_recorded_at_v6_4_2` · `test_superpowers_is_recorded_with_a_sha256_digest`. Where the source must be was DP-3; see the DEC-194 row below | No Superpowers entry |
| **CAP-25.a.** Tool registry with pins, sha256, install/uninstall commands, date, approving decision | `test_w1_06_registry.py` (and the pins file above) | `test_the_registry_is_committed` · `test_the_registry_is_valid_against_the_committed_schema` · `test_the_registry_records_at_least_one_tool` · `test_every_entry_states_all_seven_facts` · `test_each_tool_is_recorded_once` · `test_every_sha256_is_a_sha256_digest` · `test_every_date_is_a_calendar_date` | The file is not committed, or an entry breaks the schema |
| **Failure 1.** Any tool installed without a recorded owner approval | `test_w1_06_approvals.py` | `test_every_entry_names_one_decision_as_its_approval` · `test_every_approving_decision_is_in_the_register` · `test_every_approving_decision_is_accepted_by_the_owner` · and the two ccusage approval tests above | An `approved_by` that is not an owner-accepted decision of the register |
| **Failure 2.** A registry entry lacks an uninstall command | `test_w1_06_registry.py` | `test_every_entry_has_an_uninstall_command` · `test_no_uninstall_command_is_the_install_command` · `test_the_schema_refuses_this_registry_once_an_entry_loses_its_uninstall_command` · `test_the_recorded_uninstall_command_removes_ccusage` | An entry with no, an empty or a copied uninstall command |

| **Success 1 and failure 1, as answered (DEC-192, DEC-193, DEC-197).** Each install has its own register entry, which `approved_by` cites | `test_w1_06_install_approvals.py` | `test_an_install_of_this_ticket_is_recorded_at_the_approved_version[2]` · `test_an_install_of_this_ticket_cites_a_decision_that_names_the_tool_and_its_version[2]` · `test_an_install_of_this_ticket_has_its_own_register_entry[2]` · `test_the_approval_of_an_install_of_this_ticket_is_made_under_dec_083[2]` · `test_an_install_of_this_ticket_is_not_dated_before_its_approval[2]` · `test_the_ccusage_install_command_is_the_approved_one` · `test_the_ccusage_uninstall_command_uses_the_same_npm` · `test_the_superpowers_install_command_fetches_the_approved_source` · `test_a_stack_pin_cites_dec_074[10]` · `test_pyyaml_cites_dec_191` · `test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool` | No ccusage or Superpowers entry; then an `approved_by` that is the rule (DEC-083) and not the approval |
| **Success 2, second half, as answered (DEC-195, DEC-196).** gitleaks 8.30.1 is a pin; a single-file tool's sha256 is its binary's | `test_w1_06_digests.py` | `test_gitleaks_is_recorded_at_8_30_1` · `test_gitleaks_is_recorded_with_a_sha256_digest` · `test_a_single_file_tool_is_recorded_with_the_sha256_of_its_binary[7]` (`local_only`) · `test_the_gitleaks_on_this_machine_is_the_pinned_version` (`local_only`) | No gitleaks entry |
| **Success 2, first half, as answered (DEC-194).** The three skills and the licence are committed; nothing else of Superpowers is | `test_w1_06_vendor.py` | `test_the_vendor_folder_is_committed` · `test_a_skill_folder_is_there_with_its_skill_md[3]` · `test_a_skill_md_declares_the_skill_of_its_folder[3]` · `test_the_upstream_licence_is_there` · `test_no_other_skill_is_there` · `test_no_plugin_is_there` · `test_no_hook_is_there` · `test_nothing_but_the_three_skills_and_the_licence_is_there` · `test_the_excluded_parts_are_nowhere_in_the_repository` · `test_the_scratch_clone_is_deleted` (`local_only`) | The vendor folder does not exist |
| **Success 2, first half, as answered (DEC-199).** The Superpowers entry's sha256 is the digest of the committed vendor folder | `test_w1_06_vendor_digest.py` | `test_the_superpowers_sha256_is_the_digest_of_the_committed_vendor_folder` · `test_the_digest_rule_gives_the_value_worked_out_by_hand` | Red at `58113a8a`: the registry holds the sha256 of `git archive --format=tar HEAD` of the deleted clone |

**Count.** KPI lines with tests: 4 of 4 (2 success, 2 failure). Covers ids with tests: 1 of 1 (CAP-25.a). Owner
answers with tests: 7 of 7 (DEC-192 … DEC-197, DEC-199). The suite has 96 cases.

## Third batch: what was added

Written after the implementation was committed (`5faec8cb`), against `w1/integrate` at `58113a8a`.

- **Added:** `test_w1_06_vendor_digest.py` (2 cases, 2 functions, neither `local_only`); the helpers `folder_digest`
  and `committed_files` at the end of `w1_06_support.py`.
- **Result at `58113a8a`: 95 passed, 1 failed.**
  - `test_the_superpowers_sha256_is_the_digest_of_the_committed_vendor_folder` is **red**: the registry records
    `fb46c877…1ac94ef1` (by its own note, the sha256 of `git archive --format=tar HEAD` of the clone); the digest of
    the 15 committed files by DEC-199's rule is
    `f2a95244bc977742ee2cf6e5228fd1c24c276d63e7c1e732b3fcf9b2e8c0b90a`.
  - `test_the_digest_rule_gives_the_value_worked_out_by_hand` is **green**: it fixes the rule on two files against a
    value computed with `sha256sum` alone, and does not read the registry.
- **Rewritten: nothing.** DEC-200, DEC-201 and DEC-202 were read against every existing case; none contradicts one.
  - DEC-200 (openspec, check-jsonschema, copier may carry the digest of their installed entry script where ADR-0002
    pins it): those three are tested against ADR-0002 §2's digests (`test_w1_06_pins.py`), which is that value. Reading
    22's reason for not recomputing them ("their artefact is not on this machine") is superseded: the entry script is
    there, and `gov doctor` re-checks it. No recomputing case is added in this batch.
  - DEC-201 (gitleaks and PyYAML dated 2026-10-03, PyYAML by `sudo apt-get`): no case fixes their dates or commands.
  - DEC-202 (the ccusage commands carry `PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH`): the cases of reading 18 ask
    for the npm of Node v22.23.3 by its path and do not refuse a prefix. **No case requires the prefix**: a command
    without it would still pass. That is a gap, left as it is because this batch's brief is DEC-199.

## Second batch: what was added and what was revised

- **Added:** `test_w1_06_install_approvals.py` (25 cases, 11 functions), `test_w1_06_digests.py` (10 cases, 4
  functions), `test_w1_06_vendor.py` (14 cases, 10 functions); the `vendor` fixture; helpers at the end of
  `w1_06_support.py`.
- **Revised (2 cases, both `local_only`, in `test_w1_06_ccusage.py`):** `test_ccusage_is_installed_on_this_machine`
  and `test_the_installed_ccusage_is_the_pinned_version` looked for `ccusage` on `PATH`. DEC-192 approves the install
  with the npm of Node v22.23.3, whose `bin` is not on `PATH` (the nvm default stays v18.20.8), so an install made as
  approved would have failed them. They now look under `~/.nvm/versions/node/v22.23.3`. Reason: owner answer DEC-192;
  the implementation had not begun. Reading 10 is revised with them.
- **Unchanged:** the ten pins (DEC-195 confirms them) and every other case of the first batch. Three module
  docstrings that pointed at open packages now point at the answers.

Not tested here, by the brief: Claude Code, bubblewrap and socat (W1-48 records them). Comparing pins with what is found
on the machine is `gov doctor` (W1-27); the only such comparison here is ccusage, because its KPI says "installed".

## Readings the sources do not spell out

1. **"Every DEC-074 pin" is read from ADR-0002 §2**, whose heading is "Stack (DEC-074, Balanced) — exact pins". DEC-074
   itself states only two versions (codebase-memory-mcp 0.11.0, ticket v0.3.2). The tests require the ten rows of that
   table that state both one exact version and a sha256: OpenSpec 1.13.2, check-jsonschema 0.38.2, ticket v0.3.2,
   codebase-memory-mcp 0.11.0, Ollama 0.35.0, rulesync 24.0.0, Copier 9.18.2, lefthook 2.1.15, uv 0.12.21, Node
   v22.23.3. The rows with no sha256 were DP-1; DEC-195 confirms the ten and adds gitleaks 8.30.1.
2. **The sha256 of those ten is the table's.** The table abbreviates nine digests (`ca136f0e…32e797c6`); the registry
   must hold a full 64-character digest that begins and ends as the table says. For ticket the full digest is given.
3. **Entry names** are compared without case. Accepted: `openspec`, `check-jsonschema`, `ticket` / `wedow/ticket` /
   `tk`, `codebase-memory-mcp`, `ollama`, `rulesync`, `copier`, `lefthook`, `uv`, `node` / `nodejs` / `node.js`,
   `ccusage`, `superpowers`, `pyyaml`.
4. **Versions** are compared without a leading `v` (`v0.3.2` = `0.3.2`).
5. **One entry per tool.** A name recorded twice fails: a pin is one version.
6. **"Recorded" means committed.** The registry must be tracked by git and equal to the committed file.
7. **The registry is read with a plain YAML load** (`yaml.safe_load`) and the result is given to the schema. An unquoted
   `date: 2026-10-03` loads as a date, not a string, and the schema refuses it: dates must be quoted.
8. **Every required fact is a non-blank string**; `sha256` is 64 hexadecimal characters for every entry; `date` starts
   with `YYYY-MM-DD`. DEC-195 and DEC-196 keep a digest for every entry, so the sha256 test stands.
9. **"Pinned" for ccusage** means: `version` is one exact version (digits and dots, optional suffix; no range, tag or
   `latest`), and the recorded `install` command names both `ccusage` and that version.
10. **"Installed" for ccusage** means (revised for DEC-192): the package `ccusage` is a global package of
    `~/.nvm/versions/node/v22.23.3` (its `bin/ccusage` and its `lib/node_modules/ccusage/package.json` exist), and
    that package's version is the registry's. It was: found on `PATH`.
11. **An uninstall command that equals the install command is no uninstall command**, and the ccusage one names
    `ccusage`.
12. **A recorded owner approval, as far as tested:** `approved_by` is one `DEC-nnn` id, that id is a
    `### DEC-nnn — …` entry of `docs/DECISION_REGISTER.md`, and its status line starts `ACCEPTED (owner`. `DONE` and
    `PROPOSED` entries do not count. What more the decision must say was DP-4: readings 15 to 21.
13. **ccusage's install date is not before its approval's date** (DEC-083: "installs only after the owner's explicit
    approval"). The approval's date is the first date in the decision's status line, else in its heading. This is
    applied to ccusage only, the one install this ticket makes; the other pins were installed before the registry
    existed.
14. **PyYAML 6.0.1 (DEC-191)** is tested as an entry at that version. Its sha256, install and uninstall commands fall
    under the general tests; its digest is the distribution package's (DEC-196), which is tested by form only.

Readings of the second batch:

15. **"Its own register entry naming the tool and its exact version" (DEC-197)** is tested without naming an id. For
    ccusage and Superpowers, the decision the registry cites must (i) hold the tool's name and the registry's version
    in its own text, (ii) be cited by no other registry entry, (iii) be `ACCEPTED (owner…)` with `DEC-083` in its
    status line ("through a DEC-083 decision package"), and (iv) not be dated after the registry's date for the tool.
    In the register as it stands only DEC-192 fits ccusage 20.0.26 and only DEC-193 fits Superpowers 6.4.2.
16. **A decision's own text** is its heading and its lines up to the next `## ` heading or table row. Without that cut,
    the last entry of a register section (DEC-198 today) would hold the section's change-log row, which names every
    tool, and would pass as anyone's approval.
17. **The approved versions are fixed:** ccusage 20.0.26 (DEC-192) and Superpowers 6.4.2 (DEC-193).
18. **The ccusage commands (DEC-192):** `install` holds `.nvm/versions/node/v22.23.3/bin/npm`, `install`, `-g` or
    `--global`, and `ccusage@20.0.26`; `uninstall` holds the same npm path, an npm uninstall word and `ccusage`. How
    the home directory is written (`~`, `$HOME`, absolute) is free.
19. **The Superpowers install command (DEC-193)** holds `github.com/obra/superpowers` and `v6.4.2`. The clone's target
    folder is not tested.
20. **"Older pins cite the decision that names them" (DEC-197):** the ten stack pins cite exactly `DEC-074`, and PyYAML
    exactly `DEC-191`, as DP-4 option (a) spelled out and the owner accepted. DEC-074's text does not hold the words
    Copier, lefthook, uv or Node; it names them through ADR-0002 §2, whose heading is "Stack (DEC-074, Balanced)". So
    the "decision's text holds the tool's name" test is applied to every entry **but** the ten stack pins.
21. **gitleaks' approving decision is not fixed by id.** DEC-197's list (DEC-074, DEC-191, DEC-141) has none that
    names gitleaks. The tests ask for a decision that names gitleaks and is accepted by the owner: DEC-195 and DEC-055
    fit; DEC-056 (the one ADR-0002 §2 cites) does not, because its status is `DONE`, which the first batch's
    `test_every_approving_decision_is_accepted_by_the_owner` refuses.
22. **Single-file tools (DEC-196)** are those whose binary on this machine has the digest ADR-0002 §2 gives, checked
    by hashing on 2026-10-03, plus gitleaks: `tk` (ticket), `codebase-memory-mcp`, `rulesync`, `lefthook`, `uv` and
    `gitleaks` as found on `PATH`, and Node at `~/.nvm/versions/node/v22.23.3/bin/node`. The test hashes the file the
    command resolves to and requires the registry's digest to equal it. OpenSpec, check-jsonschema, Copier (packages),
    Ollama (not on `PATH`), ccusage, Superpowers and PyYAML keep the form test only: their artefact is not on this
    machine, so recomputing would need a download. (Since then: DEC-199 gives Superpowers a digest the third batch
    recomputes, and DEC-200 lets the three packages carry their entry script's digest.)
23. **The vendor folder's layout is not fixed.** A skill folder may sit directly in
    `template/governance/kernel/vendor/superpowers/` or under `skills/` as upstream has it; each must appear once, with
    a non-empty `SKILL.md` directly in it.
24. **"Unchanged" (DEC-194) cannot be compared with upstream offline.** What is tested: each `SKILL.md` opens with
    frontmatter whose `name` is the folder's name, as an upstream skill does.
25. **"Only" (DEC-194) is read to the letter:** every file under the vendor folder is inside one of the three skill
    folders or is a licence file (`LICENSE`, `LICENCE` or `COPYING`, any extension, outside the skill folders, holding
    the word "copyright"). A README or a provenance note there fails; provenance is the registry entry.
26. **The plugin and the hook** are recognised by: a folder whose name holds `plugin`, a `plugin.json` or
    `marketplace.json`; a folder named `hooks`, a `hooks.json`, or a file whose name starts `session-start`. Repository
    wide, no tracked path may have a `subagent-driven-development` or `.claude-plugin` component.
27. **"Committed"** for the vendor folder: every file on disk there is tracked by git, and `git status` reports nothing
    for the folder.
28. **"The scratch clone is deleted afterwards"** is tested (`local_only`) as: once the vendor folder exists,
    `.gov-runtime/scratch/orchestrator/vendor-src/superpowers/` (DEC-193) does not.

Readings of the third batch (DEC-199: "the sha256 of the sorted lines `<sha256 of the file>  <relative path>` over
every file under `template/governance/kernel/vendor/superpowers/`"). Each keeps to the sentence's letter; together
they are the rule the test computes:

29. **"Every file"** is every file `HEAD` holds under the vendor folder (git blobs at any depth), with its committed
    bytes, unconverted. A file's mode is not part of the digest. A symbolic link would count as a file whose bytes
    are its target path, as git stores it; there is none today. In a clean checkout this is the folder on disk, which
    `test_the_vendor_folder_is_committed` already requires.
30. **"`<sha256 of the file>`"** is the sha256 of those bytes, as 64 lowercase hexadecimal characters.
31. **"`<relative path>`"** is the path relative to the vendor folder, as DP-5 option (a) worded it: components joined
    by `/`, no leading `./` or `/`, the name as git records it, encoded as UTF-8 (`LICENSE`,
    `skills/systematic-debugging/SKILL.md`). No escaping is applied; no name there has a line feed or a backslash.
32. **A line** is the digest, exactly two spaces (as the sentence prints them), the path, and one line feed (`\n`).
    Every line ends with the line feed, the last one too; there is no carriage return and no header or trailer.
33. **"Sorted lines"** means the lines themselves are sorted, as bytes (`LC_ALL=C sort`), not the paths. A line starts
    with the file's digest, so the order is by digest: `LICENSE` is the tenth of the fifteen lines today.
34. **"The sha256 of"** those lines is the sha256 of the sorted lines concatenated, in lowercase hexadecimal; the
    registry's value is compared without case. In a clean checkout it is what this prints:
    `cd template/governance/kernel/vendor/superpowers && git ls-files -z | xargs -0 sha256sum | LC_ALL=C sort | sha256sum`.
    For the folder as committed at `58113a8a` (15 files) it is
    `f2a95244bc977742ee2cf6e5228fd1c24c276d63e7c1e732b3fcf9b2e8c0b90a`. The test recomputes it and holds no fixed
    value, so a later change of the vendor folder (W1-37) needs the registry's digest re-recorded, not the test.

## Decision packages

DP-1 to DP-5 are **answered** (owner, 2026-10-03). They are kept as asked, for the record. None is open.

| Package | Answer | Recorded as | Tested in |
|---|---|---|---|
| DP-1 | Option (a), with an addition: the ten pins, plus gitleaks 8.30.1 with the sha256 of its binary | DEC-195 | `test_w1_06_pins.py`, `test_w1_06_digests.py` |
| DP-2 | Option (a), with a clarification: the one downloaded artefact, or the binary itself for a single-file tool | DEC-196 | `test_w1_06_digests.py` (recomputed where the binary is on this machine; the form elsewhere) |
| DP-3 | Option (a): only the three skill folders and the upstream licence are committed | DEC-194 | `test_w1_06_vendor.py` |
| DP-4 | Option (a): each install has its own register entry, cited by `approved_by`; older pins cite the decision that names them | DEC-197 (with DEC-192, DEC-193) | `test_w1_06_install_approvals.py` |
| DP-5 | Option (a): a digest of the committed vendor folder, which a test and `gov doctor` recompute offline | DEC-199 | `test_w1_06_vendor_digest.py` (readings 29 to 34) |

### DP-5 — What the Superpowers entry's `sha256` covers when the source is fetched by `git clone` (ANSWERED: DEC-199)

- **Question.** DEC-196 says `sha256` covers "the one downloaded artefact (npm tarball, release tarball, distribution
  package)". DEC-193 approves `git clone --depth 1 --branch v6.4.2`, which downloads no single artefact, and DEC-194
  deletes the clone afterwards. What is hashed for the Superpowers entry?
- **Why now.** The schema requires a `sha256` and ADR-0002 §2 says "recorded at vendoring". The tests can assert only
  the form (64 hex) for this entry, so any digest passes, and W1-27's `gov doctor` has no rule to re-check it.
- **Options.** (a) A digest of the committed vendor folder by a rule written down once: the sha256 of the sorted lines
  `<sha256 of the file>  <path relative to the vendor folder>` over every committed file. (b) The sha256 of
  `git archive --format=tar v6.4.2` taken from the clone before it is deleted. (c) The sha256 of GitHub's release
  tarball of the tag, which needs a second approved download. (d) The tag's commit id, padded or re-hashed.
- **Impact.** (a) covers exactly what the repository ships, and a test and `gov doctor` can recompute it offline at
  any time; it is not a "downloaded artefact", so it widens DEC-196 by one case. (b) covers the whole upstream tree
  and matches DEC-196's wording best, but nobody can recompute it once the clone is gone. (c) is DEC-196 to the
  letter, with one more download and a tarball GitHub generates on demand. (d) is not a sha256 of content.
- **Reversibility.** High: one field of one entry.
- **Cost.** (a) a ten-line rule, in the test and later in `gov doctor`. (b) one command before the clone is deleted.
  (c) one more owner approval.
- **Recommendation.** (a). I would then add one case that recomputes the digest from the committed folder (not
  `local_only`).
- **Confidence.** Medium.

### DP-1 — Which rows of the stack table are "DEC-074 pins" when the table gives no sha256 (ANSWERED: DEC-195)

- **Question.** ADR-0002 §2 has rows with a pin but no sha256: SQLite 3.45.1 (`—`), sqlite-vec 0.1.9 (`venv`), gitleaks
  8.30.1 (`—`), the embedding model `qwen3-embedding:0.6b` (Ollama model id `ac6da0dfba84`), the reranker
  `Qwen/Qwen3-Reranker-0.6B@e61197ed…` with sentence-transformers 6.1.0, torch 2.14.1+cu130 and transformers 5.18.0
  ("HF etag"). Must W1-06 record them in the registry, and with what in `sha256`, which the schema requires?
- **Why now.** The KPI says "every DEC-074 pin … with sha256", and the schema refuses an entry without `sha256`. The
  tests need a fixed list.
- **Options.** (a) Only the ten rows with a version and a sha256 are registry entries now; the others enter when the
  ticket that installs them runs (W1-16, W1-18, W1-40 and the retrieval tickets), each through its own DEC-083 package.
  (b) All rows are entries now; W1-06 computes a sha256 for each from what is on the machine or in the S0b2 record, by
  a rule fixed under DP-2. (c) All rows are entries now, and the schema is changed so that `sha256` may be absent or
  carry another identifier (model id, git revision, HF etag).
- **Impact.** (a) the registry is incomplete against the table until later tickets close, and `gov doctor` (W1-27) has
  no pin for those tools yet. (b) complete, but W1-06 must find or compute artefacts it may not have (the S0b2 output
  is outside the repository). (c) complete, but revises W1-04's schema and its tests, and weakens CAP-25.a's "sha256".
- **Reversibility.** High for all three: entries can be added or changed in a later commit.
- **Cost.** (a) none now. (b) about an hour, and possibly owner help to locate artefacts. (c) a W1-04 test rewrite and
  a schema change.
- **Recommendation.** (a), with the owner confirming that "every DEC-074 pin" means the ten rows the tests list.
- **Confidence.** Medium.

### DP-2 — What `sha256` is the digest of for a tool that is not one file (ANSWERED: DEC-196)

- **Question.** For ccusage (an npm package; npm records sha512 integrity), Superpowers (a source tree), PyYAML 6.0.1
  (already on this machine as a system package) and any tool installed as a directory: what is hashed?
- **Why now.** DEC-083's package must state "source and checksum", and CAP-25.a requires a sha256 per entry. The tests
  can check only the form (64 hex) until the rule is fixed, so two different digests for the same install would both
  pass.
- **Options.** (a) The sha256 of the one downloaded artefact, as the source publishes or serves it: the npm tarball
  (`npm pack ccusage@<version>` and hash the `.tgz`), the release tarball of the Superpowers tag, the wheel or sdist of
  PyYAML. (b) The sha256 of the installed entry-point file. (c) A tree hash of the installed or vendored directory by a
  rule written down once (sorted relative paths and file digests).
- **Impact.** (a) is checkable before the install and is what a decision package can show the owner; `gov doctor`
  cannot re-check it from the installed files alone. (b) and (c) are re-checkable on the machine, but are known only
  after the install, and (b) covers one file of many.
- **Reversibility.** High: a digest can be re-recorded. Changing the rule later means re-recording every entry.
- **Cost.** (a) one download per tool by the orchestrator, under the install rule. (c) a small hashing rule that
  W1-27 must then implement.
- **Recommendation.** (a) for ccusage, Superpowers and PyYAML; for PyYAML, when the installed copy came from the
  distribution's package, the digest of that package file, with the owner's command as install and uninstall.
- **Confidence.** Medium. Once answered, tests can recompute the digest wherever the artefact is kept in the
  repository.

### DP-3 — Where the Superpowers v6.4.2 source must be to count as "available for vendoring" (ANSWERED: DEC-194)

- **Question.** Is the source (i) committed under `template/governance/kernel/vendor/superpowers/` (the ticket's second
  allowed path), (ii) kept outside the repository with only its pin and sha256 in the registry, or (iii) something
  else? And is "the source" the whole upstream tree at v6.4.2 or only the three skills of DEC-074 Q5
  (test-driven-development, systematic-debugging, verification-before-completion)?
- **Why now.** W1-37 (three-skill vendoring) depends on W1-06 and copies from this source. Charter v5 and DEC-076
  exclude subagent-driven-development, the plugin and its SessionStart hook; a whole-tree copy inside the kernel
  template would ship those files to every adopting repository unless something filters them.
- **Options.** (a) Commit only the three skill folders and the upstream licence under
  `template/governance/kernel/vendor/superpowers/`, unchanged from v6.4.2; the registry sha256 is the release
  tarball's. (b) Commit the whole upstream tree there. (c) Commit nothing; the registry entry (version, sha256, source
  URL in the install command) is the availability, and W1-37 fetches under its own approval.
- **Impact.** (a) W1-37 works offline and the excluded parts never enter the repository; tests can assert the three
  `SKILL.md` files exist and that no `subagent-driven-development` folder or hook does. (b) offline too, but ships
  excluded content in the template. (c) smallest diff, but W1-37 (an engineer ticket) cannot install or download
  (DEC-083, DEC-157), so the orchestrator would have to fetch again.
- **Reversibility.** High: files under `vendor/` can be removed or replaced.
- **Cost.** (a) and (b) one approved download; (a) a few files, (b) the whole tree in the template.
- **Recommendation.** (a).
- **Confidence.** Medium-high on the location (the allowed path), medium on the three-skills-only scope. Once answered,
  I would add tests for the files' presence and for the absence of the excluded parts.

### DP-4 — How a "recorded owner approval" is identified (ANSWERED: DEC-197)

- **Question.** The tests accept any `approved_by` that is an owner-accepted decision of the register. Must the
  approving decision also name the tool and its exact version? For example, would `approved_by: DEC-083` (the rule) or
  `DEC-086` (ccusage is a prerequisite, no version) count as the approval of ccusage, or must each install approved in
  chat from W1-06 on get its own register entry?
- **Why now.** KPI success 1 says "through a DEC-083 decision package" and failure 1 says "without a recorded owner
  approval". W1-04's schema tests use `DEC-083` as an example value, so the weaker reading is not excluded by any
  source, and with it the failure line can never fire for an entry that cites the rule.
- **Options.** (a) Each install made by the orchestrator has its own register entry, naming tool and exact version,
  and `approved_by` is that entry; pins that predate the registry cite the decision that names them (DEC-074 for the
  stack, DEC-191 for PyYAML, DEC-141 for bubblewrap and socat). (b) Any owner-accepted decision is enough, including
  DEC-083 itself. (c) As (a), and the entry must also name the sha256.
- **Impact.** (a) the register alone shows what the owner approved, and a test can check that the approving decision's
  text contains the tool's name and version. (b) no register growth, but the approval of a particular version is
  recorded nowhere outside the chat. (c) strongest, with a longer entry per install.
- **Reversibility.** High: `approved_by` values and register entries can be corrected later.
- **Cost.** (a) one short register entry per install. (b) none. (c) as (a).
- **Recommendation.** (a). I would then add: the decision cited by the ccusage entry names `ccusage` and the pinned
  version; every other entry's approving decision names the tool.
- **Confidence.** High that (b) is too weak for failure 1; medium between (a) and (c).
