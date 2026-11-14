{
  "ticket": "DAEO-drhj",
  "ticket_text": "---\nid: DAEO-drhj\nstatus: in_progress\ndeps: []\nlinks: []\ncreated: 2026-10-30T23:20:54Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-104\ntags: [wave-2, implementation, skills, standard]\nwbs_id: W2-104\ntitle: 'The skill evaluation harness: each skill''s three scenarios run on a fresh session and recorded, and every imported skill''s licence check recorded before adoption'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- docs/probes/DAEO-drhj/**  # the probe record (run 3's narrow check)\n- src/gov/skilleval/**\n- tests/unit/skilleval/test_w2_104*\n- governance/project/skill-imports.yaml\n- src/gov/check/commands.py\nkpis:\n  success:\n  - 'gov skilleval <skill> runs each of the skill''s three committed scenarios on a fresh session with only that skill loaded (the model and effort from the role defaults), judges each against its stated pass line, and writes a scenario record (skill version, scenario, verdict, cost, time) beside the skill; it is the evidence CIT-E reads [DEC-959 item 5, ROLES-RESEARCH-1 \u00a75.3 item 13] Verify: with a stub model in a temporary project, each of a planted skill''s three scenarios runs in a new session folder holding only that skill, with -p, --model and --effort from the role defaults, is judged by a separate process against its pass line, and appends a record with the skill version, scenario, verdict, cost and time beside the skill; a skill that cannot be evaluated ends 5 with nothing run or recorded (tests/acceptance/W2-104/, the README''s Success 1 row)'\n  - 'An imported skill (Anthropic''s collection or another source) is adopted only when governance/project/skill-imports.yaml records its source, version, licence and the licence''s verdict for this use, and its three scenarios pass; the harness refuses to mark an import adopted otherwise [DEC-959 item 5] Verify: --adopt with a full allowing record and three passes marks it adopted and leaves other entries unchanged; each gap in the record, no entry, no record file, or fewer than three passes ends 6 with adopted false (tests/acceptance/W2-104/, the README''s Success 2 row)'\n  - 'A scenario run that cannot reach a model (no network, no key) is recorded as not run with its cause, never as a pass; the harness reads no secret and prints none [DEC-959 item 5, DEC-820 (a)] Verify: a session that exits non-zero, prints no JSON or reports is_error, a judgement that exits non-zero, no claude on the PATH and a session past --timeout are each recorded not run with a one-line cause and no cost (tests/acceptance/W2-104/, the README''s Success 3 row)'\n  - 'Planted skills with a passing and a failing scenario give the expected verdicts, in a temporary project, with a stub model [DEC-959 item 5] Verify: a passing planted skill gives three passes; a FAIL and an unanswered judgement give fail; the last verdict line of the judgement decides and the session''s own verdict line is not read (tests/acceptance/W2-104/, the README''s Success 4 row)'\n  failure:\n  - 'A scenario reported as passing that did not run, or failed. Verify: every not-run case (the stub''s judgement would say PASS if asked) and every failed case (FAIL, no verdict, PASS then FAIL, a session that says PASS itself) is never recorded pass (tests/acceptance/W2-104/, the README''s F1 row)'\n  - 'An import marked adopted with no licence record or a failing scenario. Verify: each of the 7 licence-record gaps, no entry, no record file and each of the 3 not-three-passes variants starts adopted true and ends adopted false (tests/acceptance/W2-104/, the README''s F2 row)'\n  - 'A secret read or printed. Verify: two planted values (the environment''s ANTHROPIC_API_KEY and the project''s .env) never appear in gov''s output or records, when the stub prints them on stderr, as non-JSON stdout or in an is_error reply, on a passing run, and with the .env unreadable (tests/acceptance/W2-104/, the README''s F3 row)'\nprofile: STANDARD\nsources:\n- DEC-959\n- DEC-820\nest_loc: 250\nacceptance_tests:\n  path: tests/acceptance/W2-104/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7); planted skills and a stub model, no network\ntrack: B\nlist_rows: []\n---\n# W2-104 The skill evaluation harness\n\nCard: ROLES-RESEARCH-1 \u00a75.3 item 13, approved (DEC-959 items 5 and 8): with or just after W2-11 r1, so the template's scenarios have a runner.\n\n- **Paths:** a new command module `src/gov/skilleval/` (`gov skilleval`), and the import record `governance/project/skill-imports.yaml` (new). No overlap.\n- **Re-listed (CTO, 2026-11-13):** run 3 parked by the emergency's freeze on 11-02 and never re-listed; now run 3 merges integrate (W1-07, W1-32 and commands.py conflicts), builds the two gitleaks literals from parts, a narrow check, the land.\n\n**Reopened 2026-11-14 by the CTO under DEC-1164 (18) (a P2 listed for the owner's reading):** the harness copies a skill's folder into the session's `.claude/skills/` leaving out `scenarios.md` and `scenario-records.yaml` (`src/gov/skilleval/harness.py:167-168`), but not a hand-written `scenario-summaries.md` beside them (W2-100's and W2-101's interface, P-W2-100-IF-1 (a)), so the session under test could read its own runs' summaries (W2-101's review F1, fails open). The fix: the harness also leaves out `scenario-summaries.md`; one unit case plants it and checks the session's folder lacks it; a narrow independent check.\n",
  "authority": [
    {
      "id": "DEC-959",
      "sha256": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "reason": "declared in sources",
      "tokens": 1329
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    }
  ],
  "mandatory": [
    {
      "id": "DEC-959",
      "sha256": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "99cdbe5dfb7aaf847d3f51f29fdf13c818e4df6ca35c552a04062b701c87938c",
      "reason": "declared in sources",
      "tokens": 1329
    },
    {
      "id": "DEC-820",
      "sha256": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32aab8ba141b0957202f50528a12671130686f6476d0178a16b88f75e8b85c1d",
      "reason": "declared in sources",
      "tokens": 638
    }
  ],
  "supplementary": [],
  "supplementary_query": "The skill evaluation harness: each skill's three scenarios run on a fresh session and recorded, and every imported skill's licence check recorded before adoption\ngov skilleval <skill> runs each of the skill's three committed scenarios on a fresh session with only that skill loaded (the model and effort from the role defaults), judges each against its stated pass line, and writes a scenario record (skill version, scenario, verdict, cost, time) beside the skill; it is the evidence CIT-E reads [DEC-959 item 5, ROLES-RESEARCH-1 \u00a75.3 item 13] Verify: with a stub model in a temporary project, each of a planted skill's three scenarios runs in a new session folder holding only that skill, with -p, --model and --effort from the role defaults, is judged by a separate process against its pass line, and appends a record with the skill version, scenario, verdict, cost and time beside the skill; a skill that cannot be evaluated ends 5 with nothing run or recorded (tests/acceptance/W2-104/, the README's Success 1 row)\nAn imported skill (Anthropic's collection or another source) is adopted only when governance/project/skill-imports.yaml records its source, version, licence and the licence's verdict for this use, and its three scenarios pass; the harness refuses to mark an import adopted otherwise [DEC-959 item 5] Verify: --adopt with a full allowing record and three passes marks it adopted and leaves other entries unchanged; each gap in the record, no entry, no record file, or fewer than three passes ends 6 with adopted false (tests/acceptance/W2-104/, the README's Success 2 row)\nA scenario run that cannot reach a model (no network, no key) is recorded as not run with its cause, never as a pass; the harness reads no secret and prints none [DEC-959 item 5, DEC-820 (a)] Verify: a session that exits non-zero, prints no JSON or reports is_error, a judgement that exits non-zero, no claude on the PATH and a session past --timeout are each recorded not run with a one-line cause and no cost (tests/acceptance/W2-104/, the README's Success 3 row)\nPlanted skills with a passing and a failing scenario give the expected verdicts, in a temporary project, with a stub model [DEC-959 item 5] Verify: a passing planted skill gives three passes; a FAIL and an unanswered judgement give fail; the last verdict line of the judgement decides and the session's own verdict line is not read (tests/acceptance/W2-104/, the README's Success 4 row)\nA scenario reported as passing that did not run, or failed. Verify: every not-run case (the stub's judgement would say PASS if asked) and every failed case (FAIL, no verdict, PASS then FAIL, a session that says PASS itself) is never recorded pass (tests/acceptance/W2-104/, the README's F1 row)\nAn import marked adopted with no licence record or a failing scenario. Verify: each of the 7 licence-record gaps, no entry, no record file and each of the 3 not-three-passes variants starts adopted true and ends adopted false (tests/acceptance/W2-104/, the README's F2 row)\nA secret read or printed. Verify: two planted values (the environment's ANTHROPIC_API_KEY and the project's .env) never appear in gov's output or records, when the stub prints them on stderr, as non-JSON stdout or in an is_error reply, on a passing run, and with the .env unreadable (tests/acceptance/W2-104/, the README's F3 row)",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 3332,
  "budget": {
    "limit": 6000,
    "used": 3332
  },
  "hash": "b58b6fe9219a7927e6f844ef92af33b2ab0af3de7183329e014db7c84910a90d"
}
