# Lead brief: FM-1 proven in the real writer launch (a fix under W2-204; it gates the 0.1.6 patch release)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies**, in particular never open a hidden sets root and never glob `/home/usain/*`. Decide, never ask (I-10). Use the `systematic-debugging` skill.

## Why
The owner's order (DEC-1248 (1)): "every writer's questions are form-checked by code before its session ends, with any refused question returned to it to fix". The fix landed on `w2/integrate` as `2ff945336` (read `.gov-runtime/scratch/orchestrator/log/landings/fix-memaudit-20261124.md` and the `## Fix:` sections of `.tickets/DAEO-ma4q.md`): `gov memaudit brief --kind writer` writes a Stop hook running `gov memaudit writer-check` into `<out>/.claude/settings.json`. **It was never proven in a real writer session, and it probably does not load there:** a writer launched through `governance/project/orchestration/tools/indep_launch.py` runs in its wall with the wall's own settings (`--settings <wall>/.claude/settings.json --setting-sources project`, written from the launcher's `settings.json.tmpl` with approved template hashes), not the brief's file; and a session started with `--safe-mode` may load no hooks at all. The 0.1.6 patch release is cut only when this holds.

## What (a K-line FM-5 added to the `## Fix:` section of `.tickets/DAEO-ma4q.md`; the CTO approves it by this brief)
- **FM-5 The check runs in every real writer launch.** Find every way a writer session is launched for the fresh 80 (read `src/gov/memaudit/` and `indep_launch.py`; the EXAMIN CTO's launch may differ: `gov memaudit brief` must print the exact launch command a CTO uses). In each: the writer-check runs before the session ends, a refused question goes back to that writer with its ids and codes only, at most 3 returns, and the refused ids are recorded. Where a Stop hook can load (the wall's settings template, its approved hashes updated as the launcher requires), use it; where a launch cannot load hooks, the same check-and-return loop is held by code around the session (the session is resumed or called again with its own output and the refusals, never a fresh writer). **Prove it with one real session:** a real `claude -p` writer on Sonnet, launched exactly as the product launches it, on a planted 2-question set in a temporary folder with one planted form fault (no real repository's sets, nothing under any sets root), shows in its transcript and in `WRITER-CHECK.json` the refusal returned and the fixed file accepted. Keep the cost of that run small (one session, a minimal brief).
- Keep the hidden-set protections and the wall's other settings unchanged.

Code area: `src/gov/memaudit/` (`brief.py`, `writercheck.py`, the launch), `indep_launch.py` and its templates (only the hook line and the approved hashes). Another lead (eval-roots) edits `gov memaudit`'s root resolution: keep clear of it.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-memaudit-3`, branch `e2/fix-memaudit-3` from `w2/integrate`.

## Green
The test designer adds FM-5's acceptance cases (red on the base); the engineer builds; the real session is run once and its evidence kept under the run folder. Then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-ma4q=e2/fix-memaudit-3 --onto w2/integrate --select`) and `gov accept W2-204`, both through the heavy slot (DEC-1244 X-1). I-22's W1-35 and dispatch import errors and the two warm-latency timings (W2-13, W1-19) under load are not yours. **Commit trailers as one paragraph, with no blank line before `Co-Authored-By`** (a blank line hides `Role:` and `Fix:` from the patch rule; it happened in the last lead). Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; every writer launch path found and how the check runs in each; the real session's evidence (transcript lines, `WRITER-CHECK.json`); the selected suites' summary lines; reds not yours; your `gov retrieve` calls (count, queries) and the records used.

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut, as `gov retrieve` printed it)
Query: How is a fresh 80 writer session launched (indep_launch.py wall, its settings.json template, approved template hashes, gov memaudit brief out folder) and where do hooks load? Code locations, conventions, earlier fixes and findings.

