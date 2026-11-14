{
  "ticket": "DAEO-03ub",
  "ticket_text": "---\nid: DAEO-03ub\nstatus: in_progress\ndeps: []\nlinks: [DAEO-fau3]\ncreated: 2026-11-02T10:58:34Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-42a\ntags: [wave-2, implementation, guard, full]\nwbs_id: W2-42a\ntitle: 'The product''s guard reads what a Bash command writes: ACT-GUARD-FIX-3''s eight parser lines in src/gov/guard, before EXAMIN''s copy (DEC-1028 item 4)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- docs/probes/DAEO-03ub/**  # the probe record (the resume after the emergency, DEC-1158; CTO)\n- src/gov/guard/decide.py\n- src/gov/guard/reads.py\n- src/gov/guard/bash_writes.py\n- tests/unit/guard/test_w2_42a*\n- docs/changes/W2-42a-evidence.md\n- tests/unit/guard/test_decide.py\nkpis:\n  success:\n  - 'A heredoc''s body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body''s `$(\u2026)` is text, an unquoted body''s `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body''s `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body''s `$(\u2026)`, fails them'\n  - 'A variable the command sets once at its top level, before any use, is expanded; a literal `for` loop''s words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them'\n  - '`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command''s name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command''s name gives no write and fails them'\n  - 'An unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both'\n  - '`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them'\n  - 'The read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc''s body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body''s `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them'\n  - 'A backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them'\n  - 'A data heredoc''s body written to a file that a later word of the command may run is judged as that file''s code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them'\n  - 'Measured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product''s parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer''s record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it'\n  - 'The read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them'\n  - 'Replayed against every refusal in the CTO''s `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it'\n  - 'R4 (D1, 2026-11-14): `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a blob that exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a revision word that names no commit, tree or blob is refused as today, not passed [DND row 122, W2-141''s review, DEC-1157 (12), DEC-1180 (4)] Verify: the `test_r4_*` cases in tests/acceptance/W2-42a/ pass on planted repositories (both sides blobs: judged as reads; a path the role may not read: still refused; a revision that does not resolve: refused, rule not `error`)'\n  - 'R5 (the error path, 2026-11-14): no Bash or tool input makes the guard''s judge raise inside itself: the `list index out of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule), never rule `error`; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second deadline) [DND row 123, DEC-1128 (3), DEC-1133 (2), DEC-1157 (12)] Verify: the `test_r5_*` cases in tests/acceptance/W2-42a/ pass: the crashing forms the engineer finds in the code (empty words, a lone operator, a trailing pipe, `&&` or `;`, an option with no value, an unterminated `$(`), each ruled; a property case over generated token sequences that never sees rule `error` from an exception; a planted genuine fault still gives `error` and refuses'\n  failure:\n  - 'Any write the parser misses that today''s parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write'\n  - 'An unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them'\n  - 'R4/R5: a call refused today that the fix lets through although it writes into a walled path or reads a refused one (a fail-open). Verify: the `test_r45_failure_*` cases in tests/acceptance/W2-42a/ pass (a blob read of a held-out or secrets path, a `git diff` whose output is redirected into tests/acceptance/, each still refused)'\nprofile: FULL\nsources:\n- DEC-1040\n- DEC-1028\n- DEC-1027\n- DEC-958\n- DEC-953\n- DEC-1044\n- DEC-1128\n- DEC-1133\n- DEC-1157\n- DEC-1180\nest_loc: 600\nacceptance_tests:\n  path: tests/acceptance/W2-42a/\n  author: independent-test-designer (MR-3)\ntrack: A\nlist_rows: []\n---\n# W2-42a The product's guard reads what a Bash command writes\n\nThe owner's DEC-1028 item 4 (P1-GUARD-PARSER-W2 (a)): ACT-GUARD-FIX-3 fixed this repository's five-rule hook\n(`.claude/hooks/bash_writes.py`, `e662684a`), but the product's guard, which every adopted repository runs, keeps the\nold parser (`_extract_bash_write_targets` in `src/gov/guard/decide.py`; `_set_aside` and `_Judge.tool`/`command` in\n`src/gov/guard/reads.py`) and refuses the writes of 22 of the 61 logged commands it cannot resolve. EXAMIN's agents\nwould meet those refusals. This ticket brings the eight parser lines (ACT-GUARD-FIX-3 \u00a77) into the product, before\nEXAMIN's copy. The engineer may port the reviewed `bash_writes.py` as its basis (a new `src/gov/guard/bash_writes.py`\nmodule); the test designer works from the KPIs and may take the package's planted cases and the logged corpus as\nfixtures (no secrets in them). W2-42 (`DAEO-fau3`) keeps its other rows in Wave 3. W2-09 and W2-10 hold\n`src/gov/guard/**`: start beside W2-09 only with the files split, or after it. Once it lands, the five-rule hook can\ncall the product's parser and `bash_writes.py` slims away (a later ACT).\n\n**Reopened 2026-11-13 by the CTO under DEC-1164 (18) (DEC-1174 (1), a P2 listed for the owner's reading).** A defect\ninside this ticket's scope: a Bash call whose heredoc body (to a shell) holds a comment with an apostrophe\n(`bash <<'EOF'` / `# it's fine` / `ls` / `EOF`) is refused whole, \"the command cannot be read\", although it writes\nnothing; the same body without the comment is allowed. It fails closed (the four F1 reversal calls of ACT-GUARD-FIX-5's\nround-2 review stay refused), but it refuses ordinary work, and the live hook is to copy this parser (DEC-1174 (1)).\nThe fix: comment text in a shell body is dropped before the body is tokenised (a `#` that starts a word, outside\nquotes, to the end of its line), so an apostrophe there is no unclosed quote; a body still unreadable after that stays\nrefused. A test designer adds the cases (the harmless forms allowed; the F1 reversal calls and a body that writes into\n`tests/acceptance/` after such a comment still refused), the engineer fixes `bash_writes.py`, then a narrow independent\ncheck of that change only.\n\n**Reopened 2026-11-14 by the CTO under DEC-1164 (18) (a P2 listed for the owner's reading): R3 and the fallback's here-string forms.** A defect inside this ticket's scope, found by its own apos-2 check: the line parser splits a command at `<<`/`<<<` (`decide.py` `_line_write_targets`), so a write argument after a here-string is missed (`tee <<< \"x\" T`, `tee -a <<< \"x\" T`): ordinary work yes, fails open. The same check named three older fail-opens in the unreadable fallback: `bash <<< 'touch T'`, `xargs touch <<< T`, and a body-less heredoc after a `python3 -c` write. The live hook is to copy this parser (DEC-1174 (1)), so they are fixed before that ACT. The fix: the word after `<<<` is the here-string's text (judged, as a `bash <<<`/`sh <<<` body is a command), never the command's end; the words after it stay the command's arguments; anything still unreadable fails closed. A test designer adds the cases, the engineer fixes `src/gov/guard/` within these paths, then a narrow independent check of that change only (DEC-1154).\n\n**Reopened 2026-11-14 by the CTO within the ticket's purpose (DEC-1157 (12), DEC-1180 (4); listed for the owner's reading): R4 (D1) and R5 (the error path).** The DND sweep of 11-14 found both still in the code (rows 122 and 123, triggers met: the lift DEC-1158; DEC-1128 (3) \"the guard's own error-path faults are fixed first after the lift\"): `reads.py:1721-1725` resolves every revision word as a commit, so a blob ref is refused; and nothing guards the judge against the three `list index out of range` crashes logged on 11-10. Both sit in `reads.py`/`decide.py`, already in this ticket's paths. Order: a fresh test designer writes R4, R5 and the failure line as described behaviour (DEC-136), from the code and planted repositories only (never the guard's call log `~/.gov-os/guard-calls`, the bar's held-out source, SETUP-A-BAR S2, DEC-1108 (4)); a fresh engineer fixes; gov accept; a narrow independent check (DEC-1156 (7)). The live hook takes the fix by ACT (DEC-1133 (2): \"each by ACT\"), with the parser copy already planned (DEC-1174 (1)). The CTO's own Bash line naming a revision-colon-path in text was refused on 11-14 by this very fault.\n",
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
      "sha256": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "reason": "declared in sources",
      "tokens": 708
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
    },
    {
      "id": "DEC-1128",
      "sha256": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "reason": "declared in sources",
      "tokens": 978
    },
    {
      "id": "DEC-1133",
      "sha256": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "reason": "declared in sources",
      "tokens": 557
    },
    {
      "id": "DEC-1157",
      "sha256": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "reason": "declared in sources",
      "tokens": 1274
    },
    {
      "id": "DEC-1180",
      "sha256": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "reason": "declared in sources",
      "tokens": 6270
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
      "sha256": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "31443f85e7cddccb6ca68f2b3a9ee91d6be5d02d45e46ed1c653948e7cae97d0",
      "reason": "declared in sources",
      "tokens": 708
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
    },
    {
      "id": "DEC-1128",
      "sha256": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0dc46f4ec1abccd5241cf0b259885339afd8d632167fbd3fe13504b975d5c0fd",
      "reason": "declared in sources",
      "tokens": 978
    },
    {
      "id": "DEC-1133",
      "sha256": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "7a2dc3aa02e7584ac4d11f5245b8e8f989bd9049f88d3ef1c4551796402faff9",
      "reason": "declared in sources",
      "tokens": 557
    },
    {
      "id": "DEC-1157",
      "sha256": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "92e80a8f4cd0a118de5041d7c6dbaa28b270d2629dc4c4d86b028c801100afd3",
      "reason": "declared in sources",
      "tokens": 1274
    },
    {
      "id": "DEC-1180",
      "sha256": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4e202adab37b976d22d8fe225dd0ba2123445d09aaca4cbeb4141b8d3a74d620",
      "reason": "declared in sources",
      "tokens": 6270
    }
  ],
  "supplementary": [
    {
      "id": "cfe76d6913b9cbde21f9b215",
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "text": "| 121 | DEC-1103 (3): `~/gov-os-writer` and `~/gov-os-checker` left as they are until the launch script is the default, then retired; the budgets and timeouts decided with the fixed briefs | (added audit a, 11-11) WAITS: the launch script as the default (rows 43-45, 117). Home: DAEO-sdxk (an ACT for the operator at that point); the budgets and timeouts go with row 44's briefs |\n| 122 | D1: the guard refuses a git diff of two blob refs (revision-colon-path on both sides; `src/gov/guard/reads.py:1638`, W2-141's review) | NOT STARTED, trigger met (the lift: DEC-1158; the re-pin 8f00bb90810b): an engineer round, a reopening of W2-42a (reads.py is in its allowed_paths) or a ticket from the owner; W2-42a's closes 77220f814 did not touch reads.py (sweep 11-14 notes, DEC-1180 (4); evidence: reads.py:1721-1725 still resolves each revision word with ^{commit}; W2-42a's commits 9196ce961, df7468015, 885b0d0f6, 07fb14799, 1388fcec6, fa77bb331, 669d87c91, f16075e43 change bash_writes.py and decide.py only) \u00b7 was: NOT STARTED: after the lift |\n",
      "tokens": 262
    },
    {
      "id": "391b113a14504cd32f31009a",
      "path": "docs/changes/W2-42a-evidence.md",
      "text": "## Tests\n- `tests/unit/guard/test_w2_42a_parser.py` and `tests/unit/guard/test_w2_42a_reads.py`: 105 passed.\n- The scoped set, the history differential and the acceptance tests: below, when run.\n\n",
      "tokens": 49
    },
    {
      "id": "3c22e4a63faf47a7a3910efc",
      "path": "docs/changes/W2-42a-evidence.md",
      "text": "## No fail-open (the failure lines)\n- Every planted write of ACT-GUARD-FIX-3 is still refused through the hook (167 of 167).\n- Unit file `tests/unit/guard/test_w2_42a_parser.py`:\n  - Each write the line parser catches is still caught: `before \u2212 {sentinel} \u2286 after`. An unresolvable write\n    stays unresolvable, unless it is now resolved to its place in the tests.\n  - This covers the plain writers, redirects, `cd`, globs, variables, substitutions and backticks.\n  - Unparseable forms (an unbalanced quote, an unclosed substitution) still refuse. So does `decide()`.\n  - A heredoc the scan cannot read is read by the line parser, as before.\n- Unit file `tests/unit/guard/test_w2_42a_reads.py`. These reads of a protected file stay refused:\n  - a listing loop whose variable is used, after the loop too;\n  - `eval`, `${!\u2026}` and an assignment inside such a loop;\n  - `seq -f`;\n  - `$(( $(cat hidden) ))`;\n  - a Python or shell heredoc that reads the hidden part or `.env`;\n  - a heredoc-written script run by `bash`;\n  - an unquoted body's `$(\u2026)`;\n  - `cat <<EOF | bash`;\n  - an unknown reader's text naming the hidden file;\n  - a numbered name in a folder with a numbered protected file.\n\n",
      "tokens": 298
    },
    {
      "id": "b26fd71c8bddbabe03cce2e5",
      "path": "docs/changes/W2-42a-evidence.md",
      "text": "  - W2-50 secrets-scan scale: a gitleaks suite (DEC-1045);\n  - W2-54 `green_here`: no store in this worktree;\n  - containment `test_committed_rename_names_old_path`.\n\n**Review round 1, F1 (the fix round).** Before the fix, a shell given an option with a value took that value for a\nscript's name. Spellings: `bash -euo pipefail <<'EOF'`, `-eu -o pipefail`, `sh -o errexit`, `-O extglob`,\n`+o posix`, `--rcfile f`, and the same through `cat <<EOF | bash -o pipefail`. So the parser read the heredoc body as\ndata, and the read judge dropped it.\n- **The fix:** `_kind` (`src/gov/guard/bash_writes.py`) now finds the script word with `_shell_script`. `-o`, `+o`,\n  `-O` and `+O` take a value, once for each such letter in a cluster. `--rcfile` and `--init-file` take one too. A `-s`\n  in a cluster, or an option it does not know, means the shell reads standard input. As F4's ride-along,\n  `/dev/stdin`, `/dev/fd/0` and `/proc/self/fd/0` count as standard input.\n- **Fail closed:** the reading before the fix is kept as a floor. `_script_words` counts option values the same way.\n- **Unit cases:** `test_f1_*` in `test_w2_42a_parser.py` and `test_w2_42a_reads.py`. The base code fails 32 of them.\n",
      "tokens": 299
    },
    {
      "id": "5b582a9ab9b7a8ab644b42e1",
      "path": ".claude/hooks/bash_writes.py",
      "text": "  a ``for`` loop over literal words is judged once per word; a variable bound any other way is unresolvable;\n- each command substitution, process substitution, ``sh -c`` string and ``eval`` is judged as a command of its own;\n- inline Python (``python3 -c``) is read for its own writes: ``open`` in a write mode, the path methods and the\n  ``os`` and ``shutil`` calls that write, and the commands it runs. A write whose target cannot be worked out, code\n  that runs code (exec, eval, getattr, ...), and code the shell rewrites (``$VAR``) are \"unresolvable\".\n\nRound 2 (the independent review's F1-F4): variables are expanded in source order; backslash-newline is removed before\nthe text is read; a data heredoc's body written to a file is judged as code whenever a later word may run that file\n(bash name after a cd, ./name, chmod +x and the path, a loop variable, xargs, runpy, ...), and refused under rule 1\nwhen the run cannot be read and the body names the tests; code that names the tests in any spelling and writes\nthrough a path the guard cannot work out (a glob, listdir, walk, chdir or computed path) is refused.\n\n",
      "tokens": 281
    },
    {
      "id": "9e8be39daa38c677b0db3ab0",
      "path": ".claude/hooks/bash_writes.py",
      "text": "def heredocs(command):\n    \"\"\"``command`` without its heredoc bodies, and the bodies. Each heredoc operator and its delimiter become\n    ``< __gov_hdl_<k>__`` (an input redirect the parser skips), so the reader is known by position. Raises\n    Unreadable for anything the scan cannot read for certain.\"\"\"\n    out, bodies, pending = [], [], []\n    # The shell's contexts: \"top\"; '\"' (double quotes); \"$(\" (a command substitution, whose quoting starts\n    # afresh, with the depth of its own parentheses); \"`\" (a backtick substitution); \"((\" (arithmetic).\n    stack = [[\"top\", 0]]\n    i, n = 0, len(command)\n    while i < n:\n        c = command[i]\n        ctx = stack[-1]\n        if command.startswith(\"\\\\\\n\", i):\n            # A line continuation (ACT-GUARD-FIX-3 round 2, F3): the shell removes backslash-newline outside single\n            # quotes, so \"cp /tmp/x \\<newline> tests/...\" is one command with both words.\n            i += 2\n            continue\n        if c == \"\\\\\" and i + 1 < n:\n            out.append(command[i:i + 2])\n            i += 2\n            continue\n        if ctx[0] == '\"':\n            if c == '\"':\n                stack.pop()\n",
      "tokens": 289
    },
    {
      "id": "f3bce9a576f72a5913998ad4",
      "path": ".claude/hooks/bash_writes.py",
      "text": "def joined(command):\n    \"\"\"``command`` with each backslash-newline removed (round 2, F3), for the checks that read its text whole. Inside\n    single quotes the shell keeps them; removing them there too only makes the text name more, never less.\"\"\"\n    return command.replace(\"\\\\\\n\", \"\")\n",
      "tokens": 72
    },
    {
      "id": "4cf8f5264edcfaabed2bbc0d",
      "path": ".claude/hooks/pretooluse.py",
      "text": "def parse_both(parse, command, cwd):\n    \"\"\"The product's parser on a command it is to read as before this fix, and, when the command continues a line\n    with a backslash-newline, on the text with each one removed too (ACT-GUARD-FIX-3 round 2): the targets of both,\n    so a write split over lines is not missed.\"\"\"\n    found = parse(command, cwd)\n    if \"\\\\\\n\" not in command:\n        return found\n    more = parse(command.replace(\"\\\\\\n\", \"\"), cwd)\n    if found is None and more is None:\n        return None\n    return list(found or []) + list(more or [])\n",
      "tokens": 140
    }
  ],
  "supplementary_query": "The product's guard reads what a Bash command writes: ACT-GUARD-FIX-3's eight parser lines in src/gov/guard, before EXAMIN's copy (DEC-1028 item 4)\nA heredoc's body is not read as shell: a body that cat, tee or grep takes as data is no write; its unquoted `$(\u2026)` is judged; a `bash`/`sh` body is judged as commands [DEC-1028 item 4, ACT-GUARD-FIX-3 \u00a77 line 1] Verify: the `test_kpi1_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass on the tree under test (a data body for cat, tee and grep gives no write, a quoted body's `$(\u2026)` is text, an unquoted body's `$(\u2026)` and a `bash`/`sh` body are judged as commands); a planted parser that reads a cat body's `touch` line or `>` as a write, or that skips the `touch` inside an unquoted body's `$(\u2026)`, fails them\nA variable the command sets once at its top level, before any use, is expanded; a literal `for` loop's words are judged one by one; any other binding is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 2] Verify: the `test_kpi2_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a variable set once before its use, and one built from an earlier one, give the real path; each word of a literal `for` loop is judged; a use before the set, a set inside an `if`, by `read` or in a pipeline, and a loop over a substitution give the unresolvable target); a planted parser that expands a variable set inside an `if` or reads `do touch` as the command `do` fails them\n`$(\u2026)` and backticks inside double quotes, `sh -c` strings and `eval` words are judged as commands; shell keywords and the prefixes `timeout`, `env`, `nohup`, `nice` and `command` are not taken for the command's name [ACT-GUARD-FIX-3 \u00a77 line 3] Verify: the `test_kpi3_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (`echo \"$(touch b)\"`, `sh -c` and `eval` give the write of the command inside; `then rm` and each of the five prefixes before `touch` give the write, not the command name `then` or `timeout`); a planted parser that takes `echo`, `sh`, `then` or `timeout` for the command's name gives no write and fails them\nAn unmatched glob is the literal path bash passes (no `nullglob`), not unresolvable [ACT-GUARD-FIX-3 \u00a77 line 4] Verify: the `test_kpi4_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (an unmatched glob, also after a `cd`, is its literal path; a matched glob is still its matches), and line 40 of the replay (`rm -f chain-*.json`) in tests/acceptance/W2-42a/test_w2_42a_replay.py is allowed by the hook; a planted parser that returns the unresolvable target for an unmatched glob fails both\n`git checkout`/`restore`/`rm`/`mv` on paths, `dd of=`, `truncate`, `sort -o` and `rsync` are read as writes; `git apply`, `git am` and `patch` are writes to unresolvable targets [ACT-GUARD-FIX-3 \u00a77 line 5] Verify: the `test_kpi5_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (each named writer gives its path, `git mv` both paths, `rsync` its destination; `git apply`, `git am` and `patch` give the unresolvable target); a planted parser that gives no write for `dd of=` or `git checkout` on a path, or a real path for `git apply`, fails them\nThe read judge does not take `$((\u2026))` for a command substitution, nor a data heredoc's body for commands [ACT-GUARD-FIX-3 \u00a77 line 6] Verify: the `test_kpi6_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (arithmetic is no substitution; a data body naming `.env` or a key path is no read; a data body holding a listing loop is no listing), and the kept refusals in the same cases still refuse (a `bash` body, an unquoted body's `$(cat .env)`, a `$(\u2026)` inside `$((\u2026))`, a plain `cat .env`); a planted judge that reads a data body as commands, or that stops reading the substitution inside `$((\u2026))`, fails them\nA backslash-newline outside single quotes is removed before the command is read [ACT-GUARD-FIX-3 \u00a77 line 7] Verify: the `test_kpi7_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a continued word is one word, a continued command writes its target, a continued `cp` writes its destination with no newline in it, a backslash-newline inside single quotes is kept) and in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a secret or a hidden file named across a continued line is refused); a planted reader that leaves the newline in the word, or that removes it inside single quotes, fails them\nA data heredoc's body written to a file that a later word of the command may run is judged as that file's code; a run the parser cannot read is unresolvable [ACT-GUARD-FIX-3 \u00a77 line 8] Verify: the `test_kpi8_*` cases in tests/acceptance/W2-42a/test_w2_42a_parser.py pass (a script written then run by `bash` or by its path is judged as its code, also after a `cd`; a Python file written then run is its code or unresolvable; a run by a word that does not expand, or one the parser cannot read, is unresolvable; a written file that is only read is data); a planted parser that treats a run Python body as no write and no sentinel, or a read-only body as a write, fails them\nMeasured in docs/changes/W2-42a-evidence.md: on the 61 logged commands the product's parser resolves the writes of all but at most 2 (today 22 unresolvable); no planted write into the acceptance folder or outside a reviewer's record is missed; every unknown form still fails closed [DEC-1028 item 4, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_measured.py passes on the tree under test (`test_kpi9_the_parser_resolves_the_writes_of_all_but_at_most_2_of_the_61_logged_commands`: at most 2 of the 61 unresolvable, 22 on the base; `test_kpi9_no_planted_shell_write_is_missed_by_the_parser`: each of the 81 planted shell writes and unknown forms gives a target or the unresolvable target; `test_kpi9_the_measures_are_stated_in_the_evidence_file`: docs/changes/W2-42a-evidence.md exists and names the 61 commands and the planted cases), and the planted cases that hold Python code are refused through the hook in test_w2_42a_replay.py; a planted parser change that leaves 3 of the 61 unresolvable, or that returns no target and no sentinel for one planted write, or a missing evidence file, fails it\nThe read judge does not misread a literal path as a run-time listing: a command that names its files literally (in a heredoc, a `for` loop over `$(seq \u2026)`, a `$(\u2026)` that yields no file name) is judged by those files [DEC-1040 item 2] Verify: the `test_kpi10_*` cases in tests/acceptance/W2-42a/test_w2_42a_read_judge.py pass (a `for` over `$(seq \u2026)` reading a literal file, a `$(\u2026)` that yields no file name, a Python heredoc and a data heredoc appended to a record are judged by their literal files and not refused as a listing; names given at run time are still refused as a listing, and a literal hidden file is still refused); a planted judge that refuses the `seq` loop as a listing, or that passes a run-time listing or a literal hidden file, fails them\nReplayed against every refusal in the CTO's `log/guard-refusals.jsonl` (the full command from its transcript): each one judged false now passes and each one judged true is still refused, through the five-rule hook as it runs after re-pin window 2; and every planted case of ACT-GUARD-FIX-3 still refused [DEC-1040 item 2, DEC-958] Verify: tests/acceptance/W2-42a/test_w2_42a_replay.py passes on the tree under test with `PYTHONPATH` at its `src` (`test_kpi11_each_logged_refusal_replayed`: each of the 76 recovered lines judged false is allowed by the hook, and lines 74 and 77, judged true, are refused by their logged rule; `test_kpi11_each_planted_case_still_refused`: each of the 155 planted cases is refused by its write rule with exit 0); the five lines the case holds (47, 65, 72, 73 and 76, in `HELD`) are expected still refused by their logged rule until the CTO decides them, and a line taken out of `HELD` becomes a must-pass case; a planted parser that lets line 75, 78, 79 or 80 stay refused as a listing, or lets one planted write through, fails it\nR4 (D1, 2026-11-14): `git diff REV:PATH REV:PATH` (a revision-colon-path on one or both sides, each naming a blob that exists) and `git show REV:PATH` are judged as reads of those paths, under the read rules the path names; a revision word that names no commit, tree or blob is refused as today, not passed [DND row 122, W2-141's review, DEC-1157 (12), DEC-1180 (4)] Verify: the `test_r4_*` cases in tests/acceptance/W2-42a/ pass on planted repositories (both sides blobs: judged as reads; a path the role may not read: still refused; a revision that does not resolve: refused, rule not `error`)\nR5 (the error path, 2026-11-14): no Bash or tool input makes the guard's judge raise inside itself: the `list index out of range` crash and the revision it cannot classify each get a ruled decision (allow, or a refusal naming its rule), never rule `error`; the error path stays and still fails closed for a genuine fault (a missing file, the 20-second deadline) [DND row 123, DEC-1128 (3), DEC-1133 (2), DEC-1157 (12)] Verify: the `test_r5_*` cases in tests/acceptance/W2-42a/ pass: the crashing forms the engineer finds in the code (empty words, a lone operator, a trailing pipe, `&&` or `;`, an option with no value, an unterminated `$(`), each ruled; a property case over generated token sequences that never sees rule `error` from an exception; a planted genuine fault still gives `error` and refuses\nAny write the parser misses that today's parser catches (a fail-open). Verify: `test_failure1_no_write_the_base_parser_catches_is_missed` in tests/acceptance/W2-42a/test_w2_42a_measured.py passes for each of the 53 planted writes the base parser catches (marked `base_caught` in fixtures/planted.json), and `test_kpi11_each_planted_case_still_refused` in test_w2_42a_replay.py passes; a planted parser change that drops one catch the base has (for example the target of a `git rm` or a redirect) fails the case for that write\nAn unknown or unparseable form that passes instead of refusing. Verify: the `test_failure2_*` cases pass in tests/acceptance/W2-42a/test_w2_42a_parser.py (unbalanced quotes, `eval \"$X\"`, `sh -c \"$X\"` and unbalanced quotes inside `bash -c` give the unresolvable target; an unterminated heredoc and a shift in arithmetic keep their write or give the unresolvable target) and in test_w2_42a_read_judge.py (an unparseable command naming a secret is refused), and the planted unknown forms in `test_kpi9_no_planted_shell_write_is_missed_by_the_parser` and `test_kpi11_each_planted_case_still_refused` pass; a planted parser that returns no write for `eval \"$X\"` or for unbalanced quotes fails them\nR4/R5: a call refused today that the fix lets through although it writes into a walled path or reads a refused one (a fail-open). Verify: the `test_r45_failure_*` cases in tests/acceptance/W2-42a/ pass (a blob read of a held-out or secrets path, a `git diff` whose output is redirected into tests/acceptance/, each still refused)",
  "further_batch": [
    {
      "id": "3b997f43e53edd0c9e8b7fab",
      "path": "docs/changes/W2-141-hook/pretooluse.py"
    },
    {
      "id": "37882aa93530423574099a16",
      "path": "docs/changes/W2-42a-evidence.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "cfe76d6913b9cbde21f9b215",
          "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md"
        },
        {
          "id": "391b113a14504cd32f31009a",
          "path": "docs/changes/W2-42a-evidence.md"
        },
        {
          "id": "3c22e4a63faf47a7a3910efc",
          "path": "docs/changes/W2-42a-evidence.md"
        },
        {
          "id": "b26fd71c8bddbabe03cce2e5",
          "path": "docs/changes/W2-42a-evidence.md"
        },
        {
          "id": "5b582a9ab9b7a8ab644b42e1",
          "path": ".claude/hooks/bash_writes.py"
        },
        {
          "id": "9e8be39daa38c677b0db3ab0",
          "path": ".claude/hooks/bash_writes.py"
        },
        {
          "id": "f3bce9a576f72a5913998ad4",
          "path": ".claude/hooks/bash_writes.py"
        },
        {
          "id": "4cf8f5264edcfaabed2bbc0d",
          "path": ".claude/hooks/pretooluse.py"
        },
        {
          "id": "3b997f43e53edd0c9e8b7fab",
          "path": "docs/changes/W2-141-hook/pretooluse.py"
        },
        {
          "id": "37882aa93530423574099a16",
          "path": "docs/changes/W2-42a-evidence.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "37882aa93530423574099a16",
      "reason": "budget exceeded"
    },
    {
      "id": "3b997f43e53edd0c9e8b7fab",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-03ub): 8 paths, 25 chunks; 8 by role_paths.engineer.reads_denied {ticket_tests} (tests/acceptance/W2-42a/**) (DEC-1065 (2))"
    }
  ],
  "tokens": 19893,
  "budget": {
    "limit": 20000,
    "used": 19893
  },
  "hash": "75dfa88f59b1faf844f876f8257864c5bd03f22272542921e9f10cb99340ccb8"
}
