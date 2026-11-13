---
type: probe
task: DAEO-52ku
reviewer_session: 1b3d373d-540c-4b53-975d-d80e0e2c560a
implementer_session: not recorded
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 2ef060a65c7712c11556b82eb8931f9b7222e32f
---

# Probe record: W2-149 (DAEO-52ku) The independent sessions' launch script, FULL review of the merged code (DEC-1010, DEC-1131)

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (session `1b3d373d-540c-4b53-975d-d80e0e2c560a`, Opus 5.5 at high, RUBRIC-2), commissioned by the CTO (orchestrator DAEO-sdxk, session b40cba91) on 2026-11-11, from the brief `.gov-runtime/scratch/orchestrator/briefs/W2-149-A3-probe.md`, launched in W2-149's worktree.
- **What was probed.** The merged code at w2/integrate's head `2ef060a65c77`, judged on all 42 KPI lines (DEC-1010, DEC-1131). No file under W2-149's allowed paths changed between that head and the close (git diff, empty).
- **Judged by the threat model (DEC-801, DEC-808, DEC-1010).** READY computed from the verdict block below: every line passes; no finding is in scope, reachable in ordinary work and failing open or losing work. Rows FR-1 to FR-4 are carried.

## The reviewer's record (as returned)

This is a full review of the launch script as merged at the head of `w2/integrate`, judged on all 42 of the ticket's KPI lines. Every line passes and nothing blocks.

These parts hold:
- Every refusal before the wall is built writes nothing.
- The seed comes first and the script draws it.
- The tree is plain and read-only.
- The canary and the launched command are as S9 and S10 state.
- No free text from a session reaches the counts, the output or the log.
- Deliveries land only at their flow's destination, all or nothing, and never after a stop or a bad result.
- The rule script runs confined.
- The overlap auditor's disputes arrive blind.

Every scoped test that can run in the sandbox passed. One probe of my own drove the script's own ten documented lines through the guard hook, which closes row F28's gap.

Four findings land as rows:
- **FR-1:** a memory checker or auditor re-run replaces its delivered file. S16's "existing destination refuses 20" is read here as set-up A's.
- **FR-2:** a set-up A writer's selection can name paths its tree leaves out. This is designed.
- **FR-3:** a failed pack leaves the wall in place. This is not ordinary work.
- **FR-4:** a reused variable name with no effect.

The known rows F16, F17, F24, F25, F27, F30, F37 and F40 were met again with no worse consequence than their records state.

```
task: W2-149 (DAEO-52ku): a FULL, read-only review of the merged launch script at w2/integrate's head 2ef060a65c77, judged on S1-S31 and F1-F11 (42 lines)
status: DONE — every line passes; no finding is in scope, ordinary work yes and fails open or loses work
work_completed: read the ticket whole; the script (2,456 lines) whole; kinds.yaml, tree-exclude.txt, the six template files, the ten schemas, the overlap auditor's brief, the acceptance README's interface, the S19 case and the unit test World; ran the scoped unit and acceptance tests through the gate; three probes (the guard hook driven with the script's 10 documented lines; a checker and an auditor delivered twice on planted roots; a search of the overlap auditor's would-be tree for the dispute-side tell); the rule-script prelude's seccomp filter checked instruction by instruction
files_changed: none
evidence: Step 0 held: the write outside the tree failed (read-only file system); the object write gave 1ae28402a109 and the index refresh exited 0. No ollama or llama-server process mine. Clone head 2ef060a65c77; nothing under the ticket's paths changed since 7b5c3cb94fd9 or 2f98aecbc525. Script sha256 90b943aef8be, kinds.yaml ddd84ae25910, tree-exclude.txt e8395088167e. Refusals: git grep of a revision (worked round as an open read, Grep over the clone's files without fixtures/); one probe command naming the sets root with indep-walls (taken; that half dropped). Scratch peak 126M, 7,762 inodes; removed.
tests: unit + acceptance with lifted,breadth and the exclusion: 326 passed, 0 failed, 38 skipped (3 live, 35 bwrap), 1 deselected (the stub-based S6 "real builds" case: run alone, 1 passed); unit alone without opt-ins: 90 passed, 3 skipped, 63 deselected
discoveries: the five set-up A documented lines pass the guard hook (F28 answered); no file in the auditor's tree states the dispute-side tell at this head (F40 stands); memory checker/auditor re-delivery replaces the earlier file (FR-1); a set-up A writer's selection can name excluded paths (FR-2)
risks: the bwrap cases and the live cases rest on the CTO's runs outside the sandbox
lessons: drive the guard with the lines taken from the script's own docstring, not a copy
proposed_decisions: none
unresolved: S16's existing-destination clause: set-up A's only (this record) or every kind (FR-1)
recommended_next_action: compute READY from the verdict block; FR-1 to FR-4 as rows
```

