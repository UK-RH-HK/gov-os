{
  "ticket": "DAEO-h2k3",
  "ticket_text": "---\nid: DAEO-h2k3\nstatus: in_progress\ndeps: [DAEO-m1u3]\nlinks: []\ncreated: 2026-10-29T15:55:50Z\ntype: task\npriority: 1\nassignee: independent-test-designer\nexternal-ref: W2-61h\ntags: [wave-2, audit, evaluation, held-out, standard, keystone-4]\nwbs_id: W2-61h\ntitle: 'W2-61''s enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session'\nclass: audit\nstate_class: AUTHORITATIVE\nrole: independent-test-designer\ndepends_on: [DAEO-m1u3]\nallowed_paths:\n- fixtures/evaluation/memory-retrieval/visible/q21.yaml\n- fixtures/evaluation/memory-retrieval/visible/q22.yaml\n- fixtures/evaluation/memory-retrieval/visible/q23.yaml\n- fixtures/evaluation/memory-retrieval/visible/q24.yaml\n- src/gov/retrieval/measure.py\n- tests/unit/retrieval/test_w2_61h_families*\n- tests/unit/retrieval/test_w2_61h_anchor*\n- governance/project/path-map.yaml\nkpis:\n  success:\n  - 'Twenty-eight new questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner''s operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084]'\n  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]'\n  - 'The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40''s table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084]'\n  - 'Every gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]'\n  - 'The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8]'\n  - 'The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)]'\n  - 'S7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract''s `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source''s family counts as a hit on that source when its text holds the gold span''s text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure''s per-question line; with no family declared, every score is as today; a run''s kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)]'\n  - 'S8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source''s block again in the commit it measures (the block read at the source''s own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]'\n  failure:\n  - A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.\n  - 'A measure that writes a label file or the sets root, or scores a commit against another commit''s lines.'\n  - A question copied from or paraphrasing lens B's visible 20.\n  - A gold source that does not hold its answer.\n  - 'A family hit counted on a member whose text does not hold the gold span''s text.'\nprofile: STANDARD\nsources:\n- DEC-828\n- DEC-820\n- DEC-845\n- DEC-833\n- DEC-873\n- DEC-941\n- DEC-954\n- DEC-957\n- DEC-950\n- DEC-1052\n- DEC-1055\n- DEC-1068\n- DEC-1069\n- DEC-1070\n- DEC-1074\n- DEC-1078\n- DEC-1079\n- DEC-1083\n- DEC-1084\n- DEC-866\nest_loc: 0\nacceptance_tests:\n  path: tests/acceptance/W2-61h/\n  author: independent-test-designer (MR-3); form only (count, fields, sources exist), never printing a question or an answer\ntrack: A\nlist_rows: []\n---\n# W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources\n\n**Re-scoped by DEC-954 Q9a; the size confirmed by DEC-957:** 48 questions with lens B's 20 (24 visible, 24 hidden); K9's \"memory proven\" is judged on the hidden half, at least 21 of 24 hit@5, against the owner's target of 95 %. Est. 12 to 14 lead-hours (MEMORY-SPEC-MAP B.2).\n\nCompanion to W2-61 (DEC-941). W2-61's engineer writes the measure and runs the visible half's baseline. The engineer is a measured role (`measures: roles: [engineer, research]` in the path map's `evaluation_sets.memory-retrieval`), so the hidden half is written here, by an independent auditor whose role is not measured, in a session the orchestrator starts, never a retrieval ticket's lead.\n\n- **Why:** a measure tuned on its own questions overstates itself. The hidden half keeps W2-61's figures honest across the memory chain (DEC-828 item 3, DEC-820 (d)).\n- **Form:** the auditor reads W2-61's script's input form once it is merged (`src/gov/retrieval/measure.py` and its README or docstring) and writes in that form. Before then, one YAML file per question with `question`, `gold_answer` and `sources` (path plus heading or line).\n- **After it:** the orchestrator, which no set measures, runs W2-61's script on the hidden half and records the scores only (never the questions or answers) beside the visible baseline in `docs/research/W2-61-baseline.md`.\n- **No path map change:** the hidden folder and its refusal are already in the path map (`evaluation_sets.memory-retrieval`, W2-58).\n\n**DEC-1069 (owner, 2026-11-04 ~13:00):** the set grows to about 40 per half (DEC-1009 amended); **this ticket's category quotas are amended to fit R5** (each governing domain, the plan, tickets, the Contract, decisions and code, at least 10 % of each half; no subsystem above 25 %; at least 3 on failure and lesson memory, at least 2 on the kernel's skills or roles), as stated in `docs/research/memory-measure-audit/RUBRIC.md`'s R5 for a 40-question half; R11 (no answer that changes with ordinary work unless its gold is computed at the measured head) and R1.3 (test-harness code never governs a code fact, except for a question about the harness) apply. The hidden 16 new questions and the corrections of h03 and h08 are written by the owner's operator as the independent checker (ACT-HLABEL-2, ACT-HNEW-1), outside the guard; nothing about them reaches the CTO's session.\n\n**DEC-1079 placed here (CTO, 2026-11-06):** S7, the source families, is DEC-1078 (4)'s rubric row built into the\nmeasure's code, here because W2-61 (the measure's ticket) is closed and this ticket holds the measure's sets. Tests\nfirst (an independent test designer from S7's text, on a planted repository and planted sets), then an engineer; the\nCTO re-scores every kept run (`~/gov-os-eval/runs/`) once it lands, counts only.\n\n**S7's interface (CTO, 2026-11-06, delegated P3, from the designer's choices):** (1) `evaluation_families:` is a\ntop-level key of the path map: a map of a family's name to the list of its member path globs; (2) kept outputs are\nre-scored with `python3 -m gov.retrieval.measure <set> ... --kept <dir>`, where `<dir>` holds the kept ranked outputs\nin call order (`00001.json` \u2026, beside `.n` and `.n.lock`), and the output is the measure's own; (3) a family hit is\nnamed in the question's line by the member's path and the word \"family\", the line keeping its present pattern.\n\n**Role changed to engineer (CTO, 2026-11-06, delegated P3):** W2-61h's remaining work is S7's code; `gov launch`\nstarts an engineer only on an engineer's ticket, and a test designer launches on an engineer's ticket as before. The\nguard so keeps S7's engineer from this ticket's own acceptance tests (DEC-1056).\n\n**Role restored to independent-test-designer (CTO, 2026-11-06, the same day):** S2 requires this ticket's questions to\ncome from no measured role, and its acceptance case checks the ticket's role front matter; the engineer role broke it.\nS7's code was built under this ticket's id while the role read engineer (`ab18f6f5`, launched 09:40); the role is\nback, and the case passes again. Any later engineering on the measure goes under a ticket of its own.\n\n**S8 placed here (CTO, 2026-11-06, DEC-1084):** the measure re-anchors in memory, never rewriting the sets root\n(h23 was re-anchored on 11-05 at 14:40 to another clone's commit by `repin_gold.py` and so misjudged on the score-once\nclone). Tests first, from S8's text, by an independent test designer. The code, by the note above, goes under an\nengineer's ticket of its own, which the CTO asks the owner to file.\n",
  "authority": [
    {
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    },
    {
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-873",
      "sha256": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "reason": "declared in sources",
      "tokens": 627
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-950",
      "sha256": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "reason": "declared in sources",
      "tokens": 571
    },
    {
      "id": "DEC-1052",
      "sha256": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "reason": "declared in sources",
      "tokens": 1880
    },
    {
      "id": "DEC-1055",
      "sha256": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "reason": "declared in sources",
      "tokens": 759
    },
    {
      "id": "DEC-1068",
      "sha256": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "reason": "declared in sources",
      "tokens": 983
    },
    {
      "id": "DEC-1069",
      "sha256": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "reason": "declared in sources",
      "tokens": 1134
    },
    {
      "id": "DEC-1070",
      "sha256": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "reason": "declared in sources",
      "tokens": 1245
    },
    {
      "id": "DEC-1074",
      "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "reason": "declared in sources",
      "tokens": 900
    },
    {
      "id": "DEC-1078",
      "sha256": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
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
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "mandatory": [
    {
      "id": "DEC-828",
      "sha256": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "607fe3327303796890c09db6bfccd54490d42ea6ffd2272ab868d955d2fa117b",
      "reason": "declared in sources",
      "tokens": 275
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    },
    {
      "id": "DEC-845",
      "sha256": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "774f337ea77577463ad2a36212e4eba845367298c4d9e6a11c19e5cb99d344c2",
      "reason": "declared in sources",
      "tokens": 167
    },
    {
      "id": "DEC-833",
      "sha256": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "22cb19bac1b13c1c54ea69cdadb8a8b4cfa69f6429529ab51525396244825a3b",
      "reason": "declared in sources",
      "tokens": 268
    },
    {
      "id": "DEC-873",
      "sha256": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "181572534ff51dede868f2652fb719dcbcc26479c8c9cbe4937b9c55735043ce",
      "reason": "declared in sources",
      "tokens": 627
    },
    {
      "id": "DEC-941",
      "sha256": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c9ed774f62d1b8ac2d0d20f9e79bc9ffcce5afe683738674788c9e7bad3bc89b",
      "reason": "declared in sources",
      "tokens": 1640
    },
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-957",
      "sha256": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "af187984bc2a02f1a8230fa23b75f76a95f3d0626d197b55bf84e82e420b43e5",
      "reason": "declared in sources",
      "tokens": 2056
    },
    {
      "id": "DEC-950",
      "sha256": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4dea9a51250bcabfa787e64751b39d45cdbe1101bdbb127f418797d2e2e70080",
      "reason": "declared in sources",
      "tokens": 571
    },
    {
      "id": "DEC-1052",
      "sha256": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0074d4e1c3f918d264c472e2090276ee374784efa4ccecd568e8deb627233f14",
      "reason": "declared in sources",
      "tokens": 1880
    },
    {
      "id": "DEC-1055",
      "sha256": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0735718d54dfe52cea9fa28517cd4255d41303342c4bc071d6afdd9cff919d87",
      "reason": "declared in sources",
      "tokens": 759
    },
    {
      "id": "DEC-1068",
      "sha256": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c4e2ef93f3fb80e51a5de61a1cb03e3d0ee599fbfa06ae17948e67c729c8ed30",
      "reason": "declared in sources",
      "tokens": 983
    },
    {
      "id": "DEC-1069",
      "sha256": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "daece4f80d526eb3fa032162690b307b49a12a600fc11ab87ae5bda6f6625ba8",
      "reason": "declared in sources",
      "tokens": 1134
    },
    {
      "id": "DEC-1070",
      "sha256": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "714e11e5a94d3a4a3e9982df7a19a1a6ffbfb08dfabbb4a33e8d87fd137cdb29",
      "reason": "declared in sources",
      "tokens": 1245
    },
    {
      "id": "DEC-1074",
      "sha256": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "a3c09b10aa9e1e02957b9bfe37f8129899708b7d823cc1f1672458e34cc8b34c",
      "reason": "declared in sources",
      "tokens": 900
    },
    {
      "id": "DEC-1078",
      "sha256": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3e3221df551b2d91980e8df7636f7c1d944f1470d25d95364409d772244f0675",
      "reason": "declared in sources",
      "tokens": 642
    },
    {
      "id": "DEC-1079",
      "sha256": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1d6da7edf708a0b7543141e997baf326f5a76491761e807f1e48f42fe4dbfefd",
      "reason": "declared in sources",
      "tokens": 866
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1084",
      "sha256": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "01a357165613caa2238918c60e26bc6223bd1acf500bcf44133eb3e69e0ff373",
      "reason": "declared in sources",
      "tokens": 750
    },
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
      "id": "DAEO-m1u3",
      "sha256": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "af422e63bd4f849a3fc9953146159280ccea1cdecd0e5975d9c5def429471a9f",
      "reason": "declared in sources",
      "tokens": 763
    }
  ],
  "supplementary": [
    {
      "id": "621f5faae9b6d6055c0c909e",
      "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py",
      "text": "\"\"\"W2-61h (DAEO-h2k3): the 4 new visible questions, ``q21.yaml`` to ``q24.yaml`` -- KPI lines S1, S2, S3 (the\nvisible share), S4, F2 and F3.\n\nS1: \"Twenty-eight new questions ... in the form W2-61's visible half takes; after writing, a recorded seeded draw,\nstratified by category, sends 4 to the visible half ... (fixtures/evaluation/memory-retrieval/visible/q21.yaml to\nq24.yaml in the repository ...)\". S4: \"Every gold source exists at the commit the auditor reads and holds the answer,\ncited by path and heading or line\". F2: \"A question copied from or paraphrasing lens B's visible 20\". F3: \"A gold\nsource that does not hold its answer\". S2: \"Written by a session independent of the retrieval tickets\", judged from\nthe record: the commits' ``Role`` trailers (the CTO's decision of 2026-11-03, P2: by the role, not the ``Task``,\nsince D-4's cut rewrote these tests under the coordination ticket's id).\n\nThese cases read only this tree's tracked files and git record; they never open the sets root.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\nimport yaml\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n\n",
      "tokens": 296
    },
    {
      "id": "fb96a256eb4278b964203cca",
      "path": "tests/acceptance/W2-61h/test_w2_61h_families.py",
      "text": "\"\"\"W2-61h, KPI S7 and failure line 4 -- source families in the measure (DAEO-h2k3; DEC-1078 (4), DEC-1079,\nDEC-1068 (4)).\n\nS7, as the ticket states it: the measure counts a gold source and its official copies as one **family**. The\nfamilies are declared in the path map (``evaluation_families:``, each a list of member path globs). An evidence item\nin another member of the gold source's family counts as a hit on that source when **its text holds the gold span's\ntext** (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the\nmeasure's per-question line; with no family declared, every score is as today; a run's kept outputs are re-scored\nwith families without running again. Failure line 4: a family hit counted on a member whose text does not hold the\ngold span's text.\n\nEverything here is planted in ``tmp_path``: a measured root (which is also the sets root) with its own path map, its\nown set ``planted`` and its own questions, and a stand-in ``gov`` that returns chosen evidence (no store, no model,\nno network; never this repository's sets, never ``~/gov-os-eval``). The measure is run as a command, from this\ntree's ``src``.\n\n",
      "tokens": 298
    },
    {
      "id": "92d02c0f44b56ac8af8ac345",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "Cases: 15 in the full run, 9 in `breadth`, 0 in `lifted` (S2's planted case added by the CTO's decision of 2026-11-03, P2: its engineer's row in the full run, its six others in `breadth`).\n\n| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |\n|---|---|---|\n| S1: Twenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources an answer... | `test_w2_61h_visible_new.py::test_s1_the_visible_four_are_the_stratified_draw_s_share`, `test_w2_61h_visible_new.py::test_s1_the_four_new_visible_questions_are_in_the_question_form`, `test_w2_61h_hidden_form.py::test_s1_the_hidden_half_holds_40_question_files` | the ticket's words |\n| S2: Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61's engineer, W2-64, W2... | `test_w2_61h_visible_new.py::test_s2_the_new_questions_and_these_tests_come_from_no_measured_role`, `test_w2_61h_visible_new.py::test_s2_judges_the_role_on_a_planted_commit` (1 of 7: the engineer's row) | the ticket's words (the planted case added by the CTO's decision of 2026-11-03, P2) |\n",
      "tokens": 297
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "- The size, the spread and the time cost are in `.gov-runtime/scratch/orchestrator/drafts/plan-dec954/MEMORY-SPEC-MAP.md` part B.\n- **Why:** W2-61's engineer is a measured role, so the hidden half of the standing measure is written by an independent auditor in a ticket of its own, started by the orchestrator, never by a retrieval ticket's lead.\n- **Starts:** beside W2-61, on 2026-10-29. No path map change: the hidden folder and its refusal are already there (`evaluation_sets.memory-retrieval`, W2-58).\n- **Allowed paths:** `fixtures/evaluation/memory-retrieval/hidden/**`.\n- **KPIs, success:**\n  - 20 hidden questions with gold answers and governing sources, in the visible half's form and spread, none paraphrasing lens B's 20;\n  - every gold source holds its answer at the commit read;\n  - nothing hidden written or quoted outside the hidden folder.\n- **KPIs, failure:**\n  - a hidden question or answer readable by a measured role by an honest route;\n  - a gold source that does not hold its answer.\n\n",
      "tokens": 252
    },
    {
      "id": "6262171d2757882181c97d4e",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| F1: A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. | `test_w2_61h_hidden_form.py::test_s1_the_hidden_half_holds_40_question_files`, `test_w2_61h_hidden_form.py::test_s1_every_hidden_question_is_in_the_question_form`, `test_w2_61h_hidden_form.py::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure` | the ticket's words |\n| F2: A question copied from or paraphrasing lens B's visible 20. | `test_w2_61h_visible_new.py::test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`, `test_w2_61h_hidden_form.py::test_f2_no_hidden_question_repeats_a_visible_one` | the ticket's words |\n| F3: A gold source that does not hold its answer. | `test_w2_61h_visible_new.py::test_f3_each_new_visible_gold_source_holds_its_answer`, `test_w2_61h_hidden_form.py::test_s4_f3_every_hidden_gold_source_resolves_at_head`, `test_w2_61h_visible_new.py::test_s4_f3_every_new_visible_gold_source_resolves_at_head` | the ticket's words |\n\n",
      "tokens": 252
    },
    {
      "id": "82de7c78949cb8b459c68034",
      "path": "governance/project/path-map.yaml",
      "text": "  # planted-problem variants per synthetic repository, written blind by the walled writer (brief PROVING-GROUND-writer),\n  # kept under the sets root. The visible half is W2-81's own questions folder; the runner reads the hidden half from\n  # its --hidden folder. Every role but the orchestrator is refused the hidden half.\n  adoption-proving-ground:\n    visible: [\"tests/acceptance/W2-81/questions/**\"]\n    hidden: [\"fixtures/evaluation/adoption-proving-ground/hidden/**\"]\n    measures:\n      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]\n# The source families (DEC-1078 (4), DEC-1079; W2-61h S7): a gold source and its official copies, each family a list\n# of member path globs. The memory measure (gov.retrieval.measure) counts an evidence item in another member of a gold\n# source's family as a hit on that source only when the item's text holds the gold span's text (whitespace and\n# Markdown or YAML formatting normalised), never by its path alone.\nevaluation_families:\n  contract: [\"docs/contract/CONTRACT_v4.md\", \"docs/contract/contract.yaml\",\n             \"docs/contract/capabilities/*.md\", \"docs/contract/master-rules/*.md\"]\n",
      "tokens": 295
    },
    {
      "id": "306a0ee65f3b854674456ae5",
      "path": "tests/unit/retrieval/test_w2_61h_families.py",
      "text": "def test_this_repository_declares_its_families():\n    root = Path(__file__).resolve().parents[3]\n    declared = {f.reason: f for f in measure.families(root, root)}\n    assert set(declared) >= {\"contract\", \"kernel\", \"agents\"}\n    for name, paths in {\"contract\": [\"docs/contract/CONTRACT_v4.md\", \"docs/contract/contract.yaml\",\n                                     \"docs/contract/capabilities/CAP-10.a.md\", \"docs/contract/master-rules/MR-1.md\"],\n                        \"kernel\": [\"template/governance/kernel/roles/engineer.md\", \".claude/agents/engineer.md\",\n                                   \".rulesync/subagents/engineer.md\"],\n                        \"agents\": [\"AGENTS.md\", \"CLAUDE.md\"]}.items():\n        assert all(declared[name].match(p) for p in paths), name\n    assert not declared[\"contract\"].match(\"docs/contract/SOURCE_MAP.csv\")\n    lines = (root / \"governance/project/path-map.yaml\").read_text().splitlines()\n    at = lines.index(\"evaluation_families:\")\n    comment = []\n    while lines[at - 1 - len(comment)].startswith(\"#\"):\n        comment.append(lines[at - 1 - len(comment)])\n    assert \"DEC-1078 (4)\" in \" \".join(comment)\n",
      "tokens": 284
    },
    {
      "id": "db28e269fd9bebcf7aabad94",
      "path": "tests/acceptance/W2-171/README.md",
      "text": "  (`w2_171_world.SRC`); a session fixture fails the run when a child would import `gov` from elsewhere.\n- **Everything is planted under pytest's `tmp_path`:** the sets root (its own path map with `memory-verdict-2`,\n  `memory-retrieval` and an earlier audit's set among comments, and an `evaluation_families` block), the repository (three\n  commits), the store (a planted file whose sha256 `declare` records), the launch log, the set of 40, the control set\n  (`memory-retrieval/visible`, 40 questions, gold files `docs/ctl/`), the pool, the fake `gov`, the fake `claude`, the stub\n  servers, and `HOME`. W2-170's own `preflight` and `void` prepare the state `measure` starts from (`measure` calls\n  `declare`, Interface 1): a world that W2-170's checks accept (36 to 40 questions; see the reading below). Never the real\n  sets root (`~/gov-os-eval`), the real runs folder, a real search, a real model call or a GPU.\n- **The planted `gov`** (`--gov`, a script in a `pin-0123456789ab` folder; Interface 6) answers `gov retrieve ... --json`\n  from a plan: per question text, the ranked calls (a gold item at a planted position, in one call or two or three with\n",
      "tokens": 290
    },
    {
      "id": "0f9bf3aeb3b8949dfd823522",
      "path": "tests/acceptance/W2-171/w2_171_world.py",
      "text": "      roles: [engineer, research]\n\"\"\"\nROLES = [\"engineer\", \"research\", \"product-spec\", \"independent-test-designer\", \"independent-auditor\"]\nSETS_MAP = f\"\"\"# The sets root's own path map (planted for W2-171's acceptance tests).\nversion: 1\nevaluation_sets:\n  # memory-verdict-2, the verdict set of 80, in its shape\n  memory-verdict-2:\n    visible: []\n    hidden: [\"fixtures/evaluation/memory-verdict-2/hidden/**\"]\n    measures:\n      roles: [{', '.join(ROLES)}]\n  # the standing control set (the visible 40)\n  memory-retrieval:\n    visible: [\"fixtures/evaluation/memory-retrieval/visible/**\"]\n    hidden: [\"fixtures/evaluation/memory-retrieval/hidden/**\"]\n    measures:\n      roles: [{', '.join(ROLES)}]\n  # an earlier audit's set, among comments\n  {EARLIER}:\n    visible: []\n    hidden: [\"fixtures/evaluation/{EARLIER}/hidden/**\"]\n    measures:\n      roles: [{', '.join(ROLES)}]\n  # the last comment inside the block\n\n# a comment between the blocks\nevaluation_families:\n  kernel: [\"template/governance/kernel/**\"]\n\"\"\"\nCONTROL_N = 40\nCONTROL_FILES = [f\"docs/ctl/c{k:02d}.md\" for k in range(1, CONTROL_N + 1)]\n\n\n",
      "tokens": 277
    },
    {
      "id": "DAEO-qzca",
      "path": ".tickets/DAEO-qzca.md",
      "text": "# W2-151 MR-1 to MR-6 regenerated from contract.yaml\n\nCard: DEC-1074 (8)'s \"MR-1..MR-6 status row\", and the W2-130 sitting's row to D-6 part 2 (DECIDED-NOT-DONE row 24).\n`02ee7e33` (DEC-623) generated one record per master rule from `contract.yaml` so the ids resolve; they still say\n`status: PROPOSED` and \"Contract v4, version 4.1\", while `contract.yaml` says `ACCEPTED`, version 4.2. `gov links`\nreports six STATUS_CONFLICTs, owner product-spec (W2-129's settled point (10)).\n\n- **Why a new ticket (checked):** no open ticket holds `docs/contract/master-rules/`; W2-139 holds `contract.yaml`,\n  `CONTRACT_v4.md` and `capabilities/**`, not these records; D-5's list carried the row but no ticket of D-5 holds the\n  path. This ticket takes the row out of D-5's list.\n- **Order:** after W2-139 lands if it changes a master rule's text in `contract.yaml`; otherwise now (a re-run after\n  W2-139 costs minutes).\n- **Plan:** `governance/project/orchestration/packages/LIFT-1/D6-PART2.md` item C: a product-spec worker, one review.\n\n**Filed 2026-11-09 by the CTO (DEC-1109 (2)).**\n",
      "tokens": 270
    },
    {
      "id": "10a9349768c43af9e76cd6d2",
      "path": "governance/project/orchestration/packages/SETUP-A-BAR.md",
      "text": "| 7 | the `tests` entry's own line, \"tests/acceptance by the independent test designer only (MR-3)\", with the `acceptance_exemptions` list | every role but the test designer | writes | `tests/acceptance/**` in any tree of this repository |\n\nRows 1 to 6 are blocks the guard parses. **Row 7 is prose in the path map that no code parses; I include it on purpose** (it is the guard's\nrule 1, the one the 53 let-through cases come from, and the path map does name it). If you do not want prose to count, drop row 7 (variant V1\nin section 2); the tests rule then stays outside the bar.\n\n**Not constraint-bearing, so covering nothing:** the fourteen `namespaces` (each lists every role as permitted everywhere), `capabilities`,\n`policies`, `systems`, the three ratchet lists, `evaluation_families`, `retrieval_authority`. **Not in the path map at all:** secrets and keys\n(rule 3), the held-out list (a separate file the guard loads), installs and sudo (rule 4), `rm` (the catastrophic rule), a reviewer's allowed\nrecord paths (rule 5), write scope (DEC-820 (4): the live guard has no such rule; allowed paths live in the tickets), an engineer's wide\n",
      "tokens": 286
    },
    {
      "id": "2f2de6f274780a66a788abcf",
      "path": "governance/project/orchestration/reviews/D10-W2-92-review.md",
      "text": "## Answers to the checks\n\n**1. No expectation lowered: yes, none is lowered.**\n- **Dropped:** `decision_citations_base`, `acceptance_exemptions`, `close_timeout`, `accepted_reds`, `load_sensitive`, `evaluation_sets`, `evaluation_families`, `role_paths`, `sets_root_hidden`, `session_hidden` and `write_refused`. Each system's `where`/`reason` is replaced. `retrieval_authority` was already removed before this revision.\n- **Not read by these cases:** none of the dropped blocks is read on any path these cases call (see the evidence).\n- **Unchanged reads:** what the cases do read is the same as before: the `everything` namespace, `decision_register`, and `capabilities` copied whole.\n- **The only channel left:** the map's own text in the planted index. The new map's content is a subset of the old map's, so it can only remove matches, and it removes them only from the \"who calls \u2026\" answers.\n- **By case family:**\n  - The marina (`links_corpus()`), the hop, stated links and status compare the integrated code with head on one marina, judged by record text. Stated links read only the new store tables, built from front matter and the register.\n",
      "tokens": 288
    },
    {
      "id": "df05e2995d286b45fdfe9a6d",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "## S7 and F4: source families (DEC-1078 (4), DEC-1079; DEC-1068 (4))\n\n`test_w2_61h_families.py`, by the independent test designer from S7's text and failure line 4 alone (no\nimplementation existed; the integrated `measure.py` and RUBRIC.md section 1 item 2 read for the matching rule,\nDEC-963). Everything is planted in `tmp_path`: a measured root that is also the sets root, its own path map with the\nset `planted`, its own questions, and a stand-in `gov` that returns chosen evidence and can keep its answers as a run's\nkept outputs. No store, no model, no network; never this repository's sets, `~/gov-os-eval` or `~/gov-os-runs`. The\n13 cases take about 5 seconds.\n\n**Interface choices the tests make** (S7 names the key and the behaviour, not these details):\n\n1. `evaluation_families:` is a top-level key of the planted path map, a **map of family name to a list of member\n   globs** in the path map's glob language (`*` stays in one folder), for example\n   `contract: [docs/contract/CONTRACT.md, docs/contract/contract.yaml, \"docs/contract/capabilities/*.md\"]`.\n2. Kept outputs are re-scored with **`python3 -m gov.retrieval.measure <set> ... --kept <dir>`**, `<dir>` in the\n",
      "tokens": 296
    },
    {
      "id": "b2e74f702fb08bf4d0a755f3",
      "path": "governance/project/orchestration/packages/ACT-GUARD-SETS-1.md",
      "text": "# ACT-GUARD-SETS-1: the guard refuses the hidden sets outside the repository to the measured roles (DEC-1082 (3))\n\n- **For:** the owner, to decide the four points in \u00a75, then the owner's operator (a guard change: P-ACT-SPLIT).\n- **By:** the CTO, 2026-11-06. A read-only design, built and rehearsed in a clone by an engineer, reviewed by the CTO.\n- **Nothing live is changed** until the operator runs \u00a73.\n- **Rebuilt 2026-11-08 under DEC-1097 (2).** `apply.sh check` had stopped: the path map moved (W2-61h's\n  `evaluation_families`, `cc8139a1c8f4` \u2192 `6d79946fdbbd`); the live hook had not (`e406653ef6c9`), and the new pin's\n  guard code is byte for byte the old pin's. The rebuild adds the glob `runs/fresh-80/**` (the fresh 80's reader run and\n  kept outputs, FRESH-80-1 \u00a72 item 7) and deletes W2-84's hidden-half test cases with the ACT (DEC-1061 (4)). Rehearsed\n  again end to end: 0 failures (\u00a74). The 11-06 build is kept in `drafts/sets-root-guard/build-2026-11-06/`.\n- **The line rule, 2026-11-08 (readiness review 5 F1; the CTO's option A, within DEC-1097 (2)/(3)).** A path the shell\n",
      "tokens": 274
    },
    {
      "id": "a4f00af19dfb2772bf51f7e2",
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-SCORE-ONCE.md",
      "text": "## Every kept run re-scored with source families (DEC-1079; W2-61h S7 and W2-134 merged at `50d79efe`)\n`drafts/score-once/rescore_families.sh`: 26 kept runs (B0, the 16 cells, the four models alone, E1 to E4, L6), each\nre-scored by the merged measure under `--kept`, with no retrieval and no GPU. Each was scored twice.\n- **Without families** (the g1 clone at `e884675b`): a control. Every run equals its own counts, 0 of 138 differing in\n  each. Unresolved: 0 in all.\n- **With families** (`~/gov-os-runs/D4B/g1-fam`, the same commit with integrate's `evaluation_families` block only;\n  the first line `families: contract (4 members), kernel (3 members), agents (2 members)`). **Every count is\n  unchanged in all 26 runs:** hit@5, MRR, per set and spread.\n- **The families do match:** B0 names a family hit on 6 question lines, and M3 on 6. Each falls where the gold's own\n  path already had a hit in the top 5, so no verdict moves.\n- **So every figure above stands as measured,** with families or without. Against B0, with families: M3 118 (13 gains,\n  2 losses, p 0.007); M2 118 (14 and 3, p 0.013); E4 109 (2 and 0, p 0.50).\n\n",
      "tokens": 283
    },
    {
      "id": "2321102dcbe8a107a0d2e367",
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md",
      "text": "   - *Do (recommended):* the checker session re-reads the 80's gold answers against the measured commit and flags any fact that changed; the writer updates those, in one round. Only counts come back to the CTO.\n   - *Cost:* about 1 to 2 hours of the owner's operator and the two sessions.\n4. **The visible q12 sync does not apply.** The CTO synced the sets root's visible q12 once, for E0 (E0-DECLARATION). The 80 have their own labels, and nobody in the CTO's system edits them.\n5. **Source families.** The sets root's path map declares no `evaluation_families` (read: only `evaluation_sets`), so the measure takes the measured clone's. At `c00d525f` that block holds contract, kernel and agents (checked with `git show`).\n   - *Do:* the run's first line must read `families: contract (4 members), kernel (3 members), agents (2 members)`; anything else stops the run before its first search.\n   - The 80 were written before the family rule. A family hit counts only where the item's text holds the gold span's text, and on the 138 the families moved no count.\n6. **The nonexistent-id question.** There is 1 in the 80 (DEC-1078 (1)). It is counted apart, so the judged figures are on 79.\n",
      "tokens": 297
    },
    {
      "id": "4d7b04da27e0bab39bd0e366",
      "path": "src/gov/retrieval/measure.py",
      "text": "def _families_in(root: Path) -> dict | None:\n    \"\"\"One path map's ``evaluation_families``: ``None`` when it declares none; a fault when malformed.\"\"\"\n    path = root / PATH_MAP_REL\n    try:\n        text = path.read_text(encoding=\"utf-8\")\n    except FileNotFoundError:\n        return None\n    except (OSError, UnicodeDecodeError):\n        raise MeasureError(f\"{PATH_MAP_REL} cannot be read\") from None\n    if FAMILIES_KEY not in text:\n        return None\n    try:\n        data = yaml.safe_load(text)\n    except yaml.YAMLError:\n        raise MeasureError(f\"{PATH_MAP_REL} cannot be read\") from None\n    if not isinstance(data, dict) or data.get(FAMILIES_KEY) is None:\n        return None\n    block = data[FAMILIES_KEY]\n    if not (isinstance(block, dict) and all(\n            isinstance(name, str) and isinstance(globs, list) and globs and all(\n                isinstance(g, str) and g and not g.startswith(\"/\") and \"..\" not in g.split(\"/\") for g in globs)\n            for name, globs in block.items())):\n        raise MeasureError(f\"{PATH_MAP_REL}: {FAMILIES_KEY} is not a map of names to lists of path globs\")\n    return block\n",
      "tokens": 282
    },
    {
      "id": "66564e934ea9983d37b91020",
      "path": "src/gov/retrieval/measure.py",
      "text": "**The figures**, always together (DEC-833 item 3): hit@5, a source matched by one of the first five items of the\nstacked context (in the bundle: by an item of the first call), against CAP-10's floor of 85; full evidence, every\nentry matched by the stacked context across batches, against the owner's target of 99 %. The stacked context is\nthe calls' items in order, each taken once, within the stack budget (an item's size: its text's length / 4,\nrounded up); a call continues the last while it returned a continuation and the stack budget is not reached\n(DEC-860). For the hidden part, only ids, counts, ranks, digests and pass or fail are shown or written.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport hashlib\nimport json\nimport os\nimport re\nimport shutil\nimport subprocess\nimport sys\nfrom datetime import datetime, timezone\nfrom pathlib import Path\n\nimport yaml\n\nfrom gov.util.parts import PATH_MAP_REL, SETS_KEY, PolicyError, _Part, _ticket, evaluation_sets, set_fault\n\nEVALUATION = \"fixtures/evaluation\"\nFAMILIES_KEY = \"evaluation_families\"\nFLOOR, TARGET = 85, 99\nTOKEN_CHARS = 4\nFIGURES = (\"hit_at_5\", \"in_bundle\", \"full_evidence\", \"first_gold_rank\", \"stacked_digest\")\n",
      "tokens": 299
    },
    {
      "id": "d46e2a3ae6486b51171bf47f",
      "path": "src/gov/retrieval/measure.py",
      "text": "nowhere or more than once, is unresolved: named by question id and ``entry <n>`` (``<n>.<m>`` for an alternative) and\ncounted as not found (on standard output, or standard error with ``--json``). A source with no commit keeps its stated\nlines. The measure never writes the sets root or a question file.\n\n**Source families** (S7; DEC-1078 (4), DEC-1079): the path map's top-level ``evaluation_families`` (the sets root's,\nelse the measured root's) maps a family's name to the list of its member path globs: a gold source and its official\ncopies. An evidence item in another member of a gold source's family is a hit on that source only when its own text\nholds the gold span's text, both normalised (whitespace; Markdown and YAML formatting: ``#`` heading marks, list\nmarks, ``>`` quote marks, quotes, backticks, ``*`` emphasis and ``key:`` prefixes, but never an id such as\n``DEC-1078:``); never by its path alone. The gold's normalised text must be at least 4 words and 24 characters\n(below that it counts only in its own path) and is held only on token edges (``CAP-1`` is not held by ``CAP-10``, nor\n",
      "tokens": 276
    },
    {
      "id": "efbf8350b6e1042902ed3c3d",
      "path": "tests/acceptance/W2-134/w2_134_support.py",
      "text": "def path_map(families: dict | None = FAMILIES) -> str:\n    doc = {\"evaluation_sets\": {SET: {\"visible\": [\"docs/sets/planted.md\"],\n                                     \"hidden\": [f\"fixtures/evaluation/{SET}/hidden/**\"],\n                                     \"measures\": {\"roles\": [\"engineer\"]}}}}\n    if families is not None:\n        doc[\"evaluation_families\"] = families\n    return yaml.safe_dump(doc, sort_keys=False)\n",
      "tokens": 105
    },
    {
      "id": "7effef16368f1978a2753259",
      "path": "tests/acceptance/W2-170/w2_170_world.py",
      "text": "  # an earlier audit's set, among comments\n  {EARLIER}:\n    visible: []\n    hidden: [\"fixtures/evaluation/{EARLIER}/hidden/**\"]\n    measures:\n      roles: [engineer, research, product-spec, independent-test-designer, independent-auditor]\n  # the last comment inside the block\n\n# a comment between the blocks\nevaluation_families:\n  kernel: [\"template/governance/kernel/**\"]\n\"\"\"\n\n\n",
      "tokens": 95
    },
    {
      "id": "752f667fdadb37a6d46fa52a",
      "path": "tests/acceptance/W2-61h/README.md",
      "text": "| S7 | `test_w2_61h_families.py::test_s7_a_file_outside_the_family_is_no_hit_by_its_text` | A file outside the gold's family is no hit even when it holds the text byte for byte: `in-no-family`, `in-another-family` (the kernel family's role file), `a-folder-below-the-glob` (`capabilities/old/CAP-7.md`; `*` stays in one folder). With the same control |\n| S7 | `test_w2_61h_families.py::test_s7_with_no_family_declared_every_score_is_as_today` | No `evaluation_families`: the items that would be family hits count for nothing; per question hit@5, first gold rank (MRR's input: none, 1, 6), in the bundle, full evidence and pieces, and the total line (1 of 3, 33.3 %) are today's; no line mentions a family. **Green today by design** (it guards today's figures) |\n",
      "tokens": 191
    },
    {
      "id": "5f88cfce6f23fe68f3d438c8",
      "path": "tests/acceptance/W2-61h/test_w2_61h_families.py",
      "text": "no network; never this repository's sets, never ``~/gov-os-eval``). The measure is run as a command, from this\ntree's ``src``.\n\nInterface choices these tests make (S7 names the key and the behaviour, not these details):\n\n- ``evaluation_families:`` is a top-level key of the path map, **a map of family name to a list of member globs**\n  in the path map's glob language (``*`` stays in one folder);\n- the kept outputs are read with ``python3 -m gov.retrieval.measure <set> ... --kept <dir>``, ``<dir>`` in the form\n  ``~/gov-os-eval/runs/<point>/<name>-run<k>/`` takes (``drafts/d4b/measure_verdict.sh``): each ``gov retrieve``\n  call's ``--json`` output as ``00001.json``, ``00002.json``, ... in call order, beside ``.n`` and ``.n.lock``; the\n  output is the measure's own (text, or the record with ``--json``);\n- a family hit is named by the member's path and the word \"family\" in the question's line.\n\nRed on today's integrated code: every case but the one for \"with no family declared, every score is as today\",\nwhich passes today by design (it guards today's figures). Each negative case carries a positive control in the same\nrun, so it is red until families work, then judges the negative.\n\"\"\"\n",
      "tokens": 300
    },
    {
      "id": "dc1838ec8ec7ccbd797ba80f",
      "path": "tests/acceptance/W2-61h/test_w2_61h_families.py",
      "text": "    def set_families(self, families: dict | None) -> None:\n        doc = {\"evaluation_sets\": {SET: {\"visible\": [\"docs/sets/planted.md\"],\n                                         \"hidden\": [f\"fixtures/evaluation/{SET}/hidden/**\"],\n                                         \"measures\": {\"roles\": [\"engineer\"]}}}}\n        if families is not None:\n            doc[\"evaluation_families\"] = families\n        path = self.root / \"governance/project/path-map.yaml\"\n        path.parent.mkdir(parents=True, exist_ok=True)\n        path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding=\"utf-8\")\n",
      "tokens": 148
    },
    {
      "id": "8967e71d39728294702fcfe0",
      "path": "tests/unit/retrieval/test_w2_134_reanchor.py",
      "text": "    write(repo / \"docs/gone.md\", [\"keep\", \"keep\"])\n    write(repo / \"docs/twice.md\", [\"one\", \"two\", \"dup line here\", \"dup line here\"])  # moved, and found twice\n    subprocess.run([*git, \"commit\", \"-q\", \"-am\", \"two\"], check=True)\n    c2 = subprocess.run([*git, \"rev-parse\", \"HEAD\"], capture_output=True, text=True, check=True).stdout.strip()\n    bin_dir = tmp_path / \"bin\"\n    bin_dir.mkdir()\n    gov = bin_dir / \"gov\"\n    gov.write_text(GOV.format(python=sys.executable))\n    gov.chmod(0o755)\n    monkeypatch.setenv(\"GOV_ROLE\", \"orchestrator\")\n    monkeypatch.delenv(\"GOV_TICKET\", raising=False)\n    monkeypatch.delenv(\"GOV_KEEP\", raising=False)\n\n    def path_map(families=None):\n        doc = {\"evaluation_sets\": SETS, **({\"evaluation_families\": families} if families is not None else {})}\n        write(sets / \"governance/project/path-map.yaml\", [yaml.safe_dump(doc)])\n\n    def ask(part, name, plan, **question):\n        folder = sets / \"fixtures/evaluation/s\" / part\n        folder.mkdir(parents=True, exist_ok=True)\n        (folder / f\"{name}.yaml\").write_text(yaml.safe_dump({\"gold_answer\": f\"the {SECRET}\", **question}))\n",
      "tokens": 282
    },
    {
      "id": "120d3eba093bf54a47bf1773",
      "path": "tests/unit/retrieval/test_w2_61h_families.py",
      "text": "def planted(tmp_path, monkeypatch):\n    repo = tmp_path / \"repo\"\n    (repo / \"governance/project\").mkdir(parents=True)\n    (repo / \"docs/contract/caps\").mkdir(parents=True)\n    (repo / \"docs/report.md\").write_text(\"quote\\n\")\n    (repo / \"docs/contract/CONTRACT.md\").write_text(CONTRACT_MD)\n    (repo / \"docs/contract/contract.yaml\").write_text(CONTRACT_YAML)\n    (repo / \"docs/other.md\").write_text(CONTRACT_YAML)\n    (repo / \"AGENTS.md\").write_text(\"# Agents\\n\\nRule one: every change has a ticket.\\n\")\n    (repo / \"CLAUDE.md\").write_text(\"# Claude\\n\\n- Rule one: every change has a ticket.\\n\")\n\n    def path_map(families=FAMILIES):\n        doc = {\"evaluation_sets\": SETS, **({\"evaluation_families\": families} if families is not None else {})}\n        (repo / \"governance/project/path-map.yaml\").write_text(yaml.safe_dump(doc))\n\n    path_map()\n    subprocess.run([\"git\", \"init\", \"-q\", str(repo)], check=True)\n    git = [\"git\", \"-C\", str(repo), \"-c\", \"user.name=t\", \"-c\", \"user.email=t@t\"]\n    subprocess.run([*git, \"add\", \"-A\"], check=True)\n    subprocess.run([*git, \"commit\", \"-q\", \"-m\", \"planted\"], check=True)\n    bin_dir = tmp_path / \"bin\"\n    bin_dir.mkdir()\n    gov = bin_dir / \"gov\"\n",
      "tokens": 298
    },
    {
      "id": "625ca7ad0b47618c3354c1da",
      "path": "tests/unit/retrieval/test_w2_61h_families.py",
      "text": "def test_malformed_families_refuse_the_run(planted, capsys):\n    _, _, ask, run, path_map = planted\n    ask(\"visible\", \"q1\", [[YAML_ITEM]], question=\"q one\", sources=[OUTCOME])\n    path_map({\"contract\": \"docs/contract/*\"})\n    code, _, err = run(capsys=capsys)\n    assert code != 0 and \"evaluation_families\" in err\n",
      "tokens": 79
    },
    {
      "id": "W2-27-CIT-P",
      "path": "docs/changes/W2-27-CIT-P.md",
      "text": "| 3 | `docs/contract/capabilities/CAP-45.a.md` | Title, heading and `Item:` hold 4.2's item. `Wave:` W2 | Regenerated from the approved `contract.yaml` (\u00a75.3) by a throwaway generator. The generator first reproduces the unchanged records byte for byte, as W2-49's CIT-E did | Same |\n| 4 | `docs/contract/capabilities/CAP-45.md` | `Wave:` W2 | `Wave:` W3 under A (i); unchanged under A (ii) | Same |\n| 5 | The other 274 capability records under `docs/contract/capabilities/` (276 in all) | Each says \"(Contract v4, version 4.2)\" once | Only that occurrence changes, to 4.3, under V (i) (DEC-741 K (1)'s precedent). Nothing changes under V (ii) | Same |\n| 6 | `docs/contract/master-rules/MR-1.md` to `MR-6.md` | \"(Contract v4, version 4.1)\" | **Unchanged.** 4.2 left them at 4.1, and this change touches no master rule | Nobody |\n| 7 | `docs/contract/SOURCE_MAP.csv` rows 107, 224, 286 (Contract v3 S5, Framework \u00a782, Distribution Protocol \u00a712) | \"Contract v4 CAP-45 (KEPT, wave W2)\" | \"wave W3\" under A (i) (\u00a75.4); unchanged under A (ii). Row 222 (Framework \u00a780) names CAP-45 with no wave and stays as it is | The apply ticket |\n",
      "tokens": 282
    },
    {
      "id": "ADOPT-A1",
      "path": "governance/adoption/A1-inventory.md",
      "text": "  blob: 4d87bdf01fa09beb67126aa2c59f7ae6b72997f7\n- path: docs/contract/capabilities/CAP-61.a.md\n  blob: 9a52d50a520b81212d375910afba07f102434d28\n- path: docs/contract/capabilities/CAP-61.b.md\n  blob: e2f7c1588a77dbb8b99206e13416b60b914f3de4\n- path: docs/contract/capabilities/CAP-61.c.md\n  blob: aa63dbb4650d802ab6c0020207be577042e0afbe\n- path: docs/contract/capabilities/CAP-61.d.md\n  blob: eada5854f6f22fc7ae2a7acb188074819eb533f5\n- path: docs/contract/capabilities/CAP-61.e.md\n  blob: fd1f6e19719e355d1d6c92f5c28e87031c173ba7\n- path: docs/contract/capabilities/CAP-61.f.md\n  blob: 5760d1e2ea5f1eddd89eb7d8ddfb28dfc06f7ecc\n- path: docs/contract/capabilities/CAP-61.md\n  blob: 9eae8b05842bb39a9c4327c3ae430ee258c21adf\n- path: docs/contract/capabilities/CAP-62.a.md\n  blob: 46bb08e3227c3e89e66f9e71dbcbe4eb4faf1454\n- path: docs/contract/capabilities/CAP-62.md\n  blob: 98a868f0cfe6392e9bfa6004b061cfa7b3364b2c\n- path: docs/contract/contract.yaml\n  blob: a483451024eb3f13e0264301346c3413751def14\n- path: docs/contract/master-rules/MR-1.md\n  blob: 6e1c3a7dc6b7c24e8f5f03624ebc4fc7599feb2c\n- path: docs/contract/master-rules/MR-2.md\n  blob: d35b061bb1f96a63ec50647c130e398f9bc3f0b9\n",
      "tokens": 295
    },
    {
      "id": "ADOPT-A2",
      "path": "governance/adoption/A2-classification.md",
      "text": "- path: docs/contract/capabilities/CAP-61.a.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-61.b.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-61.c.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-61.d.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-61.e.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-61.f.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-61.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-62.a.md\n  namespace: root-files\n- path: docs/contract/capabilities/CAP-62.md\n  namespace: root-files\n- path: docs/contract/contract.yaml\n  namespace: root-files\n- path: docs/contract/master-rules/MR-1.md\n  namespace: root-files\n- path: docs/contract/master-rules/MR-2.md\n  namespace: root-files\n- path: docs/contract/master-rules/MR-3.md\n  namespace: root-files\n- path: docs/contract/master-rules/MR-4.md\n  namespace: root-files\n- path: docs/contract/master-rules/MR-5.md\n  namespace: root-files\n- path: docs/contract/master-rules/MR-6.md\n  namespace: root-files\n- path: docs/contract/readiness-dimensions.yaml\n  namespace: root-files\n",
      "tokens": 293
    }
  ],
  "supplementary_query": "W2-61's enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session\nTwenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half (fixtures/evaluation/memory-retrieval/visible/q21.yaml to q24.yaml in the repository; the hidden 24 in the sets root outside every worktree, ~/gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/); the set then grows to about 40 per half (DEC-1069 (4) and (8)): 16 more visible questions written by a session independent of the retrieval work, and 16 more hidden ones written by the owner's operator from the rubric, so the hidden half holds 40 [DEC-954 Q9a, DEC-957, DEC-828 items 3 and 4, DEC-820 (d), DEC-1055 (4), DEC-1069] [re-worded, DEC-1084]\nWritten by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61's engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]\nThe spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded), exact strings and identifiers with file and line 4, callers, callees and definitions 4, code facts by paraphrase 3, the kernel template (roles, skills, hooks) 3, multi-file stacked 3 (each needing two or more files), history 2, failure memory 2, a plan, ticket or path-map fact 1, an id that exists nowhere 1; for the set of about 40 per half the quotas are amended to fit R5 (DEC-1069 (5)): each governing domain at least 10 % of each half, no subsystem above 25 %; the hidden 40's table may end one short in the decision, callers and code-paraphrase categories, with every governing domain at least 4 of 40 (accepted, DEC-1069) [DEC-954 Q9a, Q9c, DEC-833, DEC-866, DEC-1069] [re-worded, DEC-1084]\nEvery gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]\nThe hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or commit; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-1052 G-3, DEC-1055 (4), ACT-D8]\nThe hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is checked by tests that report counts and pass or fail only, never its contents [DEC-954 Q9b, DEC-1052 G-3, DEC-1055 (4)]\nS7 Source families (DEC-1078 (4), DEC-1079): the measure counts a gold source and its official copies as one family. The families are declared in the path map (`evaluation_families:`, each a list of member path globs, e.g. the Contract's `docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml` and the generated `docs/contract/capabilities/*.md` and `master-rules/*.md`; the kernel template and its generated `.claude/` and `.rulesync/` copies; `AGENTS.md` and `CLAUDE.md`). An evidence item in another member of the gold source's family counts as a hit on that source when its text holds the gold span's text (whitespace and Markdown-or-YAML formatting normalised), never by path alone; each family hit is named in the measure's per-question line; with no family declared, every score is as today; a run's kept outputs are re-scored with families without running again [DEC-1078, DEC-1079, DEC-1068 (4)]\nS8 The measure re-anchors in memory (DEC-1084): before it scores, the measure finds each line-cited gold source's block again in the commit it measures (the block read at the source's own commit, found once at the measured root, as repin_gold.py does), and scores against those lines; it never writes the sets root or any label file; an unresolved source is named by question id and entry number only and counts as not found. Two measures on different commits, run one after the other, score each commit against its own lines and leave every label file byte for byte as it was. Verify: tests on a planted repository with two commits where a cited block moves, and a planted sets root hashed before and after [DEC-1084, DEC-1083, DEC-820 (d)]\nA hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.\nA measure that writes a label file or the sets root, or scores a commit against another commit's lines.\nA question copied from or paraphrasing lens B's visible 20.\nA gold source that does not hold its answer.\nA family hit counted on a member whose text does not hold the gold span's text.",
  "further_batch": [
    {
      "id": "ADOPT-A3",
      "path": "governance/adoption/A3-target-path-map.md"
    },
    {
      "id": "7cff9f7b1a2b2c5b313c2b83",
      "path": "tests/acceptance/W2-04/test_w2_04_refusal.py"
    },
    {
      "id": "c1dd1922c9e3e74566373a64",
      "path": "tests/acceptance/W2-49/test_w2_49_owner_answers.py"
    },
    {
      "id": "5f8960efe7ac83c893025825",
      "path": "tests/acceptance/W2-61h/test_w2_61h_families.py"
    },
    {
      "id": "2746d3d80f7dcc10ba5dfc4d",
      "path": "governance/project/indep-briefs/memory-audit/writer.md"
    },
    {
      "id": "aca07156e3d5e5599d7311cb",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md"
    },
    {
      "id": "DAEO-m4rq",
      "path": ".tickets/DAEO-m4rq.md"
    },
    {
      "id": "DAEO-qzca",
      "path": ".tickets/DAEO-qzca.md"
    },
    {
      "id": "DAEO-rd0g",
      "path": ".tickets/DAEO-rd0g.md"
    },
    {
      "id": "DAEO-rd0g",
      "path": ".tickets/DAEO-rd0g.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "621f5faae9b6d6055c0c909e",
          "path": "tests/acceptance/W2-61h/test_w2_61h_visible_new.py"
        },
        {
          "id": "fb96a256eb4278b964203cca",
          "path": "tests/acceptance/W2-61h/test_w2_61h_families.py"
        },
        {
          "id": "92d02c0f44b56ac8af8ac345",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "6262171d2757882181c97d4e",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "82de7c78949cb8b459c68034",
          "path": "governance/project/path-map.yaml"
        },
        {
          "id": "306a0ee65f3b854674456ae5",
          "path": "tests/unit/retrieval/test_w2_61h_families.py"
        },
        {
          "id": "db28e269fd9bebcf7aabad94",
          "path": "tests/acceptance/W2-171/README.md"
        },
        {
          "id": "0f9bf3aeb3b8949dfd823522",
          "path": "tests/acceptance/W2-171/w2_171_world.py"
        },
        {
          "id": "DAEO-qzca",
          "path": ".tickets/DAEO-qzca.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "10a9349768c43af9e76cd6d2",
          "path": "governance/project/orchestration/packages/SETUP-A-BAR.md"
        },
        {
          "id": "2f2de6f274780a66a788abcf",
          "path": "governance/project/orchestration/reviews/D10-W2-92-review.md"
        },
        {
          "id": "df05e2995d286b45fdfe9a6d",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "b2e74f702fb08bf4d0a755f3",
          "path": "governance/project/orchestration/packages/ACT-GUARD-SETS-1.md"
        },
        {
          "id": "a4f00af19dfb2772bf51f7e2",
          "path": "governance/project/orchestration/packages/LIFT-1/D4B-SCORE-ONCE.md"
        },
        {
          "id": "2321102dcbe8a107a0d2e367",
          "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-1.md"
        },
        {
          "id": "4d7b04da27e0bab39bd0e366",
          "path": "src/gov/retrieval/measure.py"
        },
        {
          "id": "66564e934ea9983d37b91020",
          "path": "src/gov/retrieval/measure.py"
        },
        {
          "id": "d46e2a3ae6486b51171bf47f",
          "path": "src/gov/retrieval/measure.py"
        },
        {
          "id": "efbf8350b6e1042902ed3c3d",
          "path": "tests/acceptance/W2-134/w2_134_support.py"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "7effef16368f1978a2753259",
          "path": "tests/acceptance/W2-170/w2_170_world.py"
        },
        {
          "id": "752f667fdadb37a6d46fa52a",
          "path": "tests/acceptance/W2-61h/README.md"
        },
        {
          "id": "5f88cfce6f23fe68f3d438c8",
          "path": "tests/acceptance/W2-61h/test_w2_61h_families.py"
        },
        {
          "id": "dc1838ec8ec7ccbd797ba80f",
          "path": "tests/acceptance/W2-61h/test_w2_61h_families.py"
        },
        {
          "id": "8967e71d39728294702fcfe0",
          "path": "tests/unit/retrieval/test_w2_134_reanchor.py"
        },
        {
          "id": "120d3eba093bf54a47bf1773",
          "path": "tests/unit/retrieval/test_w2_61h_families.py"
        },
        {
          "id": "625ca7ad0b47618c3354c1da",
          "path": "tests/unit/retrieval/test_w2_61h_families.py"
        },
        {
          "id": "W2-27-CIT-P",
          "path": "docs/changes/W2-27-CIT-P.md"
        },
        {
          "id": "ADOPT-A1",
          "path": "governance/adoption/A1-inventory.md"
        },
        {
          "id": "ADOPT-A2",
          "path": "governance/adoption/A2-classification.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "ADOPT-A3",
          "path": "governance/adoption/A3-target-path-map.md"
        },
        {
          "id": "7cff9f7b1a2b2c5b313c2b83",
          "path": "tests/acceptance/W2-04/test_w2_04_refusal.py"
        },
        {
          "id": "c1dd1922c9e3e74566373a64",
          "path": "tests/acceptance/W2-49/test_w2_49_owner_answers.py"
        },
        {
          "id": "5f8960efe7ac83c893025825",
          "path": "tests/acceptance/W2-61h/test_w2_61h_families.py"
        },
        {
          "id": "2746d3d80f7dcc10ba5dfc4d",
          "path": "governance/project/indep-briefs/memory-audit/writer.md"
        },
        {
          "id": "aca07156e3d5e5599d7311cb",
          "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md"
        },
        {
          "id": "DAEO-m4rq",
          "path": ".tickets/DAEO-m4rq.md"
        },
        {
          "id": "DAEO-qzca",
          "path": ".tickets/DAEO-qzca.md"
        },
        {
          "id": "DAEO-rd0g",
          "path": ".tickets/DAEO-rd0g.md"
        },
        {
          "id": "DAEO-rd0g",
          "path": ".tickets/DAEO-rd0g.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "2746d3d80f7dcc10ba5dfc4d",
      "reason": "budget exceeded"
    },
    {
      "id": "5f8960efe7ac83c893025825",
      "reason": "budget exceeded"
    },
    {
      "id": "7cff9f7b1a2b2c5b313c2b83",
      "reason": "budget exceeded"
    },
    {
      "id": "ADOPT-A3",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-m4rq",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-qzca",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-rd0g",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-rd0g",
      "reason": "budget exceeded"
    },
    {
      "id": "aca07156e3d5e5599d7311cb",
      "reason": "budget exceeded"
    },
    {
      "id": "c1dd1922c9e3e74566373a64",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-h2k3): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 29755,
  "budget": {
    "limit": 30000,
    "used": 29755
  },
  "hash": "71bb6b781c8ad45ffc2f0746590cb473d681fe7465bf7d2c2917ca05085a5ec7"
}
