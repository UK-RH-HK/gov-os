# W1-06 — Wave 1 tool prerequisites: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-ipqy` (W1-06), CAP-25 / CAP-25.a
and CAP-40 of Contract v4, DEC-074, DEC-083, DEC-086, DEC-121, DEC-127, DEC-141, DEC-191, ADR-0002 §2 and the "Interim
install rule" of `governance/project/bootstrap.md`. Written before implementation. No earlier ticket's test was
rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-06 -q -p no:cacheprovider
```

`pytest`, the standard library and PyYAML (the project's declared dependency, used only to parse the registry). No
network. **No test installs, downloads, uninstalls or runs an install command.** The tests read three committed files
(the registry, its schema, the decision register) and ask git whether the registry is committed.

Two cases are marked `local_only`: they look for `ccusage` on `PATH` and read the version from the installed package's
own `package.json` (only when no such file is found is `ccusage --version` run). They fail, not skip, when ccusage is
absent: on this machine it must be installed. Deselect them elsewhere with `-m "not local_only"`.

## KPI → tests → red reason today

Red run on `w1/integrate` at `175c5ef3`: **45 errors, 0 passed, 0 failed** (45 cases, 27 test functions). Every case
errors in the `registry` fixture with the same reason: **`governance/project/tool-registry.yaml does not exist: W1-06
has not created the tool registry`**. The last column gives what each group fails on first once the file exists.

| KPI line | Test file | Test functions | Red reason after the file exists |
|---|---|---|---|
| **Success 1.** ccusage installed and pinned through a DEC-083 decision package and recorded in the registry | `test_w1_06_ccusage.py` | `test_ccusage_is_recorded_in_the_registry` · `test_ccusage_is_pinned_to_one_exact_version` · `test_the_recorded_install_command_installs_the_pinned_version` · `test_the_recorded_uninstall_command_removes_ccusage` · `test_ccusage_carries_a_sha256_digest` · `test_ccusage_was_approved_by_an_owner_decision_of_the_register` · `test_ccusage_was_not_installed_before_its_approval` · `test_ccusage_is_installed_on_this_machine` (`local_only`) · `test_the_installed_ccusage_is_the_pinned_version` (`local_only`) | No ccusage entry; there is no `ccusage` on `PATH` today |
| **Success 2, second half.** Every DEC-074 pin is recorded in the registry with sha256 **[CAP-25.a]** | `test_w1_06_pins.py` | `test_a_dec_074_pin_is_recorded_at_its_pinned_version[10]` · `test_a_dec_074_pin_is_recorded_with_the_sha256_of_the_stack_table[10]` · `test_pyyaml_is_recorded_at_6_0_1` (DEC-191) | No entry for the pin |
| **Success 2, first half.** The Superpowers v6.4.2 source is available for vendoring | `test_w1_06_pins.py` | `test_superpowers_is_recorded_at_v6_4_2` · `test_superpowers_is_recorded_with_a_sha256_digest`. Where the source must be is **not tested: DP-3** | No Superpowers entry |
| **CAP-25.a.** Tool registry with pins, sha256, install/uninstall commands, date, approving decision | `test_w1_06_registry.py` (and the pins file above) | `test_the_registry_is_committed` · `test_the_registry_is_valid_against_the_committed_schema` · `test_the_registry_records_at_least_one_tool` · `test_every_entry_states_all_seven_facts` · `test_each_tool_is_recorded_once` · `test_every_sha256_is_a_sha256_digest` · `test_every_date_is_a_calendar_date` | The file is not committed, or an entry breaks the schema |
| **Failure 1.** Any tool installed without a recorded owner approval | `test_w1_06_approvals.py` | `test_every_entry_names_one_decision_as_its_approval` · `test_every_approving_decision_is_in_the_register` · `test_every_approving_decision_is_accepted_by_the_owner` · and the two ccusage approval tests above | An `approved_by` that is not an owner-accepted decision of the register |
| **Failure 2.** A registry entry lacks an uninstall command | `test_w1_06_registry.py` | `test_every_entry_has_an_uninstall_command` · `test_no_uninstall_command_is_the_install_command` · `test_the_schema_refuses_this_registry_once_an_entry_loses_its_uninstall_command` · `test_the_recorded_uninstall_command_removes_ccusage` | An entry with no, an empty or a copied uninstall command |

**Count.** KPI lines with tests: 4 of 4 (2 success, 2 failure); success 2's first half is tested only through the
registry entry (DP-3). Covers ids with tests: 1 of 1 (CAP-25.a).

Not tested here, by the brief: Claude Code, bubblewrap and socat (W1-48 records them). Comparing pins with what is found
on the machine is `gov doctor` (W1-27); the only such comparison here is ccusage, because its KPI says "installed".

## Readings the sources do not spell out

1. **"Every DEC-074 pin" is read from ADR-0002 §2**, whose heading is "Stack (DEC-074, Balanced) — exact pins". DEC-074
   itself states only two versions (codebase-memory-mcp 0.11.0, ticket v0.3.2). The tests require the ten rows of that
   table that state both one exact version and a sha256: OpenSpec 1.13.2, check-jsonschema 0.38.2, ticket v0.3.2,
   codebase-memory-mcp 0.11.0, Ollama 0.35.0, rulesync 24.0.0, Copier 9.18.2, lefthook 2.1.15, uv 0.12.21, Node
   v22.23.3. The rows with no sha256 are DP-1.
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
   with `YYYY-MM-DD`. If DP-1 or DP-2 is answered with "no digest for some tools", the sha256 test changes with it.
9. **"Pinned" for ccusage** means: `version` is one exact version (digits and dots, optional suffix; no range, tag or
   `latest`), and the recorded `install` command names both `ccusage` and that version.
10. **"Installed" for ccusage** means: `ccusage` is found on the `PATH` of the session that runs the tests, and that
    installation's version is the registry's.
11. **An uninstall command that equals the install command is no uninstall command**, and the ccusage one names
    `ccusage`.
12. **A recorded owner approval, as far as tested:** `approved_by` is one `DEC-nnn` id, that id is a
    `### DEC-nnn — …` entry of `docs/DECISION_REGISTER.md`, and its status line starts `ACCEPTED (owner`. `DONE` and
    `PROPOSED` entries do not count. What more the decision must say is DP-4.
13. **ccusage's install date is not before its approval's date** (DEC-083: "installs only after the owner's explicit
    approval"). The approval's date is the first date in the decision's status line, else in its heading. This is
    applied to ccusage only, the one install this ticket makes; the other pins were installed before the registry
    existed.
14. **PyYAML 6.0.1 (DEC-191)** is tested as an entry at that version. Its sha256, install and uninstall commands fall
    under the general tests and DP-2.

## Decision packages

### DP-1 — Which rows of the stack table are "DEC-074 pins" when the table gives no sha256

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

### DP-2 — What `sha256` is the digest of for a tool that is not one file

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

### DP-3 — Where the Superpowers v6.4.2 source must be to count as "available for vendoring"

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

### DP-4 — How a "recorded owner approval" is identified

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