---

task: DAEO-52ku
decisions: DEC-801, DEC-802, DEC-803, DEC-808, DEC-1010, DEC-1131, DEC-1120, DEC-137, DEC-1101, DEC-1112, DEC-1113, DEC-1099, DEC-1097, DEC-1073, DEC-1064, DEC-1065, DEC-820
probed_commit: 2ef060a65c77

**Scope.** These files at head 2ef060a65c77:
- `governance/project/orchestration/tools/indep_launch.py`
- `governance/project/orchestration/tools/indep-schemas/**`
- `governance/project/indep-walls/kinds.yaml`
- `governance/project/indep-walls/tree-exclude.txt`
- `tests/unit/orchestration/test_w2_149*`
- `docs/changes/W2-149-evidence.md`

Reachable context, read to judge the lines:
- The template files of ACT-INDEP-WALLS-1: `settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`, `README.md`.
- `tests/acceptance/W2-149/**` and `.claude/hooks/pretooluse.py`.
- The set-up A briefs under `governance/project/indep-briefs/sgx1/`.

Nothing under the ticket's paths changed between 7b5c3cb94fd9 or 2f98aecbc525 and the head; the only change since 7b5c3cb94fd9 is `DECIDED-NOT-DONE.md`. Line numbers below are the script's at the head.

