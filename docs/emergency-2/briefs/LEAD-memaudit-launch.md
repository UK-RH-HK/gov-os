# Lead brief: memaudit-launch, the fresh 80's launch lines and the writer check's visible record (I-33, I-37, I-38); fixes under W2-204 (DAEO-ma4q)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. **Never open a hidden question-set root**
(`/home/usain/examin-eval`, `/home/usain/gov-os-eval`): every test plants its own sets root under a temporary folder.

## Why
EXAMIN's fresh 80 on 0.1.7 (EXAMIN `FRESH80-2026-11-25.md`) met three faults in `gov memaudit`. Read FINDINGS I-33, I-37, I-38
(`docs/emergency-2/integration/FINDINGS.md`):
- **I-33:** `gov memaudit brief --kind writer` exits 4 after its BRIEF line with two "REFUSED: a line that names a sets-root folder
  was not printed" lines and prints no LAUNCH line, though `<out>/LAUNCH.txt` is written complete.
- **I-38:** `brief --kind checker` writes no `LAUNCH.txt` and prints no LAUNCH line (`src/gov/memaudit/brief.py:274-277`, `if kind == "writer"`).
- **I-37:** the writer's Stop hook (`src/gov/memaudit/writercheck.py:43-62`) writes `WRITER-CHECK.json` only in the audit's run folder on the
  sets-root side (`layout.make_run(p)`), which no adopter session may open, and a clean pass prints nothing: the adopter cannot see the
  hook ran.