```
store: eb4361855319 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "eb43618553192002624d712d351f92878609f482",
    "head": "eb43618553192002624d712d351f92878609f482",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "cb60aa1305046fa086767aef",
      "sha256": "65298d3468484515ca18e2dd3db5e6eb867221f1d9d6318e5e07998a2a5aef49",
      "path": "governance/project/indep-walls/README.md",
      "start_line": 1,
      "end_line": 21,
      "text": "# The walls' template (ACT-INDEP-WALLS-1, DEC-1101 (2))\n\nThe launch script (DEC-1101 (3) step 2) builds every independent session's walled folder from these files. They\nchange only by an ACT the owner approves; their sha256s are in `<sets root>/indep-walls/APPROVED`, and the launch script\nrefuses to build from a file that does not match.\n\n| File | What |\n|---|---|\n| `settings.json.tmpl` | The wall's settings: allow its own folder (writes `out/` only); deny the shell, the web, subagents, memory's search, git, the repository, the worktrees, the run outputs, `~/.claude`, the rest of the sets root, the approved list and every other wall; the wall hook on every tool. |\n| `wall_hook.py` | The wall's PreToolUse guard: reads and writes closed to the wall (links followed), writes into `out/` only, the tools named and no others, fail closed. |\n| `CLAUDE.md.tmpl` | The session's standing note: its kind, its brief's sha256, its commit, its folder rules. |\n| `kinds.yaml` | The job kinds (writer, checker, auditor, labeller): tools, inputs, what is delivered where, proposed budgets and timeouts. |\n| `tree-exclude.txt` | The paths left out of every wall's plain tree (the evaluation sources and sets, the measure results). |\n\nA wall: `<sets root>/indep-walls/<kind>/<run>/` holding `WALL.json`, `seed.txt`, `brief.md`, `CLAUDE.md`, `.claude/`,\n`input/` and `out/` (the only writable folder); its plain tree at `~/gov-os-wall-trees/<kind>-<run>/` (read-only,\noutside the sets root: the repository's own content, which the guard's walk of the hidden part must not count). The\nsession runs as `claude -p --restricted --settings <wall>/.claude/settings.json --add-dir <tree> --tools <the kind's>\n--no-session-persistence --strict-mcp-config`, from the wall, so Claude Code's restricted mode confines its file tools\nto the wall and its tree as well. A finished wall is packed into `indep-walls/<kind>/<run>.tar` (one file) and its tree\nremoved, so the hidden part stays far under the guard's 10,000-file walk.\n",
      "chunk_id": "cb60aa1305046fa086767aef",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b1571457a8301043b05a49af",
      "sha256": "183e71a5727d722a1910dded19c0fd10c90128dc5b8fd1d9b3824ec4c8f16ffc",
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "start_line": 1,
      "end_line": 10,
      "text": "#!/usr/bin/env python3\n\"\"\"The independent sessions' launch script (W2-149; DEC-1101 (2)-(3) step 2, DEC-1109 (2); ACT-INDEP-WALLS-1).\n\nBuilds one walled folder for one job (writer, checker, auditor, labeller) from an owner-approved brief and the walls'\ntemplate, chooses its content by rule from a seed recorded first, checks with a canary that the wall's settings load,\nstarts one closed headless `claude -p` session in it, delivers its product by its own code and returns only counts.\nStandard library, PyYAML and git; no gov import. The CTO runs it, from the repository:\n\n  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/writer.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1\n  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind checker --brief governance/project/indep-briefs/checker.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1\n",
      "chunk_id": "b1571457a8301043b05a49af",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "598d48b61632a2b1c00d8440",
      "sha256": "65298d3468484515ca18e2dd3db5e6eb867221f1d9d6318e5e07998a2a5aef49",
      "path": "src/gov/_shipped/governance/project/indep-walls/README.md",
      "start_line": 1,
      "end_line": 21,
      "text": "# The walls' template (ACT-INDEP-WALLS-1, DEC-1101 (2))\n\nThe launch script (DEC-1101 (3) step 2) builds every independent session's walled folder from these files. They\nchange only by an ACT the owner approves; their sha256s are in `<sets root>/indep-walls/APPROVED`, and the launch script\nrefuses to build from a file that does not match.\n\n| File | What |\n|---|---|\n| `settings.json.tmpl` | The wall's settings: allow its own folder (writes `out/` only); deny the shell, the web, subagents, memory's search, git, the repository, the worktrees, the run outputs, `~/.claude`, the rest of the sets root, the approved list and every other wall; the wall hook on every tool. |\n| `wall_hook.py` | The wall's PreToolUse guard: reads and writes closed to the wall (links followed), writes into `out/` only, the tools named and no others, fail closed. |\n| `CLAUDE.md.tmpl` | The session's standing note: its kind, its brief's sha256, its commit, its folder rules. |\n| `kinds.yaml` | The job kinds (writer, checker, auditor, labeller): tools, inputs, what is delivered where, proposed budgets and timeouts. |\n| `tree-exclude.txt` | The paths left out of every wall's plain tree (the evaluation sources and sets, the measure results). |\n\nA wall: `<sets root>/indep-walls/<kind>/<run>/` holding `WALL.json`, `seed.txt`, `brief.md`, `CLAUDE.md`, `.claude/`,\n`input/` and `out/` (the only writable folder); its plain tree at `~/gov-os-wall-trees/<kind>-<run>/` (read-only,\noutside the sets root: the repository's own content, which the guard's walk of the hidden part must not count). The\nsession runs as `claude -p --restricted --settings <wall>/.claude/settings.json --add-dir <tree> --tools <the kind's>\n--no-session-persistence --strict-mcp-config`, from the wall, so Claude Code's restricted mode confines its file tools\nto the wall and its tree as well. A finished wall is packed into `indep-walls/<kind>/<run>.tar` (one file) and its tree\nremoved, so the hidden part stays far under the guard's 10,000-file walk.\n",
      "chunk_id": "598d48b61632a2b1c00d8440",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d805baee7476460d86a328e6",
      "sha256": "5f40e2698010bd93bb79dd5e94951c67f04e73a459974db1effe612762d62741",
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "start_line": 15,
      "end_line": 40,
      "text": "## 1. What already exists, and what it means for the rule\n- **The walled writer** is `governance/project/orchestration/tools/indep_launch.py` (W2-149, ACT-INDEP-WALLS-1) with the\n  owner-approved brief `governance/project/indep-briefs/memory-audit/writer.md` (sha256 `bc089423\u2026`), checked by\n  `\u2026/checker.md` (`cea517b8\u2026`). One writer run writes **40** questions about Gov OS at a pinned commit into\n  `<sets root>/fixtures/evaluation/<set>/hidden/`, refusing a set that already exists (`indep_launch.py:1883-1884`), so \"no\n  set is reused\" is already how it delivers. Its quotas are fixed (`writer.md:65-69`): decision 6, contract 4, plan 4,\n  ticket 4, exact-string 4, callers 4, code-paraphrase 3, kernel-template 3, multi-file 3, failure-memory 3, history 1,\n  nonexistent-id 1; the five areas at least 4 each, no subsystem over 10 (`writer.md:89-93`). **Kinds and areas are\n  therefore the same every time; difficulty is not fixed** (only \"at most 6 keyword\", \"at least 2 supersession\").\n- **The writer's output form is the measure's form** (id, question, gold_answer, sources with path, heading, lines and\n  alternatives, commit: `writer.md:149-170` against `src/gov/retrieval/measure.py:249-265`), so a fresh set is measured\n  by W2-15a's measure in its four modes unchanged; the measure takes `n` from the set (no 39/40 assumption in code).\n- **The judged configuration is in the pinned product:** `gov.memaudit judge` (`src/gov/memaudit/judge.py`, W2-171; the\n  fresh 80's `fresh80_reader.py` generalised): the reader (Opus) answers from the whole ranked bundle, searches again\n  once through `--gov` or settles; the grader (Opus) judges, a Sonnet grade is kept beside it; the citation is checked by\n  the measure's matcher; $0.157 a question; its model calls are `claude -p --safe-mode --tools \"\"\n  --no-session-persistence` (no tools, no session: walled by construction). It runs on an audit's layout\n  (`memory-audit-<8 digits>`: writer, `preflight`, checker, `void`, `measure`, `judge`), so each half is one audit.\n- **The frozen state** has a precedent: JOB-20261116-02's script (`drafts/w2-15a-close/walled_hidden_counts.sh`) cloned\n  the repository at the commit and built that clone's own store (seeded; about one minute), so nothing live stopped.\n- **The guard already walls every fresh set's hidden half:** `governance/project/path-map.yaml:639` lists\n  `fixtures/evaluation/*/hidden/**` under `sets_root_hidden`. A new set needs only its `evaluation_sets` entry in the\n  sets root's path map (the measure refuses an undeclared set, `measure.py:478`), which `gov.memaudit declare` writes itself.\n- **The weekly audit is not live yet:** no `gov.memaudit` cron line is installed (crontab), so changing it now costs no\n  migration.\n\n",
      "chunk_id": "d805baee7476460d86a328e6",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2f40ac768ec3c37a6e91f47c",
      "sha256": "f7e26942b45f7343e9528c6059854e6189a2cdc2169d9048121fabd4037f45b2",
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "start_line": 100,
      "end_line": 115,
      "text": "KINDS = (\"writer\", \"checker\", \"auditor\", \"labeller\")\nTOOLS_OK = (\"Read\", \"Grep\", \"Glob\", \"Write\", \"Edit\", \"MultiEdit\", \"TodoWrite\")\nREFUSAL_KEYS = (\"Read\", \"Grep\", \"Glob\", \"Write\", \"Edit\", \"MultiEdit\", \"TodoWrite\", \"Bash\", \"WebFetch\", \"WebSearch\",\n                \"Task\", \"Agent\", \"NotebookEdit\", \"Skill\", \"other\")\nWALLS = \"indep-\" + \"walls\"  # the walls' folder under the sets root, and the template's folder in the repository\nTEMPLATE_DIR = \"governance/project/\" + WALLS\nTEMPLATE_FILES = (\"settings.json.tmpl\", \"wall_hook.py\", \"CLAUDE.md.tmpl\", \"kinds.yaml\", \"tree-exclude.txt\",\n                  \"README.md\")\nPATH_MAP = \"governance/project/path-map.yaml\"\nSCHEMAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"indep-schemas\")\nCOUNTS_SCHEMA = \"indep-counts.schema.json\"\nNAME_RX = re.compile(r\"[a-z0-9][a-z0-9-]{0,63}\")\nFIX_RX = re.compile(r\"q[0-9]{2}\")  # the one-question fix flow's id and its reason codes (W2-94)\nFIX_CODES = (\"SOURCE_IS_SCAFFOLD\", \"SOURCE_PATH_ABSENT\", \"SOURCE_NOT_TEXT\", \"SPAN_OUT_OF_FILE\", \"HEADING_NOT_FOUND\",\n             \"ANSWER_NOT_IN_SPANS\", \"NONEXISTENT_NAME_FOUND\", \"NONEXISTENT_NO_NAME\")\nFIX_ACTIONS = (\"corrected\", \"replaced\")\n",
      "chunk_id": "2f40ac768ec3c37a6e91f47c",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "991c891114493f708c46f63d",
      "sha256": "cd87e264ac40dbc465b07a3705125ef260adfba1ffe75b01e0c0012e5355a512",
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "start_line": 13,
      "end_line": 19,
      "text": "# Fixed brief: the memory audit's question writer (DEC-1101 (1)-(2), DEC-1125 (2))\n\nVersion 1. This text is hashed, and its sha256 is recorded in the approved list. The CTO may not change it without the\nowner's approval. The launch script starts you headless in your walled folder, gives you only what \u00a72 names, and\ndelivers only what \u00a77 names. It starts you twice for one audit: round 1 writes the set, round 2 revises it after a\nchecker's notes.\n\n",
      "chunk_id": "991c891114493f708c46f63d",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "69aa2e8a9dd1999126b1e28b",
      "sha256": "f52b794a0775f09a65017e8f1c5b9f3b5af27779689209810f0b48b150ae6bb1",
      "path": "governance/project/memory-audit.yaml",
      "start_line": 32,
      "end_line": 50,
      "text": "    paths: [\"src/gov/guard/**\", \"src/gov/hooks/**\", \"template/governance/kernel/hooks/**\", \".claude/hooks/**\"]\n  - name: close\n    paths: [\"src/gov/close/**\", \"src/gov/closure/**\", \"src/gov/accept/**\", \"src/gov/check/**\",\n            \"src/gov/readiness/**\", \"src/gov/ci/**\", \"docs/close/**\",\n            \"governance/project/orchestration/tools/nightly*\"]\n  - name: checkpoint\n    paths: [\"src/gov/checkpoint/**\", \"src/gov/pause/**\", \"docs/checkpoints/**\"]\n  - name: rebuild\n    paths: [\"src/gov/rebuild/**\", \"src/gov/secrets/**\", \"src/gov/doctor/**\"]\n  - name: launch\n    paths: [\"src/gov/launch/**\", \"src/gov/brief/**\", \"template/governance/kernel/launch/**\",\n            governance/project/orchestration/tools/indep_launch.py, \"governance/project/indep-walls/**\"]\n  - name: release\n    paths: [\"src/gov/release/**\", \"src/gov/adopt/**\", \"src/gov/adapters/**\", \"docs/releases/**\"]\nspread: {domain_min: 4, subsystem_max: 10}\n# The paths a writer and a checker leave unread and no question cites: the walls' tree-exclude.txt, and the records the\n# approved briefs name by hand (the standing measure's miss records, the audit's own package and walls).\nexclude:\n  - \"fixtures/evaluation/**\"\n",
      "chunk_id": "69aa2e8a9dd1999126b1e28b",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "5ab64ba30c66b9cdb3b38cbf",
      "sha256": "0dd454ddd4206145fd97458126b0092d8700d196eaf671f4b34a9efc2b6dc991",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "start_line": 20,
      "end_line": 30,
      "text": "## 2 Where it stands today (M: the files named)\n- **The walls are in.** ACT-INDEP-WALLS-1 was applied by your operator (`147706ae`): the walls' template, the path\n  map's hidden globs, the walls' approved list (row 28 and row 42 of DECIDED-NOT-DONE).\n- **The launch script is merged and installed.** W2-149 (`DAEO-52ku`) merged `b4de529b` (11-09); set-up A's wiring\n  `7f0e71519`, its fixes `90c1fea6c` and `2f98aecbc` (row 86). ACT-W2-149-INSTALL-1 was applied by your operator\n  (`baac0b2c2`, 11-10 15:41; list `6b923cb4d552`, 0 mismatches; row 75). ACT-SETS-GLOBS-1 applied `9cce7430d`; ACT-PATHMAP-NS-2\n  placed the briefs' folder in the path map. **So the walls and the launch script wait for nothing but briefs.**\n- **The fixed briefs that exist are set-up A's five** (`governance/project/indep-briefs/sgx1/`: two writers, two\n  labellers, the overlap auditor), for the guard experiment. **There is no brief for the memory audit's writer,\n  checker or auditor.** The walls' template and the script already support those three kinds (`kinds.yaml`, W2-149's\n  schemas), so this package supplies them. The old operator folders `~/gov-os-writer` and `~/gov-os-checker` stay as they\n",
      "chunk_id": "5ab64ba30c66b9cdb3b38cbf",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1101",
      "sha256": "06d7ec7fc1d07d9a4a24e19ec3c3fe7097c699a0afb54c4b6b492d65397e99bf",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1581,
      "end_line": 1590,
      "text": "    weekly in the digest; a structural-pass notice of an unindexed path resolved within a day.\n  - (2) **Standing: automated independent sessions, a priority now.** Every question writer, checker and labeller is\n    launched automatically, without the owner opening sessions: headless sessions in their own walled folders. From now\n    for the periodic audits, the sandbox experiment's labellers (DEC-1099 (1) Q5) and the sets W2-88 needs for\n    EXAMIN's copy. Independence: a fixed brief per job that the owner approves once, hashed, which the CTO may not\n    change without the owner's approval; the writer chooses its content by rule (what changed since the last audit,\n    from git, plus a random sample of older areas from a seed recorded before writing), not by the CTO; memory's own\n    search, run outputs, the CTO's scratch and the other sessions' folders denied to them by their settings, the guard,\n    and the sandbox once proven; only counts reach the CTO.\n  - (3) **The order:** first what must land in the path map, the guard and the folders' settings, as one ACT for the\n",
      "chunk_id": "ded17b26ebc3d29ae5d790b4",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1101",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "30aecec3ade9252297a59de4",
      "sha256": "7da9979f47fee1c7700d44e84e5b466b60708a98b4dc411d0061571ddcc1d347",
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "start_line": 126,
      "end_line": 127,
      "text": "      \"text\": \"## The CTO's decisions (not to be reopened)\\n\\n1. The domain table, subsystem table, categories with quotas and the control set with its baseline move into\\n   `governance/project/memory-audit.yaml` (schema `template/governance/kernel/schemas/memory-audit.schema.json`). Gov OS's\\n   file holds today's constants. No silent default. A subsystem by path or by record key.\\n2. The steps an adopter runs are on the CLI under `gov memaudit` and one command runs a whole fresh 80 on a pinned snapshot\\n   it builds. `python3 -m gov.memaudit` keeps working.\\n3. The writer and checker are independent fresh sessions the adopter's CTO launches; the walls launcher stays Gov OS's.\\n   The product gives the filled briefs and takes the delivered halves from the sets root.\\n4. F-1 and F-2 are fixed here (the driver follows the cycle; the writer's result counts areas in the configuration's domain list).\\n5. The reader's and graders' prompts, schemas, models are not touched.\\n6. No real session, no measure, no rebuild of a shared store, nothing under `~/gov-os-eval`; the CTO runs the first real\\n   fresh 80 after the land.\\n\\n\",\n      \"chunk_id\": \"a6712fb2309e3e434974cdf8\",\n",
      "chunk_id": "30aecec3ade9252297a59de4",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1101",
      "sha256": "cebe3cc3ac6811891fbc57277d7b13fa115a221fcb6195a2d18017b13952f841",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1589,
      "end_line": 1597,
      "text": "    and the sandbox once proven; only counts reach the CTO.\n  - (3) **The order:** first what must land in the path map, the guard and the folders' settings, as one ACT for the\n    owner's operator, rehearsed; then the launch script, tests first, with one review; then the fixed briefs for writer,\n    checker, auditor and labeller, to the owner for approval; then it becomes the default. With the briefs: the set\n    size per audit, how each wall is enforced and tested, the costs per audit (tokens, GPU, the owner's time), the home\n    tickets for Gov OS and the lines for W2-88, and when the first audit runs.\n- **Basis:** question 1 (memory kept right as the repository grows, judged on fresh questions) and question 2 (the\n  sets' independence enforced by walls, not by trust).\n\n",
      "chunk_id": "4fd5229099b8c30e780be4f6",
      "routes": [
        "lexical"
      ],
      "batch": 2,
      "entry": "DEC-1101",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DAEO-52ku",
      "sha256": "5cdb12e54d08e866318042cb3612ca727c2fa1c03ce8cd144118a2b2e8b7a36e",
      "path": ".tickets/DAEO-52ku.md",
      "start_line": 92,
      "end_line": 103,
      "text": "# W2-149 The independent sessions' launch script: a walled headless session per job from an approved brief\n\nThe owner's DEC-1101 (3) step 2, restarted by DEC-1109 (2): the launch script for the independent writers, checkers,\nauditors and labellers (DEC-1101 (2)), tests first, one review. Built on ACT-INDEP-WALLS-1 (applied, `147706ae`): its\ntemplate `governance/project/indep-walls/`, the path-map entries and its rehearsal\n(`governance/project/orchestration/packages/ACT-INDEP-WALLS-1.md`). The specification is LAUNCH-SPEC (its \u00a71 to \u00a75;\nits \u00a76 is these KPI lines), copied into the worktrees as `.gov-runtime/scratch/ref/LAUNCH-SPEC.md`.\n\n- **What is built here:** `governance/project/orchestration/tools/indep_launch.py` (the CTO's committed tool; standard\n  library, PyYAML and `git`, no `gov` import), the counts schema and the four kinds' result schemas in\n  `governance/project/orchestration/tools/indep-schemas/`, the engineer's unit tests, and the evidence record.\n- **What is not built here:** the four fixed briefs (DEC-1101 (3) step 3, to the owner) and their `brief <kind>`\n",
      "chunk_id": "157109d96cbb17a1670299eb",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "893ce0465aa42fb9ac0f5ee9",
      "sha256": "56bee3fb3c3fa6cb8dfdee345bc0cf2dda069149d470b85d23abd7445cc37b7a",
      "path": "docs/changes/W2-204-evidence.md",
      "start_line": 213,
      "end_line": 223,
      "text": "- **A fresh pair of halves is one command run until it ends:** `gov memaudit fresh --sets-root R --repo D --commit C\n  --tag YYYYMMDD`, on a snapshot it clones and builds; the repository's own store is not the one measured.\n- **The writer and the checker are the adopter's CTO's own fresh sessions**, each given the folder `gov memaudit\n  brief` writes and nothing else; their output enters the sets root only through `gov memaudit deliver`. The walls\n  launcher (`indep_launch.py`) and the approved briefs under `governance/project/indep-briefs/` are Gov OS's own\n  and are not part of what an adopter runs. \"Behind the walls\" in step 6 holds for Gov OS; for an adopter it reads\n  \"by independent fresh sessions, closed by the transcript scan\".\n- **The CTO never reads the sets root;** the transcript scan at the end of `fresh` (or `gov memaudit scan`) is the\n  check, and a finding voids the measure.\n- **The practice record** (`docs/research/W2-88-memory-practice.md`) should name the file as the place of a\n  repository's domains, categories and control, and say that the control's baseline of a repository without an earlier\n",
      "chunk_id": "893ce0465aa42fb9ac0f5ee9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "99cc7aeaded965198ccb3c40",
      "sha256": "cd87e264ac40dbc465b07a3705125ef260adfba1ffe75b01e0c0012e5355a512",
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "start_line": 13,
      "end_line": 19,
      "text": "# Fixed brief: the memory audit's question writer (DEC-1101 (1)-(2), DEC-1125 (2))\n\nVersion 1. This text is hashed, and its sha256 is recorded in the approved list. The CTO may not change it without the\nowner's approval. The launch script starts you headless in your walled folder, gives you only what \u00a72 names, and\ndelivers only what \u00a77 names. It starts you twice for one audit: round 1 writes the set, round 2 revises it after a\nchecker's notes.\n\n",
      "chunk_id": "99cc7aeaded965198ccb3c40",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "03705ce422823d1c11a009aa",
      "sha256": "64b726c74b6e00f27d3d53335f8044e7dce10c9bfac4185928402f0d2be1bce7",
      "path": "governance/project/indep-briefs/sgx1/writer-tuning.md",
      "start_line": 12,
      "end_line": 17,
      "text": "# Fixed brief: SANDBOX-GUARD-EXP-1, planted-case writer 1, for the tuning half (DEC-1099 (1), DEC-1101 (2), DEC-1113)\n\nVersion 3. This text is hashed, and its sha256 is recorded in the declaration and in the approved list. The CTO may not\nchange it without the owner's approval. The launch script starts you headless in your walled folder, gives you only\nwhat \u00a72 names, and reads back only what \u00a77 names.\n\n",
      "chunk_id": "03705ce422823d1c11a009aa",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "c2a32ef4dfa8a7be5cfa6ce9",
      "sha256": "29a3f5403900201e1212691bcd8eb013a785984ac965bb769190ddf71fbad5e9",
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "start_line": 10,
      "end_line": 13,
      "text": "  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind checker --brief governance/project/indep-briefs/checker.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --round 1\n  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind auditor --brief governance/project/indep-briefs/auditor.md --brief-sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 --commit 6ff398a28 --set memory-recall-3 --audit e0\n  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/sgx1/writer-tuning.md --brief-sha256 82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57 --commit 6ff398a28 --set tuning --round 1\n  python3 governance/project/orchestration/tools/indep_launch.py --sets-root ~/gov-os-eval --kind writer --brief governance/project/indep-briefs/sgx1/writer-heldout.md --brief-sha256 137a73d1df4c265fd5ce4e24716797703e2b12dcaeb90663c0170834a60fafe6 --commit 6ff398a28 --set held-out --round 1\n",
      "chunk_id": "c2a32ef4dfa8a7be5cfa6ce9",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "8322f1dbdc004e179050f3d7",
      "sha256": "f0648a369ab5c6bf56fa244f73e723ef3aaeafad08d25637ab2bbbf0a8add231",
      "path": "src/gov/memaudit/briefs/__init__.py",
      "start_line": 1,
      "end_line": 9,
      "text": "\"\"\"The writer's and the checker's brief templates (W2-204 I5, S9), filled by ``gov.memaudit.brief`` from a repository's\nown configuration. They follow the sections of Gov OS's approved briefs (``governance/project/indep-briefs/memory-audit/``):\nthe job, the folder, what to read, what never to read, the rules, round 2, the output, the result, the stops. A template\nnames no repository's category, domain or subsystem: every such name is a ``{{field}}`` the configuration fills. The\ntext is kept in Python modules so that an installed release carries it without a package-data entry.\"\"\"\n\nfrom gov.memaudit.briefs import checker, writer\n\nTEMPLATES = {\"writer\": writer.TEXT, \"checker\": checker.TEXT}\n",
      "chunk_id": "8322f1dbdc004e179050f3d7",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "f3ef3503397017b85e73305b",
      "sha256": "28adc41927559e8f7ea16a633dc9960fe354f90a740c241248864fc33356a781",
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "start_line": 41,
      "end_line": 50,
      "text": "   (`indep_launch.py`) stays Gov OS's own tool and is not the product's. The product gives the adopter the writer's and\n   the checker's briefs filled from the repository's configuration (`gov memaudit brief --kind writer|checker`), and the\n   driver takes the delivered halves from the sets root. Gov OS's own approved briefs\n   (`governance/project/indep-briefs/memory-audit/*.md`, pinned by sha) are not changed tonight: show in your return\n   how the generated brief for Gov OS's configuration differs from the approved one (F-2's `by_area` list is expected).\n4. **F-1 and F-2 are fixed here** (fixes in W2-187's record): the driver follows the cycle above; the writer's result\n   counts areas in the configuration's own domain list.\n5. **Comparability.** The reader's and the graders' prompts, schemas and models are not touched (DEC-1098; pinned by\n   hash in `prompts.py`): a figure from this change compares with FRESH-80-RESULT. No model substitution reaches them.\n6. **The hidden halves.** You and your helpers never read anything under `~/gov-os-eval` or any real question set.\n",
      "chunk_id": "f3ef3503397017b85e73305b",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-52ku",
      "sha256": "335865e95e47b802437cc77622ec245c76a43a37d3cb1538cf33a5255ce5f8bc",
      "path": ".tickets/DAEO-52ku.md",
      "start_line": 111,
      "end_line": 120,
      "text": "     its own temporary folder and adds that folder with `--add-dir` for the canary only (otherwise the same flags):\n     restricted mode allows that Read, and only the wall's settings and hook (which know only the wall and its tree)\n     refuse it. A Read in `permission_denials` means the settings loaded; an allowed Read refuses with code 16. The CTO\n     proves it live (S9): valid settings refused, one corrupted key not refused.\n  2. **Planted roots:** every location other than `--sets-root` derives from `HOME` (`~/gov-os-wall-trees/`,\n     `~/gov-os-runs/indep/`) and the repository is the git top level of the folder the script runs in; tests plant\n     HOME, the sets root and the repository. For the CTO's live trial, which needs the real HOME for the session's\n     login, the interface names one environment override each for the runs folder and the trees folder (tests and the\n     trial only); a run with an override says so in `WALL.json` and in a boolean of `counts.json`.\n  3. **Where the bytes come from:** the brief and the template files are read from the repository at `--commit`\n",
      "chunk_id": "ecdc53a85c1a00a82b60bbd7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-52ku",
      "sha256": "14282973622431005c7cc2af595081d829fa7962bb6b691986064c86abcf74e9",
      "path": ".tickets/DAEO-52ku.md",
      "start_line": 27,
      "end_line": 29,
      "text": "  - 'S1 The brief is the approved one: a launch whose brief''s bytes at `--commit`, `--brief-sha256` and the `brief <kind>` line of `<sets root>/indep-walls/APPROVED` do not all agree refuses with code 10 and builds nothing. Verify: three launches in a planted sets root (one byte of the brief altered, a wrong hash argument, the line removed): exit 10 each; `indep-walls/<kind>/` unchanged; no tree folder; no `SEEDS.log` line [DEC-1101 (2)-(3)]'\n  - 'S2 The template is the approved one: one changed byte in any of the six template files (`settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`, `kinds.yaml`, `tree-exclude.txt`, `README.md`) against its `template` line in `APPROVED` refuses with code 11. Verify: six launches, one per file: exit 11 each; nothing built [DEC-1101 (2)-(3)]'\n  - 'S3 A wall is built only into nothing: a wall folder holding any entry, or an existing tree folder, refuses with code 12 and leaves both untouched. Verify: one file planted in the wall; the tree folder planted; exit 12 each; the planted entries'' hashes unchanged [DEC-1101 (2)-(3)]'\n",
      "chunk_id": "c0c33a204ac0f005dc9c94df",
      "routes": [
        "lexical"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 14,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "cb60aa1305046fa086767aef",
      "parent_id": "4a9bdf2e6ca7bfb74c05f97e",
      "path": "governance/project/indep-walls/README.md",
      "start_line": 1,
      "end_line": 21
    },
    {
      "chunk_id": "598d48b61632a2b1c00d8440",
      "parent_id": "b65f0718dfb94fa0b177722d",
      "path": "src/gov/_shipped/governance/project/indep-walls/README.md",
      "start_line": 1,
      "end_line": 21
    },
    {
      "chunk_id": "d805baee7476460d86a328e6",
      "parent_id": "fe2e2596a9274da0a7f44bbb",
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "start_line": 15,
      "end_line": 40
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "governance/project/indep-briefs/sgx1/writer-heldout.md",
      "chunk_id": "fe32c7ec6536a210856cd2e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "8b9b80941079dafcbcccbee8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5818612a63380ac727419dee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "3c0791f039df5f63a6523bb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "5c07bb2fd2f43276c30d1390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.1/manifest.json",
      "chunk_id": "5e115e093d94f1cb0cd13b6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "f2012a73b495a78ee190d14f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "chunk_id": "140716e5f145ba00070e327d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "f6a385f58a57a665d3cb1150",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "c8f383b9233cb2f8baea7b2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "23e95645b26102b364955f91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "49cf5d74a9b9d181271360b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-27-SETTINGS.md",
      "chunk_id": "c2ed70b61d02ba4149c78fc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "41f0b008ab4e8430df89fe72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "48260d02b656211f5ddde451",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "8b8bb0151646cfec1df28284",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "4cb998327b05eb4baa68b2d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "ec94cb4b14c8e30f82690d3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "8509f5ae1bb3cf5de8536a52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "a03867c80b4920e3d71b6c93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json",
      "chunk_id": "2c0549cefa067b398999dca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "67e8b4052b3dcfcb0e145656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/brief.py",
      "chunk_id": "6f44fa6f8bf1b3c714047e25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "b8d59c8ff45f5a2abefd73bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-149-evidence.md",
      "chunk_id": "fe3cd14811e6873078edb214",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md",
      "chunk_id": "ad5432c8fb79fcce4b2fca87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "chunk_id": "37360152a2f5efeda2ccd336",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "0ba3d6865df682bc690e64ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "e752700c5387b3c7d2e1ee59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "f489081e493e9401551c774d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "24e9b7f3d25119cdff350243",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "d22a8cbe3edf700f6738c410",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "0a0673937cec6eb5302a7d3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "996d39d549dc5929fd4470c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "389e8f4fe08fb5b1c0d45552",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "8509e3854f6fffe1bc9128f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "21f961cb407982410c3db6eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "89148e05b97f18d532f1688d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ktiw.md",
      "chunk_id": "15adfc217b74076a62e89ff7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "d367c2cbf6f63746bc3288a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "966ba3094d548fd4abe2e8e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "762536e5374e9e7df3929090",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "63aef0b7c1d7d83b0c4b5117",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "2fe8a66aa59018cae85f53fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "35a067095798f94c4ff838f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md",
      "chunk_id": "8ab2a0bf3caba9906dc47e8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mtg.md",
      "chunk_id": "52f6d72f30c22e71b54939d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "314e2293dbe9252f5eb1c61d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "f0dda0eaf6543b22139c5d2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "c168c38f0394cc0af67faf5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md",
      "chunk_id": "2603c2f510271444a7f77f3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-xwro.md",
      "chunk_id": "c8cf50693711bee2d7a83940",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "3c6ae9042e521f5abfd25738",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md",
      "chunk_id": "d5af49362ec8be43706b5c09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "86a917a2e419e905860b9761",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "5d72db0d5eecccc17cdcd764",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "20bdc474cd8c7da63168bbc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "2571e4c1837a2b1fad372002",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "5d529e40ce3d0bead410dbe6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "5bb4e2f47b5f514db258340b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "a1ceee2f6a85ffffc733ebe0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "7972f68466d892c8f3394655",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "c323838b02ce5e15083e5b17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "c1e65751fa45cd08890fa8ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/EXAMIN-writer.md",
      "chunk_id": "e1f5f19e7fd03896655fc862",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "d09977efb1fa027d45b0974f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/sessionstart.py",
      "chunk_id": "e0e1bf9539e60cda05ffa730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "5d1de1533bfe799a5c32ad66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "016ea775ed98fabe3221df0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "fedc64cf47718cde60dc1c64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "6aec846aa4cfb41d0dc52bb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mtg.md",
      "chunk_id": "ec726e13e31de8d308f06715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "13f9ab4896ba85c679f72892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B2.md",
      "chunk_id": "450ba25c76fad05da0c8ee7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "0ee06630801a2f642d21106e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "65c0b329f8ecdf0e3ce48b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "cecd34dcea9bee3d7e09644b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "86ad7690c8e4e28b9765fff0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/EXAMIN-writer.md",
      "chunk_id": "0c2e16a250dcef4e48324c14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "96c841120339cf6a03164cd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "1db6a1c38f72df639d934806",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-reds-launch.md",
      "chunk_id": "0f9ab42cb1585649afe21294",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "fcf6da238b045f714db35f49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "e12bd64afd6ea9759abc54d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "chunk_id": "2ccb31481c864687f60b6ccc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B2.md",
      "chunk_id": "eb37c6ebaaec36f8c9c2b279",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json",
      "chunk_id": "d788c6a6d1cd706fdbd69a71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qyt2.md",
      "chunk_id": "d3b183ff19596db0eb175c83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/01-landing-templates-briefs.md",
      "chunk_id": "fa611c10adae4a5dbcb2b24b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "48c38ad265f7f5745cbac80a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A1-inventory.md",
      "chunk_id": "09e2c409e227ef14fed369ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "chunk_id": "aeb67269b38911637e1539a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "a193e229a8cd79d839121786",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8a113b5a017f3da3d6c15efe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qyt2.md",
      "chunk_id": "0f25989b91ca518113748de4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qz4p.md",
      "chunk_id": "e00f1e4ebd4d77025e887d33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "24d03e9ecb16e172cbe0f494",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "587b2b4da4acc1837f81b279",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "4a2cb79ebbd87173975dbd2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "32c5cd5d94e9175c86040ec7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "430e48b47cbfdaf28df72318",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "55814c0f27f9a0b153a9617b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-52ku.md",
      "chunk_id": "790eec250e6555426a85929e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "66fb4639a1926bf615bf7033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "7c1e1427c1bf3652182411cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "9c6eb3a89cc1b37715b94a83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "bb2877b3341712fe03f839fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "76c047ce8b62e8b618e89e0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-149-evidence.md",
      "chunk_id": "d16ef3c51a4acbe6b37c8dab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "652797d6dcfe032dcca205b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/memory_sets.py",
      "chunk_id": "06c0586f6ba8bf31b62173a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "4a2d1f2744ad834fa3875726",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "0751767c169390217e45b94b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "7429758bcfcefe84b82613d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-g87r/PR-DAEO-g87r-fix.md",
      "chunk_id": "3a64b0853ec940bfda997ea4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/memaudit/test_maintain_reanchor_launch.py",
      "chunk_id": "c5fb3ad4c1c116deec6f3043",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/orchestration/test_w2_94_fix_flow_unit.py",
      "chunk_id": "26f9b6b31d3fda57a90e7a80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/memaudit/test_maintain_reanchor_launch.py",
      "chunk_id": "a935225438ce7f76cdb82f7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md",
      "chunk_id": "4fc16f6efc253f8819b55c49",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5800
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLTUya3UubWQiLDI3LDI5LCJjMGMzM2EyMDRhYzBmMDA1ZGM5Yzk0ZGYiXSxbIi50aWNrZXRzL0RBRU8tNTJrdS5tZCIsOTIsMTAzLCIxNTcxMDlkOTZjYmIxN2ExNjcwMjk5ZWIiXSxbIi50aWNrZXRzL0RBRU8tNTJrdS5tZCIsMTExLDEyMCwiZWNkYzUzYTg1YzFhMDBhODJiNjBiYmQ3Il0sWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwxNTgxLDE1OTAsImRlZDE3YjI2ZWJjM2QyOWFlNWQ3OTBiNCJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMTU4OSwxNTk3LCI0ZmQ1MjI5MDk5YjhjMzBlNzgwYmU0ZjYiXSxbImRvY3MvY2hhbmdlcy9XMi0yMDQtZXZpZGVuY2UubWQiLDIxMywyMjMsIjg5M2NlMDQ2NWFhNDJmYjlhYzBmNWVlOSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1ldmFsLXJvb3RzLm1kIiwxMjYsMTI3LCIzMGFlY2VjM2FkZTkyNTIyOTdhNTlkZTQiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtbWVtYXVkaXQtYWRvcHRlZC5tZCIsNDEsNTAsImYzZWYzNTAzMzk3MDE3Yjg1ZTczMzA1YiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L2luZGVwLWJyaWVmcy9tZW1vcnktYXVkaXQvd3JpdGVyLm1kIiwxMywxOSwiOTkxYzg5MTExNDQ5M2Y3MDhjNDZmNjNkIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3QvaW5kZXAtYnJpZWZzL3NneDEvd3JpdGVyLXR1bmluZy5tZCIsMTIsMTcsIjAzNzA1Y2U0MjI4MjNkMWMxMWEwMDlhYSJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L21lbW9yeS1hdWRpdC55YW1sIiwzMiw1MCwiNjlhYTJlOGE5ZGQxOTk5MTI2YjFlMjhiIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9NRU1PUlktQVVESVQtMS5tZCIsMjAsMzAsIjVhYjY0YmEzMGM2NmI5Y2RiM2IzOGNiZiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vdG9vbHMvaW5kZXBfbGF1bmNoLnB5IiwxLDEwLCJiMTU3MTQ1N2E4MzAxMDQzYjA1YTQ5YWYiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3Rvb2xzL2luZGVwX2xhdW5jaC5weSIsMTAsMTMsImMyYTMyZWY0ZGZhOGE3YmU1Y2ZhNmNlOSJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vdG9vbHMvaW5kZXBfbGF1bmNoLnB5IiwxMDAsMTE1LCIyZjQwYWM3NjhlYzNjMzdhNmU5MWY0N2MiXSxbInNyYy9nb3YvX3NoaXBwZWQvZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvTUVNT1JZLUFVRElULTEvYnJpZWZzL3dyaXRlci5tZCIsMTMsMTksIjk5Y2M3YWVhZGVkOTY1MTk4Y2NiM2M0MCJdLFsic3JjL2dvdi9tZW1hdWRpdC9icmllZnMvX19pbml0X18ucHkiLDEsOSwiODMyMmYxZGJkYzAwNGUxNzkwNTBmM2Q3Il1dLCJmIjoiL2hvbWUvdXNhaW4vZ292LW9zLXdvcmt0cmVlcy9XMi0wMC1zdG9yZS1hIiwiaSI6W10sIm8iOjIwLCJwIjp7ImIiOiJzZXJ2aWNlIiwiZCI6ImN1ZGE6MCIsImgiOiI0MzhmZjU3YzVjZjY5NGVjIiwibyI6WzIsMTAsMSw4LDIzLDI1LDMwLDMyLDAsMywxNCw0LDEyLDksMTksMzQsMzYsMzgsNywyOSwxMSwxMywyMCwyNyw2LDI0LDIyLDE3LDIxLDE2LDM1LDM3LDI4LDM5LDE1LDE4LDUsMzMsMjYsMzFdfSwicSI6IkhvdyBpcyBhIGZyZXNoIDgwIHdyaXRlciBzZXNzaW9uIGxhdW5jaGVkIChpbmRlcF9sYXVuY2gucHkgd2FsbCwgaXRzIHNldHRpbmdzLmpzb24gdGVtcGxhdGUsIGFwcHJvdmVkIHRlbXBsYXRlIGhhc2hlcywgZ292IG1lbWF1ZGl0IGJyaWVmIG91dCBmb2xkZXIpIGFuZCB3aGVyZSBkbyBob29rcyBsb2FkPyBDb2RlIGxvY2F0aW9ucywgY29udmVudGlvbnMsIGVhcmxpZXIgZml4ZXMgYW5kIGZpbmRpbmdzLiIsInIiOjAsInMiOiJlYjQzNjE4NTUzMTkyMDAyNjI0ZDcxMmQzNTFmOTI4Nzg2MDlmNDgyIiwidCI6bnVsbCwieCI6WyI0YTliZGYyZTZjYTdiZmI3NGMwNWY5N2UiLCJiNjVmMDcxOGRmYjk0ZmEwYjE3NzcyMmQiLCJmZTJlMjU5NmE5Mjc0ZGEwYTdmNDRiYmIiXX0=",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "How is a fresh 80 writer session launched (indep_launch.py wall, its settings.json template, approved template hashes, gov memaudit brief out folder) and where do hooks load? Code locations, conventions, earlier fixes and findings.",
      "fresh 80 writer session launched indep_launch.py wall settings.json template approved template hashes gov memaudit brief out folder hooks load Code locations conventions earlier fixes findings."
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": []
  }
}
```
