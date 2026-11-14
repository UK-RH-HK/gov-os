{
  "ticket": "DAEO-cv58",
  "ticket_text": "---\nid: DAEO-cv58\nstatus: in_progress\ndeps: []\nlinks: []\ncreated: 2026-10-29T15:55:50Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-60a\ntags: [wave-2, implementation, full, launch, roles, keystone-3]\nwbs_id: W2-60a\ntitle: 'The role, its skills and its model and effort loaded at launch; the launch record'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/launch/launcher.py\n- src/gov/launch/role.py\n- src/gov/launch/record.py\n- src/gov/launch/criticality.py\n- governance/project/criticality.yaml\n- tests/unit/launch/test_role*\n- tests/unit/launch/test_launch_record*\n- tests/unit/launch/test_runs.py\n- tests/unit/launch/test_w1_28.py\n- tests/unit/launch/test_w1_32.py\n- docs/changes/W2-60a-CIT-E.md\n- docs/research/W2-60-rules-probe.md\n- tests/acceptance/W2-50/w2_50_support.py  # the merge of integrate: conflict resolution by a test designer (DEC-1157 (12))\n- tests/acceptance/W2-58/README.md  # the same\n- tests/acceptance/W2-58/test_w2_58_launched_sessions.py  # the same\n- tests/acceptance/W2-58/w2_58_support.py  # the same\n- tests/unit/launch/test_w2_136_plan_check.py  # older fixtures planting no role file (DEC-1156 (7), P-3)\n- tests/unit/launch/test_w2_153_template.py  # the same\n- tests/unit/launch/test_w2_56.py  # the same\n- tests/acceptance/W2-153/test_w2_153_launch.py  # the same; the appended-file value and line asserts (P-3, P-4 (A))\n- tests/acceptance/W2-56/test_w2_56_environment.py  # the same\n- tests/acceptance/W2-56/test_w2_56_endings.py  # the same\n- tests/acceptance/W2-56/test_w2_56_refused_arguments.py  # the same\nkpis:\n  success:\n  - 'gov launch <role> <ticket> starts the session as its role: the role''s text (its generated agent, or the role file''s text appended) is in the session''s context at its start, shown by a launched session''s log; the launch record holds the role file''s path, version and content hash. Verify: a planted role file and a launch of that role: the session''s first context names the role''s text, and the launch record holds the file''s path, version and sha256 [DEC-826 Q1, lens E F2] [Verify clause added, DEC-1157 (12)]'\n  - 'The skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those, so the engineer''s skill packs load with no code change once W2-33 writes them; a named skill that is missing refuses the launch. Verify: a planted role file naming two skills: the launch record lists each with its name, version and sha256 from the loaded copy; the same file naming a missing skill: the launch is refused naming it [DEC-826 Q1, DEC-832 item 1, lens E F15] [Verify clause added, DEC-1157 (12)]'\n  - 'The role''s default model and effort, read from its role file''s `Launch default` line, are applied on the launch line (--model, --effort) and recorded with `model_source` (role default, or after --); a missing or malformed default line refuses the launch; an effort given after -- is applied and recorded as the launch''s own. Verify: a planted role file''s default line is applied and recorded; a missing or malformed line is refused naming the file; an effort after -- is recorded as the launch''s own (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1, 2 and 5, CAP-35.c lite, lens F R1] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2''s form moved to W2-184]'\n  - 'A model given after -- that is not the role''s is refused, naming both; the subagent model is set to the session''s model (CLAUDE_CODE_SUBAGENT_MODEL in the settings'' env) and recorded. Verify: a model after -- that is not the role''s is refused naming both; the planted launch''s settings carry CLAUDE_CODE_SUBAGENT_MODEL equal to its model, recorded (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1 and 3, lens E F14] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; the trial moved to W2-184]'\n  - 'No launch sets a compaction threshold: no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the settings or the session''s environment, one given after -- refused; the launch record states the threshold as none. Verify: the launch line and settings of a planted launch hold no --autocompact and no CLAUDE_CODE_AUTO_COMPACT_WINDOW; one given after -- is refused; the record says none [DEC-838 items 1 and 2] [Verify clause added, DEC-1157 (12)]'\n  - 'A launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session''s start; what the CLI gives no switch for is a package naming it, never passed silently. Verify: a test home planted with one connector, one user-level agent, one user-level skill and model-side memory: a launched session''s start shows none of them [DEC-826 Q5, lens E R6] (folds W2-21 S4) [Verify clause added, DEC-1157 (12)]'\n  - 'The arguments the launcher now sets itself are refused after --: --agent, --append-system-prompt and its file form, --session-id. Verify: a launch with each of these after --: each is refused, naming the argument [lens E R6, DEC-826 Q5] [Verify clause added, DEC-1157 (12)]'\n  - 'Every launch writes one launch record, keyed by the session id the launcher gives with --session-id, before the session starts: role, ticket, the ticket''s class, model, effort, subagent model, threshold none, the role text''s and each skill''s version and hash, the CLI''s version and the start time; in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch. Verify: a planted launch writes exactly one record under its --session-id holding every field named here, before the session starts; with the record folder unwritable the launch is refused (tests/acceptance/W2-60a/test_w2_60a_launch_record.py) [DEC-826 Q1, CAP-36.a lite, lens F R6] (folds W2-21 S3, its launch record) [restored by P1-W2-60a-P5 (B), DEC-1167; tier, criticality, trial and promotion fields moved to W2-184]'\n  - 'Research first, by the lead before the engineer starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker started by gov launch, its token cost, and whether the worker can change it; recorded in docs/research/W2-60-rules-probe.md. Verify: the research record exists and answers the three questions, each with its evidence [lens G Q4] [Verify clause added, DEC-1157 (12)]'\n  - 'On a FULL ticket that could fail open, the second review is launched with a different model or effort setting from the first, taken from the role defaults; the launch record shows both, and the same setting twice is refused unless the owner named it. Verify: a planted FULL ticket''s two review launches record different settings; the same setting twice is refused unless an owner-named decision is given [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3] [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2''s Opus high then max moved to W2-184]'\n  - 'Routed from W2-33 (its S2, DEC-1156 (3)): the launcher''s plan for a planted ticket prints the model and effort of the role file''s `- **Launch default:**` line (W2-33''s line form). Verify: a planted ticket whose role file says `model claude-sonnet-5-5, effort high`: the plan prints that model and effort; a role file without the line fails the plan naming the file [DEC-954, DEC-957, DEC-1156 (3)]'\n  failure:\n  - 'A launch that starts with no role text, an unrecorded skill, a model not the role''s, a compaction threshold, a user-level agent, skill or connector, or model-side memory. Verify: S1, S2, S3, S5 and S6''s planted cases: none of these launches starts [Verify clause added, DEC-1157 (12)]'\n  - 'A role file without its default line that still launches; a launch with no record, or a record naming another session. Verify: a planted role file without its Launch default line is refused; every planted launch has its record, keyed by its own session id [Verify clause added, DEC-1157 (12)]'\n  - 'A refusal the launcher makes today that no longer refuses. Verify: the launcher''s existing refusal cases under tests/unit/launch/ pass unchanged on the branch [Verify clause added, DEC-1157 (12)]'\nprofile: FULL\nsources:\n- DEC-826\n- DEC-838\n- DEC-839\n- DEC-832\n- DEC-801\n- DEC-786\n- DEC-941\n- CAP-35.c\n- CAP-36.a\n- DEC-1014\n- DEC-1015\n- DEC-1119\n- DEC-1120\n- DEC-1126\nest_loc: 250\nacceptance_tests:\n  path: tests/acceptance/W2-60a/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\nlist_rows: []\n---\n# W2-60a The role, its skills and its model and effort loaded at launch; the launch record\n\nCard: the draft card `W2-60` (W2-60a part), from the accepted plan (`docs/plan/WAVE_2_REVISED_PLAN.md` \u00a74.3, \u00a72 row 5 and the CAP-35.c and CAP-36.a lite rows; DEC-826 Q1 and Q5, DEC-838, DEC-839); keystone 3, agents know what to do. Started now by the re-plan the owner accepted on 2026-10-29 (DEC-941), beside the memory work.\n\n- **Why:** a launched session loads none of its role's text (lens E F2). No launch sets effort, and the compaction threshold was a user-level value (lens F F1). The model a subagent runs on is not the one recorded (lens E F14), and the loaded skill copy has no version (lens E F15). Until this lands, the prompt's launch forms carry the values by hand (prompt v3 \u00a76, DEC-839 item 5).\n- **Profile FULL (the plan said STANDARD):** this ticket rewrites the CLI line and the settings that carry the sandbox. It also keeps connectors out, and connectors run outside the sandbox with network. A mistake here fails open in ordinary work (DEC-801).\n- **Place:** starts as soon as filed (DEC-941), stacked on `w2/integrate` (DEC-786), where W2-58's launcher is merged (`af5d1a25`). It runs beside W2-56 on `launcher.py`: each keeps its work in modules of its own and touches `launcher.py` at its call sites and argument checks only, and the second to merge merges the first back first. W2-05 (`DAEO-0z8c`) holds `src/gov/**/*.py` for git-environment lines only, so those lines are left alone. W2-21 follows. W2-60b follows it.\n- **Merges after the role files carry their default line** (model and effort, no threshold), which W2-33's widening writes through CIT-P (DEC-839 item 5). It is built and tested against fixture role files until then.\n- **Paths:** `launcher.py` for the CLI line, the settings' env lines it sets, its argument checks and the calls only. The probe record is the lead's. The role files, generated agents and skills are not in the paths (W2-11, W2-33).\n- **The test designer's files** (MR-3): `tests/acceptance/W2-60a/**`.\n\n## Interface for run 4's additions (the CTO, at claim, DEC-1157 (3), (12); 2026-11-13 01:25)\n\n- **S12, the launcher's plan (P-2 (A)):** `gov launch --plan <role> <ticket>` prints one line `model <id>, effort <e>` read from the role file's `- **Launch default:**` line (W2-33's line form; with `- **Launch by criticality:**` applied for the ticket's class where the file has it) and exits 0, starting nothing; a role file without the line refuses with `LAUNCH_REFUSED` naming the file (exit 2). About 40 lines and one case.\n- **The role text and the template in one appended file (P-4 (A), kept):** the role file's text, one blank line, then the template's bytes; W2-153's value and whole-line asserts are revised to that form (P-3).\n- **Older cases (P-3, DEC-1156 (7)):** a test designer plants a role file (and, for W2-60a's own suite, the template and an open gate file) in the fixtures of W2-136, W2-153 and W2-56 listed in the paths, and revises W2-153's appended-file asserts to \"the one appended file starts with the role text and ends with the template's bytes\"; each with its Rewrite-Reason; no case loses its point.\n- **The merge's four acceptance conflicts** (W2-50's and W2-58's files in the paths): resolved by a test designer keeping both sides' cases.\n\n",
  "authority": [
    {
      "id": "DEC-826",
      "sha256": "32305de690255923f4099d533b06df1471c6df5a613d78606f0e41f7a3664020",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32305de690255923f4099d533b06df1471c6df5a613d78606f0e41f7a3664020",
      "reason": "declared in sources",
      "tokens": 447
    },
    {
      "id": "DEC-838",
      "sha256": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "reason": "declared in sources",
      "tokens": 321
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
      "id": "DEC-832",
      "sha256": "50fb9bc6e73bda99645f24ecffbcaa84a79508044eb679e1e710a4ca8cd9e9b3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "50fb9bc6e73bda99645f24ecffbcaa84a79508044eb679e1e710a4ca8cd9e9b3",
      "reason": "declared in sources",
      "tokens": 391
    },
    {
      "id": "DEC-801",
      "sha256": "d1d4ef638deffe7a94afd381a4e6b87a25fab66d17d680b3eaf9d47dcbad200e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d1d4ef638deffe7a94afd381a4e6b87a25fab66d17d680b3eaf9d47dcbad200e",
      "reason": "declared in sources",
      "tokens": 478
    },
    {
      "id": "DEC-786",
      "sha256": "2bee76d135bda19ee91d6431a3636e86d7819cabb014ab63656e44a4f16cbb8f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2bee76d135bda19ee91d6431a3636e86d7819cabb014ab63656e44a4f16cbb8f",
      "reason": "declared in sources",
      "tokens": 211
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
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
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
      "id": "DEC-1126",
      "sha256": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "reason": "declared in sources",
      "tokens": 662
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
      "id": "CAP-36.a",
      "sha256": "320c6a5033882d5aa7d9edcc7182b5ebfc1e3ee666ba3ff242b37899f9d18bb5",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "320c6a5033882d5aa7d9edcc7182b5ebfc1e3ee666ba3ff242b37899f9d18bb5",
      "reason": "declared in sources",
      "tokens": 164
    }
  ],
  "mandatory": [
    {
      "id": "DEC-826",
      "sha256": "32305de690255923f4099d533b06df1471c6df5a613d78606f0e41f7a3664020",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "32305de690255923f4099d533b06df1471c6df5a613d78606f0e41f7a3664020",
      "reason": "declared in sources",
      "tokens": 447
    },
    {
      "id": "DEC-838",
      "sha256": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "6eb4e599ac060506d5aaaf5ccc76fe4cf25096258c4ebb8be08bee1651a90fdc",
      "reason": "declared in sources",
      "tokens": 321
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
      "id": "DEC-832",
      "sha256": "50fb9bc6e73bda99645f24ecffbcaa84a79508044eb679e1e710a4ca8cd9e9b3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "50fb9bc6e73bda99645f24ecffbcaa84a79508044eb679e1e710a4ca8cd9e9b3",
      "reason": "declared in sources",
      "tokens": 391
    },
    {
      "id": "DEC-801",
      "sha256": "d1d4ef638deffe7a94afd381a4e6b87a25fab66d17d680b3eaf9d47dcbad200e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "d1d4ef638deffe7a94afd381a4e6b87a25fab66d17d680b3eaf9d47dcbad200e",
      "reason": "declared in sources",
      "tokens": 478
    },
    {
      "id": "DEC-786",
      "sha256": "2bee76d135bda19ee91d6431a3636e86d7819cabb014ab63656e44a4f16cbb8f",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2bee76d135bda19ee91d6431a3636e86d7819cabb014ab63656e44a4f16cbb8f",
      "reason": "declared in sources",
      "tokens": 211
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
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
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
      "id": "DEC-1126",
      "sha256": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "194ea0230dcf92e243da9af052f20deb6f47fa79b8311aca83e4cc6ecdffc413",
      "reason": "declared in sources",
      "tokens": 662
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
      "id": "CAP-36.a",
      "sha256": "320c6a5033882d5aa7d9edcc7182b5ebfc1e3ee666ba3ff242b37899f9d18bb5",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "320c6a5033882d5aa7d9edcc7182b5ebfc1e3ee666ba3ff242b37899f9d18bb5",
      "reason": "declared in sources",
      "tokens": 164
    }
  ],
  "supplementary": [
    {
      "id": "a77aea769abab1e9e4fdab50",
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "text": "| src/gov/launch/launcher.py (main tree) | no model or effort logic: arguments after `--` pass verbatim | C2 (C3, section 3) | **KPI** (W2-60a); its branch already has the subagent env (launcher.py:439) and record (:457-459) in the worktree |\n| w2/W2-60a worktree: tests/acceptance/W2-60a/w2_60a_support.py:93-105; test_w2_60a_model_and_effort.py:33-42, 59-67, 101-114, 143-158; test_w2_60a_kept_out.py:79; test_w2_60a_launch_record.py:49,75; README S3, S4, 201-206 | one default per role (O/O/Om/S-medium/O-low fixtures); a Sonnet or Haiku engineer refused; subagent model = session model; record fields | C3 | **KPI** then designer revision (section 3). Main tree has no `tests/acceptance/W2-33` or `W2-60a` |\n| `.tickets/DAEO-cv58.md`:33, 34, 40, 69, 72; `.tickets/DAEO-lrre.md`:27 | role default, \"a model not the role's refused\", second review; DEC-839 items | C1 | **KPI** (section 3) |\n| `.tickets/DAEO-ecac.md`:28 (W2-60b) | session record: model, effort, task class from W2-60a's record | C2 | **KPI**: add tier, criticality, promotion (record only) |\n",
      "tokens": 266
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "  - A launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session's start; what the CLI gives no switch for is a package naming it, never passed silently [DEC-826 Q5; lens E R6].\n  - The arguments the launcher now sets itself are refused after `--`: `--agent`, `--append-system-prompt` and its file form, `--session-id` [lens E R6].\n  - Every launch writes one launch record, keyed by the session id the launcher gives with `--session-id`, before the session starts: role, ticket, the ticket's class, model, effort, subagent model, threshold none, the role text's and each skill's version and hash, the CLI's version and the start time; in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch [DEC-826 Q1; CAP-36.a lite; lens F R6].\n  - **Research first,** by the lead before the engineer starts: whether a `paths:`-scoped `.claude/rules/` file loads in a headless worker started by `gov launch`, its token cost, and whether the worker can change it; recorded in `docs/research/W2-60-rules-probe.md` [lens G Q4].\n",
      "tokens": 296
    },
    {
      "id": "35fdc31aefbef2f221fa27a8",
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "text": "orchestrator, leads, senior engineers Oh; engineer Sh (C3 Oh); test designer C3 Oh, else Sh; QA engineer (the reviewer) C3 Oh, C2 Oh if FULL else Sh, C1 Sh;\nindependent auditor Oh; product-spec, research Sh; the `Model tier` field stays and names the line [DEC-1120 (2), W1-33]. The through-D-10 rule is not\nwritten into a role file; it is the CTO's launch practice until the lift ends. Verify: a test per role file reads both lines and the values equal the table; the\ngenerated agents carry the same [W2-153 S3].\" (The QA engineer's split from the auditor, already in W2-33's KPI 3, is what lets reviews vary by class.)\n\n**Tests to revise (DEC-866).** W2-60a's acceptance tests (worktree files above): `DEFAULTS` becomes the table by criticality; the \"Sonnet or Haiku engineer refused\"\ncases (`test_w2_60a_model_and_effort.py:105-114`) become \"refused unless trial or tier\"; the subagent-model, launch-record (tier, criticality, promotion)\nand README rows S3, S4, 201-206 follow. By an independent test designer (Opus high), in the tests worktree, `Rewrite-Reason: DEC-1120`, never the\n",
      "tokens": 272
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "#### W2-60a The role, its skills and its model and effort loaded at launch; the launch record (FULL, engineer; DEC-826 Q1 and Q5, DEC-838, DEC-839, DEC-832; keystone 3)\n- **Ticket file:** `DAEO-cv58`.\n- **Allowed paths:** `src/gov/launch/launcher.py` (the CLI line, the settings' env lines it sets, its argument checks, and the calls to the new modules only), `src/gov/launch/role.py` (new), `src/gov/launch/record.py` (new), `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*`, `docs/changes/W2-60a-CIT-E.md`, `docs/research/W2-60-rules-probe.md` (the lead's probe record).\n- **KPIs, success:**\n  - `gov launch <role> <ticket>` starts the session as its role: the role's text (its generated agent, or the role file's text appended) is in the session's context at its start, shown by a launched session's log; the launch record holds the role file's path, version and content hash [DEC-826 Q1, lens E F2].\n",
      "tokens": 232
    }
  ],
  "supplementary_query": "The role, its skills and its model and effort loaded at launch; the launch record\ngov launch <role> <ticket> starts the session as its role: the role's text (its generated agent, or the role file's text appended) is in the session's context at its start, shown by a launched session's log; the launch record holds the role file's path, version and content hash. Verify: a planted role file and a launch of that role: the session's first context names the role's text, and the launch record holds the file's path, version and sha256 [DEC-826 Q1, lens E F2] [Verify clause added, DEC-1157 (12)]\nThe skills the session can load are in the launch record, each with its name, version and content hash, taken from the copy the session loads; a role file that names its skills gets those, so the engineer's skill packs load with no code change once W2-33 writes them; a named skill that is missing refuses the launch. Verify: a planted role file naming two skills: the launch record lists each with its name, version and sha256 from the loaded copy; the same file naming a missing skill: the launch is refused naming it [DEC-826 Q1, DEC-832 item 1, lens E F15] [Verify clause added, DEC-1157 (12)]\nThe role's default model and effort, read from its role file's `Launch default` line, are applied on the launch line (--model, --effort) and recorded with `model_source` (role default, or after --); a missing or malformed default line refuses the launch; an effort given after -- is applied and recorded as the launch's own. Verify: a planted role file's default line is applied and recorded; a missing or malformed line is refused naming the file; an effort after -- is recorded as the launch's own (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1, 2 and 5, CAP-35.c lite, lens F R1] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2's form moved to W2-184]\nA model given after -- that is not the role's is refused, naming both; the subagent model is set to the session's model (CLAUDE_CODE_SUBAGENT_MODEL in the settings' env) and recorded. Verify: a model after -- that is not the role's is refused naming both; the planted launch's settings carry CLAUDE_CODE_SUBAGENT_MODEL equal to its model, recorded (tests/acceptance/W2-60a/test_w2_60a_model_and_effort.py) [DEC-839 items 1 and 3, lens E F14] (folds W2-21 S4) [restored by P1-W2-60a-P5 (B), DEC-1167; the trial moved to W2-184]\nNo launch sets a compaction threshold: no --autocompact on the line, no CLAUDE_CODE_AUTO_COMPACT_WINDOW in the settings or the session's environment, one given after -- refused; the launch record states the threshold as none. Verify: the launch line and settings of a planted launch hold no --autocompact and no CLAUDE_CODE_AUTO_COMPACT_WINDOW; one given after -- is refused; the record says none [DEC-838 items 1 and 2] [Verify clause added, DEC-1157 (12)]\nA launched session loads no connectors, no user-level agents or skills and no model-side memory: a test home planted with one of each shows none in the session's start; what the CLI gives no switch for is a package naming it, never passed silently. Verify: a test home planted with one connector, one user-level agent, one user-level skill and model-side memory: a launched session's start shows none of them [DEC-826 Q5, lens E R6] (folds W2-21 S4) [Verify clause added, DEC-1157 (12)]\nThe arguments the launcher now sets itself are refused after --: --agent, --append-system-prompt and its file form, --session-id. Verify: a launch with each of these after --: each is refused, naming the argument [lens E R6, DEC-826 Q5] [Verify clause added, DEC-1157 (12)]\nEvery launch writes one launch record, keyed by the session id the launcher gives with --session-id, before the session starts: role, ticket, the ticket's class, model, effort, subagent model, threshold none, the role text's and each skill's version and hash, the CLI's version and the start time; in one folder every worktree of the repository shares, stated in the CIT-E; a record that cannot be written refuses the launch. Verify: a planted launch writes exactly one record under its --session-id holding every field named here, before the session starts; with the record folder unwritable the launch is refused (tests/acceptance/W2-60a/test_w2_60a_launch_record.py) [DEC-826 Q1, CAP-36.a lite, lens F R6] (folds W2-21 S3, its launch record) [restored by P1-W2-60a-P5 (B), DEC-1167; tier, criticality, trial and promotion fields moved to W2-184]\nResearch first, by the lead before the engineer starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker started by gov launch, its token cost, and whether the worker can change it; recorded in docs/research/W2-60-rules-probe.md. Verify: the research record exists and answers the three questions, each with its evidence [lens G Q4] [Verify clause added, DEC-1157 (12)]\nOn a FULL ticket that could fail open, the second review is launched with a different model or effort setting from the first, taken from the role defaults; the launch record shows both, and the same setting twice is refused unless the owner named it. Verify: a planted FULL ticket's two review launches record different settings; the same setting twice is refused unless an owner-named decision is given [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3] [restored by P1-W2-60a-P5 (B), DEC-1167; RUBRIC-2's Opus high then max moved to W2-184]\nRouted from W2-33 (its S2, DEC-1156 (3)): the launcher's plan for a planted ticket prints the model and effort of the role file's `- **Launch default:**` line (W2-33's line form). Verify: a planted ticket whose role file says `model claude-sonnet-5-5, effort high`: the plan prints that model and effort; a role file without the line fails the plan naming the file [DEC-954, DEC-957, DEC-1156 (3)]\nA launch that starts with no role text, an unrecorded skill, a model not the role's, a compaction threshold, a user-level agent, skill or connector, or model-side memory. Verify: S1, S2, S3, S5 and S6's planted cases: none of these launches starts [Verify clause added, DEC-1157 (12)]\nA role file without its default line that still launches; a launch with no record, or a record naming another session. Verify: a planted role file without its Launch default line is refused; every planted launch has its record, keyed by its own session id [Verify clause added, DEC-1157 (12)]\nA refusal the launcher makes today that no longer refuses. Verify: the launcher's existing refusal cases under tests/unit/launch/ pass unchanged on the branch [Verify clause added, DEC-1157 (12)]",
  "further_batch": [
    {
      "id": "DAEO-6f0s",
      "path": ".tickets/DAEO-6f0s.md"
    },
    {
      "id": "DAEO-6f0s",
      "path": ".tickets/DAEO-6f0s.md"
    },
    {
      "id": "487c15ace9204c9fc37fd9f9",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
    },
    {
      "id": "b8aea606480a92a577b3c117",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
    },
    {
      "id": "84f315c28c271cfa48f9f2df",
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
    },
    {
      "id": "DAEO-6f0s",
      "path": ".tickets/DAEO-6f0s.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "a77aea769abab1e9e4fdab50",
          "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "35fdc31aefbef2f221fa27a8",
          "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "DAEO-6f0s",
          "path": ".tickets/DAEO-6f0s.md"
        },
        {
          "id": "DAEO-6f0s",
          "path": ".tickets/DAEO-6f0s.md"
        },
        {
          "id": "487c15ace9204c9fc37fd9f9",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
        },
        {
          "id": "b8aea606480a92a577b3c117",
          "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md"
        },
        {
          "id": "84f315c28c271cfa48f9f2df",
          "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md"
        },
        {
          "id": "DAEO-6f0s",
          "path": ".tickets/DAEO-6f0s.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "487c15ace9204c9fc37fd9f9",
      "reason": "budget exceeded"
    },
    {
      "id": "84f315c28c271cfa48f9f2df",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6f0s",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6f0s",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6f0s",
      "reason": "budget exceeded"
    },
    {
      "id": "b8aea606480a92a577b3c117",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-cv58): 1 paths, 1 chunks; 1 by role_paths.engineer.reads_denied {ticket_tests} (the ticket's cases revised in other folders) (DEC-1065 (2))"
    }
  ],
  "tokens": 11777,
  "budget": {
    "limit": 12000,
    "used": 11777
  },
  "left_out": {
    "count": 1,
    "superseded": [
      "DEC-636"
    ],
    "done": []
  },
  "hash": "3561b4c584ee0b6713e557615e3fc189a2a56f0a6e093306ee053c0aae531fb5"
}
