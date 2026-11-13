{
  "ticket": "DAEO-pg6i",
  "ticket_text": "---\nid: DAEO-pg6i\nstatus: in_progress\ndeps: []\nlinks: [DAEO-2bdu, DAEO-zmo4]\ncreated: 2026-11-12T16:55:43Z\ntype: task\npriority: 1\nassignee: product-spec\nexternal-ref: W2-88a\nparent: DAEO-2bdu\ntags: [wave-2, product-spec, adoption, memory, kernel-skill, standard]\nwbs_id: W2-88a\ntitle: 'W2-88a The adopt skill states Wave 0''s memory practice in order, and the Verify pass (W2-88''s and W2-174''s kernel skill text)'\nclass: specification\nstate_class: AUTHORITATIVE\nrole: product-spec\nprofile: STANDARD\ndepends_on: []\nwaits_on: []\nallowed_paths:\n- template/governance/kernel/skills/adopt/SKILL.md\n- template/.rulesync/skills/adopt/SKILL.md\n- .rulesync/skills/adopt/SKILL.md\n# .claude/skills/adopt/SKILL.md out of the paths: generated from the kernel skill by the copies ACT after the owner's approval (DEC-315)\n- docs/changes/W2-88a-CIT-P.md\n- docs/research/W2-88-memory-practice.md  # the practice record the skill points to, refreshed to S17's order (from W2-88)\nest_loc: 80\nreads:\n- .tickets/DAEO-2bdu.md\n- .tickets/DAEO-zmo4.md\n- docs/research/W2-88-memory-practice.md\n- template/governance/kernel/skills/\nneeds: []\nkpis:\n  success:\n  - 'S17 The Wave 0 order in the adopt skill: A9''s step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)]'\n  - line: \"The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]\"\n    verify: \"tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section\"\n  - 'The CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill''s sha256 before and after, the lines added or removed, the independent review and the owner''s approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections Verify: the record holds both hashes and the review''s verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116]'\n  failure: []\nnon_goals:\n- the adopt code (W2-88, W2-174) and the proofs (W2-88b); the .claude/ copy (the copies ACT)\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1150, DEC-996, DEC-995, DEC-1098, DEC-1130, CAP-33]\nacceptance_tests:\n  path: tests/acceptance/W2-88a/\n  author: independent-test-designer (MR-3); written before the text\ntrack: A\n---\n# W2-88a The adopt skill's kernel text (a child of W2-88)\n\nFiled by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the kernel skill text: W2-88's S17 (moved word for word) and W2-174's skill line (its S5, moved word for word, so the adopt skill is written once under one CIT-P). The two `test_w2_174_skill.py` and S17 string tests named in the moved lines are this ticket's acceptance tests, written by its test designer under `tests/acceptance/W2-88a/`. It can start now; the owner approves the skill's bytes before the merge (CAP-33).\n",
  "authority": [
    {
      "id": "DEC-1150",
      "sha256": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "reason": "declared in sources",
      "tokens": 4054
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1130",
      "sha256": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "reason": "declared in sources",
      "tokens": 428
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1150",
      "sha256": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "091ea97d4a5880210003e70153f8adb9b62f8c8eac7a7f494fefdd763ed2f396",
      "reason": "declared in sources",
      "tokens": 4054
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-995",
      "sha256": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b0543edf119247c03260286eb37528a0156ba8cbf7324a74d30ba078edf9bb11",
      "reason": "declared in sources",
      "tokens": 660
    },
    {
      "id": "DEC-1098",
      "sha256": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ecc0acf03f76d6a8bba861e7ec59436e065fcf1305ccfbe214e58297017bee73",
      "reason": "declared in sources",
      "tokens": 869
    },
    {
      "id": "DEC-1130",
      "sha256": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5ab0080f7f976ce8e6c34ab226ef63bad8eec55fb5a87df46e32d083e71e43b1",
      "reason": "declared in sources",
      "tokens": 428
    },
    {
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "supplementary": [
    {
      "id": "DAEO-xxxx",
      "path": "governance/project/orchestration/packages/ADOPT-VERIFY-1/TICKET-DRAFT.md",
      "text": "    verify: \"tests/unit/adopt/test_w2_174_checks.py: one case per refusal (unknown ticket, closed ticket, unknown label, an unanswered line, an empty clause, a `TBD` clause), each refused with a named code and nothing written\"\n  - line: \"The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]\"\n    verify: \"tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section\"\n  failure:\n  - line: \"The apply never writes anything if one entry is refused (all or nothing), never edits a ticket the answers file does not name, never edits a closed ticket, and never marks a ticket `verify_pass` while one of its lines still has no verify [DEC-1130]\"\n",
      "tokens": 266
    },
    {
      "id": "DEC-1074",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1074 \u2014 The night's result decided: 67.8 % the 0.6B's honest figure; every used set now tuning or diagnostic; the 60's misses classified before the next lever; a new verdict set of 80; consistency within 5 points; v456 and the stated links approved for window 4; W2-54's premise rewritten; LINK-INTEGRITY adopted; the open items\n- **Status:** ACCEPTED (owner, 2026-11-05 morning, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-05)`) \u00b7 **Under:** DEC-1071, DEC-1072, DEC-1073 \u00b7 **Changes:** DEC-1071 (3) (the consistency bound, item 4), DEC-1070 (2)-(4) (the sets' jobs, item 1) \u00b7 **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-MORNING-2026-11-05.md` (`7f5a80b7`), `LINK-INTEGRITY.md` (`23610a2e`) \u00b7 **Changed by:** DEC-1076 (1) \u00b7 **Changed by:** DEC-1087 (7)\n- **Decision:**\n  - **(1) 67.8 % is recorded as the 0.6B's honest figure on this structure:** v456 + the stated links, 40/59 on\n    `memory-verdict`.\n    - **The owner's reading:** the gap is mainly both halves having become tuning sets since DEC-1071 (every fix\n",
      "tokens": 286
    },
    {
      "id": "373357077b247cf363833ae8",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S17 The Wave 0 order in the adopt skill: A9''s step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1098 (1)]'\n  failure:\n  - 'A verdict set read by a measured role, measured twice, or used to choose anything; a declaration committed after the first search [added, DEC-1098 (1)]'\n  - 'A store served with a setting other than the standard''s and no decision id in the A9 record [added, DEC-1098 (1)]'\n  - 'A tuning or verdict question written with the product''s own search, or by a session in the retrieval work [added, DEC-1098 (1)]'\n```\n\n",
      "tokens": 296
    },
    {
      "id": "DAEO-2bdu",
      "path": ".tickets/DAEO-2bdu.md",
      "text": "- DEC-630\n- DEC-718\n- DEC-723\n- DEC-728\n- DEC-388\n- DEC-694\n- DEC-530\n- DEC-833\n- DEC-860\n- DEC-941\n- DEC-105\n- CAP-44\n- CAP-17\n- CAP-20\n- CAP-10\n- CAP-19\n- DEC-957\n- CAP-44.b\n- CAP-44.f\n- CAP-44.g\n- DEC-016\n- DEC-1083\n- DEC-1084\n- DAEO-mb2t\n- DAEO-2ds6\n- DEC-1098\n- DEC-1099\n- DEC-1097\n- DEC-1072\n- DEC-1071\n- DEC-1070\n- DEC-1074\n- DEC-1092\n- DEC-1094\n- CAP-33\n- DEC-1010\n- DEC-1046\n- DEC-1069\n- DEC-1076\n- DEC-1078\n- DEC-1079\n- DEC-1101\n- DEC-1125\n- DEC-315\n- DEC-1112\nest_loc: 750  # [changed, DEC-1099 (2)] was 500 (W2-88-STANDARD-1 \u00a74)\nacceptance_tests:\n  path: tests/acceptance/W2-88/\n",
      "tokens": 148
    },
    {
      "id": "DAEO-n0wb",
      "path": ".tickets/DAEO-n0wb.md",
      "text": "  failure:\n  - 'A question that names no record or symbol gets a different bundle than today.'\n  - 'A whole-graph query, or one over the tool''s row cap.'\n  - 'A missing index reported ok, or failing the whole answer.'\n  - 'A figure of the measure reported without the other, or the hidden half read or run.'\n  - 'A partial supersession that drops its target from what is current; a register chunk in a bundle without its status.'\n  - 'A verbless change label''s prose id counted as a changer, or a clause-head changer lost (S11) [DEC-1109 (2)]'\nprofile: STANDARD\nsources:\n- DEC-385\n- DEC-1098\n- DEC-1109\n- DEC-957\n- DEC-954\n- DEC-859\n- DEC-860\n- DEC-424\n- DEC-833\n- CAP-12\n- CAP-13\n- CAP-18\n- DEC-1071\n- DEC-1072\n- DEC-1073\n- DEC-1074\n- DEC-1055\n- DEC-1065\n- DEC-423\nest_loc: 200\nacceptance_tests:\n  path: tests/acceptance/W2-92/\n  author: independent-test-designer (MR-3); written before implementation; a planted repository with a register, records and code, its store and a stand-in code index built in a temporary folder; never this repository's store\ntrack: B\nlist_rows: []\n---\n",
      "tokens": 271
    },
    {
      "id": "DAEO-n0wb",
      "path": ".tickets/DAEO-n0wb.md",
      "text": "  - 'S7 The stated links (DEC-1072 (1), the census''s kinds 1 to 4): at rebuild the store keeps, in a table of its own outside the digest, the links the records state that no edge holds: the front-matter id keys (sources, closes, decisions, decisions_applied, decisions_carried, decisions_recorded, decisions_read, requirements_implemented) as CITES, task as OF_TASK, the register''s **Under:** as UNDER, a supersession naming ids alone as SUPERSEDES and every other supersession or amendment as AMENDS, by the census''s patterns in one function (register_statements) that gov links reads too; on this repository''s register they match the census''s statements one for one; the closure, gov dangling and every reader of edges are unchanged [DEC-1072, DEC-1073]'\n  - 'S8 One bounded hop: from what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and SUPERSEDES in (from the changed decision to its changer), at most 12 records, after today''s closure chunks; adopted only under DEC-1071''s rule (all 80 not lower, the halves'' gap not wider) [DEC-1071, DEC-1072]'\n",
      "tokens": 279
    },
    {
      "id": "1ab780b262b811cbbe6ef6d8",
      "path": "docs/changes/W2-92-evidence.md",
      "text": "| F4 a figure without the other, or the hidden half read or run | the measure record (\u00a74 gives both figures together; \u00a78: the hidden half neither read nor run) | measure: D-4b measure 1 | earlier record as cited; re-measured: D-4b measure 1 | `d72c96fc029c` (record); D-4b measure 1 |\n| S7 the stated links (DEC-1072 (1), the census's kinds 1 to 4) | the store keeps `stated_links` (CITES, OF_TASK, UNDER, SUPERSEDES, AMENDS) outside the digest and `edges`; `loader.register_statements` is the census's \u00a71 code's output one for one, on a planted register and on this repository's (3,171 statements, same order) | unit `tests/unit/store/test_w2_92_links.py` (9 cases); `gov accept` after the designer's S7 tests merge | unit pass; `gov accept`: after the merge | `21623ae258a1` |\n| S8 one bounded hop | `graph_route.follow`: CITES, UNDER, OF_TASK out, AMENDS and SUPERSEDES in, at most 12 records of 2 chunks each, after today's closure chunks; the links never reach `edges` or the authority order | unit `tests/unit/retrieval/test_w2_92_follow.py` (12 cases); adoption under DEC-1071's rule: the CTO's measure | unit pass; measure: CTO | `21623ae258a1` |\n",
      "tokens": 289
    },
    {
      "id": "DEC-1073",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1073 \u2014 The structure finished before the measurement set's single use; drift's definitions; M5 retested with the register links; waits and stops by process id only; link integrity as a Gov OS capability, as one package first\n- **Status:** ACCEPTED (owner, 2026-11-04 ~23:55, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) \u00b7 **Under:** DEC-1071, DEC-1072, L-0075, DEC-1052 \u00b7 **Source:** `.gov-runtime/scratch/orchestrator/drafts/d4b/DAY.md` (v456 and the halves' agreement), `docs/research/D4B-link-census.md` (`3d1c459e`)\n- **Decision:**\n  - **(1) The measurement set's single use is held until the structure is final.** D4B-STRUCTURE's steps 2 and 4 to 7 are measured first, each under DEC-1071's rule on the best structure so far:\n    - the reranker shown title and section;\n    - one place per identical text;\n    - the heading and answer-unit prototypes;\n    - the graph links.\n\n    If the halves still agree within 3 points after them, the 60 are used once on that final structure; if they drift apart, it goes to the owner first.\n  - **(2) Drift: the register is the authority.**\n",
      "tokens": 299
    },
    {
      "id": "dc4afdccedefaaebf4f7512e",
      "path": "docs/changes/W2-92-evidence.md",
      "text": "## S7 to S10: the stated links (DEC-1072 (1), DEC-1073 (2), DEC-1074 (5); re-pin window 4)\n\nBuilt from the prototype `w2/W2-92-proto` (`e884675b`, the measured reference), on `w2/W2-92` at `5a9e36c07571`\n(today's `w2/integrate`); the code commit is `21623ae258a1`. Built to the KPI text; the engineer has not read\n`tests/acceptance/W2-92/`.\n\n- **S7, `store/loader.py`:** `register_statements(text, entries=None)` is the census's \u00a71 (its labels, free text and\n  change log, every class, its form strings and its de-duplication), public, for `gov links` (W2-129) to import.\n  `_stated_links` turns the front-matter keys (`sources`, `closes`, `decisions`, `decisions_applied`,\n  `decisions_carried`, `decisions_recorded`, `decisions_read`, `requirements_implemented` as CITES; `task` as OF_TASK;\n  a W2 id through `wbs_id`/`external-ref`) and the register's statements (under \u2192 UNDER; a supersession naming ids\n  alone \u2192 SUPERSEDES; every other supersession or amendment \u2192 AMENDS) into rows of `stated_links (type, source,\n  target, via)`: both ends records, none `edges` holds with the same type. The table is outside the digest and part\n",
      "tokens": 284
    },
    {
      "id": "DRAFT-W2-129",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-129-gov-links.md",
      "text": "  - 'A finding older than the mark lost: neither listed nor counted.'\n  - 'gov links --all over 10 s on this repository.'\nprofile: STANDARD\nsources:\n- DEC-1073\n- DEC-1072\n- DEC-1071\n- DEC-1052\n- DEC-866\n- DEC-825\n- DEC-927\n- DEC-861\n- DEC-182\n- CAP-27\nest_loc: 400\nacceptance_tests:\n  path: tests/acceptance/W2-129/\n  author: 'independent-test-designer (MR-3); written before implementation, from this ticket''s KPIs and LINK-INTEGRITY.md \u00a74. A planted repository in a temporary folder: a register with each statement form (Changes:, Changed by:, Supersedes: with ids alone and with a part, free text \"amended by\", an entry with no mark, a PROPOSED and a REJECTED entry), ARCHIVE-SUPERSEDED with \u00a7A and \u00a7B, DECISIONS-IN-FORCE, tickets with sources, KPI brackets, an unknown id and a missing acceptance path, commits with Task:, Implements: and Role: (a landing commit among them), a lesson, a plan file, a kernel skill line citing a PROPOSED decision, and a contract.yaml with a provider that does not exist; a second planted repository with no register and no tickets. Never this repository''s store. The timing is the CTO''s measured run, not a test.'\ntrack: B\nlist_rows: []\n---\n",
      "tokens": 296
    },
    {
      "id": "DEC-1072",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1072 \u2014 D4B-STRUCTURE's order stands; steps 5 to 7 as prototypes only; step 7 widened to every stated link, with a drift count; memory-building a Gov OS practice for every adopted repository's Wave 0\n- **Status:** ACCEPTED (owner, 2026-11-04 ~22:15, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) \u00b7 **Under:** DEC-1071, DEC-1070 \u00b7 **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-STRUCTURE.md` (`33ba2842`)\n- **Decision:** **The order of D4B-STRUCTURE stands.** Steps 5 to 7 are approved as **prototypes in measure clones only**, each coming back to the owner with its figures before any product change. Steps 2 onward go on; the stand-by ends.\n  - **(1) Step 7 widens from decisions to every link the repository states.**\n    - **First a census:** each kind of relationship stated in records, front matter, commit trailers and text, against the edges the graph holds, in counts. The kinds include:\n      - a decision supersedes, amends or cites a decision;\n      - a ticket implements or depends on a decision;\n      - commits' `Task:` and `Implements:` trailers;\n",
      "tokens": 298
    },
    {
      "id": "DAEO-q7lk",
      "path": ".tickets/DAEO-q7lk.md",
      "text": "  - 'A finding older than the mark lost: neither listed nor counted.'\n  - 'gov links --all over 10 s on this repository.'\n  - 'A real citation in a test file''s comment, docstring or non-Python file dropped as planted, or a planted literal id still reported (S17) [DEC-1109 (2)]'\nprofile: STANDARD\nsources:\n- DEC-1098\n- DEC-1109\n- DEC-1073\n- DEC-1072\n- DEC-1071\n- DEC-1052\n- DEC-866\n- DEC-825\n- DEC-927\n- DEC-861\n- DEC-182\n- CAP-27\n- DEC-1088\nest_loc: 400\nacceptance_tests:\n  path: tests/acceptance/W2-129/\n",
      "tokens": 127
    },
    {
      "id": "a1b21b7e769dcbb6efa7924f",
      "path": "docs/research/D4B-link-census.md",
      "text": "# D4B link census: every link the repository states, against the graph's edges (DEC-1072 (1))\n\n- **By:** the research role (one session, Claude Opus 5.5), for the CTO, under DEC-1072 (1), DEC-1071 (1) (the graph)\n  and D4B-STRUCTURE G1.\n- **Date:** 2026-11-04.\n- **Measured at:** the m6 clone `~/gov-os-runs/D4B/m6/repo`, commit `24f06026`. Its store `.gov-runtime/store.db` was\n  built by a rebuild at that head (fingerprints row `24f06026\u2026`, kind `rebuild`).\n- **Method:** read-only. No model, no GPU, no `gov retrieve`, no network.\n  - **The graph as the product sees it:** `gov.records.records/edges` and `gov.closure.closure`.\n  - **Its rules:** read in `src/gov/store/loader.py` and `src/gov/retrieval/retrieve.py` (`_graph`), and in\n    `authority.py` (`register_entries_of`, `Order`).\n  - **The stated links:** the clone's files, its `git log` and the store's `lexical_chunk` table, parsed by one script,\n    `docs/research/D4B-link-census.py`. It is run as\n    `PYTHONPATH=<clone>/src python3 census.py <clone> <out.json>` and takes about a minute.\n  - **Columns:** *pairs* counts distinct source\u2192target pairs. A pair is *resolvable* when its target is a store record\n",
      "tokens": 295
    },
    {
      "id": "1d5208160407692b68dbeca6",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "text": "  - `'S8 One bounded hop: from what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and SUPERSEDES in (from the changed decision to its changer), at most 12 records, after today''s closure chunks; adopted only under DEC-1071''s rule (all 80 not lower, the halves'' gap not wider) [DEC-1071, DEC-1072]'`\n  - `'S9 Status in the bundle: every register chunk a bundle carries names its entry''s status word and the entries that change it; a PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED decision is marked not in force, so no agent takes it as a rule [DEC-1073 (2)]'`\n  - `'S10 The drift count before and after, by the census''s definitions (docs/research/W2-92-proto-drift.py on the rebuilt store): of the decisions current though stated changed, how many a search reaching the decision also reaches a changer of, in docs/research/W2-92-memory-measure.md [DEC-1072 (1)]'`\n- **Add to failure:** `'A partial supersession that drops its target from what is current; a register chunk in a bundle without its status.'`\n- **Add to `allowed_paths`:** `docs/research/W2-92-proto-drift.py`.\n- **Add to `sources`:** DEC-1071, DEC-1072, DEC-1073.\n\n",
      "tokens": 296
    },
    {
      "id": "5c620c3a6b763964b25cc914",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "text": "  - `'S7 The stated links (DEC-1072 (1), the census''s kinds 1 to 4): at rebuild the store keeps, in a table of its own outside the digest, the links the records state that no edge holds: the front-matter id keys (sources, closes, decisions, decisions_applied, decisions_carried, decisions_recorded, decisions_read, requirements_implemented) as CITES, task as OF_TASK, the register''s **Under:** as UNDER, a supersession naming ids alone as SUPERSEDES and every other supersession or amendment as AMENDS, by the census''s patterns in one function (register_statements) that gov links reads too; on this repository''s register they match the census''s statements one for one; the closure, gov dangling and every reader of edges are unchanged [DEC-1072, DEC-1073]'`\n  - `'S8 One bounded hop: from what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and SUPERSEDES in (from the changed decision to its changer), at most 12 records, after today''s closure chunks; adopted only under DEC-1071''s rule (all 80 not lower, the halves'' gap not wider) [DEC-1071, DEC-1072]'`\n",
      "tokens": 280
    },
    {
      "id": "91e142181324abe2f409150a",
      "path": "tests/acceptance/W2-92/test_w2_92_hop.py",
      "text": "\"\"\"KPI success 8 (DEC-1071, DEC-1072) and the failure line \"a partial supersession that drops its target from what\nis current\": one bounded hop.\n\nFrom what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and\nSUPERSEDES in (from the changed decision to its changer), at most 12 records, after today's closure chunks. A\nquestion that reaches no record gets today's bundle.\n\nEach question is a record's title alone: the record route reaches the record, and no word of the question is in the\nrecord the hop must bring, so only the hop can bring it (no id is in the question, so the lexical route's id boost\nbrings nothing). Each case first checks that today's bundle (the integrated code ``support.LINKS_BASE`` on the same\nmarina) holds the named record and not the hop's record. A record is in a bundle when an evidence item holds its\ntext. No reranker, no vector, no code index.\n\nNot a case here: \"adopted only under DEC-1071's rule (all 80 not lower, the halves' gap not wider)\" is the CTO's\nmeasure, verified by the evidence file (README map).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport pytest\n\nimport w2_92_support as support\n\n",
      "tokens": 296
    },
    {
      "id": "993f4315ffcceae303003736",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md",
      "text": "  widen. **The proof is consistency:** the halves agree within 3 points; then memory-verdict (60) is measured once as\n  the confirmation (if it disagrees, to the owner first). **Then** all three rerankers on the three sets. The\n  nonexistent-id question passes on `UNRESOLVED_IDS` naming its id, scored apart from hit@5. Basis: questions 1 and 2.\n- DEC-1072 (2026-11-04): D4B-STRUCTURE's order stands; its steps 5-7 are prototypes in measure clones only, back to\n  the owner with figures before any product change. **Step 7 covers every stated link:** a census of each kind of\n  relationship stated (records, front matter, trailers, text) against the graph's edges; the missing kinds built as\n  the evidence supports; a drift count (decisions retrievable as current though superseded or amended). **Memory-building\n  is a Wave 0 practice** for every adopted repository, kept in its ticket as D-4b goes, a kernel skill after the\n  refactoring.\n- DEC-1073 (2026-11-04; its \"within 3 points\" is now 5, DEC-1074 (4)): the measurement set is used once, **after the structure is final** (D4B-STRUCTURE steps 2 and\n",
      "tokens": 277
    },
    {
      "id": "DAEO-q7lk",
      "path": ".tickets/DAEO-q7lk.md",
      "text": "  - 'NOT_IN_FORCE_AS_RULE: a decision whose status is PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED, named in a rule-bearing place: an open or in-progress ticket''s sources or KPI brackets; a judged commit''s Implements:; a register entry''s Under:; a kernel role, skill or template line; a project brief or prompt line; a path-map comment; CONTRACT_v4.md. A PROPOSED decision is never counted as current [DEC-1073 (2)]'\n  - 'ENFORCES_SUPERSEDED: W2-55''s gov.decisions.propagation findings, as that module gives them, carried in the same output [DEC-866, DEC-1073]'\n  - 'One source of patterns: the register''s statements are read by the loader''s register_statements (W2-92, the census''s patterns), never a second pattern set; on this repository at the clean-up''s starting head the decisions UNMARKED_CHANGE names agree with docs/research/W2-92-proto-drift.py''s drifting list. If W2-92''s product change is not in, the function moves unchanged into src/gov/decisions/statements.py under this ticket and W2-92 imports it [DEC-1072 (1), DEC-1073 (2)]'\n",
      "tokens": 264
    },
    {
      "id": "301dc852a348c005826fa415",
      "path": "docs/research/W2-92-memory-measure.md",
      "text": "## 10. Drift before and after the stated links (S10, DEC-1072 (1), DEC-1073 (2))\n\n- **The question:** of the decisions current though the register states them changed, how many does a search that reaches the decision also reach a changer of?\n- **The definitions are the census's** (`docs/research/D4B-link-census.py`, `3d1c459e`). A statement is a register label, its free text, the change log or ARCHIVE-SUPERSEDED \u00a7A. The register's statements come from `loader.register_statements`, which gives the census's 3,171 statements one for one on this repository's register (S7; `tests/unit/store/test_w2_92_links.py`). Current means status ACCEPTED and no SUPERSEDES edge in `edges`. DEC-1073 (2): the decisions ARCHIVE-SUPERSEDED \u00a7B calls spent are listed apart for a status reconciliation and are not counted; a decision that is not ACCEPTED (PROPOSED above all) is never current and is counted apart, by status.\n",
      "tokens": 228
    },
    {
      "id": "DRAFT-W2-129",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-129-gov-links.md",
      "text": "  - 'NOT_IN_FORCE_AS_RULE: a decision whose status is PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED, named in a rule-bearing place: an open or in-progress ticket''s sources or KPI brackets; a judged commit''s Implements:; a register entry''s Under:; a kernel role, skill or template line; a project brief or prompt line; a path-map comment; CONTRACT_v4.md. A PROPOSED decision is never counted as current [DEC-1073 (2)]'\n  - 'ENFORCES_SUPERSEDED: W2-55''s gov.decisions.propagation findings, as that module gives them, carried in the same output [DEC-866, DEC-1073]'\n  - 'One source of patterns: the register''s statements are read by the loader''s register_statements (W2-92, the census''s patterns), never a second pattern set; on this repository at the clean-up''s starting head the decisions UNMARKED_CHANGE names agree with docs/research/W2-92-proto-drift.py''s drifting list. If W2-92''s product change is not in, the function moves unchanged into src/gov/decisions/statements.py under this ticket and W2-92 imports it [DEC-1072 (1), DEC-1073 (2)]'\n",
      "tokens": 264
    },
    {
      "id": "42b9b621c79b085c507a09a8",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "text": "### 6.1 Existing tickets that change (text for the CTO to apply after the owner decides)\n**W2-92** (`DAEO-n0wb`, in progress)\n- **Why:** the prototype is built under W2-92's id, but none of its KPIs states it. DEC-1073 (2) asks that retrieval\n  show a decision's status.\n- **Add to success:**\n  - `'S7 The stated links (DEC-1072 (1), the census''s kinds 1 to 4): at rebuild the store keeps, in a table of its own outside the digest, the links the records state that no edge holds: the front-matter id keys (sources, closes, decisions, decisions_applied, decisions_carried, decisions_recorded, decisions_read, requirements_implemented) as CITES, task as OF_TASK, the register''s **Under:** as UNDER, a supersession naming ids alone as SUPERSEDES and every other supersession or amendment as AMENDS, by the census''s patterns in one function (register_statements) that gov links reads too; on this repository''s register they match the census''s statements one for one; the closure, gov dangling and every reader of edges are unchanged [DEC-1072, DEC-1073]'`\n",
      "tokens": 265
    },
    {
      "id": "cab7fa13f5e05fe2893ddcd2",
      "path": "src/gov/store/loader.py",
      "text": "  ``**Status:**`` on its first line that is not blank, its path the register file. Its heading, title, span and\n  ``content_hash`` are kept in ``register_entries`` (AR-1): the span is its own text, the hash the sha256 of it.\n  A heading alone, one inside an HTML comment, an id outside the ``decision_id`` grammar, a status word not in\n  capitals and an id under two headings make no record (W2-L221, W2-M145, W2-M106). A named register that\n  ``HEAD`` does not hold as a file of text refuses the load (DEC-579: one that is not in the commit too).\n- A record of a file whose frontmatter ``title`` is a string keeps it in ``record_titles`` (W2-92 S6), outside the\n  digest.\n- The links the records state that no edge holds are kept in ``stated_links`` (W2-92 S7, DEC-1072 (1)), outside the\n  digest: a record's frontmatter id keys (``CITE_KEYS`` as CITES, ``task`` as OF_TASK, a W2 id read through\n  ``wbs_id``/``external-ref``), and the register's statements (``register_statements``): a supersession that names\n  ids alone as SUPERSEDES, any other supersession or amendment as AMENDS, ``**Under:**`` as UNDER.\n- ``Task:`` and ``Implements:`` trailers are read from the final trailer block;\n",
      "tokens": 298
    },
    {
      "id": "0e28079969af60fb5bf83e38",
      "path": "tests/unit/store/test_w2_92_links.py",
      "text": "\"\"\"Builder tests for W2-92 S7 (DEC-1072 (1)): the links the repository states, kept at the load.\n\nRegression evidence only (DEC-136). A planted repository in a temporary folder: a register whose entries supersede,\namend and stand under one another, a ticket, a checkpoint, a close record and a plan. Each kind the census ranks 1 to\n4 becomes a typed row of ``stated_links``; a supersession that names ids alone is SUPERSEDES, one of a part AMENDS;\nonly links between records are kept, none that ``edges`` holds; the digest and every reader of ``edges`` are unchanged.\nOn this repository's register, ``register_statements`` gives the census's own statements one for one.\n\"\"\"\nfrom __future__ import annotations\n\nimport collections\nimport re\nimport sqlite3\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nREPO = Path(__file__).resolve().parents[3]\nsys.path.insert(0, str(REPO / \"src\"))\n\nfrom gov import records, store  # noqa: E402\nfrom gov.rebuild import seed  # noqa: E402\nfrom gov.store import loader  # noqa: E402\n\nREGISTER = \"docs/DECISION_REGISTER.md\"\nREGISTER_TEXT = \"\"\"\\\n# Register\n\n| Version | Change |\n|---|---|\n| 0.2 | DEC-108 (the second rule; supersedes DEC-110) |\n\n",
      "tokens": 300
    },
    {
      "id": "ADR-0002",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "text": "decisions: [DEC-064, DEC-065, DEC-066, DEC-067, DEC-073, DEC-074, DEC-075, DEC-076, DEC-078, DEC-080, DEC-083, DEC-084, DEC-085, DEC-086, DEC-087, DEC-088, DEC-089, DEC-090, DEC-091, DEC-092, DEC-093, DEC-094, DEC-095, DEC-096, DEC-138, DEC-141, DEC-150, DEC-152, DEC-153, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-170, DEC-171, DEC-172, DEC-173, DEC-174, DEC-192, DEC-261, DEC-396, DEC-397, DEC-419, DEC-530, DEC-637, DEC-649, DEC-700, DEC-953, DEC-954, DEC-963, DEC-979, DEC-1010, DEC-1015, DEC-1029, DEC-1030, DEC-1031, DEC-1032, DEC-1033, DEC-1034, DEC-1035, DEC-1036, DEC-1037, DEC-1038, DEC-1039, DEC-1043, DEC-1045, DEC-1046, DEC-1047, DEC-1048, DEC-1049, DEC-1052, DEC-1055, DEC-1056, DEC-1057, DEC-1058, DEC-1059, DEC-1061, DEC-1064, DEC-1065, DEC-1066, DEC-1067, DEC-1068, DEC-1069, DEC-1070, DEC-1072, DEC-1073, DEC-1074, DEC-1075, DEC-1076, DEC-1077, DEC-1079, DEC-1081, DEC-1082, DEC-1084, DEC-1085, DEC-1086, DEC-1087, DEC-1088, DEC-1089, DEC-1090, DEC-1092, DEC-1093, DEC-1094, DEC-1095, DEC-1096, DEC-1097, DEC-1098]\nsupersedes: []\nimplements: [CHARTER-v5, CONTRACT-v4]\nstate_class: AUTHORITATIVE\n---\n\n",
      "tokens": 300
    },
    {
      "id": "2aa97e8505d0c25fe3a65616",
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft",
      "text": "decisions: [DEC-064, DEC-065, DEC-066, DEC-067, DEC-073, DEC-074, DEC-075, DEC-076, DEC-078, DEC-080, DEC-083, DEC-084, DEC-085, DEC-086, DEC-087, DEC-088, DEC-089, DEC-090, DEC-091, DEC-092, DEC-093, DEC-094, DEC-095, DEC-096, DEC-138, DEC-141, DEC-150, DEC-152, DEC-153, DEC-156, DEC-157, DEC-158, DEC-159, DEC-160, DEC-161, DEC-162, DEC-163, DEC-164, DEC-165, DEC-166, DEC-167, DEC-168, DEC-170, DEC-171, DEC-172, DEC-173, DEC-174, DEC-192, DEC-261, DEC-396, DEC-397, DEC-419, DEC-530, DEC-637, DEC-649, DEC-700, DEC-953, DEC-954, DEC-963, DEC-979, DEC-1010, DEC-1015, DEC-1029, DEC-1030, DEC-1031, DEC-1032, DEC-1033, DEC-1034, DEC-1035, DEC-1036, DEC-1037, DEC-1038, DEC-1039, DEC-1043, DEC-1045, DEC-1046, DEC-1047, DEC-1048, DEC-1049, DEC-1052, DEC-1055, DEC-1056, DEC-1057, DEC-1058, DEC-1059, DEC-1061, DEC-1064, DEC-1065, DEC-1066, DEC-1067, DEC-1068, DEC-1069, DEC-1070, DEC-1072, DEC-1073, DEC-1074, DEC-1075, DEC-1076, DEC-1077, DEC-1079, DEC-1081, DEC-1082, DEC-1084, DEC-1085, DEC-1086, DEC-1087, DEC-1088, DEC-1089, DEC-1090, DEC-1092, DEC-1093, DEC-1094, DEC-1095, DEC-1096, DEC-1097]\nsupersedes: []\nimplements: [CHARTER-v5, CONTRACT-v4]\nstate_class: AUTHORITATIVE\n---\n\n",
      "tokens": 297
    },
    {
      "id": "11b688c21b3cff5c55e3dd49",
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "text": "| W2-56 | wnnz | in_progress | re-scope: status back to open (built nothing, W-6); S1 becomes T-8's daemon folder; takes W2-127, W2-21's S5\u2013S8 and **(audit 23)** W2-21's F1 (a raw `claude` launch stays unallowed in the template, beside S7's allow rule) | 10 + 11 | K9 (DEC-799) |\n| W2-60b | ecac | open | re-scope; **(audit 38)** its `deps` set to its `depends_on` (W2-60a, W2-07) | 13 | |\n| W2-82 | 4k3l | open | re-scope: a light readiness check the dispatcher calls; **(audit 39)** it calls W2-128 S10's check, the one home of a ticket's readiness (W-2) | 12 | leaves K9 |\n| W2-88 | 2bdu | open | **re-scope (\u0394 D-4b)** | 19, plus LINK-INTEGRITY \u00a76.1's two lines (DEC-1074 (7), not yet written); S5 to W2-124; **(re-check 3)** F6 drops the clause \"a figure of the measure reported without the other\" (W-3, a re-word) | gains a dep on W2-129; owns memory-building (DEC-1072 (2)); W2-15b's other corpora run on its tools |\n| W2-98 | wi46 | open | re-scope; its dep on W2-104 cut | 13, plus one link line (DEC-1074 (7), not yet written). **(re-check 3)** S5 and F4 (the three scenarios) lifted, now optional (W-3); S6 keeps the licence and drops \"and its three scenarios passing\" (a re-word) | |\n",
      "tokens": 299
    },
    {
      "id": "DEC-1071",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1071 \u2014 Structural fixes only, judged on all 80; consistency across the sets as the proof; then the measurement set once; then all three rerankers; the nonexistent-id question scored apart\n- **Status:** ACCEPTED (owner, 2026-11-04 ~22:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) \u00b7 **Under:** DEC-1070 (amended here), DEC-1067 (b) (amended here for structural fixes), DEC-1009 \u00b7 **Source:** the owner's message after stage A (`.gov-runtime/scratch/orchestrator/drafts/d4b/DAY.md`, stage A's result) \u00b7 **Changed by:** DEC-1074 (4)\n- **Decision:** (1) **Fixes are structural, never per question.** The diagnosis goes beyond why each question missed, to what in memory's structure causes misses of each kind across the whole memory:\n  - **chunking:** code cut away from its definition; answers that are one list item, table row, field or line; long diluted chunks; split sections;\n  - **embedding:** what is embedded and how (headers, duplicated or generated copies);\n  - **ranking:** the routes' depth, the cuts, the fusion, the pool the reranker sees, the authority lift;\n",
      "tokens": 297
    },
    {
      "id": "edd84696d44a8e9a77713126",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md",
      "text": "### 1.2 Why the spent 59 are the best guide\n- **The same writer and checker** wrote the spent 60 and the fresh 80 (DEC-1076 (1)), blind, by the same rubric.\n- **The spent set was used once, on 11-05,** and has been diagnostic since. No configuration was adopted on it: the grid's leaders wait for E4. Its hit@5 was 40 of 59 on 11-05, and it is still 40 of 59 at window 4 (DEC-1074 (1), E0).\n- **The visible 40 are the tuning set,** and the hidden half was tuned too (the owner's reading in DEC-1074 (1)). Their higher figures are not a guide to a fresh set.\n- **A useful sign:** at A2 the hidden and spent sets agree almost exactly (89.7 % and 89.8 %), although they differ by 14 points at hit@5. An agent that reads the whole bundle and searches once more absorbs most of the ranking gap. End to end is the most consistent figure across sets, which is DEC-1071 (3)'s test of a sound structure.\n\n",
      "tokens": 224
    },
    {
      "id": "DAEO-0pyc",
      "path": ".tickets/DAEO-0pyc.md",
      "text": "  failure:\n  - An improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.\n  - 'A pool setting absent or 0 that changes what a search returns; a rerank pass that sends a request past the padded bound.'\nprofile: STANDARD\nsources:\n- CAP-10.b\n- CAP-19.a\n- CAP-19.c\n- DEC-725\n- DEC-954\n- DEC-957\n- DEC-1031\n- DEC-1055\n- DEC-1064\n- DEC-1065\n- DEC-1066\n- DEC-1067\n- DEC-1068\n- DEC-1069\n- DEC-1071\n- DEC-1074\n- DEC-1083\n- DEC-1086\n- DEC-1097\n- DEC-1098\n- DEC-1129\nest_loc: 320\nacceptance_tests:\n  path: tests/acceptance/W2-32/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-10.b\n- CAP-19.a\n- CAP-19.c\n- DEC-725\nlist_rows:\n- W2-L029\n- W2-L065\n- W2-L066\n- W2-L068\n- W2-L239\n- W2-M001\n- W2-M073\n- W2-M103\n- W2-M104\n- W2-M191\n- W2-M341\n---\n",
      "tokens": 203
    },
    {
      "id": "DAEO-2bdu",
      "path": ".tickets/DAEO-2bdu.md",
      "text": "  - 'S16 A miss is a result. A verdict below either limit stands as recorded. It is never run again, never re-scored to pass, and its labels are never changed after its figures exist. The spent set becomes a diagnostic set. An independent auditor classifies its misses by kind, counts only: never retrieved, ranked low, vocabulary, correct answer citing an unlisted place, other. The result goes to the repository''s owner with options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual with its cause. The store stays in service. The four settings of S10 change only by Gov OS''s owner''s decision (a CIT-P), never at the adopted repository. Verify: the result record''s miss section on a planted miss (stand-in figures); the runner refuses a set marked USED [DEC-1098 (1), DEC-1074 (1)-(2), DEC-1071 (1), DEC-1083 (2), DEC-954 Q9e, DEC-1070 (14)] [added, DEC-1099 (2); DEC-1098 (1)]'\n",
      "tokens": 240
    },
    {
      "id": "c7ffed82b541d17e34524d39",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S16 A miss is a result. A verdict below either limit stands as recorded. It is never run again, never re-scored to pass, and its labels are never changed after its figures exist. The spent set becomes a diagnostic set. An independent auditor classifies its misses by kind, counts only: never retrieved, ranked low, vocabulary, correct answer citing an unlisted place, other. The result goes to the repository''s owner with options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual with its cause. The store stays in service. The four settings of S10 change only by Gov OS''s owner''s decision (a CIT-P), never at the adopted repository. Verify: the result record''s miss section on a planted miss (stand-in figures); the runner refuses a set marked USED [DEC-1098 (1), DEC-1074 (1)-(2), DEC-1071 (1), DEC-1083 (2), DEC-954 Q9e, DEC-1070 (14)] [added, DEC-1098 (1)]'\n",
      "tokens": 236
    },
    {
      "id": "DAEO-n0wb",
      "path": ".tickets/DAEO-n0wb.md",
      "text": "67/79 with v456, drift 184 \u2192 0 unjoined); the engineer builds from it, the test designer from these KPIs and never from\nthe prototype's code. W2-54's `test_an_empty_retrieval_result_gives_one_packet` has its premise rewritten by its test\ndesigner (DEC-1074 (6)), with `Task:` this ticket, since the links now legitimately bring a record into it.\n\n**D9-FATES (DEC-1083):** Close formally at the lift (DEC-1083), lines met: 14 of 15, all but S6 (S1 to S5 at `0d33901a`; S7 to S10 and F5 at `3679ca0b`, acceptance 116/0, READY, DEC-1071's rule); met in part: S6 (14/15 at `88748f99`, green only at `3679ca0b`; its 1.2 s median is recorded nowhere, evidence:120); the pin carries them at re-pin window 4. The CTO closes it at the lift (P1-13).\n\n",
      "tokens": 186
    },
    {
      "id": "668e2014830b97333c15b0d2",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "text": "## Fixes made (only the two record files; each cites its source)\nDECISIONS-IN-FORCE.md\n- F1 header (lines 3-5): \"to DEC-1122 on 2026-11-10\" now also \"to DEC-1125 on 2026-11-11\". Source: register v0.509.\n- F2 new line after G-14's: DEC-1063 (ACT-G14b, `e02d55e40424`): a `class: coordination` ticket has as its own tests only\n  its own folder. Source: DEC-1063 (it had no line).\n- F3 DEC-1057 cited at R-11/R-8, O-6, R-6, R-12 and the restart classes; DEC-1058 at P-ACT-SPLIT (and the shared servers\n  now class (a), DEC-1104 (2)). Source: DEC-1057 (Changes, Decision (4), (6)), DEC-1058, DEC-1104 (2). Both had no id in\n  the list although their rules were there by name.\n- F4 marks of changed entries: DEC-1069 (12) by DEC-1076 (4) and DEC-1079; DEC-1070 (2)-(4) by DEC-1074 (1);\n  DEC-1071 (3) by DEC-1074 (4); DEC-1073's \"within 3 points\" now 5 (DEC-1074 (4)); DEC-1074 (3) by DEC-1076 (1) and\n  (7) O1 (A) by DEC-1087 (3); DEC-1075 (1) by DEC-1076 (1); DEC-1080 (2) by DEC-1081 (1) and its premise by DEC-1082 (0);\n  DEC-1083's K9 bar by DEC-1097 (1)(d) and DEC-1098, W2-66b/W2-90c by DEC-1084, W2-33's layers by DEC-1087 (13);\n",
      "tokens": 283
    },
    {
      "id": "efc2858f591d785da8d8f785",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md",
      "text": "5. **Proven before the product:** nothing here enters the product. \"Search again once\" is already a standing practice (DEC-1092 (1), DEC-1094 (2)), and the scripts stay in scratch.\n\n**Sources read:** E0-DECLARATION, E0-RESULT, E0B-RESULT, E1-DECLARATION (with its amendment), E1-PILOT-RESULT, E2-RESULT, E3-E5-DESIGN (with \"As run\"), E3-RESULT, E3-SA-RESULT, E5-RESULT, E2G-DECLARATION, E2G-RESULT, G1-PROFILE, PAT-1-RESULT, SEVEN-ANSWERS \u00a71 and \u00a77, D4B-SCORE-ONCE (the grid, version 6, the family re-score); DEC-1052, DEC-1070, DEC-1071, DEC-1074 to DEC-1078, DEC-1083 to DEC-1096; both path maps' `evaluation_sets`; the pin's `gov/retrieval/measure.py` and `gov/retrieve/command.py`; `drafts/d4b/` `e0_run.sh`, `e0_figures.py`, `e2_run.py`, `e3_run.py`, `e4_run.py`; CAP-10 in `docs/contract/CONTRACT_v4.md`.\n",
      "tokens": 203
    },
    {
      "id": "DAEO-rd0g",
      "path": ".tickets/DAEO-rd0g.md",
      "text": "  - The stacking test (a question needing about 24k tokens, retrieved in 8k batches, assembled complete, no duplicates by span hash), run once as a baseline [AR-10].\n  - Closes when the evidence record holds every measure per corpus and mode, with commands, versions and raw answers kept, and names the gaps that W2-32 will work on (at most three, chosen with the owner's\n    approval of the metric).\n  failure: []\n  moved:\n  - 'Corpora: the dev tiers; ~/workspace read-only; EXAMIN through this ticket''s own clone of the owner''s copy. W2-26''s clone sits under /tmp and may be gone. [moved to W2-15b, DEC-1083] (was S2)'\n  - 'Indexing time, peak RSS and incremental update per corpus, against DEC-078''s envelope [W2-L102, W2-L321]. [moved to W2-15b, DEC-1083] (was S4)'\n  - 'Decision-level retrieval after W2-03 [AR-10]. The thin-margin cases and the two dev queries without gold paths are fixed or named [W2-M342, W2-L322, W2-M340]. [moved to W2-15b, DEC-1083] (was S6)'\nprofile: FULL\nsources:\n- DEC-074\n- DEC-078\n- DEC-954\n- DEC-957\n- DEC-1055\n- DEC-1072\n- DEC-1083\n- DAEO-swdu\nest_loc: 100\nacceptance_tests:\n  judged_by: 'its class (WBS \u00a70 rule 1, W2-07): its evidence record'\ntrack: A\n",
      "tokens": 299
    },
    {
      "id": "e66d1b95499bcd365895a0ff",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "text": "- **Add to failure:** `'A link finding that stops or refuses an adoption; a link fixed by the tool in an adopted repository.'`\n- **Add to `allowed_paths`:** `template/governance/kernel/checks/link-integrity.yaml`.\n- **Add to `depends_on`:** W2-129.\n- **Add to `sources`:** DEC-1073, DEC-1072.\n\n**W2-98** (`DAEO-wi46`, open)\n- **Why:** product-spec records links in specs (\u00a75).\n- **Add to success:** `'Its Done when also checks the links: every decision and capability the spec rests on is in its decisions: or sources: front matter, each ACCEPTED; a PROPOSED one is an open question, never a rule [DEC-1073 (5)(c)]'`\n\n**W2-128** (P1-7's proposed templates ticket, not yet filed)\n- **Why:** (c) belongs in D-5's templates, as the owner suggests.\n- **When it is filed, add:**\n",
      "tokens": 194
    },
    {
      "id": "DAEO-2bdu",
      "path": ".tickets/DAEO-2bdu.md",
      "text": "  - 'S12 The repository''s own tuning set: about 80 questions, written blind under the rubric (docs/research/memory-measure-audit/RUBRIC.md, its version in force) by an independent writer, and cross-checked by an independent checker in at most two rounds. The checker lists every other place that states each answer. Both are sessions outside the retrieval work, opened by the owner''s operator. The writer never reads search results and never finds gold with the product''s search. The categories follow the fresh 80''s twelve (callers, code paraphrase, exact string, multi-file, decision, ticket, plan, contract or spec, kernel or template, history, failure memory, nonexistent id), mapped to the repository''s own domains. A category the repository has no domain for is dropped, and the drop is recorded. R5 applies: each domain at least 10 %, no subsystem over 25 %. There is at least one nonexistent-id question, scored apart. The set is split into two halves of 40: the first is used to choose fixes; the second is reported in counts only and never chooses. Source families (official copies) are declared in the path map. Verify: the set''s checks in the proof record (path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS) [DEC-1098 (1), DEC-1070 (2)-(3), DEC-1074 (4), DEC-1069 (5), DEC-1076 (5), DEC-1078 (4), DEC-1071 (5), DEC-1010] [added, DEC-1099 (2); DEC-1098 (1)]'\n",
      "tokens": 356
    },
    {
      "id": "e9f22a28ef54745975b3a586",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S12 The repository''s own tuning set: about 80 questions, written blind under the rubric (docs/research/memory-measure-audit/RUBRIC.md, its version in force) by an independent writer, and cross-checked by an independent checker in at most two rounds. The checker lists every other place that states each answer. Both are sessions outside the retrieval work, opened by the owner''s operator. The writer never reads search results and never finds gold with the product''s search. The categories follow the fresh 80''s twelve (callers, code paraphrase, exact string, multi-file, decision, ticket, plan, contract or spec, kernel or template, history, failure memory, nonexistent id), mapped to the repository''s own domains. A category the repository has no domain for is dropped, and the drop is recorded. R5 applies: each domain at least 10 %, no subsystem over 25 %. There is at least one nonexistent-id question, scored apart. The set is split into two halves of 40: the first is used to choose fixes; the second is reported in counts only and never chooses. Source families (official copies) are declared in the path map. Verify: the set''s checks in the proof record (path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS) [DEC-1098 (1), DEC-1070 (2)-(3), DEC-1074 (4), DEC-1069 (5), DEC-1076 (5), DEC-1078 (4), DEC-1071 (5), DEC-1010] [added, DEC-1098 (1)]'\n",
      "tokens": 352
    },
    {
      "id": "e11c480dbe67bab8cd5c5e1b",
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "text": "## 3. The links\n**W2-92 built** (merged `3679ca0b`, 11-05 16:55; **not in the live pin**; it rides window 4):\n\n| kind | count | what an agent sees |\n|---|---|---|\n| UNDER | 2,481 | |\n| CITES | 1,679 | |\n| AMENDS | 388 | |\n| OF_TASK | 381 | |\n| SUPERSEDES | 7 | |\n| **statements** | **3,171** | the census's, one for one |\n| one bounded hop | at most 12 records of 2 chunks each, after the closure's chunks | CITES, UNDER and OF_TASK followed out; AMENDS and SUPERSEDES followed in |\n| status in the bundle (S9) | every register item | its entry, status, changers, in force or not |\n| drift (S10) | 190 decisions current though stated changed (83 with no hint in their own entry) | before the links 0 reached a changer; after, 190 of 190 |\n\nIts measured effect on retrieval: 106 against 105 on the 138 (DEC-1071's measure). The links help an agent see\nstatus and changers, not hit@5.\n\n**Still open:**\n\n| item | what | state | date | needed before the experiments? |\n|---|---|---|---|---|\n| W2-129 (`DAEO-q7lk`) | `gov links`: a record's links listed | open, tests first | filed 11-06 | no |\n",
      "tokens": 273
    },
    {
      "id": "DAEO-0pyc",
      "path": ".tickets/DAEO-0pyc.md",
      "text": "  - 'S11 The candidate pool, v456 (DEC-1071 (2), approved for re-pin window 4 by DEC-1074 (5)): five query-time settings in governance/project/retrieval.yaml, each absent or 0 meaning today''s behaviour, the loader refusing an invalid value with CONFIG_INVALID naming the key: pool.meaning_uncut (the meaning route''s phrasings fused and not cut back to its depth), pool.route_depth (the keyword and meaning routes'' depth, 30 today), pool.rerank_depth (the first n fused candidates reranked once, in one pass under the padded request bound, and the pages cut from that order, in place of each page''s 20 reranked apart), pool.per_file_first10 (at most n chunks of one file in the first 10 of the final order, the rest kept after them) and pool.drop_nested (an item whose lines lie inside an earlier item''s of the same file dropped from the bundle); with 60, 40, 2 and both true, the product''s own path gives, on the D-4b measure clone with the stated links (e884675b), a hit@5 on the 138 within 2 of the research harness''s v456 with the question (the CTO''s measure, the hidden half in counts only), and a plain search''s median stays at or under the pin''s, measured by the CTO on the shared servers, the pin and the candidate side by side in re-pin window 4 [DEC-1071, DEC-1074, DEC-1065] [re-worded, DEC-1086 A]'\n",
      "tokens": 330
    },
    {
      "id": "DEC-1076",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-1076 \u2014 The 80 written and cross-checked by the 60's writer and checker sessions (DEC-1074 (3) amended); the writer varies its phrasing by role; D4B-MISSES decided: the reranker trial now, its choice rule on the 79 and the spent 59, then phrasing, then the embedder; extra sources listed by the checker\n- **Status:** ACCEPTED (owner, 2026-11-05 ~13:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-05)`) \u00b7 **Under:** DEC-1074, DEC-1075, DEC-1071, DEC-1070 \u00b7 **Changes:** DEC-1074 (3) (the writer and the checker), DEC-1075 (1) (the folders), DEC-1069 (12) (the trial's choice rule) \u00b7 **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-MISSES.md` (`c44257b2`), `ACT-MSET-3.md`, `ACT-MSET-4.md`\n- **Decision:**\n  - **(1) The same sessions (DEC-1074 (3) amended):** the 80 are written and cross-checked by the 60's writer and\n    checker sessions, not new ones. Their folders stay `~/gov-os-writer` and `~/gov-os-checker`; their settings gain\n    ACT-MSET-3 section 9's denials and the writer's write rule, never a denial of a session's own folder; the owner's\n",
      "tokens": 295
    },
    {
      "id": "e7014c81d079ab2652efcea6",
      "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md",
      "text": "## Approved restarts by class (owner, O-6)\nApproved (owner, DEC-1057 (4), D-3 answer 4, 2026-11-03): the five classes in `governance/project/orchestration/RESTART-CLASSES.md`\n(the shared embedder :11434, the query server :11435, the shared reranker service, the CTO's samplers and slot\nwatcher, the sentinel). Each is restarted by the CTO from its committed config, with its check, without an ACT; any\nother restart is an ACT.\n- DEC-1071 (2026-11-04, standing for the measure; its (3) changed by DEC-1074 (4): consistency within 5 points on\n  sets of about 80, and the spent 60 are no longer a confirmation set, DEC-1074 (1)): **structural fixes only**, never per question, from one structural\n  review (chunking, embedding, ranking, the graph). **The rule:** a structural fix is judged on **all 80 together**\n  (hit@5, then MRR), the hidden half in counts only. It is adopted if the 80 do not fall and the halves' gap does not\n  widen. **The proof is consistency:** the halves agree within 3 points; then memory-verdict (60) is measured once as\n  the confirmation (if it disagrees, to the owner first). **Then** all three rerankers on the three sets. The\n",
      "tokens": 289
    },
    {
      "id": "6b119e692246efb206db8d4d",
      "path": "src/gov/retrieval/pool.py",
      "text": "\"\"\"The candidate pool (W2-32 S11; DEC-1071 (2), DEC-1074 (5)): five query-time settings in\n``governance/project/retrieval.yaml``, each absent or 0 meaning today's behaviour exactly (``gov.config.loader``\nvalidates them, ``CONFIG_INVALID`` naming ``pool.<key>``):\n\n    pool:\n      meaning_uncut: true     # the meaning route's phrasings fused and not cut back to its depth\n      route_depth: 60         # the keyword and meaning routes' depth (``lexical.TOP_K``, ``semantic.TOP_K``: 30)\n      rerank_depth: 40        # the first 40 fused candidates reranked once; the pages cut from that one order\n      per_file_first10: 2     # at most 2 chunks of one file in the first 10 of the final order, the rest after\n      drop_nested: true       # an item whose lines lie inside an earlier item's of the same file left out\n\nThe measured form is the research harness's v456 (``night/harness/rx.py``: ``sem_uncut``, ``sem_k``/``lex_k``,\n``depth``, ``perfile``, ``dedup``); ``retrieve`` builds the same behaviour into its own path. The depth is passed to\neach search (``top_k``), never set on a module: one search's setting never reaches another's.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport hashlib\n",
      "tokens": 299
    },
    {
      "id": "5c851ca74091b3efebebea52",
      "path": "tests/acceptance/W2-32/README.md",
      "text": "## Round 21 (S11: the candidate pool, v456; DEC-1071 (2), DEC-1074 (5))\n\n`test_w2_32_s11_pool.py` (35 cases from 14 functions) with `w2_32_pool.py` (the planted stores and helpers), written\nfrom S11's text alone: never the research harness, never W2-32's new code; the integrated code at `0748bdd6`\n(integrate merged) read for today's interfaces (DEC-963).\n\n- **The settings this suite assumes** (S11's names): a `pool` block in `governance/project/retrieval.yaml`, beside\n  `routing`: `meaning_uncut` and `drop_nested` true or false; `route_depth`, `rerank_depth` and `per_file_first10`\n  whole numbers; each absent or 0 (false) today's behaviour; an invalid value `CONFIG_INVALID` with the full key\n  (`pool.route_depth`) in the message. The file is written uncommitted, in a namespace kept out of the index\n  (`w2_32_methods.plant`), so no setting changes an indexed file; the planted path map has no authority order.\n- **Today, the setting absent:** each case's reference is the same call on the same store with the setting absent\n  (for the together cases: `V456` without that one setting), so every expected value is derived from the product's\n",
      "tokens": 288
    }
  ],
  "supplementary_query": "W2-88a The adopt skill states Wave 0's memory practice in order, and the Verify pass (W2-88's and W2-174's kernel skill text)\nS17 The Wave 0 order in the adopt skill: A9's step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1099 (2); DEC-1098 (1)]\n{'line': \"The adopt skill, in the kernel copy and the two generated-source copies, states the pass: when it runs (for a ticket about to launch, not for the whole tracker), who writes the clauses (a product-spec session), what checks them (the tool, the ticket's test designer, the auditor's sample), and that the owner approves the rule once [DEC-1130, DEC-1083]\", 'verify': 'tests/unit/adopt/test_w2_174_skill.py: the three files carry the section `Verify clauses for adopted tickets` with the four statements, and the three copies are equal in that section'}\nThe CIT-P record (docs/changes/W2-88a-CIT-P.md) gives the kernel skill's sha256 before and after, the lines added or removed, the independent review and the owner's approval of the bytes before the merge; the two .rulesync copies equal the kernel copy in the changed sections Verify: the record holds both hashes and the review's verdict; a diff of the three files shows the same changed sections [CAP-33, DEC-1116]",
  "further_batch": [
    {
      "id": "cb8806879f65474234ed6d41",
      "path": "tests/acceptance/W2-32/README.md"
    },
    {
      "id": "c9c26917302d28ac64927692",
      "path": "tests/acceptance/W2-32/test_w2_32_s11_pool.py"
    },
    {
      "id": "77faf48bef7558916bb387f4",
      "path": "tests/acceptance/W2-32/w2_32_pool.py"
    },
    {
      "id": "e8bb6351a64ace7bfb5d6e0b",
      "path": "tests/unit/retrieval/test_w2_32_pool.py"
    },
    {
      "id": "DEC-1070",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "DEC-1070",
      "path": "docs/DECISION_REGISTER.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DAEO-xxxx",
          "path": "governance/project/orchestration/packages/ADOPT-VERIFY-1/TICKET-DRAFT.md"
        },
        {
          "id": "DEC-1074",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "373357077b247cf363833ae8",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "DAEO-2bdu",
          "path": ".tickets/DAEO-2bdu.md"
        },
        {
          "id": "DAEO-n0wb",
          "path": ".tickets/DAEO-n0wb.md"
        },
        {
          "id": "DAEO-n0wb",
          "path": ".tickets/DAEO-n0wb.md"
        },
        {
          "id": "1ab780b262b811cbbe6ef6d8",
          "path": "docs/changes/W2-92-evidence.md"
        },
        {
          "id": "DEC-1073",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "dc4afdccedefaaebf4f7512e",
          "path": "docs/changes/W2-92-evidence.md"
        },
        {
          "id": "DRAFT-W2-129",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-129-gov-links.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DEC-1072",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DAEO-q7lk",
          "path": ".tickets/DAEO-q7lk.md"
        },
        {
          "id": "a1b21b7e769dcbb6efa7924f",
          "path": "docs/research/D4B-link-census.md"
        },
        {
          "id": "1d5208160407692b68dbeca6",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
        },
        {
          "id": "5c620c3a6b763964b25cc914",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
        },
        {
          "id": "91e142181324abe2f409150a",
          "path": "tests/acceptance/W2-92/test_w2_92_hop.py"
        },
        {
          "id": "993f4315ffcceae303003736",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "DAEO-q7lk",
          "path": ".tickets/DAEO-q7lk.md"
        },
        {
          "id": "301dc852a348c005826fa415",
          "path": "docs/research/W2-92-memory-measure.md"
        },
        {
          "id": "DRAFT-W2-129",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-129-gov-links.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "42b9b621c79b085c507a09a8",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
        },
        {
          "id": "cab7fa13f5e05fe2893ddcd2",
          "path": "src/gov/store/loader.py"
        },
        {
          "id": "0e28079969af60fb5bf83e38",
          "path": "tests/unit/store/test_w2_92_links.py"
        },
        {
          "id": "ADR-0002",
          "path": "docs/adr/ADR-0002-architecture-and-stack.md"
        },
        {
          "id": "2aa97e8505d0c25fe3a65616",
          "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft"
        },
        {
          "id": "11b688c21b3cff5c55e3dd49",
          "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md"
        },
        {
          "id": "DEC-1071",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "edd84696d44a8e9a77713126",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md"
        },
        {
          "id": "DAEO-0pyc",
          "path": ".tickets/DAEO-0pyc.md"
        },
        {
          "id": "DAEO-2bdu",
          "path": ".tickets/DAEO-2bdu.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "c7ffed82b541d17e34524d39",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "DAEO-n0wb",
          "path": ".tickets/DAEO-n0wb.md"
        },
        {
          "id": "668e2014830b97333c15b0d2",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md"
        },
        {
          "id": "efc2858f591d785da8d8f785",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md"
        },
        {
          "id": "DAEO-rd0g",
          "path": ".tickets/DAEO-rd0g.md"
        },
        {
          "id": "e66d1b95499bcd365895a0ff",
          "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md"
        },
        {
          "id": "DAEO-2bdu",
          "path": ".tickets/DAEO-2bdu.md"
        },
        {
          "id": "e9f22a28ef54745975b3a586",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "e11c480dbe67bab8cd5c5e1b",
          "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md"
        },
        {
          "id": "DAEO-0pyc",
          "path": ".tickets/DAEO-0pyc.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DEC-1076",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "e7014c81d079ab2652efcea6",
          "path": "governance/project/orchestration/DECISIONS-IN-FORCE.md"
        },
        {
          "id": "6b119e692246efb206db8d4d",
          "path": "src/gov/retrieval/pool.py"
        },
        {
          "id": "5c851ca74091b3efebebea52",
          "path": "tests/acceptance/W2-32/README.md"
        },
        {
          "id": "cb8806879f65474234ed6d41",
          "path": "tests/acceptance/W2-32/README.md"
        },
        {
          "id": "c9c26917302d28ac64927692",
          "path": "tests/acceptance/W2-32/test_w2_32_s11_pool.py"
        },
        {
          "id": "77faf48bef7558916bb387f4",
          "path": "tests/acceptance/W2-32/w2_32_pool.py"
        },
        {
          "id": "e8bb6351a64ace7bfb5d6e0b",
          "path": "tests/unit/retrieval/test_w2_32_pool.py"
        },
        {
          "id": "DEC-1070",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-1070",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "77faf48bef7558916bb387f4",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1070",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-1070",
      "reason": "budget exceeded"
    },
    {
      "id": "c9c26917302d28ac64927692",
      "reason": "budget exceeded"
    },
    {
      "id": "cb8806879f65474234ed6d41",
      "reason": "budget exceeded"
    },
    {
      "id": "e8bb6351a64ace7bfb5d6e0b",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-pg6i): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 19755,
  "budget": {
    "limit": 20000,
    "used": 19755
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-045",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "cfa82381eae75a24a75db02fb92248db959dc87e185de6eba0724b22dc17157f"
}
