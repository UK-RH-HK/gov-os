{
  "ticket": "DAEO-6f0s",
  "ticket_text": "---\nid: DAEO-6f0s\nwbs_id: W2-184\nexternal-ref: W2-184\ntitle: \"RUBRIC-2 at launch: criticality from criticality.yaml, the Launch by criticality line, the effort floor, trials, the second review's setting, promotion (from W2-60a)\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: FULL\nstatus: in_progress\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-13\ndeps: [DAEO-cv58]\nallowed_paths:\n- src/gov/launch/launcher.py\n- src/gov/launch/role.py\n- src/gov/launch/record.py\n- src/gov/launch/criticality.py\n- governance/project/criticality.yaml\n- tests/unit/launch/test_w2_184_*.py\n- docs/changes/W2-184-CIT-E.md\n- docs/probes/DAEO-6f0s/**  # the probe record\n- src/gov/launch/command.py\nreads:\n- .tickets/DAEO-cv58.md\n- governance/project/orchestration/packages/P1-W2-60a-P5.md\n- governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md\n- template/governance/kernel/roles/**\nneeds: []\nwaits_on: []\nkpis:\n  success:\n  - 'The session''s model and effort are RUBRIC-2''s for its role and criticality: read from the role file''s `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket''s criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket''s `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [from W2-60a S3, DEC-1167]'\n  - 'A model after -- that is not the resolved tier''s is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session''s tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings'' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [from W2-60a S4, DEC-1167]'\n  - 'The launch record also holds `tier`, `criticality`, `model_source` (role default, by criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them null [DEC-1120 (3)] [from W2-60a S8, DEC-1167]'\n  - 'On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [from W2-60a S10, DEC-1167]'\n  - 'A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table''s effort, recorded as `promotion` with the reason and the record''s path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [from W2-60a S11, DEC-1167]'\n  failure:\n  - 'A model below its tier with no trial; a promotion not applied; an effort below the floor. Verify: S3 and S4''s planted cases: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below high for a judgement role is refused [from W2-60a F4, DEC-1167]'\nnon_goals:\n- 'not W2-60a''s reviewed core (role text, skills, the record''s base fields, no compaction, the refused arguments): W2-60a lands it first'\n- 'not a gate for W2-27 (EXAMIN''s copy): launches during the copy use each role''s `Launch default` line (P1-W2-60a-P5 (B), DEC-1167)'\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1167, DEC-1126, DEC-1120, DEC-1119, DEC-839, DEC-1010, CAP-35.c, DEC-1014, DEC-1015, DAEO-cv58]\nacceptance_tests: {path: tests/acceptance/W2-184/}\n---\n\n# W2-184 RUBRIC-2 at launch (from W2-60a)\n\nThe owner's P1-W2-60a-P5 (B) (DEC-1167): RUBRIC-2's lines, added to W2-60a by DEC-1126 (3) after its three review\nrounds and never built, move here, so W2-60a lands its reviewed core and EXAMIN's copy runs on each role's\n`Launch default` line. The interface is the CTO's at claim, from W2-60a run 4d's proposal (`log/W2-60a-A5-run4d.json`):\n`criticality.yaml` and `ticket_criticality(root, ticket)`, the `Launch by criticality` line with its \"on FULL ... otherwise\"\nform, the effort floor and `--reason`, `--trial` reading `governance/project/trials/<id>.yaml`, promotion from the probe\nrecords, S10 counting the auditor's launch records with `--owner-named <DEC-id>`. Starts after W2-60a merges; its own\nreview rounds (new scope).\n\n**The CTO, 2026-11-14:** P-W2-184-2 (a), `src/gov/launch/command.py` added (the interface at claim puts `--trial`, `--reason` and `--owner-named` before `--`). P-W2-184-3 confirmed: 1.4 (no `criticality.yaml`: a launch behaves as before W2-184, DEC-1167 (2)); 3.2a (a max after `--` equal to the resolved effort needs no `--reason`); `probe` as a sixth `model_source`/`effort_source`; the lead's matching rule. P-W2-184-1 (round 2's F1) is the owner's (DEC-1010).\n\n**The owner, 2026-11-14 (chat, ~11:40): P-W2-184-1 (a), with (c) as the stop-gap until it lands (DEC-1010; round 2's F1).** (a): `_probe_files` (`src/gov/launch/launcher.py`) also reads `docs/probes/<id>/` under each worktree root that the ticket's launch records name, so a test designer launched from its tests worktree sees the ticket's probe records; a root that no longer exists is skipped. (c): until (a) lands, a lead brings the ticket branch's probe-record commit into its tests branch before it launches a test designer. The fix is followed by a narrow independent check of that change only (DEC-1154).\n",
  "authority": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1126",
      "sha256": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "reason": "declared in sources",
      "tokens": 662
    },
    {
      "id": "DEC-1120",
      "sha256": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-839",
      "sha256": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "reason": "declared in sources",
      "tokens": 429
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
    },
    {
      "id": "CAP-35.c",
      "sha256": "cf16855d86b74db31bffde48825d00a4a0c693cc5fb995ee5ce426b028a4e18b",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "cf16855d86b74db31bffde48825d00a4a0c693cc5fb995ee5ce426b028a4e18b",
      "reason": "declared in sources",
      "tokens": 127
    },
    {
      "id": "DAEO-cv58",
      "sha256": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "reason": "declared in sources",
      "tokens": 1529
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1167",
      "sha256": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d3c196337a6a1ef5fbcc55345eb477c5d04febd257b25a6f8934739b319812c6",
      "reason": "declared in sources",
      "tokens": 745
    },
    {
      "id": "DEC-1126",
      "sha256": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "reason": "declared in sources",
      "tokens": 662
    },
    {
      "id": "DEC-1120",
      "sha256": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "0a2f524e0c888fd1b3e594c1d28f538a123f826175a2fda990c82f3793b571e7",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-839",
      "sha256": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5a7451b1c40e7ddafd600189082ebf1b4b37dd1888de12b2a1604160e22a8b72",
      "reason": "declared in sources",
      "tokens": 429
    },
    {
      "id": "DEC-1010",
      "sha256": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ce2f4f1fec7f772a13888f3ae234f9bf6b11e06b00aea2e0455ef24f00e6b628",
      "reason": "declared in sources",
      "tokens": 964
    },
    {
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
    },
    {
      "id": "CAP-35.c",
      "sha256": "cf16855d86b74db31bffde48825d00a4a0c693cc5fb995ee5ce426b028a4e18b",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "cf16855d86b74db31bffde48825d00a4a0c693cc5fb995ee5ce426b028a4e18b",
      "reason": "declared in sources",
      "tokens": 127
    },
    {
      "id": "DAEO-cv58",
      "sha256": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "e2e5d4a5e23069563439307229b66e4cf79481aaa0b89b1727af02a3fca47d34",
      "reason": "declared in sources",
      "tokens": 1529
    }
  ],
  "supplementary": [],
  "supplementary_query": "RUBRIC-2 at launch: criticality from criticality.yaml, the Launch by criticality line, the effort floor, trials, the second review's setting, promotion (from W2-60a)\nThe session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket's criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the launch line (--model, --effort) and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses the launch; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3), CAP-35.c lite, lens F R1] (folds W2-21 S4) [from W2-60a S3, DEC-1167]\nA model after -- that is not the resolved tier's is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session's tier model (CLAUDE_CODE_SUBAGENT_MODEL in the settings' env), as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after -- with no trial: refused naming both [DEC-1120 (3), lens E F14] (folds W2-21 S4) [from W2-60a S4, DEC-1167]\nThe launch record also holds `tier`, `criticality`, `model_source` (role default, by criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them null [DEC-1120 (3)] [from W2-60a S8, DEC-1167]\nOn a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [from W2-60a S10, DEC-1167]\nA ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [from W2-60a S11, DEC-1167]\nA model below its tier with no trial; a promotion not applied; an effort below the floor. Verify: S3 and S4's planted cases: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below high for a judgement role is refused [from W2-60a F4, DEC-1167]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 8876,
  "budget": {
    "limit": 24000,
    "used": 8876
  },
  "hash": "f49ef8ecb1e525d1692e2106aca65f987aa9895339b67e45b33801562b8ee2a8"
}
