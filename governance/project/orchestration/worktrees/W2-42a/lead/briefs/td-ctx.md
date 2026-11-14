{
  "ticket": "DAEO-03ub",
  "ticket_text": "---\nid: DAEO-03ub\nstatus: in_progress\ndeps: []\nlinks: [DAEO-fau3]\ncreated: 2026-11-02T10:58:34Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-42a\ntags: [wave-2, implementation, guard, full]\nwbs_id: W2-42a\ntitle: 'The product''s guard reads what a Bash command writes: ACT-GUARD-FIX-3''s eight parser lines in src/gov/guard, before EXAMIN''s copy (DEC-1028 item 4)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- docs/probes/DAEO-03ub/**  # the probe record (the resume after the emergency, DEC-1158; CTO)\n- src/gov/guard/decide.py\n- src/gov/guard/reads.py\n- src/gov/guard/bash_writes.py\n- tests/unit/guard/test_w2_42a*\n- docs/changes/W2-42a-evidence.md\n- tests/unit/guard/test_decide.py\nkpis:\n  success:\n  - 'A heredoc''s body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body''s `$(\u2026)` is text, an unquoted body''s `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body''s `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body''s `$(\u2026)`, fails them'\n  - 'A variable the command sets once at its top level, before any use, is expanded; a literal `for` loop''s words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them'\n  - '`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command''s name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command''s name gives no write and fails them'\n  - 'An unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both'\n  - '`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them'\n  - 'The read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc''s body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body''s `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them'\n  - 'A backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them'\n  - 'A data heredoc''s body written to a file that a later word of the command may run is judged as that file''s code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them'\n  - 'Measured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product''s parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer''s record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it'\n  - 'The read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them'\n  - 'Replayed against every refusal in the CTO''s `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it'\n  failure:\n  - 'Any write the parser misses that today''s parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write'\n  - 'An unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them'\nprofile: FULL\nsources:\n- DEC-1040\n- DEC-1028\n- DEC-1027\n- DEC-958\n- DEC-953\n- DEC-1044\nest_loc: 600\nacceptance_tests:\n  path: tests/acceptance/W2-42a/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows: []\n---\n# W2-42a The product's guard reads what a Bash command writes\n\nThe owner's DEC-1028 item 4 (P1-GUARD-PARSER-W2 (a)): ACT-GUARD-FIX-3 fixed this repository's five-rule hook\n(`.claude/hooks/bash_writes.py`, `e662684a`), but the product's guard, which every adopted repository runs, keeps the\nold parser (`_extract_bash_write_targets` in `src/gov/guard/decide.py`; `_set_aside` and `_Judge.tool`/`command` in\n`src/gov/guard/reads.py`) and refuses the writes of 22 of the 61 logged commands it cannot resolve. EXAMIN's agents\nwould meet those refusals. This ticket brings the eight parser lines (ACT-GUARD-FIX-3 \u00a77) into the product, before\nEXAMIN's copy. The engineer may port the reviewed `bash_writes.py` as its basis (a new `src/gov/guard/bash_writes.py`\nmodule); the test designer works from the KPIs and may take the package's planted cases and the logged corpus as\nfixtures (no secrets in them). W2-42 (`DAEO-fau3`) keeps its other rows in Wave 3. W2-09 and W2-10 hold\n`src/gov/guard/**`: start beside W2-09 only with the files split, or after it. Once it lands, the five-rule hook can\ncall the product's parser and `bash_writes.py` slims away (a later ACT).\n",
  "authority": [
    {
      "id": "DEC-1040",
      "sha256": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "reason": "declared in sources",
      "tokens": 551
    },
    {
      "id": "DEC-1028",
      "sha256": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "reason": "declared in sources",
      "tokens": 692
    },
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1044",
      "sha256": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "reason": "declared in sources",
      "tokens": 328
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1040",
      "sha256": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "62de178737a139c71447d3bd11fad5091b96f2e52eda2cdbd3991ddc953799f6",
      "reason": "declared in sources",
      "tokens": 551
    },
    {
      "id": "DEC-1028",
      "sha256": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "43219ac6796f5321294873fe6512f1cbcae7e46a713c5d717ac6c8f0ecd7095f",
      "reason": "declared in sources",
      "tokens": 692
    },
    {
      "id": "DEC-1027",
      "sha256": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7f49abe4345bd3ac9327bb90eb36295879e0e7e9432f8bab7f54e2b5ef5d2d48",
      "reason": "declared in sources",
      "tokens": 560
    },
    {
      "id": "DEC-958",
      "sha256": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "bfeae64480680a3bc8e73620d3658a65ed655259791ffbf7810bcb93f2aec1b4",
      "reason": "declared in sources",
      "tokens": 697
    },
    {
      "id": "DEC-953",
      "sha256": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a7df2a6b83c7c1617d11a0a04c2da7299a6169022e19c60da82db8280a5246b4",
      "reason": "declared in sources",
      "tokens": 2188
    },
    {
      "id": "DEC-1044",
      "sha256": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b56ea84b346ec47dab43aa0182e7553eda0f1c1713135d3ce443f481155106c9",
      "reason": "declared in sources",
      "tokens": 328
    }
  ],
  "supplementary": [
    {
      "id": "ccaa5952016b0c6ad0702c60",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| S11 | `test_w2_42a_replay.py::test_kpi11_each_logged_refusal_replayed`, `test_w2_42a_replay.py::test_kpi11_the_replay_holds_every_recoverable_line`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |\n| F1 | `test_w2_42a_measured.py::test_failure1_no_write_the_base_parser_catches_is_missed`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |\n| F2 | `test_w2_42a_parser.py::test_failure2_an_unparseable_or_unknown_form_is_unresolvable`, `test_w2_42a_parser.py::test_failure2_a_form_read_uncertainly_keeps_its_write`, `test_w2_42a_read_judge.py::test_failure2_an_unparseable_command_naming_a_secret_is_refused`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |\n\n",
      "tokens": 202
    },
    {
      "id": "2ecc1a80964c3c71c99072d7",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| S8 | `test_w2_42a_parser.py::test_kpi8_a_script_written_then_run_by_bash_is_judged_as_its_code`, `test_w2_42a_parser.py::test_kpi8_a_script_written_after_a_cd_then_run_by_its_path_is_judged`, `test_w2_42a_parser.py::test_kpi8_a_python_file_written_then_run_is_its_code_or_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_the_parser_cannot_read_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_run_by_a_word_that_does_not_expand_is_unresolvable`, `test_w2_42a_parser.py::test_kpi8_a_written_file_that_is_only_read_is_judged_as_data` |\n| S9 | `test_w2_42a_measured.py::test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_measured.py::test_kpi9_the_measures_are_stated_in_the_evidence_file` |\n",
      "tokens": 210
    },
    {
      "id": "e725537be45b0a2633996378",
      "path": "tests/acceptance/W2-42a/README.md",
      "text": "| S9 | `test_w2_42a_measured.py::test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`, `test_w2_42a_measured.py::test_kpi9_no_planted_shell_write_is_missed_by_the_parser`, `test_w2_42a_measured.py::test_kpi9_the_measures_are_stated_in_the_evidence_file` |\n| S10 | `test_w2_42a_read_judge.py::test_kpi10_a_loop_over_seq_reading_a_literal_file_is_judged_by_that_file`, `test_w2_42a_read_judge.py::test_kpi10_a_substitution_that_yields_no_file_name_leaves_the_literal_files`, `test_w2_42a_read_judge.py::test_kpi10_a_python_heredoc_naming_its_files_literally_is_judged_by_them`, `test_w2_42a_read_judge.py::test_kpi10_a_data_heredoc_appended_to_a_record_is_judged_by_its_file`, `test_w2_42a_read_judge.py::test_kpi10_names_given_at_run_time_are_still_judged_as_a_listing`, `test_w2_42a_read_judge.py::test_kpi10_a_literal_hidden_file_is_still_refused` |\n| S11 | `test_w2_42a_replay.py::test_kpi11_each_logged_refusal_replayed`, `test_w2_42a_replay.py::test_kpi11_the_replay_holds_every_recoverable_line`, `test_w2_42a_replay.py::test_kpi11_each_planted_case_still_refused` |\n",
      "tokens": 277
    },
    {
      "id": "095f578c7b0b5f81621f236c",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py",
      "text": "def test_failure1_no_write_the_base_parser_catches_is_missed(row):\n    assert s.parser_caught(row, s.REPO), \"the base's parser catches this planted write and this one misses it\"\n",
      "tokens": 45
    },
    {
      "id": "a67dded8c554b7c80a31f241",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py",
      "text": "def test_kpi9_the_measures_are_stated_in_the_evidence_file():\n    assert os.path.isfile(s.EVIDENCE), \"docs/changes/W2-42a-evidence.md is not in the tree\"\n    text = open(s.EVIDENCE, encoding=\"utf-8\").read()\n    assert \"61\" in text and \"planted\" in text.lower(), \"the evidence names neither the 61 commands nor the planted cases\"\n",
      "tokens": 83
    },
    {
      "id": "a93879dc54f9351547516c3e",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py",
      "text": "def test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands():\n    rows = {r[\"line\"]: r for r in s.refusals() if r[\"line\"] <= 61}\n    assert len(rows) == 57 and all(rows[t][\"tool\"] == \"Bash\" for t in TWINS.values())\n    lines = [TWINS.get(n, n) for n in range(1, 62)]\n    unresolved = [n for n, src in zip(range(1, 62), lines) if _unresolved(rows[src])]\n    assert len(unresolved) <= MOST_UNRESOLVED, f\"{len(unresolved)} of 61 unresolvable: lines {unresolved}\"\n",
      "tokens": 124
    },
    {
      "id": "624e4e4005107ba3d1f2a918",
      "path": "tests/acceptance/W2-42a/test_w2_42a_replay.py",
      "text": "def test_kpi11_each_logged_refusal_replayed(row):\n    got, why, code = s.run_hook(row[\"tool\"], row[\"input\"], row[\"cwd\"], row[\"root\"], row[\"role\"],\n                                agent_type=row[\"agent_type\"], tmpdir=row[\"tmpdir\"])\n    if row[\"verdict\"] == \"true\" or row[\"line\"] in HELD:\n        assert (got, code) == (\"deny\", 0), f\"line {row['line']}: want refused, got {got} ({why[:400]})\"\n        assert why == row[\"rule\"], f\"line {row['line']}: refused by another rule: {why[:400]}\"\n    else:\n        assert got == \"allow\", f\"line {row['line']} (judged false): still refused: {why[:400]}\"\n",
      "tokens": 148
    },
    {
      "id": "91dd68a10ac78f279d046799",
      "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py",
      "text": "def test_kpi9_no_planted_shell_write_is_missed_by_the_parser(row):\n    assert s.parser_caught(row, s.REPO), \"the parser misses this planted write (no target there, no sentinel)\"\n",
      "tokens": 45
    }
  ],
  "supplementary_query": "The product's guard reads what a Bash command writes: ACT-GUARD-FIX-3's eight parser lines in src/gov/guard, before EXAMIN's copy (DEC-1028 item 4)\nA heredoc's body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body's `$(\u2026)` is text, an unquoted body's `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body's `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body's `$(\u2026)`, fails them\nA variable the command sets once at its top level, before any use, is expanded; a literal `for` loop's words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them\n`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command's name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command's name gives no write and fails them\nAn unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both\n`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them\nThe read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc's body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body's `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them\nA backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them\nA data heredoc's body written to a file that a later word of the command may run is judged as that file's code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them\nMeasured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product's parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer's record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it\nThe read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them\nReplayed against every refusal in the CTO's `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it\nAny write the parser misses that today's parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write\nAn unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them",
  "further_batch": [
    {
      "id": "6b1d070912f456816aeb182f",
      "path": "tests/acceptance/W2-42a/README.md"
    },
    {
      "id": "1345bab8a4b250286b55e142",
      "path": "tests/acceptance/W2-42a/test_w2_42a_replay.py"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "ccaa5952016b0c6ad0702c60",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "2ecc1a80964c3c71c99072d7",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "e725537be45b0a2633996378",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "095f578c7b0b5f81621f236c",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "a67dded8c554b7c80a31f241",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "a93879dc54f9351547516c3e",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "624e4e4005107ba3d1f2a918",
          "path": "tests/acceptance/W2-42a/test_w2_42a_replay.py"
        },
        {
          "id": "91dd68a10ac78f279d046799",
          "path": "tests/acceptance/W2-42a/test_w2_42a_measured.py"
        },
        {
          "id": "6b1d070912f456816aeb182f",
          "path": "tests/acceptance/W2-42a/README.md"
        },
        {
          "id": "1345bab8a4b250286b55e142",
          "path": "tests/acceptance/W2-42a/test_w2_42a_replay.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "1345bab8a4b250286b55e142",
      "reason": "budget exceeded"
    },
    {
      "id": "6b1d070912f456816aeb182f",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-03ub): 5 paths, 18 chunks; 1 by role_paths.independent-test-designer.reads_denied {ticket_impl} (docs/changes/W2-42a-evidence.md); 1 by role_paths.independent-test-designer.reads_denied {ticket_impl} (src/gov/guard/bash_writes.py); 1 by role_paths.independent-test-designer.reads_denied {ticket_impl} (src/gov/guard/decide.py); 2 by role_paths.independent-test-designer.reads_denied {ticket_impl} (tests/unit/guard/test_w2_42a*) (DEC-1065 (2))"
    }
  ],
  "tokens": 8976,
  "budget": {
    "limit": 9000,
    "used": 8976
  },
  "hash": "f59e892ebb68079f3ff3c78bed60fde20cf486dc222b46a43bc240977edea9a9"
}