## What (K-lines as `## Fix:` sections in `.tickets/DAEO-ma4q.md`; the CTO approves them by this brief)
- **ML-1 (I-33):** `brief --kind writer` prints its LAUNCH line without any sets-root path and exits 0; the refusal to print a line
  naming a sets-root folder stays (the guard keeps refusing to print sets paths; find where the line is refused and why it names
  one; the launch line must not need the sets root's path).
- **ML-2 (I-38):** every kind (`writer`, `checker`, round 1 and 2) prints one `LAUNCH <kind> <command>` line and writes
  `<out>/LAUNCH.txt`; the checker's command loads no Stop hook and has the checker's tools; both equal byte for byte.
- **ML-3 (I-37):** `writer-check` also writes `<out>/WRITER-CHECK.json` (the writer's session folder, `--folder`): `returns`,
  `ended`, and the refused codes with ids only, never a question's text or a gold answer; the run folder's record stays as it is.
- **Prove ML-3 in the real path (the CTO's rule: a hook is proven in a real session, not by its command line; FM-5):** one real
  writer session on a planted sets root (a temporary folder, a tiny repository, `claude -p` launched from the planted `LAUNCH.txt`,
  Sonnet), whose Stop hook runs: `<out>/WRITER-CHECK.json` exists after it with `ended` set. One short session; record its command,
  cost and result in your return.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-memaudit-launch`, branch `e2/memaudit-launch` from `w2/integrate`. Code area:
`src/gov/memaudit/brief.py`, `src/gov/memaudit/writercheck.py`, `tests/unit/memaudit/`, a **new** acceptance file
`tests/acceptance/W2-204/test_w2_204_ml_launch.py` with its rows in a **new section at the end** of `tests/acceptance/W2-204/README.md`
(the independent test designer only). `e2/eval-roots` (held, being merged by the bundle-b lead) also changes `src/gov/memaudit/`
(`command.py`, `driver.py`, `evalroots.py`, `judge.py`, `writerrun.py`, `__main__.py`) and W2-204's README: do not edit those files;
keep the README change to the new section so its merge stays simple. Others work meanwhile in `src/gov/release/` and the timing tests.

## Green
ML-1 to ML-3 red on the base, green after; `gov accept W2-204` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-ma4q=e2/memaudit-launch --onto w2/integrate --select`), through the heavy
slot; the real-session proof. Check the trailers (LEAD-COMMON).

## Return
Branch and head; why the LAUNCH line was refused (file:line); ML-1 to ML-3 with tests and result; the real-session proof; the selected
run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: c1e81afd3e75 (/home/usain/Dynamic-Agentic-Engineering-OS), store behind HEAD, head 763d18528026, 32 stale path(s)
{
  "store": {
    "commit": "c1e81afd3e7560e7a8f769bb51de083b07d72158",
    "head": "763d18528026573bae99bb7ac906d8377532ff62",
    "stale": [
      ".claude/agents/orchestrator.md",
      ".claude/templates/role-cto.md",
      ".rulesync/subagents/orchestrator.md",
      ".tickets/DAEO-d3sr.md",
      ".tickets/DAEO-esl1.md",
      ".tickets/DAEO-j9z6.md",
      ".tickets/DAEO-l2b2.md",
      "docs/DECISION_REGISTER.md",
      "docs/checkpoints/DAEO-sdxk/CP-DAEO-sdxk-3337.md",
      "docs/emergency-2/CTO-HANDOVER.md",
      "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "docs/emergency-2/briefs/LEAD-bundle-b.md",
      "docs/emergency-2/briefs/PRODUCT-CTO-HANDOVER-METHOD.md",
      "docs/emergency-2/integration/FINDINGS.md",
      "governance/project/orchestration/tools/start_cto.sh",
      "governance/project/test-map.yaml",
      "src/gov/_shipped/template/governance/kernel/templates/role-cto.md",
      "src/gov/close/select.py",
      "src/gov/queue/command.py",
      "src/gov/queue/dry.py",
      "template/.rulesync/subagents/orchestrator.md",
      "template/governance/kernel/roles/orchestrator.md",
      "template/governance/kernel/templates/role-cto.md",
      "tests/acceptance/W2-115b/README.md",
      "tests/acceptance/W2-115b/test_w2_115b_sel.py",
      "tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py",
      "tests/acceptance/W2-115b/w2_115b_sel_support.py",
      "tests/acceptance/W2-206/README.md",
      "tests/acceptance/W2-206/test_w2_206_sel4.py",
      "tests/unit/queue/test_queue_select_sel.py",
      "tests/unit/queue/test_queue_select_unwritten.py",
      "tests/unit/queue/test_queue_w2_206_flags.py"
    ],
    "root": "/home/usain/Dynamic-Agentic-Engineering-OS"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "2f3f4efdd5241c6ef60722df",
      "sha256": "76e815c2d8c7c388aeab0890438d972b5307024aa7a20298af82ab3a1c42defe",
      "path": "src/gov/memaudit/writercheck.py",
      "start_line": 1,
      "end_line": 78,
      "text": "\"\"\"``writer-check``: a writer's questions form-checked by code before its session ends (FM-1 of the fresh 80's writer loop).\n\n``python3 -m gov.memaudit writer-check --sets-root R --audit A --repo D --commit REV --folder F [--runs-dir X]`` is the\ncommand of the ``Stop`` hook ``brief --kind writer`` writes into the writer's session folder ``F``. It reads the hook's\nJSON on standard input and ignores it, and runs ``preflight.evaluate`` (the pre-flight's own checks, no copy) on ``F/out/set``.\nClean: nothing is printed and the end is recorded as ``pass``. Refused, with fewer than 3 returns so far: one JSON line\n``{\"decision\": \"block\", \"reason\": ...}`` whose reason is pre-flight's own refusal lines (codes, counts and ids only), one return\ncounted. The fourth stop is allowed (``ended`` is ``limit``). The record is ``WRITER-CHECK.json`` in the audit's run folder.\nExit 0 always: a fault of the check itself lets the session end, and ``deliver`` runs the same checks again.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport os\nimport sys\nfrom pathlib import Path\n\nfrom gov.memaudit import config as _config\nfrom gov.memaudit import layout, preflight\nfrom gov.memaudit.common import read_json, resolve_commit, toplevel, write_whole\n\nDESCRIPTION = (\"The Stop hook of a writer's session: runs the pre-flight's per-question and set checks on out/set and \"\n               \"blocks the stop with their codes and ids, up to 3 returns. Exit 0 always.\")\nMAX_RETURNS = 3\nNAME = \"WRITER-CHECK.json\"\n\n\ndef add_arguments(sp) -> None:\n    sp.add_argument(\"--sets-root\", required=True, metavar=\"ROOT\", help=\"the sets root\")\n    sp.add_argument(\"--audit\", required=True, metavar=\"NAME\", help=\"the half's name, memory-audit-<8 digits>\")\n    sp.add_argument(\"--repo\", metavar=\"DIR\", help=\"the repository (default: the top level)\")\n    sp.add_argument(\"--commit\", required=True, metavar=\"REV\", help=\"the pinned commit the half is written at\")\n    sp.add_argument(\"--folder\", required=True, metavar=\"DIR\", help=\"the writer's session folder (its out/set is checked)\")\n    sp.add_argument(\"--runs-dir\", metavar=\"DIR\", help=\"where indep/ is (default: $GOV_INDEP_RUNS_DIR, else ~/gov-os-runs)\")\n\n\ndef default_runs_dir(runs_dir=None) -> Path:\n    env = os.environ.get(\"GOV_INDEP_RUNS_DIR\")\n    return Path(os.path.expanduser(str(runs_dir) if runs_dir else (env if env else \"~/gov-os-runs\")))\n\n\ndef check(sets_root, audit, *, repo=None, commit, folder, runs_dir=None) -> str | None:\n    \"\"\"The hook's line (JSON) or None. Raises on a fault of the check itself.\"\"\"\n    p = layout.paths(sets_root, audit)\n    repo = Path(repo) if repo is not None else toplevel()\n    commit = resolve_commit(repo, commit)\n    cfg = _config.load(repo, commit)\n    counts, _ = preflight.evaluate(p, Path(folder) / \"out\" / \"set\", repo, commit, cfg, default_runs_dir(runs_dir), audit)\n    run_dir = layout.make_run(p)\n    state = read_json(run_dir / NAME)\n    returns = state.get(\"returns\", 0) if isinstance(state, dict) and isinstance(state.get(\"returns\"), int) else 0\n    refused = {c: list(v[\"ids\"]) for c, v in counts[\"codes\"].items() if not v[\"ok\"]}\n    if any(ids for ids in refused.values()):  # a set-level count off beside refused questions is their consequence\n        refused = {c: ids for c, ids in refused.items() if ids}\n    if not refused:\n        write_whole(run_dir, NAME, {\"returns\": returns, \"ended\": \"pass\", \"refused\": {}})\n        return None\n    if returns >= MAX_RETURNS:\n        write_whole(run_dir, NAME, {\"returns\": returns, \"ended\": \"limit\", \"refused\": refused})\n        return None\n    write_whole(run_dir, NAME, {\"returns\": returns + 1, \"ended\": None, \"refused\": refused})\n    return json.dumps({\"decision\": \"block\", \"reason\": \"\\n\".join(preflight.refused_lines(counts))})\n\n\ndef from_args(args, emit) -> str:\n    try:\n        sys.stdin.read()  # the hook's JSON: ignored\n    except Exception:  # noqa: BLE001\n        pass\n    try:\n        line = check(args.sets_root, args.audit, repo=args.repo, commit=args.commit, folder=args.folder,\n                     runs_dir=args.runs_dir)\n    except Exception:  # noqa: BLE001: a fault of the check lets the session end; deliver checks the files again\n        return \"ok\"\n    if line is not None:\n        emit(line)\n    return \"ok\"\n",
      "chunk_id": "2f3f4efdd5241c6ef60722df",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "133ce56aec39701aebd82101",
      "sha256": "14b59314968bcf17fda61b0dc21f8de016b868158500d16471d94051a1e09f12",
      "path": "src/gov/memaudit/brief.py",
      "start_line": 178,
      "end_line": 184,
      "text": "def stop_hook(p: dict, audit: str, repo, commit: str, out: Path) -> dict:\n    \"\"\"The writer's ``.claude/settings.json``: a ``Stop`` hook running ``writer-check`` on ``out/set`` (FM-1).\"\"\"\n    src = Path(__file__).resolve().parents[2]\n    argv = [\"env\", f\"PYTHONPATH={src}\", sys.executable, \"-m\", \"gov.memaudit\", \"writer-check\", \"--sets-root\", str(p[\"root\"]),\n            \"--audit\", audit, \"--repo\", str(Path(repo).resolve()), \"--commit\", commit, \"--folder\", str(out)]\n    return {\"permissions\": writer_permissions(out),\n            \"hooks\": {\"Stop\": [{\"hooks\": [{\"type\": \"command\", \"command\": shlex.join(argv)}]}]}}\n",
      "chunk_id": "133ce56aec39701aebd82101",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "aac311e1d85428769b90baad",
      "sha256": "83fb5d2dba44764e501ecf513dc12a9bae62d8dae4f065c0d54983f98f4d4840",
      "path": "src/gov/memaudit/writerrun.py",
      "start_line": 1,
      "end_line": 21,
      "text": "\"\"\"``writer-run``: one writer session run with its check in the loop, resumed on a refusal (FM-5 c).\n\n``gov memaudit writer-run --sets-root R --audit A --repo D --commit REV --folder F [--claude CMD] [--session-id UUID]``\nruns the writer's session in ``F`` (``brief --kind writer`` made it) under a kept session id, then ``writercheck.check`` on\n``F/out/set``. A refusal resumes THE SAME session (``--resume <id>``) with pre-flight's own refusal lines alone (ids and\ncodes) as the prompt: at most 3 returns; the fourth stop ends with ``limit``. ``WRITER-CHECK.json`` is written by the check.\nThe session is started without the wall's ``Stop`` hook (``--setting-sources local``) and with the writer's permissions as inline settings, so a return is counted once, here.\nPrinted: ``WRITER-RUN return <n>`` per return and one ``WRITER-RUN <ended> returns <n>``; never a question's text.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport shlex\nimport subprocess\nimport uuid\nfrom pathlib import Path\n\nfrom gov.memaudit import brief, layout, writercheck\nfrom gov.memaudit.common import read_json\n\n",
      "chunk_id": "aac311e1d85428769b90baad",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "991e292998ecd24c1bd53dff",
      "sha256": "ef1f83a0eef1bc010c532abff4b00c70465e9788a003f46e3fd46df3fecc4480",
      "path": "src/gov/memaudit/writerrun.py",
      "start_line": 17,
      "end_line": 26,
      "text": "from pathlib import Path\n\nfrom gov.memaudit import brief, layout, writercheck\nfrom gov.memaudit.common import read_json\n\nDESCRIPTION = (\"Runs a writer's session with its check in the loop: after each stop the pre-flight's checks run on out/set \"\n               \"and a refusal resumes the same session with the refusal lines alone, up to 3 returns.\")\nPROMPT = \"Read brief.md in this folder and do what it says.\"\n\n\n",
      "chunk_id": "991e292998ecd24c1bd53dff",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "db4b36eec6b7acb5ddb5622b",
      "sha256": "76962875edf967b83765b0af9a006ca524625b687938cc18de7b0a2be938921d",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 8,
      "end_line": 13,
      "text": "## What (a K-line FM-5 added to the `## Fix:` section of `.tickets/DAEO-ma4q.md`; the CTO approves it by this brief)\n- **FM-5 The check runs in every real writer launch.** Find every way a writer session is launched for the fresh 80 (read `src/gov/memaudit/` and `indep_launch.py`; the EXAMIN CTO's launch may differ: `gov memaudit brief` must print the exact launch command a CTO uses). In each: the writer-check runs before the session ends, a refused question goes back to that writer with its ids and codes only, at most 3 returns, and the refused ids are recorded. Where a Stop hook can load (the wall's settings template, its approved hashes updated as the launcher requires), use it; where a launch cannot load hooks, the same check-and-return loop is held by code around the session (the session is resumed or called again with its own output and the refusals, never a fresh writer). **Prove it with one real session:** a real `claude -p` writer on Sonnet, launched exactly as the product launches it, on a planted 2-question set in a temporary folder with one planted form fault (no real repository's sets, nothing under any sets root), shows in its transcript and in `WRITER-CHECK.json` the refusal returned and the fixed file accepted. Keep the cost of that run small (one session, a minimal brief).\n- Keep the hidden-set protections and the wall's other settings unchanged.\n\nCode area: `src/gov/memaudit/` (`brief.py`, `writercheck.py`, the launch), `indep_launch.py` and its templates (only the hook line and the approved hashes). Another lead (eval-roots) edits `gov memaudit`'s root resolution: keep clear of it.\n\n",
      "chunk_id": "db4b36eec6b7acb5ddb5622b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "3d4b269e35195a91e86b3eea",
      "sha256": "71010a0763a7ba0442347538c2da5eaf1f4ac7355ebf2573ba56a12a56fa61d1",
      "path": "docs/releases/0.1.6/manifest.json",
      "start_line": 58,
      "end_line": 66,
      "text": "    \"- FM-5: the writer's settings grant Write/Edit into out/, the launch asks no permission prompts\",\n    \"- W2-204 FM-5: the writer's settings grant Write/Edit into out/ and the launch asks no permission prompts\",\n    \"- W2-204 S9: the writer brief prints the BRIEF line plus one LAUNCH writer line (FM-5)\",\n    \"- FM-5: the writer launch line, the wall's Stop hook, writer-run\",\n    \"- DEC-1249 (2) interim: Gov OS's project settings deny reads and edits of both hidden sets roots, and shell commands naming EXAMIN's (I-28), until the eval-roots fix lands\",\n    \"- W2-204 FM-5 acceptance tests: the launch line, the wall's Stop hook, writer-run (red on the base)\",\n    \"- FM-5: the K-line (the check runs in every real writer launch)\",\n    \"- The fix-memaudit-3 lead's brief (FM-5: the writer check proven in the real writer launch; gates 0.1.6), its memory bundle pasted uncut\",\n    \"- Merge e2/fix-memaudit: the fresh 80's writer loop (FM-1 to FM-4): writer-check and deliver run pre-flight's own per-question checks and refuse with codes only; round 2 gets the pre-flight-1 refusals; the void said at once; every stop names its cause\",\n",
      "chunk_id": "3d4b269e35195a91e86b3eea",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "4df3ba7cafe29f0ea06110f30bdb710a5665bc24ab36e2e8400ff29d6df38009",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 315,
      "end_line": 322,
      "text": "- **FM-4 A stop names its cause (I-19).** Every `STOPPED` line of `fresh` is preceded by `CAUSE <audit> <step> <CODE>: <reason>`; an\n  `FR-*` refusal is followed by a `CAUSE` line; a usage fault prints `CAUSE fresh FR-USAGE-<NAME>: <reason>` before `ERROR: UsageError`.\n  Codes, ids and counts only. Verify: one planted stop per kind (final pre-flight refusal, void, measure used-marker, bad tag).\n- **FM-5 The check runs in every real writer launch (fix-memaudit-3, 2026-11-24; gates 0.1.6).** Launch paths: (a) the adopter CTO's\n  `claude -p` in the folder `gov memaudit brief --kind writer` writes: the brief prints the exact launch line (`LAUNCH writer <command>`,\n  also `LAUNCH.txt` in the folder; `--restricted --setting-sources project --settings <out>/.claude/settings.json`, never `--safe-mode`),\n  so the Stop hook of FM-1 loads; (b) Gov OS's walled writer (`indep_launch.py`): the wall's `settings.json.tmpl` carries the same Stop\n  hook (`writer` kind only), filled from the launch's own sets root, set, commit, repository and wall; the template's sha256 is the\n",
      "chunk_id": "415558c76062ff1b6daaee20",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "c8f383b9233cb2f8baea7b2d",
      "sha256": "68d17b0e0565a79afa5a4a9635e35ad2b4702f231e8a499d0815ae36e50dbd34",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "start_line": 9,
      "end_line": 9,
      "text": "- **FM-1 Every writer's questions are form-checked by code before its session ends, and a refused question goes back to the same writer to fix** (the owner, 2026-11-24, as the root fix under Q-7: four void attempts, all at writing). Before a writer session can end, code runs every per-question pre-flight check (`form_ok`, PF-IDEXISTS, PF-DRAWN, PF-SOURCE, PF-EVALNS, PF-DUPPOOL, PF-COMMIT, and the set-level ones once the half is complete) on its files, and any refused question is returned to that writer, in the same session, with its id and code only (never another question's text or gold), to fix; the session ends only when its files pass, or after a bounded number of returns (choose it, for example 3, and say it), when it ends with the refused ids recorded. Writers have no shell: use the session's own end (Claude Code's Stop hook in the writer's launch, which can block the stop and hand back a reason, is the likely mechanism; verify it and choose). `gov memaudit deliver` runs the same checks and refuses with codes only. Reuse pre-flight's own check functions; never copy them. A half that passes the writer's check passes pre-flight 1 on the same files.\n",
      "chunk_id": "c8f383b9233cb2f8baea7b2d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "20ddda96b0f175034b64f582",
      "sha256": "5b8dc247a2d5ecd98d7372b6c93f411957e8eba44541db20ba5b6193b2f7879a",
      "path": "docs/releases/0.1.6/manifest.json",
      "start_line": 54,
      "end_line": 59,
      "text": "    \"- Two fix leads' briefs for the 0.1.6 release suite's ten reds (the walls after FM-5; Phase 0's due rule and kit hook)\",\n    \"- Version 0.1.6 for patch release 0.1.6 (DEC-1248): EXAMIN's measure fixed at the root (each writer's questions form-checked by code before its session ends, refused ones returned to it, proven in a real writer session; round 2 gets the pre-flight refusals; the void said at once; every stop names its cause), the I-17 wheel fix, Phase 0's memory first (the refresh retried and checked, the kit installs the git hook), the kit's licence file\",\n    \"- Merge e2/fix-memaudit-3: FM-1 proven in the real writer launch (FM-5): the writer's launch line, the wall's Stop hook and its write permissions; a real writer session refused a planted form fault and repaired it before its session ended\",\n    \"- FM-5: the writer's permission rules use the double slash of an absolute path\",\n    \"- FM-5: the writer's settings grant Write/Edit into out/, the launch asks no permission prompts\",\n    \"- W2-204 FM-5: the writer's settings grant Write/Edit into out/ and the launch asks no permission prompts\",\n",
      "chunk_id": "20ddda96b0f175034b64f582",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "cda1f982e8ea9eb550fa6cf336120492e1ab43808bc6303f6d0e85ba157126c8",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 322,
      "end_line": 331,
      "text": "  hook (`writer` kind only), filled from the launch's own sets root, set, commit, repository and wall; the template's sha256 is the\n  owner's to enter in `APPROVED`; (c) a launch that loads no hooks (`--safe-mode`): `gov memaudit writer-run` holds the loop by code\n  (the session started with a kept session id, `writer-check` run after it, a refusal resumed into the same session with its ids and\n  codes only, at most 3 returns, never a fresh writer). In each, a refused question goes back to that writer with its ids and codes\n  only, at most 3 returns, and the refused ids are recorded in `WRITER-CHECK.json`. Verify: unit cases for the launch line, the wall's\n  rendered settings and `writer-run` with a planted session seam; one real `claude -p` Sonnet writer, launched as the product prints,\n  on a planted 2-question set with one form fault in a temporary folder: the transcript shows the refusal returned and the fixed file\n  accepted, and `WRITER-CHECK.json` shows `returns` 1 and `ended` pass.\n\nHidden-set protections unchanged (EMERGENCY-2 \u00a72.7): nothing printed or logged names a hidden question's text, gold or sources.\n",
      "chunk_id": "427ea5afd2e6a391d617ad86",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "63a860c50bf39ebf7f0a43b4",
      "sha256": "d00d898328447ac1a11af53c27a1bb9e564748ec3b0fdef0d08c75a0ddbdd5d3",
      "path": "docs/releases/0.1.6/manifest.json",
      "start_line": 66,
      "end_line": 72,
      "text": "    \"- Merge e2/fix-memaudit: the fresh 80's writer loop (FM-1 to FM-4): writer-check and deliver run pre-flight's own per-question checks and refuse with codes only; round 2 gets the pre-flight-1 refusals; the void said at once; every stop names its cause\",\n    \"- The eval-roots lead's brief (DEC-1249 (2), I-28: ER-1 to ER-5), with its memory bundle pasted uncut (DEC-1249 (1))\",\n    \"- DEC-1249: memory first by construction per role (bundle profiles, never cut a result, every return lists its retrieves); every hidden sets root refused by code to non-measure sessions; I-28 logged; LEAD-COMMON carries the rules\",\n    \"- W2-204 README map: FM-1..FM-4 and P0-2 keyed success-20..24 so gov accept reads them\",\n    \"- The fresh 80's writer loop: writer-check Stop hook, deliver pre-flight, round-2 refusals, void at once, causes (FM-1 to FM-4)\",\n    \"- Acceptance tests for the fresh 80's writer loop fix (FM-1 to FM-4)\",\n    \"- Merge w2/integrate into e2/fix-memaudit; DAEO-ma4q: KPI lines FM-1 to FM-4 per the owner's order (Stop hook, round-2 refusals, void at once, causes)\",\n",
      "chunk_id": "63a860c50bf39ebf7f0a43b4",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "3fddcea5f52fc8a95d6cf9eeb5fa3d0ed85d5fca7ffc59aab4ba73837e33e6ba",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 298,
      "end_line": 306,
      "text": "  writer to fix** (the owner, 2026-11-24, Q-7). `gov memaudit brief --kind writer` writes into the session folder a Claude Code\n  `Stop` hook (`.claude/settings.json`) that runs `gov memaudit writer-check`; the hook runs, by `preflight.py`'s own functions, every\n  per-question check (`form_ok`, `PF-COMMIT`, `PF-DRAWN`, `PF-SOURCE`, `PF-EVALNS`, `PF-DUPPOOL`, `PF-IDEXISTS`) on `out/set/`, and the\n  set-level ones (`PF-COUNT`, `PF-QUOTA`, `PF-SPREAD`) once the half is complete, and blocks the stop with a reason that names each\n  refused id and its code only (never a question's text, gold or sources). The session ends when the files pass, or after 3 returns,\n  when it ends and the refused ids are recorded (`out/` is not written; the sets root's run folder holds `WRITER-CHECK.json`).\n  `gov memaudit deliver --kind writer` runs the same checks and refuses with `DL-PREFLIGHT` and codes only. A half that passes the\n  writer's check passes pre-flight 1 on the same files. Verify: planted sets, one refused case per plantable code through the hook and\n  through deliver; a clean set ends at once; the fourth stop is allowed; delivered then `preflight` ok on the same files.\n",
      "chunk_id": "7c8f82dca6aff0001dd8f442",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "e74686b81c96ef15629475f9",
      "sha256": "6e6040d8c08156dc2cd26dd3f3b28d37b8e01bb92161eca1eae56213f30cd929",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 215,
      "end_line": 238,
      "text": "      \"chunk_id\": \"893ce0465aa42fb9ac0f5ee9\",\n      \"routes\": [\n        \"lexical\",\n        \"semantic\"\n      ],\n      \"batch\": 2\n    },\n    {\n      \"id\": \"99cc7aeaded965198ccb3c40\",\n      \"sha256\": \"cd87e264ac40dbc465b07a3705125ef260adfba1ffe75b01e0c0012e5355a512\",\n      \"path\": \"src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md\",\n      \"start_line\": 13,\n      \"end_line\": 19,\n      \"text\": \"# Fixed brief: the memory audit's question writer (DEC-1101 (1)-(2), DEC-1125 (2))\\n\\nVersion 1. This text is hashed, and its sha256 is recorded in the approved list. The CTO may not change it without the\\nowner's approval. The launch script starts you headless in your walled folder, gives you only what \\u00a72 names, and\\ndelivers only what \\u00a77 names. It starts you twice for one audit: round 1 writes the set, round 2 revises it after a\\nchecker's notes.\\n\\n\",\n      \"chunk_id\": \"99cc7aeaded965198ccb3c40\",\n      \"routes\": [\n        \"lexical\",\n        \"semantic\"\n      ],\n      \"batch\": 2\n    },\n    {\n      \"id\": \"03705ce422823d1c11a009aa\",\n      \"sha256\": \"64b726c74b6e00f27d3d53335f8044e7dce10c9bfac4185928402f0d2be1bce7\",\n",
      "chunk_id": "e74686b81c96ef15629475f9",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "91de0768c7cd6825d5819db9",
      "sha256": "afb1e0081057077f5593900d79464e8f8bb4e30605036ef48e3096a8b9c088af",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 5,
      "end_line": 7,
      "text": "## Why\nThe owner's order (DEC-1248 (1)): \"every writer's questions are form-checked by code before its session ends, with any refused question returned to it to fix\". The fix landed on `w2/integrate` as `2ff945336` (read `.gov-runtime/scratch/orchestrator/log/landings/fix-memaudit-20261124.md` and the `## Fix:` sections of `.tickets/DAEO-ma4q.md`): `gov memaudit brief --kind writer` writes a Stop hook running `gov memaudit writer-check` into `<out>/.claude/settings.json`. **It was never proven in a real writer session, and it probably does not load there:** a writer launched through `governance/project/orchestration/tools/indep_launch.py` runs in its wall with the wall's own settings (`--settings <wall>/.claude/settings.json --setting-sources project`, written from the launcher's `settings.json.tmpl` with approved template hashes), not the brief's file; and a session started with `--safe-mode` may load no hooks at all. The 0.1.6 patch release is cut only when this holds.\n\n",
      "chunk_id": "91de0768c7cd6825d5819db9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "59c84964cd0622974408b0bf",
      "sha256": "88b2033dcc4f481af3decbd592fbba84436f304c3cca8ee6184ef3a3479242c4",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 20,
      "end_line": 22,
      "text": "## Return\nBranch and head; every writer launch path found and how the check runs in each; the real session's evidence (transcript lines, `WRITER-CHECK.json`); the selected suites' summary lines; reds not yours; your `gov retrieve` calls (count, queries) and the records used.\n\n",
      "chunk_id": "59c84964cd0622974408b0bf",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "ed0a5da695a10ef996098d29",
      "sha256": "24a9a94978a184cb78b55c2d44f23459d28244e033cb3a58ecee95d5c0612cf7",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 214,
      "end_line": 214,
      "text": "      \"text\": \"- **A fresh pair of halves is one command run until it ends:** `gov memaudit fresh --sets-root R --repo D --commit C\\n  --tag YYYYMMDD`, on a snapshot it clones and builds; the repository's own store is not the one measured.\\n- **The writer and the checker are the adopter's CTO's own fresh sessions**, each given the folder `gov memaudit\\n  brief` writes and nothing else; their output enters the sets root only through `gov memaudit deliver`. The walls\\n  launcher (`indep_launch.py`) and the approved briefs under `governance/project/indep-briefs/` are Gov OS's own\\n  and are not part of what an adopter runs. \\\"Behind the walls\\\" in step 6 holds for Gov OS; for an adopter it reads\\n  \\\"by independent fresh sessions, closed by the transcript scan\\\".\\n- **The CTO never reads the sets root;** the transcript scan at the end of `fresh` (or `gov memaudit scan`) is the\\n  check, and a finding voids the measure.\\n- **The practice record** (`docs/research/W2-88-memory-practice.md`) should name the file as the place of a\\n  repository's domains, categories and control, and say that the control's baseline of a repository without an earlier\\n\",\n",
      "chunk_id": "ed0a5da695a10ef996098d29",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "3d012308355ef6fb04d594f8",
      "sha256": "d9220c4a5b6f6e2856821cbb741b2bc792f0581f37f958ffb94dc4f751b9ee2d",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 281,
      "end_line": 284,
      "text": "      \"text\": \"   (`indep_launch.py`) stays Gov OS's own tool and is not the product's. The product gives the adopter the writer's and\\n   the checker's briefs filled from the repository's configuration (`gov memaudit brief --kind writer|checker`), and the\\n   driver takes the delivered halves from the sets root. Gov OS's own approved briefs\\n   (`governance/project/indep-briefs/memory-audit/*.md`, pinned by sha) are not changed tonight: show in your return\\n   how the generated brief for Gov OS's configuration differs from the approved one (F-2's `by_area` list is expected).\\n4. **F-1 and F-2 are fixed here** (fixes in W2-187's record): the driver follows the cycle above; the writer's result\\n   counts areas in the configuration's own domain list.\\n5. **Comparability.** The reader's and the graders' prompts, schemas and models are not touched (DEC-1098; pinned by\\n   hash in `prompts.py`): a figure from this change compares with FRESH-80-RESULT. No model substitution reaches them.\\n6. **The hidden halves.** You and your helpers never read anything under `~/gov-os-eval` or any real question set.\\n\",\n      \"chunk_id\": \"f3ef3503397017b85e73305b\",\n      \"routes\": [\n        \"semantic\"\n",
      "chunk_id": "3d012308355ef6fb04d594f8",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "b6974b8d38e8c248902d40bf",
      "sha256": "618335de32a45080ca52b5609a8fbe96aec89b6d1024be841b4058e31607c682",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 256,
      "end_line": 275,
      "text": "      \"chunk_id\": \"c2a32ef4dfa8a7be5cfa6ce9\",\n      \"routes\": [\n        \"semantic\"\n      ],\n      \"batch\": 2\n    },\n    {\n      \"id\": \"8322f1dbdc004e179050f3d7\",\n      \"sha256\": \"f0648a369ab5c6bf56fa244f73e723ef3aaeafad08d25637ab2bbbf0a8add231\",\n      \"path\": \"src/gov/memaudit/briefs/__init__.py\",\n      \"start_line\": 1,\n      \"end_line\": 9,\n      \"text\": \"\\\"\\\"\\\"The writer's and the checker's brief templates (W2-204 I5, S9), filled by ``gov.memaudit.brief`` from a repository's\\nown configuration. They follow the sections of Gov OS's approved briefs (``governance/project/indep-briefs/memory-audit/``):\\nthe job, the folder, what to read, what never to read, the rules, round 2, the output, the result, the stops. A template\\nnames no repository's category, domain or subsystem: every such name is a ``{{field}}`` the configuration fills. The\\ntext is kept in Python modules so that an installed release carries it without a package-data entry.\\\"\\\"\\\"\\n\\nfrom gov.memaudit.briefs import checker, writer\\n\\nTEMPLATES = {\\\"writer\\\": writer.TEXT, \\\"checker\\\": checker.TEXT}\\n\",\n      \"chunk_id\": \"8322f1dbdc004e179050f3d7\",\n      \"routes\": [\n        \"semantic\"\n      ],\n      \"batch\": 2\n    },\n    {\n",
      "chunk_id": "b6974b8d38e8c248902d40bf",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "baab709dfa75efe08c08c6bb",
      "sha256": "d01be04bbdcdf8a83069121b5e29d91624c1a48a695bec163aadc552439f30d2",
      "path": "docs/releases/0.1.6/NOTE.md",
      "start_line": 5,
      "end_line": 24,
      "text": "## What changed\n\n- Fix: I-17 gov update refuses its own release's wheel\n- Fix: P0-1\n- Fix: P0-2\n- Fix: I-21 W2-209 S3 asserted the authority file off after the owner turned it on\n- Fix: P0-3\n- Fix: the fresh 80's writer loop (I-23 with EF-9, I-18, I-19)\n- Fix: the fresh 80's writer loop (I-23 with EF-9, I-18, I-19)\n- Fix: the fresh 80's writer loop (I-23 with EF-9, I-18, I-19)\n- Fix: the fresh 80's writer loop (I-23 with EF-9, I-18, I-19)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: FM-1 proven in the real writer launch (FM-5)\n- Fix: the 0.1.6 release suite's wall reds: the tests state the Stop hook as the one allowed difference (FM-5, DEC-1248)\n- Fix: the 0.1.6 release suite's Phase 0 reds: S2's second-time case states P0-1's due rule; the W2-208 only-committed case no longer depends on the time of day\n",
      "chunk_id": "baab709dfa75efe08c08c6bb",
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
    "duplicates": 24,
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
      "chunk_id": "2f3f4efdd5241c6ef60722df",
      "parent_id": "b2902a693187b478953dc056",
      "path": "src/gov/memaudit/writercheck.py",
      "start_line": 1,
      "end_line": 78
    },
    {
      "chunk_id": "db4b36eec6b7acb5ddb5622b",
      "parent_id": "c8b9ec77178c5ec2cf15d801",
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "start_line": 8,
      "end_line": 13
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "78e9889b221ab550b6f02bdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "1681e605033755fc598965f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ae204bbcdb9b8211a1ef9307",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "163301d7882f68794ce6adce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "01c12e6f9426ae8c0351cd55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fbb87d3428c4a8f1a58ac847",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "189449b9b3676c64da1f3045",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "be140e0dfbdf4eb3b3980f1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "07aa9bad6c4ee88bf4280c50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "59d6b754631597d744fbac14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "24d7f93984de9b88d50dd193",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "c767fd7a54cca86055e4d7d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-walls.md",
      "chunk_id": "f1b25aa848de651dd81f6a82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-walls.md",
      "chunk_id": "96ff32c62149750eadcba503",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "eb3d78c575c1b822371a4dcb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "d6224cdda5084295e978a7e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "91c433d34ab0f87811570d31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4cf85c3a37df92ad5af15501",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-walls.md",
      "chunk_id": "c666c5ec021e19b03a07f31e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-walls.md",
      "chunk_id": "d3a28b64790d1bfc1ad8fef5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "8a60c6285c43568287970ab8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "4cb998327b05eb4baa68b2d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qz4p.md",
      "chunk_id": "ee2c22bf78320eebe75a4bf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "991c891114493f708c46f63d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "3ef6bd8eaca988894236ff01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/brief.py",
      "chunk_id": "cb07f00ac1bcd246ed87f71e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/brief.py",
      "chunk_id": "11e4649b22eafece7d9f0355",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "chunk_id": "69bebe6656f512e1500a0f35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "a55e564248ede64462705f8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "e55eab2dec97edbdf8bfdb05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "6a85841e4cd548e296e2b61a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "99cc7aeaded965198ccb3c40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "b56afafabec822873db515de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "a845c20032ba35e5d821cd8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/brief.py",
      "chunk_id": "ba0a748e89634d8693417358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "5c9f6b4a4c0a556aa958d998",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "a03867c80b4920e3d71b6c93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "69225e84725cebdeaf8fdb13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/HANDOVER.md",
      "chunk_id": "b2638aa81405517fad6bcea1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "3052ed37beea2335a80aa092",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "9c0d8fbe8ddfd2543b2a626d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qz4p.md",
      "chunk_id": "e00f1e4ebd4d77025e887d33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "b81953eb96bebe3b26ed411d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "0a0673937cec6eb5302a7d3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "7020187e7ac83e347f1da73d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "0be878db3dd9d3d79d74543c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "86ad7690c8e4e28b9765fff0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "595db0a0b910e0ab441a6d72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ebacef3ce28b88f3b4f6e016",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "356a7f13ec0d9dcc2e9c9aa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/writercheck.py",
      "chunk_id": "0c720e651dfe5e953f5e02de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "2fe8a66aa59018cae85f53fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60b-CIT-E.md",
      "chunk_id": "926d914c89aed647943e8ead",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "b643ecc5195bb0977d5e4c55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/deliver.py",
      "chunk_id": "47b87b73ab5c4beac7fff804",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "0425abbaba5e0542c2047e7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "85d39a5f5a6ab5e561f2f0cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "8f9ef3922a440bffbfd5ff64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "c67292b2fff686038ddcee98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/sgx1/writer-tuning.md",
      "chunk_id": "03705ce422823d1c11a009aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/sgx1/writer-tuning.md",
      "chunk_id": "a8c5139664431215efd59f7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "4d71c4aed654a12b076fe703",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "0f8b091c6022867e4819e68d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "1bdeb2a62c9260d9a1811839",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "d08c398bb7765becfc9e9732",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "6c6a9155d4448e1ebb47bc58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/memory-audit.yaml",
      "chunk_id": "69aa2e8a9dd1999126b1e28b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "ff746ee40f0bf8e45476d83d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-173-evidence.md",
      "chunk_id": "623b9e438de39eb5f61105e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "4054ae4b66fe750c66cae7df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "841a7d6bc859eb5542b38086",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "2943af0b5b7b908e97eac2f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-178/test_w2_178_unchanged.py",
      "chunk_id": "d91e45aa8eb06f3b084a8f98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "95a8313c1e51daf4014bf685",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "1db6a1c38f72df639d934806",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "fedc64cf47718cde60dc1c64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "624b5cf847d7c9b2af679bff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md",
      "chunk_id": "ad5432c8fb79fcce4b2fca87",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-42a-evidence.md",
      "chunk_id": "d144f5e8db77ec7c47213c1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit.md",
      "chunk_id": "314e2293dbe9252f5eb1c61d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9f78a531a985c7c40ff3b892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/checker.md",
      "chunk_id": "01e5e717ec3c38022b7fb0e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/test_w2_204_fix_writer_loop.py",
      "chunk_id": "dbd01354b5f5b06aa9fad6ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "12ae53c0f0df4b639a6ef1f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/sgx1/writer-heldout.md",
      "chunk_id": "07f1bb13ebc3344c01dd8b86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6c496d5f643754ef3df0583f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4d655b6dbea4dfa32f6c5261",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cf99cd773ecf6cf6e1ed0830",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4e433d38c9370738dec705d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "4e1e8c76d89de168730c2e20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/test_w2_204_fix_writer_loop.py",
      "chunk_id": "6e70667b6b2856b9c0597471",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "7591c66df3fa654bde5cc8ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "79b7aee9706b1ef29de0931e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "abc74248c32273f1c022bc7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "82497daab714537dccd10313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9b0ebfe72ee53d6ed08dd309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6a9dee6e838a6b4ead5fa878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "19f49b00a88a8f0fb42c62e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "c941ec1c25ffb656afea885c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63ba33081f31cfb82cce61bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "213f0c02b7aaa40127bbd43f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e3f050f7c7f6d3f33560cf2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1f4fb10e2c09ba11e7666302",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1879d875a44a02135a1da4b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1bf642f128c3a3738d7c2db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "5fbd2cd6062591b55ef8d6b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "70eb80cab27469a298a9e078",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/test_w2_204_s9_s10_brief_deliver.py",
      "chunk_id": "76ae054d5c02b1e2dda23a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ccd2f7a9ecfe2fee02880502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4364c134b7f98007ccbc3386",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "46fceeb40f98e5bccf1f6794",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "22703223eb3e7b9382b7c76c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fd2bb734568e19eda709960a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cc22f8ec310fe1d07afc7ff9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "8a6e46f4154e615748350033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "52c8157855a7a5b72b7fbc78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/w2_204_writer_loop_support.py",
      "chunk_id": "a3b1e03eb0e03b16d155cb91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "b19275fc1197d0c0783bd0c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "512edda262b93b0187652c9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e854d0972b13f6cc03767a1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4d2d97f055b7b79b0349af8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fa33b9709e40bdc766fabd24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "54914e2d44b8f66576556648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9137858e4a6751c80914ac61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e753b8925f988bef182f0415",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-149/w2_149_support.py",
      "chunk_id": "647730e28862fc54517ac692",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63c42cd5ebdddc0c8563fa80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "a1c9ca78d1c305865623ce7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "60f6798d6fca501b58ac067e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "f57558a8221a57b1560a4a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-178/w2_178_support.py",
      "chunk_id": "12d2aa9ce52eac5098e26b62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "81c73ec6956191c300e304cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "7c34dce2b2108a2d42efa875",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "26ec65d12749afc6cfb1779e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "3ac9b63444a1aae7ee9c0286",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ef19d4a550ab9bc76eb65eae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6f7ee57752d2d10479d97ac7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/test_w2_204_fm5_launch.py",
      "chunk_id": "ae5b59dbb4fc84a4308896af",
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
      "used": 5840
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLW1hNHEubWQiLDI5OCwzMDYsIjdjOGY4MmRjYTZhZmYwMDAxZGQ4ZjQ0MiJdLFsiLnRpY2tldHMvREFFTy1tYTRxLm1kIiwzMTUsMzIyLCI0MTU1NThjNzYwNjJmZjFiNmRhYWVlMjAiXSxbIi50aWNrZXRzL0RBRU8tbWE0cS5tZCIsMzIyLDMzMSwiNDI3ZWE1YWZkMmU2YTM5MWQ2MTdhZDg2Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWZpeC1tZW1hdWRpdC0zLm1kIiw1LDcsIjkxZGUwNzY4YzdjZDY4MjVkNTgxOWRiOSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1maXgtbWVtYXVkaXQtMy5tZCIsMTAsMTMsImFjZGU3YWM4NzE4NzkyY2RlZjc5OTQ2YSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1maXgtbWVtYXVkaXQtMy5tZCIsMjAsMjIsIjU5Yzg0OTY0Y2QwNjIyOTc0NDA4YjBiZiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1maXgtbWVtYXVkaXQtMy5tZCIsMjE0LDIxNCwiZWQwYTVkYTY5NWExMGVmOTk2MDk4ZDI5Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWZpeC1tZW1hdWRpdC0zLm1kIiwyMTUsMjM4LCJlNzQ2ODZiODFjOTZlZjE1NjI5NDc1ZjkiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtZml4LW1lbWF1ZGl0LTMubWQiLDI1NiwyNzUsImI2OTc0YjhkMzhlOGMyNDg5MDJkNDBiZiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1maXgtbWVtYXVkaXQtMy5tZCIsMjgxLDI4NCwiM2QwMTIzMDgzNTVlZjZmYjA0ZDU5NGY4Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWZpeC1tZW1hdWRpdC5tZCIsOSw5LCJjOGYzODNiOTIzM2NiMmY4YmFlYTdiMmQiXSxbImRvY3MvcmVsZWFzZXMvMC4xLjYvTk9URS5tZCIsNSwyNCwiYmFhYjcwOWRmYTc1ZWZlMDhjMDhjNmJiIl0sWyJkb2NzL3JlbGVhc2VzLzAuMS42L21hbmlmZXN0Lmpzb24iLDU0LDU5LCIyMGRkZGE5NmIwZjE3NTAzNGI2NGY1ODIiXSxbImRvY3MvcmVsZWFzZXMvMC4xLjYvbWFuaWZlc3QuanNvbiIsNTgsNjYsIjNkNGIyNjllMzUxOTVhOTFlODZiM2VlYSJdLFsiZG9jcy9yZWxlYXNlcy8wLjEuNi9tYW5pZmVzdC5qc29uIiw2Niw3MiwiNjNhODYwYzUwYmYzOWViZjdmMGE0M2I0Il0sWyJzcmMvZ292L21lbWF1ZGl0L2JyaWVmLnB5IiwxNzgsMTg0LCIxMzNjZTU2YWVjMzk3MDFhZWJkODIxMDEiXSxbInNyYy9nb3YvbWVtYXVkaXQvd3JpdGVycnVuLnB5IiwxLDIxLCJhYWMzMTFlMWQ4NTQyODc2OWI5MGJhYWQiXSxbInNyYy9nb3YvbWVtYXVkaXQvd3JpdGVycnVuLnB5IiwxNywyNiwiOTkxZTI5Mjk5OGVjZDI0YzFiZDUzZGZmIl1dLCJmIjoiL2hvbWUvdXNhaW4vRHluYW1pYy1BZ2VudGljLUVuZ2luZWVyaW5nLU9TIiwiaSI6W10sIm8iOjIwLCJwIjp7ImIiOiJzZXJ2aWNlIiwiZCI6ImN1ZGE6MCIsImgiOiIxNjQ4NDFhYzJhYjk4Y2JlIiwibyI6WzgsMTcsMTQsMzUsMCwxLDIsMTAsMywyNCw5LDI3LDMwLDUsNCwxOCwzMSwyOSwyMCwyMywzNywxNSwzOCwxMiwyNSw2LDE5LDM0LDEzLDcsMTEsMTYsMzYsMzMsMjYsMzksMjEsMjIsMzIsMjhdfSwicSI6ImdvdiBtZW1hdWRpdCBicmllZiBMQVVOQ0ggbGluZSBhbmQgTEFVTkNILnR4dCwgdGhlIHdyaXRlciBTdG9wIGhvb2sgd3JpdGVyLWNoZWNrIGFuZCBXUklURVItQ0hFQ0suanNvbiwgdGhlIHNldHMtcm9vdCBwcmludCByZWZ1c2FsLCBGTS0xIGFuZCBGTS01IHJlYWwgd3JpdGVyIHNlc3Npb24gcHJvb2YiLCJyIjowLCJzIjoiYzFlODFhZmQzZTc1NjBlN2E4Zjc2OWJiNTFkZTA4M2IwN2Q3MjE1OCIsInQiOm51bGwsIngiOlsiYjI5MDJhNjkzMTg3YjQ3ODk1M2RjMDU2IiwiYzhiOWVjNzcxNzhjNWVjMmNmMTVkODAxIl19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "gov memaudit brief LAUNCH line and LAUNCH.txt, the writer Stop hook writer-check and WRITER-CHECK.json, the sets-root print refusal, FM-1 and FM-5 real writer session proof",
      "gov memaudit brief LAUNCH line LAUNCH.txt writer Stop hook writer-check WRITER-CHECK.json sets-root print refusal FM-1 FM-5 real writer session proof"
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
    "nested": [
      {
        "chunk_id": "acde7ac8718792cdef79946a",
        "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
        "start_line": 10,
        "end_line": 13
      }
    ]
  }
}