**Method.** All work ran from a fresh clone of `w2/integrate` under the sandbox's TMPDIR, with `PYTHONPATH=<clone>/src` and an empty planted HOME.
- **Tests (through the heavy-job gate).**
  - `tests/unit/orchestration/test_w2_149_indep_launch.py`, `test_w2_149_setup_a.py` and `tests/acceptance/W2-149/` were run with `GOV_TESTS_OPTIN=lifted,breadth` and `-m "not local_only" -k "not real and not green_here and not time_limit"`.
  - Result: 326 passed, 0 failed, 38 skipped, 1 deselected.
  - The 38 skips are 3 live cases (the CTO's) and 35 cases that need `GOV_W2_149_BWRAP=1` outside the sandbox.
  - The deselected case, `test_s6_two_real_builds_draw_different_63_bit_seeds`, is stub-based and was run alone: 1 passed.
  - The unit files alone without opt-ins: 90 passed, 3 skipped, 63 deselected.
- **Probe 1 (S19).** All 10 lines starting `python3 ` in the script's docstring (taken with `ast.get_docstring`) were each driven through the clone's `.claude/hooks/pretooluse.py` as an orchestrator Bash event (`GOV_ROLE=orchestrator`, `GOV_TICKET=W2-00`), with a planted HOME holding `gov-os-eval/`. 10 decisions.
- **Probe 2 (S16).** The unit tests' planted World (stub `claude`, planted HOME, sets root and repository) was imported read-only:
  - a memory checker launched twice for round 1 with different `out/notes.md`;
  - a memory auditor launched twice for audit `e0` with different `out/classes.json`.
  - 4 launches.
- **Probe 3 (S23, S27, row F40).** The clone's checked-out files outside every glob the overlap auditor's tree leaves out (`tree-exclude.txt` plus its `briefs:` entry) were searched for the class-14 tell (`rule_class.{0,40}14|class 14|class-14`), for `how.{0,6}script`, "script's side" and "x is labeller". `fixtures/` was not searched. 2 searches.
- **By hand.** The seccomp program of `RULES_PRELUDE` (lines 138-166) was checked instruction by instruction:
  - The arch check kills any architecture other than x86_64.
  - The x32 range returns EPERM.
  - The ten denied calls each return EPERM (jump arithmetic checked for d = 16): socket, socketpair, clone, fork, vfork, execve, unshare, setns, execveat, clone3.
  - Everything else is allowed.

**Probed and found sound.**
1. **S1, F1 (the brief).**
   - The brief's bytes come from `git cat-file` at the resolved `--commit` (lines 2126-2132) and must equal `--brief-sha256`.
   - An APPROVED `brief` line must agree on hash, kind and normalised path (line 2133). Any mismatch refuses 10.
   - Stage 10 runs before the run id and B1 (line 2196), so nothing is written: no wall, no tree, no SEEDS.log line.
2. **S2, F1 (the template).** Each of the six `TEMPLATE_FILES` (lines 67-68) is read at the commit and must match its `template` line exactly (a set holding one hash, lines 2108-2113), else 11, before anything is written. A tool beyond `TOOLS_OK` in `kinds.yaml` also refuses 11 (lines 618-637).
3. **S3, F2 (an empty wall only).**
   - B1 refuses 12 on a wall holding any entry, a link or a non-folder, and on an existing tree (lines 2208-2212). `st.built` is still False then, so `_after_refusal` packs nothing and removes nothing (lines 2446-2452).
   - After B1, every refusal and every unexpected error packs the wall and removes the tree (lines 2426-2443, 1931-1964), so no half-built wall survives for a later run. A later run takes a new run id (lines 1974-1983).
4. **S4, F3 (the seed first).**
   - `seed.txt` is written 0444 (line 2226).
   - Its SEEDS.log line, holding its sha256, is appended and fsynced after a clock tick (`wait_past`, lines 279-293, 2231-2236).
   - The tree folder and `input/` are made only after further ticks (lines 2238-2239).
   - `seed_check` refuses 13 unless seed mtime < ledger mtime < every file under `input/` and the tree, and no link exists (lines 2043-2066).
   - A tree or `input/` made before the script makes it refuses 13 (lines 1988-1989, 2274-2275).
5. **S5, F3 (the selection).**
   - `changed` is the `git diff --name-only --no-renames` paths present at the commit, less `tree-exclude.txt`.
   - `sample` is `random.Random(seed).sample` of the other tracked paths, sized by `sample` (lines 2251-2263).
   - The parser has no path-list option (lines 489-509).
6. **S6, F3.** `--seed` with an integer refuses 17 without `--dry` (lines 544-549). A real seed is `secrets.randbits(63)` (line 2224).
7. **S7 (the plain tree).**
   - The tree is built member by member from `git archive`, refusing 14 on an absolute name, `..`, a symlink, a hard link, a non-file and `.git` (lines 1997-2002).
   - Excluded paths are skipped. Files are 0444 (line 2015) and folders 0555 (lines 2024-2025).
   - A commit holding a link or submodule refuses 14 before anything is written (lines 2169-2174).
   - The trees folder may not lie under the sets root (lines 556-569).
   - The repository has no `.gitattributes`, so `export-subst` and `export-ignore` cannot change the archive.
8. **S8.**
   - `.claude/settings.json` is the template filled by `fill_text`. Its deny list gains every other kind's walls and every entry present in this kind's folder (lines 2304-2311), and its sha256 goes into WALL.json (line 2324).
   - `wall_hook.py` is copied byte for byte (line 2315).
   - The template's deny list holds each required class.
   - The F-class cases ran green.
9. **S9, F4 (the canary).**
   - The target lives in its own temporary folder, checked to be outside every root (lines 1333-1337), and is added with `--add-dir` for the canary only (line 1344). Restricted mode alone would therefore allow the Read (the CTO's reading 1).
   - Every other outcome refuses 16 before the session file exists: a non-zero exit, a timeout, unparseable output, `is_error`, or no Read of the target in `permission_denials` (lines 1347-1371).
10. **S10, F5 (the command).**
    - `session_flags` (lines 1088-1097) carries every flag the line names, in particular `--setting-sources project`, for the session and the canary alike.
    - The command runs under `timeout --kill-after` (lines 1343, 1381), from the wall, stdin `/dev/null`, with `start_new_session`.
    - The environment is `HOME PATH LANG USER` only (lines 1082-1085, 126).
    - The prompt's sha256 is checked at start (line 2416).
    - Tools, budget, timeout and model come from `kinds.yaml` and the front matter or its entry; a larger budget or timeout refuses 10 (lines 2139-2145).
11. **S11, S12.** The trace count looks at names only, at depth 1 or 2 under the four folders, keyed by the drawn and the reported ids (lines 1437-1458). It runs on every path once an id exists, and a non-zero count gives 22. The live cases are the CTO's (passed per the ticket's notes).
12. **S13, S28, F6 (counts only).**
    - The counts are filled from code: fixed words, validated ids, numbers through `is_count` and `is_number`, closed key sets (`copy_numbers` lines 1469-1484, `copy_sgx_numbers` lines 1486-1497).
    - The log takes only code words. Stderr prints status, code and reason.
    - `indep-counts.schema.json` and the five set-up A schemas are closed at every level with no free string (scanned). The four original result schemas are open at the top, but only their fixed numeric keys are copied.
13. **S14, S29, F7 (no delivery from a bad or stopped result).**
    - `check_result` refuses 20 on a missing, oversized, unreadable or schema-failing result, or a wrong `round`, before any delivery (lines 1900-1927).
    - A set-up A `stopped` other than `none` refuses 20 before the Landing exists (lines 1806-1807, 1919).
    - A timeout, a group kill or a budget subtype gives 21 with no delivery (lines 2359-2362).
14. **S15, S21, F9 (stops by pid).**
    - The session's pid and pgid are written to the counts folder (lines 1389-1392).
    - `stop_group` kills by `killpg` and waits until the group is gone (lines 1121-1138), on every exit (lines 1401-1405, 2435-2436). The rule script is handled the same way (lines 1299-1310).
    - There is no `pkill`, `killall` or `pgrep` in the script (searched).
15. **S16, F7, F11 (destinations).**
    - Memory kinds (lines 1549-1643): a writer's round 1 only into a missing `hidden/`, removed on failure; round 2 with round 1 moved aside, rolled back on failure and packed. A checker's or an auditor's file by a temporary name, hashed, renamed.
    - Set-up A (lines 1647-1716, 1801-1893): every destination by `Landing`, which refuses an existing file other than the auditor's `labels.jsonl` and `owner.jsonl`, writes temporary names read back, links or replaces them in turn, and undoes everything on failure.
    - Each flow's destination is as S16 lists it (`r1-<brief id>` gives `r1-sgx1-labeller` and `r1-sgx1-labeller-2` by `kinds.yaml`).
    - The set-up A path writes no `AUDITS.log` line.
16. **S17, F8 (packing).** `<run>.tar` is written 0400 by a temporary name, holding the wall, the session file and writer round 2's replaced files. Then the wall, the session file, the replaced files and the tree are removed (lines 1931-1964), after a delivery, a rejection, a stop and every refusal after B1.
17. **S18, F8 (the file budget).** The hidden walk plus the expected files (lines 2184, 1028-1032) is checked at stage 15, before B1, and refuses 15 over 8,000.
18. **S19.**
    - Probe 1: all 10 documented lines of the script, the five set-up A lines among them, are allowed to the orchestrator by the guard hook (10/10 allow). This answers row F28.
    - A `--sets-root` naming `indep-walls` refuses 17 (lines 518-524). An argument resolving under the root refuses 17 (lines 550-555).
19. **S20.** Labeller 2's round 2 stages exactly the staged lines with `by_rule(seed, "overlap", id, 10)`, where `str(seed)` equals `seed.txt` less its newline, with no `random.Random` (lines 1013-1017, 854-855). Its round 1 stages `input/half.json` only.
20. **S22.**
    - `resolve_brief` (lines 655-682) takes each value from the front matter, then the `briefs:` entry (which must hold the brief's kind and a known flow of that kind), then (model only) the kind.
    - A value found nowhere, a bad entry, or a labeller brief without an entry refuses 10.
21. **S23.**
    - A set-up A tree leaves out `tree-exclude.txt` plus the entry's `tree_exclude` (line 2158). The memory kinds keep `tree-exclude.txt` only (line 2161).
    - `kinds.yaml`'s entries hold the globs S23 names, the overlap auditor's six extra ones included.
    - The prefix matching (lines 690-699) covers `**` folders.
    - Probe 3: no file in the auditor's would-be tree states the dispute-side tell at this head. Row F40 stands.
22. **S24.**
    - `plan_sgx` (lines 941-974) reads every input at stage 10, before anything is written: `staged_half` keeps the brief's fields (lines 814-838); writer 2's seal follows the path map at the commit (lines 1035-1053); round 2's files must match round 1's counts (lines 858-884).
    - `--set` and `--round` outside the flow's values refuse 17 (lines 2152-2155).
23. **S25, F11 (the rule script, confined).**
    - It runs under bwrap with every namespace unshared, no network, `--cap-drop ALL`, read-only binds and a read-only root (lines 1187-1194, 1163-1184).
    - The interpreter is the pinned one with `-I`. Hard rlimits apply: no process, no file size, CPU 15 s, address space 1 GiB, 32 files. The seccomp filter is the one checked above.
    - Limits: wall clock 20 s and an output cap (lines 1267-1311).
    - Every staged id must come back exactly once and valid (lines 1233-1257).
    - At round 2 a failure is 18 before B1 (lines 2189-2194). At round 1's delivery it is 20 before any file lands (lines 1819-1823). No bwrap or no interpreter is 18 (lines 1142-1160).
24. **S26.** `merge_labels` (lines 1732-1753) requires a valid hand line for every uncertain, class 1-13 and sample id, then writes one line per staged id, hand over script, with `how`.
25. **S27, F11 (the blind audit).**
    - Disputes are the first 40 by id that differ and were not decided earlier (lines 965-969).
    - The x/y order is drawn with `random.Random(seed)` and every reason is blanked (lines 987-1000).
    - The map is written only at delivery (line 1866).
    - Tickets carry exactly `id role wbs_id allowed_paths` from `.tickets/` at the commit (lines 913-938).
    - Decisions are checked strictly, then mapped back, settled or flagged, with history kept (lines 1759-1775, 1843-1893).
    - No AUDITS.log line.
26. **S30.** `check_labels2` (lines 1781-1798) requires exactly the sample ids, once each, exactly the six keys, `how` `hand`, and stores `rule_class` as an integer.
27. **S31.** `rule_class` (lines 841-851) accepts an integer 1-14 (not a boolean) or `"1"`-`"14"` matched in full. It is used by every checking function (lines 1245, 1727, 1768, 1792), and every written file stores an integer.
28. **F10.** Every test runs on planted roots. The one reference to the real home (`test_f10_every_launch_runs_on_planted_roots`) only asserts that the planted check rejects it; nothing is opened.

**Findings** (all rows)

- **FR-1 (S16).** A memory checker launched a second time for the same round replaces the delivered `fixtures/evaluation/<set>/XCHECK-r<round>.md`, and an auditor run a second time for the same audit replaces `runs/<audit>/miss-classes.json` and adds a second `AUDITS.log` line. `deliver_file` (lines 1532-1546) renames over an existing plain file. Shown by Probe 2: both re-runs exit 0, `delivered`, and the file holds the second run's text. S16's "an existing destination file (other than the auditor's labels.jsonl and owner.jsonl) refuses 20" is read here as set-up A's clause: it was added with set-up A, its exception names only set-up A files, the acceptance README places it in set-up A's delivery section, and a general reading would contradict the memory writer's round 2, which replaces `hidden/` by design. On that reading the line is met.
  - scope: in
  - Ordinary work: yes, because the CTO can re-run a checker round or an audit after a first delivery.
  - Consequence: other (the replaced file stays in the earlier run's 0400 tar as its `out/` file; nothing fails open)
  - Reversed by: a ruling that the clause holds for every kind. S16 would then not be met, and a fix would refuse an existing checker or auditor destination with 20.
- **FR-2 (S5, S23).** A set-up A writer's `selection.json` is chosen by S5's rule, less `tree-exclude.txt` only (line 2121, line 2269). Its tree also leaves out the entry's `tree_exclude` globs (line 2158), so a sampled path may name a file the wall cannot read (for example under `src/gov/guard/`).
  - scope: in
  - Ordinary work: yes, because any set-up A writer run samples from the whole tracked list.
  - Consequence: other (names only; the excluded files stay out of the tree; the README fixes "the selection of a set-up A writer stays S5's")
  - Reversed by: none needed. If wanted, the sample could be drawn less `tree_ex`, which would change S5's stated rule.
- **FR-3 (S17, F8).** When `pack` fails, it removes the tree but leaves the wall folder and the session file in place (lines 1949-1955). This happens when the disk is full, or when the tar's name is already taken because `choose_run` fell through after five colliding seconds (line 1983). The hidden part then grows by the wall's files, not by one.
  - scope: in
  - Ordinary work: no, because it needs a full disk or five consecutive seconds of colliding run ids for one kind, set and round (compare row F27).
  - Consequence: other (the wall is not built into again; the next launch's file budget counts it)
  - Reversed by: an ordinary path that makes the tar's name exist or `tarfile` fail.
- **FR-4 (S22).** `build_and_run` reuses the name `entry`, which holds the `briefs:` entry, as the loop variable over `ls-tree` lines (line 2172). Its only later use, WALL.json's `brief_id` (line 2328), gives the same value either way, and `tree_ex` and `flow` are computed before the loop (lines 2140, 2158).
  - scope: in
  - Ordinary work: yes, because every launch runs the loop.
  - Consequence: other (no effect today; a trap for a later edit that reads `entry` after line 2172)
  - Reversed by: none needed; rename the loop variable when the script is next touched (DEC-802).

Known rows met again, with no worse consequence than their records state:
- F37: a round-1 rule rejection logs `rejected rules` without the check's word (lines 1822-1823).
- F40: shown sound at this head by Probe 3.
- F16, F17: `--setting-sources project` beside `--restricted`; the stub's model.
- F24: the rule script's overrides `GOV_INDEP_BWRAP` and `GOV_INDEP_RULES_PYTHON` are not recorded (lines 1145-1149).
- F25: all of `/usr` is bound (line 1169).
- F27: same-second run ids.
- F30: S18's estimate.
- Round 2's F2 and F11: with the owner.

**Classification:** 0 yes/fails open or loses work; 3 yes/other (FR-1, FR-2, FR-4); 1 row marked no (FR-3).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "FR-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": []}, {"kpi": "S12", "verdict": "pass", "findings": []}, {"kpi": "S13", "verdict": "pass", "findings": []}, {"kpi": "S14", "verdict": "pass", "findings": []}, {"kpi": "S15", "verdict": "pass", "findings": []}, {"kpi": "S16", "verdict": "pass", "findings": [{"id": "FR-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S17", "verdict": "pass", "findings": [{"id": "FR-3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S18", "verdict": "pass", "findings": []}, {"kpi": "S19", "verdict": "pass", "findings": []}, {"kpi": "S20", "verdict": "pass", "findings": []}, {"kpi": "S22", "verdict": "pass", "findings": [{"id": "FR-4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S23", "verdict": "pass", "findings": []}, {"kpi": "S24", "verdict": "pass", "findings": []}, {"kpi": "S25", "verdict": "pass", "findings": []}, {"kpi": "S26", "verdict": "pass", "findings": []}, {"kpi": "S27", "verdict": "pass", "findings": []}, {"kpi": "S28", "verdict": "pass", "findings": []}, {"kpi": "S29", "verdict": "pass", "findings": []}, {"kpi": "S30", "verdict": "pass", "findings": []}, {"kpi": "S31", "verdict": "pass", "findings": []}, {"kpi": "S21", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": []}, {"kpi": "F6", "verdict": "pass", "findings": []}, {"kpi": "F7", "verdict": "pass", "findings": []}, {"kpi": "F8", "verdict": "pass", "findings": []}, {"kpi": "F9", "verdict": "pass", "findings": []}, {"kpi": "F10", "verdict": "pass", "findings": []}, {"kpi": "F11", "verdict": "pass", "findings": []}]}
```
