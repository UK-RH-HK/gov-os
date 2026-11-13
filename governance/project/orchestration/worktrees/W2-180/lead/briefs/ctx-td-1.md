{
  "ticket": "DAEO-weh2",
  "ticket_text": "---\nid: DAEO-weh2\nstatus: in_progress\ndeps: []\nlinks: [DAEO-61vm, DAEO-k1e2, DAEO-c9n8]\ncreated: 2026-11-12T07:10:00Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W2-180\ntags: [wave-2, test-revision, memory, audit, lite]\nwbs_id: W2-180\ntitle: 'W2-170''s F5 path case judges any branch against W2-170''s own paths, so every later memaudit ticket (W2-171 first) is red on it and the queue would refuse its land'\nclass: test-revision\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\nprofile: LITE\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- tests/acceptance/W2-170/test_w2_170_f5_paths.py\n- tests/acceptance/W2-170/README.md\nest_loc: 15\nreads:\n- tests/acceptance/W2-170/conftest.py\n- src/gov/close/select.py\nneeds:\n- tests/acceptance/W2-170/test_w2_170_f5_paths.py\nkpis:\n  success:\n  - 'S1 `test_f5_the_branch_changes_only_paths_the_ticket_allows` judges only W2-170''s own branch: on any other branch (another ticket''s worktree, the merge queue''s candidate merge, w2/integrate, the nightly''s clone) it is skipped with its reason, never red; on W2-170''s own branch (`w2/W2-170`) it judges as today. Verify: planted repositories: a branch named w2/W2-170 with a change outside W2-170''s paths fails it; the same change on a branch named w2/W2-171, and on a detached candidate merge of w2/W2-171 into w2/integrate, skips it with the reason; on w2/integrate it skips [DEC-866, DEC-253]'\n  failure:\n  - 'A change outside W2-170''s paths on W2-170''s own branch let through. Verify: S1''s planted w2/W2-170 branch fails the revised case'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths'\nnon_goals:\n- the other tickets'' F5 cases (each judged on its own merit when found)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-866, DEC-253, DEC-966, DEC-989]\nacceptance_tests:\n  path: tests/acceptance/W2-170/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'\ntrack: B\n---\n# W2-180 W2-170's F5 case on other branches\n\nW2-171 run 2 (PKG-W2-171-F5-1, 2026-11-12 07:06): its verify is red on W2-170's F5 case, which diffs any branch against its\nmerge-base with w2/integrate and checks the result against W2-170's allowed_paths. W2-171 rightly changes `src/gov/memaudit/`\nfiles W2-170's paths do not list, so the case is red on W2-171's branch, and the merge queue's candidate merge of W2-171 would\nbe red too, attributed to W2-171's batch: the land refused. The CTO's ruling: (a) a branch-scoped red for W2-171's review now,\nand this ticket (b), which must land before W2-171's land. Class C1. A test revision with a Rewrite-Reason (DEC-866).\n",
  "authority": [
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-253",
      "sha256": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "reason": "declared in sources",
      "tokens": 202
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-989",
      "sha256": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "reason": "declared in sources",
      "tokens": 399
    }
  ],
  "mandatory": [
    {
      "id": "DEC-866",
      "sha256": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3fd0a96f9624051bf1c77dd154fff18e9c8c62e324c4ad73c0b25f8043e279a1",
      "reason": "declared in sources",
      "tokens": 566
    },
    {
      "id": "DEC-253",
      "sha256": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "69d019082dbd12572ddb5fcd1488b3decd2917df176250198a1999434ef8738a",
      "reason": "declared in sources",
      "tokens": 202
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-989",
      "sha256": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a984478df29597e3fb80b4bace0caa24e65194c920da2d9351faab2eee5d9e6d",
      "reason": "declared in sources",
      "tokens": 399
    }
  ],
  "supplementary": [
    {
      "id": "1dbf392fb200e1fc25b797a4",
      "path": "tests/acceptance/W2-170/README.md",
      "text": "| F3 | `test_w2_170_s4_map.py::test_f3_the_planted_repository_is_unwritten_after_every_subcommand`, `test_w2_170_s4_map.py::test_f3_a_refused_declaration_leaves_the_repository_unwritten`, `test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders` | `gov.memaudit` absent: the subcommands exit 1 and the open-log runner's `runpy` raises `ImportError` (its exit 99) |\n| F4 | `test_w2_170_s2_void.py::test_f4_five_drops_void_the_audit_with_no_used_and_no_declaration`, `test_w2_170_s2_void.py::test_f4_no_dropped_question_is_deleted` | `gov.memaudit` absent: `void` exits 1, not 0 or 2, and nothing is moved to `hidden/dropped/` |\n| F5 | `test_w2_170_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows` | passes on the tests' branch (it changes only this folder); judges the ticket's branch after the merge; skipped, with the reason, without `w2/integrate` |\n\n",
      "tokens": 232
    },
    {
      "id": "5ab0fdea757b9967a9500cdb",
      "path": "tests/acceptance/W2-170/test_w2_170_f5_paths.py",
      "text": "def test_f5_the_branch_changes_only_paths_the_ticket_allows():\n    if _git(\"rev-parse\", \"--verify\", \"--quiet\", \"w2/integrate^{commit}\").returncode != 0:\n        pytest.skip(\"F5 needs the w2/integrate reference, absent in this repository: not judged here\")\n    if not TICKET.is_file():\n        pytest.skip(\"F5 needs the ticket file .tickets/DAEO-61vm.md, absent here: not judged here\")\n    front = yaml.safe_load(TICKET.read_text(encoding=\"utf-8\").split(\"\\n---\", 1)[0].removeprefix(\"---\\n\"))\n    allowed = list(front[\"allowed_paths\"])\n    folder = str(front[\"acceptance_tests\"][\"path\"]).rstrip(\"/\")\n    allowed.append(folder + \"/**\")\n    base = _git(\"merge-base\", \"HEAD\", \"w2/integrate\")\n    assert base.returncode == 0, base.stderr\n    diff = _git(\"-c\", \"core.quotePath=false\", \"diff\", \"--name-only\", \"--no-renames\", f\"{base.stdout.strip()}...HEAD\")\n    assert diff.returncode == 0, diff.stderr\n    from gov.close.select import match\n    outside = [p for p in diff.stdout.splitlines() if p and not any(match(p, a) for a in allowed)]\n    assert outside == [], outside\n",
      "tokens": 267
    },
    {
      "id": "ebfda29d9f080e3456ea9e94",
      "path": "tests/acceptance/W1-01/README.md",
      "text": "    what one of its other parents holds (the same content, or absent in both);\n  - every non-merge commit on the merged side (reachable from another parent and not from the first) that touches\n    `tests/acceptance/**` carries `Role: independent-test-designer`.\n- A merge commit on the merged side is judged by the same rule when the history walk reaches it.\n\nA merge commit that holds content under `tests/acceptance/` that none of its parents holds fails. This includes a\nconflict in an acceptance test resolved by hand in the merge commit, and a file that git merged from changes on both\nsides. The second case is stricter than DEC-253 requires. It needs no write to the repository to check, and it fails\nclosed: such a merge is made by a test designer, or the owner decides.\n\n`test_w1_01_integration_merges.py` shows both directions in small temporary repositories, and the real history:\n\n| Case | Test | Result |\n|---|---|---|\n| A merge of a ticket branch with a test-designer commit and an engineer commit | `test_a_merge_of_test_designer_commits_passes` | passes |\n",
      "tokens": 268
    },
    {
      "id": "08bfa689eed2e6c2081da02f",
      "path": "docs/changes/W2-116-evidence.md",
      "text": "## Tests\n\n- Unit (stand-in embedder and code-graph tool, planted git repositories, no model):\n  - `tests/unit/rebuild/test_w2_116_integration.py`: 25 passed (19 + 6 for the review's F1, F6, F8);\n  - `tests/unit/launch/test_w2_116_store.py`: 15 passed (13 + 2 for F2, F4).\n  - The 8 new tests were run against the code before the fix (a detached worktree at `e6724c208`): 8 failed.\n- `gov accept W2-116` (`HOME=/home/usain`, after the ride-along): **pass**, 20 passed, 0 failed, 0 skipped. Lines\n  success-1/3/4/5 and failure-1/2/3; S2 is not mapped in this pass.\n- Regression, `tests/unit/rebuild`, `tests/unit/launch`, `tests/unit/retrieve` with `GOV_TESTS_OPTIN=lifted,breadth`\n  and `-m \"not local_only\" -k \"not real and not green_here and not time_limit\"`, `HOME` an empty folder: **257\n  passed** (249 + the 8 new), none deselected: the real-model exclusion removes no case in these folders.\n- Every run went through `heavy_slot.sh`. No real embedder, reranker or model was started.\n",
      "tokens": 247
    },
    {
      "id": "bff8a936fd2861d9168b2e93",
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "text": "## 6. The rest of the list: traced, fixed, or placed (2026-11-09 23:10 to 2026-11-10 UTC; FORECAST-W2-2 \u00a73 row 11 and the CTO's additions)\n\nBy the CTO's helper, for orchestrator DAEO-sdxk. Method:\n- each red reproduced by running only that case or file at integrate (a detached worktree);\n- the root cause found and measured;\n- the fix made by the right role (a test designer with `Rewrite-Reason:` under DEC-866, a product-spec worker for the\n  plan tool);\n- one independent review, READY by `verdict.py` (records in `reviews/D10-*.md`);\n- the affected cases re-run on the merge result in a scratch worktree, then a one-command `--no-ff` merge.\n\nFORECAST's two \"merged\" branches are merged: W1-06 in `dddf54782`, test_fusion in `56a1a554c`.\n\n",
      "tokens": 186
    },
    {
      "id": "01a6e52198d360065f62e9e8",
      "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md",
      "text": "## The one decision: W1-01's merge rule and `0568d91baf56`\n1. **Context:** DEC-253 (only the test designer commits acceptance tests) is judged on merges by W1-01's\n   `merge_offences`. A merge whose own tree changes an acceptance file beyond what git's own merge would hold is an\n   offence, unless the merge carries the test designer's role. `acceptance_exemptions` (DEC-906) exempts only the\n   commits a merge brings.\n2. **What happened:** `0568d91baf56` resolved one conflict in W1-30's acceptance file; the resolution was a test\n   designer's (td-9, sandboxed), committed by its lead with `Role: orchestrator`. It entered `w2/integrate` with W2-67's\n   merge, after the 10-31 baseline, so the red is new to the nightly. History is never rewritten (DEC-412).\n3. **Why it matters:** a permanent red that no ticket fixes is a standing accepted red, which DEC-968 forbids.\n4. **Options:**\n   - (a) W1-01's test designer extends `merge_offences` so a merge listed in `acceptance_exemptions` is exempt for its\n     own changes too (a test revision you name under DEC-906), and you commit one exemption entry for\n",
      "tokens": 278
    },
    {
      "id": "9f492f14ffcf6f47d7538df7",
      "path": "docs/research/W2-68-batched-close.md",
      "text": "## 0. What exists (W2-66, as it stands on w2/integrate)\n\n- **The base.** `gov.close.select.plan` picks a close's regression run against a base: the newest commit that a green record names and that is HEAD or an ancestor of it. `select._green_heads` reads two kinds of green record from the working tree, which the close has already checked is HEAD:\n  - (a) close records `docs/close/*/CL-*.md` whose `evidence.scope` is `full`;\n  - (b) `docs/close/nightly/*.json` records whose `verdict` is `green`.\n- **The evidence block.** `gov.close.evidence.block` states the scope, base, head, tree, changed paths, targets, left-out suites, skips (`skips`, `skip_count`) and failures. It also names each run's JUnit XML file, under `.gov-runtime/close/<ticket>/<stamp>/`. That folder is untracked, so the files exist only on the machine that ran the close.\n- **The nightly.** `gov.close.nightly.night` runs the full regression on a commit in the close's form, in a detached worktree, with JUnit XML under `.gov-runtime/nightly/<stamp>-<head12>/`. It re-runs each failing test alone:\n  - a red that passes alone is a flaky candidate and is not bisected;\n",
      "tokens": 286
    },
    {
      "id": "d15afbab32352372085625f9",
      "path": "docs/probes/DAEO-61vm/PR-DAEO-61vm.md",
      "text": "   - **S5/F1:** the record's keys are the 40 `q<nn>` ids and its values are 64-hex digests equal to the files' sha256. S5's unique words appear in no run-folder file and in no stdout or stderr of the three subcommands. No folder word is printed.\n3. **False refusals the fix adds:** none in the honest single-pass flow (C3), nor when the pre-flight runs again before void (C2). The one case found is RV6, after void.\n4. **F5:** `git diff --name-only w2/integrate...6ba5a6edab5b` lists only `src/gov/memaudit/**`, `tests/unit/memaudit/**`, `governance/project/test-map.yaml`, `docs/changes/W2-170-evidence.md` and the designer's `tests/acceptance/W2-170/**`.\n5. **Other:** round 1's rows RV2-RV5 rest on code the fix did not touch and stand unchanged as rows. The engineer's readings P1-P5 stand.\n\n",
      "tokens": 199
    },
    {
      "id": "9393ebf7aeddcc9d45ceaa31",
      "path": "governance/project/bootstrap.md",
      "text": "- **A worker's commit attributed to its lead.** In a ticket's worktree the lead (role orchestrator) waits for its\n  worker with its own Bash calls. When the test designer commits under `tests/acceptance/<W1-id>/` during such a\n  call, the check attributes the commit to the lead's call and flags \"committed path(s) outside allowed paths\" in\n  that worktree's `.gov-runtime/findings.jsonl`. The commit is the designer's, in the designer's scope. Seen in the\n  worktrees of W1-37, W1-18 and W1-08. A worktree's findings file is copied to\n  `.gov-runtime/scratch/orchestrator/log/<W1-id>-findings.jsonl` in the main tree before the worktree is removed.\n- **The W1-01 history test** failed on the first integration merge for the same reason, and is revised under\n  DEC-253 in W1-50's test design batch.\n\n",
      "tokens": 200
    },
    {
      "id": "DEC-256",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-256 \u2014 Order of work around W1-50\n- **Status:** ACCEPTED (owner, 2026-10-04) \u00b7 **Basis:** OWNER \u00b7 **Under:** DEC-235\n- **Decision:**\n  - W1-50 is claimed now, and only its test design batch runs, in its own worktree.\n  - That batch is merged, with the revised W1-01 test included.\n  - The orchestrator confirms W1-01 is green on `w1/integrate` (the W1-37 merge then passes).\n  - Merges and closes resume, W1-37 included.\n  - W1-50's implementation starts after W1-46 is merged, because both touch `src/gov/guard/**`.\n\n| Version | Date | Change |\n|---|---|---|\n| 0.50 | 2026-10-04 | Owner decisions: DEC-253 (the W1-01 history test accepts an integration merge whose acceptance-test changes all come from test-designer commits; a rewrite after implementation, \"owner decision: integration merges\"), DEC-254 (merge findings and worker-commit misattributions are records for now), DEC-255 (new ticket W1-50, containment attribution by commit trailers; engineer, FULL, priority high, depends on W1-03), DEC-256 (W1-50's test batch first and merged; then merges and closes resume; its implementation after W1-46). |\n\n",
      "tokens": 280
    },
    {
      "id": "DAEO-xnbx",
      "path": ".tickets/DAEO-xnbx.md",
      "text": "  - Every test fixture that copies the whole tree strips the held-out deny line from the copied settings file (DEC-399)\n  - 'A forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit: each commit''s paths against the allowed paths of its own Role and Task trailers, not against the caller (DEC-255) [CAP-58.h]'\n  - A merge commit itself is not a finding when every commit it brings passes that check (DEC-255) [CAP-58.h]\n  - A worker's commit made during another actor's call is judged by its own trailers (DEC-255) [CAP-58.h]\n  - A commit with no Role or Task trailer is judged against the caller, as today (DEC-255) [CAP-58.h]\n  - 'A commit carrying a Role: owner trailer that is made during any agent session''s call is a finding (DEC-360) [CAP-58.h]'\n  failure:\n  - An integration merge whose commits each stay inside the allowed paths of their own Role and Task trailers raises a finding\n  - A commit that changes a path outside the allowed paths of its own Role and Task trailers raises no finding, whoever the caller is\n  - A commit with no Role or Task trailer is judged by anything other than the caller\nprofile: FULL\nsources:\n- DEC-255\n- DEC-253\n",
      "tokens": 300
    },
    {
      "id": "DEC-255",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-255 \u2014 New ticket W1-50: containment attribution by commit trailers\n- **Status:** ACCEPTED (owner, 2026-10-04) \u00b7 **Basis:** OWNER \u00b7 **Under:** CAP-58, DEC-076, DEC-182, DEC-235 \u00b7 **Amends:** the Wave 1 ticket set (49 \u2192 50 tickets)\n- **Decision:**\n  - A new ticket, W1-50: role engineer, profile FULL, priority high, depends on W1-03.\n  - KPIs:\n    - a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit: each\n      commit's paths against the allowed paths of its own `Role` and `Task` trailers, not against the caller;\n    - a merge commit itself is not a finding when every commit it brings passes that check;\n    - a worker's commit made during another actor's call is judged by its own trailers;\n    - a commit with no `Role` or `Task` trailer is judged against the caller, as today.\n  - Allowed paths: `src/gov/guard/containment*`, `template/governance/kernel/hooks/posttooluse*`,\n    `template/governance/kernel/hooks/pretooluse*`, `tests/unit/containment/**`.\n  - Its test design batch also carries the W1-01 revision of DEC-253.\n  - The Contract gets a covers item under CAP-58, in its own commit.\n",
      "tokens": 290
    },
    {
      "id": "e8b78cb534e1e7cfb84eb1cc",
      "path": "docs/research/W2-68-batched-close.md",
      "text": "3. **One `gov check`** at H (`gov.check.runner.run_checks`). Its result is written to `.gov-runtime/close/batch/<stamp>/check.json`. A blocking result ends the batch red (exit 3): no regression runs and nothing closes.\n4. **One full regression** at H in the close's form. This is `nightly.night` on H: a detached worktree, one parallel run, then the serial-only cases, the per-test limit, retention `failed` and JUnit XML.\n5. **A red run** (DEC-883 item 2, DEC-889 item 2 b). Every failing test is first run again alone, which is the nightly's own step.\n   - A red that passes alone is a flaky candidate: it is named and never bisected.\n   - A red that fails alone is attributed in this order:\n     - by `git bisect run` over the batch's range (from the last green run to H) to its first bad commit, and then to the ticket that commit's `Task:` trailer names;\n     - else to the failing test's own ticket, the ticket whose acceptance folder holds the test;\n     - else `outside`, which is the orchestrator's to fix and record.\n   - Each attribution keeps its evidence: the test, its failure text, its run alone, and either the bisect range and first bad commit or the folder.\n",
      "tokens": 294
    }
  ],
  "supplementary_query": "W2-170's F5 path case judges any branch against W2-170's own paths, so every later memaudit ticket (W2-171 first) is red on it and the queue would refuse its land\nS1 `test_f5_the_branch_changes_only_paths_the_ticket_allows` judges only W2-170's own branch: on any other branch (another ticket's worktree, the merge queue's candidate merge, w2/integrate, the nightly's clone) it is skipped with its reason, never red; on W2-170's own branch (`w2/W2-170`) it judges as today. Verify: planted repositories: a branch named w2/W2-170 with a change outside W2-170's paths fails it; the same change on a branch named w2/W2-171, and on a detached candidate merge of w2/W2-171 into w2/integrate, skips it with the reason; on w2/integrate it skips [DEC-866, DEC-253]\nA change outside W2-170's paths on W2-170's own branch let through. Verify: S1's planted w2/W2-170 branch fails the revised case\nAny change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths",
  "further_batch": [
    {
      "id": "13944cfae3befb593b1fe589",
      "path": "src/gov/close/nightly.py"
    },
    {
      "id": "c07fce4656ccf06e27e96d0d",
      "path": "docs/changes/W2-170-evidence.md"
    },
    {
      "id": "c1f7d54eb7fe0171197e033b",
      "path": "docs/research/AR-2-git-sweep.md"
    },
    {
      "id": "DAEO-vhad",
      "path": ".tickets/DAEO-vhad.md"
    },
    {
      "id": "DEC-906",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "54bb0ff22c6acec4e8ec98ca",
      "path": "governance/project/briefs/LEAD-w2-common.md"
    },
    {
      "id": "6d31a2919d921cbca9b0fec5",
      "path": "governance/project/orchestration/packages/ACT-W1-01-EXEMPT-2.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "1dbf392fb200e1fc25b797a4",
          "path": "tests/acceptance/W2-170/README.md"
        },
        {
          "id": "5ab0fdea757b9967a9500cdb",
          "path": "tests/acceptance/W2-170/test_w2_170_f5_paths.py"
        },
        {
          "id": "ebfda29d9f080e3456ea9e94",
          "path": "tests/acceptance/W1-01/README.md"
        },
        {
          "id": "08bfa689eed2e6c2081da02f",
          "path": "docs/changes/W2-116-evidence.md"
        },
        {
          "id": "bff8a936fd2861d9168b2e93",
          "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md"
        },
        {
          "id": "01a6e52198d360065f62e9e8",
          "path": "governance/project/orchestration/packages/P1-NIGHTLY-2026-11-02.md"
        },
        {
          "id": "9f492f14ffcf6f47d7538df7",
          "path": "docs/research/W2-68-batched-close.md"
        },
        {
          "id": "d15afbab32352372085625f9",
          "path": "docs/probes/DAEO-61vm/PR-DAEO-61vm.md"
        },
        {
          "id": "9393ebf7aeddcc9d45ceaa31",
          "path": "governance/project/bootstrap.md"
        },
        {
          "id": "DEC-256",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DAEO-xnbx",
          "path": ".tickets/DAEO-xnbx.md"
        },
        {
          "id": "DEC-255",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "e8b78cb534e1e7cfb84eb1cc",
          "path": "docs/research/W2-68-batched-close.md"
        },
        {
          "id": "13944cfae3befb593b1fe589",
          "path": "src/gov/close/nightly.py"
        },
        {
          "id": "c07fce4656ccf06e27e96d0d",
          "path": "docs/changes/W2-170-evidence.md"
        },
        {
          "id": "c1f7d54eb7fe0171197e033b",
          "path": "docs/research/AR-2-git-sweep.md"
        },
        {
          "id": "DAEO-vhad",
          "path": ".tickets/DAEO-vhad.md"
        },
        {
          "id": "DEC-906",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "54bb0ff22c6acec4e8ec98ca",
          "path": "governance/project/briefs/LEAD-w2-common.md"
        },
        {
          "id": "6d31a2919d921cbca9b0fec5",
          "path": "governance/project/orchestration/packages/ACT-W1-01-EXEMPT-2.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "13944cfae3befb593b1fe589",
      "reason": "budget exceeded"
    },
    {
      "id": "54bb0ff22c6acec4e8ec98ca",
      "reason": "budget exceeded"
    },
    {
      "id": "6d31a2919d921cbca9b0fec5",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-vhad",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-906",
      "reason": "budget exceeded"
    },
    {
      "id": "c07fce4656ccf06e27e96d0d",
      "reason": "budget exceeded"
    },
    {
      "id": "c1f7d54eb7fe0171197e033b",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 5788,
  "budget": {
    "limit": 6000,
    "used": 5788
  },
  "left_out": {
    "count": 7,
    "superseded": [
      "DEC-038",
      "DEC-048",
      "DEC-636",
      "DEC-798",
      "DEC-869",
      "DEC-876",
      "DEC-960"
    ],
    "done": []
  },
  "hash": "2da977e89a80d37f34e3493f980ef84f4b780c5e6a1ad3495f8c301fe3e6af59"
}
