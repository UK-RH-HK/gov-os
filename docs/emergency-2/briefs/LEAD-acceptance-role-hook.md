# Lead brief: acceptance-role-hook, a commit touching `tests/acceptance/` without the test designer's role is refused by code at commit time (the owner's root fix, DEC-1254 E-01 and E-04; fixes under W2-115b DAEO-j9z6 and the kit W2-208 DAEO-kt8e)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store`.

## Why
The owner (DEC-1254, read it in `docs/DECISION_REGISTER.md`): "Root fix, since this is the fourth time (I-12, DEC-1243, now E-01 and
E-04): refuse by code, at commit time, any commit that touches tests/acceptance/ without the test designer's role, so it can never reach a
landing again." Today only the landing catches it (`src/gov/queue/checks.py:54-73`, `test_authors`, which reads a two-parent merge by its
`--remerge-diff`; `TEST_ROLES = ("independent-test-designer", "owner")` at `:31`), after the work is built on: seven exemptions in
`governance/project/path-map.yaml` `acceptance_exemptions` were the cost (FINDINGS I-12, I-15; DEC-1123, DEC-1217, DEC-1254). This
changes EMERGENCY-2 §2.1-2.2 ("no guard") for this one case, by the owner's order.

## What (K-lines as `## Fix:` sections in `.tickets/DAEO-j9z6.md` and `.tickets/DAEO-kt8e.md`; the CTO approves them by this brief)
- **AR-1 A plain commit.** A commit whose staged changes touch `tests/acceptance/` is refused unless its message's trailers (as
  `git interpret-trailers` reads them, so a blank line before `Co-Authored-By` hides them, as at the landing) carry a `Role:` in
  `TEST_ROLES` and no other role; the refusal names the paths and the role it read. Every other commit passes untouched and fast (under
  0.5 s on this repository). Verify: in a planted repository with the hook installed, a commit editing a file under `tests/acceptance/`
  with `Role: engineer`, with no `Role`, and with the trailers hidden by a blank line is refused; with `Role: independent-test-designer`
  or `Role: owner` it passes; a commit outside `tests/acceptance/` passes with any role.
- **AR-2 A merge is judged by what it resolved**, the landing's own reading: a merge whose result differs from git's automatic merge
  under `tests/acceptance/` (the conflicted or hand-changed paths there) needs the test designer's role alone; a merge that brings
  acceptance changes in cleanly (an integration branch merged into a lead branch) passes with any role. Reuse the landing's logic
  (`checks.py`), never a second copy. Verify: a clean merge carrying another branch's acceptance edits passes under `Role: orchestrator`;
  a merge that resolves a README conflict under `tests/acceptance/` is refused under `Role: orchestrator` and passes under
  `Role: independent-test-designer`.
- **AR-3 Installed by the product, everywhere.** The hook ships in the kit beside `template/governance/kernel/githooks/reference-transaction`
  and is installed by `gov adopt`, `gov adapters` and `gov update` the way that hook is (plan 0-3), into Gov OS (its main tree and every
  worktree, which share the common hooks) and every adopted repository; an existing hook of the same git event is kept and chained, never
  overwritten. `--no-verify` is the owner's escape and is not blocked (git does not allow that), but the landing's check stays as the net.
  Verify: after `gov update` in a scratch adopted repository the hook exists and AR-1's refusal happens there.
- **Prove it in the real path** (the CTO's rule: a hook is proven in a real commit, not by its command line): in a scratch clone of Gov OS
  with the hook installed by the product's own installer, one real refused commit and one real passing commit; record the commands and
  outputs in your return.

## Where
Branch `e2/acceptance-role-hook` **from `e2/bundle-b`** (head `a4aa69afc`: the kit's hook installs changed there), worktree
`/home/usain/gov-os-worktrees/E2-acceptance-role-hook`. Code area: the new hook under `template/governance/kernel/githooks/`, the
installer where the reference-transaction hook is installed (find it: `gov adopt`, `gov adapters`, `gov update`), `src/gov/queue/checks.py`
only to expose the shared reading, `tests/unit/` for them, `tests/acceptance/W2-115b/` and `tests/acceptance/W2-208/` (the independent test
designer only), the two ticket files. Do not install the hook into the main tree `/home/usain/Dynamic-Agentic-Engineering-OS` yourself:
the CTO does at the landing. Never merge into `w2/integrate` or `e2/bundle-b`.

## Green
AR-1 to AR-3 red on the base, green after; `gov accept W2-115b` and `gov accept W2-208` green; the real-path proof; then exactly the
impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-j9z6=e2/acceptance-role-hook --onto e2/bundle-b
--select`) through the heavy slot. Check the trailers (LEAD-COMMON): your own acceptance commits must pass the hook you build.

## Return
Branch and head; where the hook and installer live (file:line); AR-1 to AR-3 with tests and result; the real-path proof; the hook's time
on an ordinary commit; the selected run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: cbb322668017 (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "cbb322668017ed3ab7da111fc0cd8e2106b60905",
    "head": "cbb322668017ed3ab7da111fc0cd8e2106b60905",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "b62919e3e91dd56e83d837f4",
      "sha256": "b79f4fd96514f9828f5e1c29951867d8b07670751633505672218eb1e95061e8",
      "path": "src/gov/queue/checks.py",
      "start_line": 54,
      "end_line": 73,
      "text": "def test_authors(root: Path, base: str, tip: str, places: list[str]) -> list[dict]:\n    \"\"\"The commits of ``base..tip`` that change ``places`` without the role that may: ``{\"commit\", \"roles\",\n    \"subject\"}`` each. ``RuntimeError`` where git cannot read them (the caller refuses: fails closed).\"\"\"\n    places = [p for p in places if p and p.strip(\"/\")]\n    touched = _git(root, \"rev-list\", \"--full-history\", \"--no-merges\", f\"{base}..{tip}\", \"--\", *places).split()\n    for merge in _git(root, \"rev-list\", \"--merges\", f\"{base}..{tip}\").split():\n        if len(_git(root, \"rev-list\", \"--parents\", \"-n\", \"1\", merge).split()) == 3:\n            names = _git(root, \"log\", \"-1\", \"--remerge-diff\", \"--format=\", \"--name-only\", merge).splitlines()\n        else:\n            names = _git(root, \"diff\", \"--name-only\", f\"{merge}^1\", merge).splitlines()\n        if any(_under(n, places) for n in names):\n            touched.append(merge)\n    bad = []\n    for commit in touched:\n        roles, _, subject = _git(root, \"log\", \"-1\", \"--format=%(trailers:key=Role,valueonly,separator=%x1f)%x00%s\",\n                                 commit).rstrip(\"\\n\").partition(\"\\x00\")\n        roles = [r.strip() for r in roles.split(\"\\x1f\") if r.strip()]\n        if not roles or any(r not in TEST_ROLES for r in roles):\n            bad.append({\"commit\": commit, \"roles\": roles, \"subject\": subject[:120]})\n    return bad\n",
      "chunk_id": "b62919e3e91dd56e83d837f4",
      "routes": [
        "lexical",
        "code"
      ],
      "batch": 1
    },
    {
      "id": "a2ae0930edfc0592cfa9afe9",
      "sha256": "97db5db369278f68228b08a6b593dca5721059c9606eb305be13dfabf513e466",
      "path": "src/gov/adapters/merge.py",
      "start_line": 197,
      "end_line": 230,
      "text": "def install_hook(root: Path) -> str | None:\n    \"\"\"P0-3: the kit's ``reference-transaction`` written to the repository's hooks folder, executable and byte for byte,\n    where it is not already so; the path as ``.git/hooks/reference-transaction`` where it is there afterwards, else None\n    (Gov OS's own source tree keeps its own hook; a kit without the file, or a folder with no git, installs nothing).\n    A ``.git/hooks/reference-transaction.local`` is the site's own and is never touched.\"\"\"\n    import subprocess\n\n    from gov.adapters import portability\n    from gov.util.gitenv import git_binary, git_env\n\n    if _is_source_tree(root):\n        return None\n    kernel = portability._kernel(root)\n    kit = kernel / HOOK_KIT if kernel is not None else None\n    if kit is None or not kit.is_file():\n        return None\n    done = subprocess.run([git_binary() or \"git\", \"-C\", str(root), \"rev-parse\", \"--git-path\",\n                           \"hooks/reference-transaction\"], capture_output=True, text=True, env=git_env(root))\n    if done.returncode != 0 or not done.stdout.strip():\n        return None\n    target = Path(done.stdout.strip())\n    target = target if target.is_absolute() else root / target\n    data = kit.read_bytes()\n    try:\n        if not (target.is_file() and not target.is_symlink() and target.read_bytes() == data):\n            target.parent.mkdir(parents=True, exist_ok=True)\n            if os.path.lexists(target):\n                target.unlink()\n            target.write_bytes(data)\n        if not os.access(target, os.X_OK):\n            target.chmod(0o755)\n    except OSError as exc:\n        raise _refuse(\"HOOK_UNWRITABLE\", f\"{target} cannot be written ({exc}): nothing is written\") from None\n    return HOOK_REL\n",
      "chunk_id": "a2ae0930edfc0592cfa9afe9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "f6185b54ca11c950fd7eff1a",
      "sha256": "e6f2dfd12dffd1bc3279e0db450ef9dffba34a5310913dae187a1bc3180ac8ce",
      "path": "src/gov/update/core.py",
      "start_line": 624,
      "end_line": 627,
      "text": "def _hooks(project: Path) -> list[str]:\n    \"\"\"P0-3: the git hooks of the kit that stand in the project, byte for byte, as ``.git/hooks/<name>``.\"\"\"\n    from gov.adapters import merge\n    return [merge.HOOK_REL] if merge.install_hook(project) else []\n",
      "chunk_id": "f6185b54ca11c950fd7eff1a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-kt8e",
      "sha256": "e5df0c64b6b4ad50a67b2e9c0711c65ea83e404819ef12a1f520a1924cd829e3",
      "path": ".tickets/DAEO-kt8e.md",
      "start_line": 110,
      "end_line": 131,
      "text": "## Fix: the kit carries the git hook; adopt, adapters and update install it (plan item 0-3; phase0-memory, 2026-11-24)\n\nDEC-1245 (2), DEC-1241 G-4 (a). Gov OS's live hook `.git/hooks/reference-transaction` is untracked and written by hand; an\nadopted repository has none. The kit carries `template/governance/kernel/githooks/reference-transaction`; `gov adopt`,\n`gov adapters generate` and `gov update` write it to `.git/hooks/reference-transaction` (executable), and the update's\nrecord (`governance/updates/<B>.json`) lists it. It refreshes the integration branch read from\n`integration_refresh.branch` of `governance/project/rebuild.yaml` (never fixed to `w2/integrate`), through P0-1's retry; a\nfailed refresh leaves one inbox message (`gov.dispatch.inbox`, kind `notice`). The operator-freeze lines are not in the\nkit's file. In Gov OS the `landing_select.sh` call lives in a local hook file `.git/hooks/reference-transaction.local`\n(untracked, stays until Day M), which the kit's hook runs when present.\n\n- **P0-3 (success).** Verify: in a scratch repository after `gov adopt`, `.git/hooks/reference-transaction` exists and is\n  byte-equal to the kit's file; a commit on its integration branch makes the store's commit equal HEAD within 5 minutes (a\n  log line says so); the hook file deleted and `gov update` run, it is back and the update record lists it; a planted\n  refresh failure leaves exactly one inbox message; the kit's file holds no freeze line and no `w2/integrate`.\n  Failure: an adopted repository without the hook after adopt or update, or a failed refresh with no inbox message, or a\n  hook that refreshes only `w2/integrate`.\n  Tests: `tests/acceptance/W2-208/test_w2_208_p0_3_*.py`.\n\nAs built: `gov adapters generate` (so also adopt's path and `gov update`'s regeneration) installs the hook through\n`gov.adapters.merge.install_hook`; the update record has `hooks`. The hook keeps `PYTHONPATH` (the acceptance rig's `gov`\nshim needs it); it unsets `PYTHONHOME`, `PYTHONSTARTUP` and the git variables.\n",
      "chunk_id": "2389a07214e3705f5992e785",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "21b3f7dab4be2b0f2af48c82",
      "sha256": "982d88e35e8e6727d3978df1505f8140b1b004cb50759f2acc0fcf1e9d0f919d",
      "path": "src/gov/adapters/merge.py",
      "start_line": 191,
      "end_line": 196,
      "text": "\n\nHOOK_KIT = \"githooks/reference-transaction\"  # under the kit's kernel folder\nHOOK_REL = \".git/hooks/reference-transaction\"\n\n\n",
      "chunk_id": "21b3f7dab4be2b0f2af48c82",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "f1f7fd56d3a4ddcdf76c69c5",
      "sha256": "a101d439abe19f4bfbdeceeb500928ff56a8ef3ff8b5992985c37d3118a1479f",
      "path": "template/governance/kernel/githooks/reference-transaction",
      "start_line": 1,
      "end_line": 76,
      "text": "#!/bin/sh\n# Gov OS kit: refresh the integration store after every commit on the repository's integration branch.\n# The branch is read from governance/project/rebuild.yaml (integration_refresh: branch:). The refresh is\n# `gov rebuild --integration <branch> --when-due` (a store behind the branch head is due), run in the background,\n# retried, logged to .gov-runtime/refresh-hook.log; a refresh that still fails after its retries leaves ONE notice in the\n# CTO's inbox. A site's own additions go in .git/hooks/reference-transaction.local (same arguments, same stdin).\n# The hook never fails the git operation: it always exits 0.\n\nself=$(cd \"$(dirname \"$0\")\" 2>/dev/null && pwd)/$(basename \"$0\")\n\n# The background half: started by the committed state below, under the refresh lock.\nif [ \"$1\" = --refresh ]; then\n  root=$2 branch=$3 gov=$4\n  cd \"$root\" 2>/dev/null || exit 0\n  if [ -z \"$GOV_REFRESH_HOOK_LOCKED\" ] && command -v flock >/dev/null 2>&1; then\n    exec env GOV_REFRESH_HOOK_LOCKED=1 flock -o \"$root/.gov-runtime/refresh-hook.lock\" \\\n      sh \"$self\" --refresh \"$root\" \"$branch\" \"$gov\"\n  fi\n  tries=3 n=0\n  while [ \"$n\" -lt \"$tries\" ]; do\n    n=$((n + 1))\n    echo \"refresh-hook: $(date '+%Y-%m-%d %H:%M:%S') try $n of $tries: gov rebuild --integration $branch --when-due\"\n    if \"$gov\" rebuild --integration \"$branch\" --when-due; then\n      exit 0\n    fi\n    [ \"$n\" -lt \"$tries\" ] && sleep $((n * 10))\n  done\n  \"$gov\" msg send cto notice \"the refresh of the integration store for $branch in $root failed $tries times (REBUILD_FAILED); see $root/.gov-runtime/refresh-hook.log\" --from refresh-hook\n  exit 0\nfi\n\nstate=$1\ninput=$(mktemp 2>/dev/null) || input=\nif [ -n \"$input\" ]; then cat > \"$input\"; else input=/dev/null; fi\n\nlocal_hook=\"$(dirname \"$self\")/reference-transaction.local\"\nif [ -x \"$local_hook\" ]; then\n  \"$local_hook\" \"$@\" < \"$input\" || true\nfi\n\n[ \"$state\" = committed ] || { [ \"$input\" = /dev/null ] || rm -f \"$input\"; exit 0; }\n\nroot=$(git rev-parse --show-toplevel 2>/dev/null)\nbranch=\nif [ -n \"$root\" ] && [ -f \"$root/governance/project/rebuild.yaml\" ]; then\n  branch=$(awk -v q=\"'\" '\n    /^integration_refresh:/ { in_block = 1; next }\n    in_block && /^[^ \\t#]/ { in_block = 0 }\n    in_block && /^[ \\t]+branch:/ {\n      sub(/^[ \\t]+branch:[ \\t]*/, \"\"); sub(/[ \\t]*#.*$/, \"\"); gsub(\"^[\\\"\" q \"]|[\\\"\" q \"]$\", \"\"); print; exit\n    }' \"$root/governance/project/rebuild.yaml\")\nfi\n\nhit=\nif [ -n \"$branch\" ]; then\n  while read -r old new ref; do\n    [ \"$ref\" = \"refs/heads/$branch\" ] && hit=1\n  done < \"$input\"\nfi\n[ \"$input\" = /dev/null ] || rm -f \"$input\"\n[ -n \"$hit\" ] || exit 0\n\ngov=$(command -v gov 2>/dev/null)\n[ -n \"$gov\" ] || { [ -x \"$HOME/.local/bin/gov\" ] && gov=$HOME/.local/bin/gov; }\n[ -n \"$gov\" ] || exit 0\n\nmkdir -p \"$root/.gov-runtime\" 2>/dev/null || exit 0\nlog=\"$root/.gov-runtime/refresh-hook.log\"\nif command -v setsid >/dev/null 2>&1; then\n  setsid -f env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u PYTHONHOME -u PYTHONSTARTUP \\\n    -u GOV_REBUILD_LOCK sh \"$self\" --refresh \"$root\" \"$branch\" \"$gov\" >> \"$log\" 2>&1 < /dev/null\nelse\n  nohup env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u PYTHONHOME -u PYTHONSTARTUP \\\n    -u GOV_REBUILD_LOCK sh \"$self\" --refresh \"$root\" \"$branch\" \"$gov\" >> \"$log\" 2>&1 < /dev/null &\nfi\nexit 0\n",
      "chunk_id": "f1f7fd56d3a4ddcdf76c69c5",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "582ca0ea3581586067e1fd37",
      "sha256": "9df13e2d1a9f590650b97968a15ff27d324522202754bba691557360ad5b7082",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 51,
      "end_line": 51,
      "text": "| 0-3 | **The product installs the git hook.** `gov adopt`, `gov adapters` and `gov update` write `.git/hooks/reference-transaction` from a file the kit carries. It runs the refresh with 0-1's retry for the repository's integration branch (read from configuration, not fixed to `w2/integrate`), and puts a failure in the inbox. The retired operator freeze lines go. In Gov OS, the `landing_select.sh` line moves to a local hook file that stays until Day M. [G-4 (a); T-5's note \"the kit installing the git hook\"; P-7; A-10, A-28; map row 11] | W2-116 (hook); W2-208 (DAEO-kt8e, the kit; closed, a fix under it) | fix M | 0-1 | W3, W1 | In a scratch repository after `gov adopt`, the hook exists and equals the kit's file. A commit on its integration branch makes the store's commit equal HEAD within 5 minutes (a log line says so). Delete the hook and run `gov update`: it is back and the update record lists it. A planted refresh failure leaves one inbox message. |\n",
      "chunk_id": "582ca0ea3581586067e1fd37",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4a5d046a487473e9ff23cfde",
      "sha256": "da818d543701cd6336ffd54d5696c40756f33de9e077e9f9ddf0ab5eb51fc819",
      "path": "docs/emergency-2/release-0.1.8/TOOL-STATUS-DRAFT.md",
      "start_line": 39,
      "end_line": 39,
      "text": "| TL12 | W3 | Refresh after each commit (the `reference-transaction` git hook) | amber | C3: 0.1.7 holds Phase 0 (the kit's hook, written by `gov adapters` and `gov update`, with a retry; the store behind HEAD named; landing record `phase0-memory-20261124`, 24 new tests green), not proven on the scratch repository (TL-4; I-9). | \u2014 | Keep the cron line `30 3 * * * cd <repo> && $HOME/.local/bin/gov rebuild >> .gov-runtime/refresh.log 2>&1` (not tried on a product), run `gov rebuild` after each merge batch, and rebuild when the first line of `gov retrieve` shows a store behind HEAD. The hook does nothing without `integration_refresh` in `governance/project/rebuild.yaml` (its `branch`; `--when-due` also needs `integration_store`, `after_nightly.latest` and `second`), and the 0.1.7 kit ships no such file. | \u2014 | \u2014 |\n",
      "chunk_id": "4a5d046a487473e9ff23cfde",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "8c154695fa536effc1151589",
      "sha256": "08d833f195577d0142e45ae13a0466eab11996d23402b7ed51b066ece0d0cf67",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 36,
      "end_line": 37,
      "text": "| 10 | W3 | the refresh itself: row 11 plus `gov rebuild --integration` (`src/gov/rebuild/integration.py`; `rebuild/command.py:171` `--when-due`) | P | auto via row 11; `--when-due` has no caller | P | HEAD \u2192 refreshed store | not needed | a failed refresh is not retried (`integration-store.log` 13:53:49 `REBUILD_FAILED`, store 23 commits behind); A-10: the minute tick calls `--when-due` (a cron chore, 0.1.5) and `gov status`/`gov brief` name a stale store (code, integration); W2-116 (DAEO-f58b) |\n| 11 | W3, W6 | the reference-transaction git hook (`.git/hooks/reference-transaction`, untracked): store refresh (line 15), `landing_select.sh` (line 16), a dead operator freeze (lines 8-12) | O | auto on each `refs/heads/w2/integrate` update | Y | ref update \u2192 detached rebuild and scoped test run | not needed | lives in `.git/hooks`, in neither the product nor the kit; fires only for `w2/integrate`; silent on failure. `[absorb]`: the product installs it and the freeze lines go (A-10, A-28); fix under W2-116; integration |\n",
      "chunk_id": "8c154695fa536effc1151589",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "75a23213506da2e798e40dee",
      "sha256": "2fb7105dec57acbbf4b6803f5e1962bf85cb9900704488f3b7bc71e2dec5b635",
      "path": "docs/emergency-2/briefs/LEAD-phase0-memory.md",
      "start_line": 11,
      "end_line": 15,
      "text": "- **0-2** under W2-204 (`.tickets/DAEO-ma4q.md`, closed: a fix). `gov memaudit` preflight refuses `STORE_BEHIND`. Do **not** rebuild Gov OS's live store or run a memory measure: the CTO does the rebuild.\n- **0-3** under W2-116 and W2-208 (`.tickets/DAEO-kt8e.md`, closed: a fix). The kit carries the `reference-transaction` hook file; `gov adopt`, `gov adapters` and `gov update` install it; it refreshes the repository's integration branch read from configuration (never fixed to `w2/integrate`), with 0-1's retry, and a failure leaves one inbox message. Read Gov OS's live untracked hook `.git/hooks/reference-transaction` for what it does today; drop its retired operator-freeze lines. In Gov OS the `landing_select.sh` call moves to a local hook file that stays until Day M (the plan's row says how).\n\nCode area (stream S): `src/gov/rebuild*`, `src/gov/status*`, `src/gov/memaudit/` (preflight only), `src/gov/adopt/`, `src/gov/update/` (hook install only), the kit under `template/`. Stay out of `src/gov/dispatch/` and `src/gov/resources/` (the W2-207 lead works there) and `src/gov/launch/`, `src/gov/decisions/` (two other leads).\n\n",
      "chunk_id": "75a23213506da2e798e40dee",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "ad06e4b3e2f1a93f874c21af",
      "sha256": "597cf2fdb5f4e5e16cf32fcd9e2fd7333636bc3bc7df322a010816eee66c724d",
      "path": "docs/releases/0.1.7/TOOL-STATUS.md",
      "start_line": 32,
      "end_line": 33,
      "text": "| TL12 | W3 | Refresh after each commit (the `reference-transaction` git hook) | amber | C3: 0.1.7 holds Phase 0 (the kit's hook, written by `gov adapters` and `gov update`, with a retry; the store behind HEAD named; landing record `phase0-memory-20261124`, 24 new tests green), not proven on the scratch repository (TL-4; I-9). | \u2014 | Keep the cron line `30 3 * * * cd <repo> && $HOME/.local/bin/gov rebuild >> .gov-runtime/refresh.log 2>&1` (not tried on a product), run `gov rebuild` after each merge batch, and rebuild when the first line of `gov retrieve` shows a store behind HEAD. The hook does nothing without `integration_refresh` in `governance/project/rebuild.yaml` (its `branch`; `--when-due` also needs `integration_store`, `after_nightly.latest` and `second`), and the 0.1.7 kit ships no such file. |\n| TL13 | W3 | The embedders started at boot | not yet | In 0.1.7 the product starts no embedder at boot; Gov OS uses an `@reboot` cron line to a scratch script (I-7; TOOL-MAP row 12; plan 3-2, MA-5) (TL-4). | \u2014 | The two embedding servers are the machine's, shared by every repository: one `@reboot` line in the crontab, not one per product. |\n",
      "chunk_id": "ad06e4b3e2f1a93f874c21af",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "766b609e55d0c0824feb1026",
      "sha256": "eaccb01471f7cf7087d97209830eb02552525cf80899bcf9c099b19f7f074774",
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "start_line": 318,
      "end_line": 330,
      "text": "  intro:\"Where schedules and checks run in an adopted repository, and what triggers the impact trace.\",\n  qs:[\n  { id:\"T-5\", from:\"GOLDEN-WORKFLOW-CORRECTIONS SQ-5\",\n    title:\"Where do schedules and git hooks live in an adopted repository?\",\n    found:[\n      \"W3 (retry), W4 (weekly), W16 and rule 4 all need schedules.\",\n      \"Gov OS's are crontab lines you and the CTO keep (the minute tick, the hourly backup, <code>@reboot</code>) and one untracked git hook. The kit installs no crontab and no hook.\",\n      \"An adopted repository such as EXAMIN gets none of them, except through your shared crontab.\"],\n    opts:[\n      [\"a\",\"The product ships one scheduler: gov dispatch pass, run by one cron line, with the schedule in governance/project/ config\",\"Large (W2-207 slice 4).\",1],\n      [\"b\",\"The kit installs git hooks (a reference-transaction hook) and a crontab fragment\",\"Medium.\"],\n      [\"c\",\"Leave it as your per-machine setup, documented\",\"No code. Contradicts rule 3.\"]],\n    reason:\"(a) with the hook install of (b): one cron line and everything else in config; it also absorbs map rows 11, 12, 15, 43 and 81.\",\n",
      "chunk_id": "766b609e55d0c0824feb1026",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "9289ec3aed7973f1adcf59fe",
      "sha256": "44e6db5b385937ff05594bacdf5d8b2b8f264970da6fbb5b9c1e1678ad42872a",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 37,
      "end_line": 38,
      "text": "| 11 | W3, W6 | the reference-transaction git hook (`.git/hooks/reference-transaction`, untracked): store refresh (line 15), `landing_select.sh` (line 16), a dead operator freeze (lines 8-12) | O | auto on each `refs/heads/w2/integrate` update | Y | ref update \u2192 detached rebuild and scoped test run | not needed | lives in `.git/hooks`, in neither the product nor the kit; fires only for `w2/integrate`; silent on failure. `[absorb]`: the product installs it and the freeze lines go (A-10, A-28); fix under W2-116; integration |\n| 12 | W3 | `embedders_at_boot.sh` (`.gov-runtime/scratch/orchestrator/tools/`; crontab `@reboot`, line 9) | O | auto at boot (waits 60 s, 3 tries) | Y (added today; a reboot has not tested it) | boot \u2192 both embedders up (`~/.ollama/boot-start.log`) | not needed | `[absorb]` into the dispatcher's self-healing, W2-207 MA-5 (DAEO-rt4s, \"retires with MA-5\" in its own header); integration |\n",
      "chunk_id": "9289ec3aed7973f1adcf59fe",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "40c55acaa58f8c78c501ebc5",
      "sha256": "b39c0766fac58d9e58aa791dd13b6b172811a5ca14071eb209137a0d27b9a0de",
      "path": "tests/acceptance/W2-208/README.md",
      "start_line": 145,
      "end_line": 155,
      "text": "### P0-3 (plan item 0-3): the kit carries the git hook\n\nTests for the fix `P0-3` of DAEO-kt8e, in `test_w2_208_p0_3_kit_hook.py` (support: `w2_208_p0_support.py`; it borrows\nW2-116's stand-in embedder and project builder). The kit's file is `template/governance/kernel/githooks/reference-transaction`.\nInstallers: the project adopted (`copier copy` then `gov adapters generate`, W2-17's adoption path; `gov adopt --lite`'s\nstages are not driven, since which stage writes the hook is not fixed), `gov adapters generate` on a project whose hook was\ndeleted, and `gov update B` on a project (adopted at A1) whose hook was deleted: `.git/hooks/reference-transaction`\nexecutable and byte-equal to the kit's file; the update record `governance/updates/B.json` holds the string\n`.git/hooks/reference-transaction` anywhere in it. The runtime cases put the kit's file in a built project whose\n`integration_refresh.branch` is `trunk` (and again `main`), with a fake `HOME`. Names chosen here for the engineer to read:\n`gov` is found by `command -v gov` or at `$HOME/.local/bin/gov` (a python shim at both); the hook's log is\n",
      "chunk_id": "40c55acaa58f8c78c501ebc5",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "234d9d663fce2e9ed43fdf22",
      "sha256": "ebfd36624722e7594d3a70fe99549dd7006ab95e1a4930487910a757456cb116",
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "start_line": 99,
      "end_line": 102,
      "text": "### SQ-5. Where do schedules and git hooks live in an adopted repository?\n- **Found:** W3 (retry), W4 (weekly), W16 and rule 4 all need schedules; Gov OS's are crontab lines the owner and CTO keep (live: the minute tick, the hourly backup, `@reboot`) and one untracked git hook; the kit installs no crontab and no hook (`template/` has `lefthook.yml.jinja`, not installed here). An adopted repository such as EXAMIN gets none of Gov OS's schedules except through the owner's shared crontab (the hourly backup covers EXAMIN by an explicit second line).\n- **Options:** (a) the product ships one scheduler: `gov dispatch pass` run by the cron's single line, with the schedule in `governance/project/` config (L, W2-207 slice 4); (b) the kit installs git hooks (`gov` writes `reference-transaction` into `.git/hooks` at adopt and update) and a crontab fragment (M); (c) leave it as the owner's per-machine setup, documented (no code; contradicts rule 3).\n- **Recommendation:** (a) with the hook install of (b): one cron line, everything else in config the product reads; this is also what absorbs rows 11, 12, 15, 43, 81 of the map.\n",
      "chunk_id": "234d9d663fce2e9ed43fdf22",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "4d4bdffd40584bcf6cb52366",
      "sha256": "fdbcdb28d5240c9258b080e1954be1d9501c94b1eb797078ffa16b52e5471d06",
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "start_line": 522,
      "end_line": 535,
      "text": "### F7. `gov doctor` reports the hooks as passing when no git hook is installed, and cannot tell an editable or foreign `gov`\n\n**Evidence.**\n- *The hooks check.* `src/gov/doctor/command.py`:506\u2013515 returns \"pass\" when `lefthook.yml` exists and the lefthook program is found. It never looks at what git will actually run.\n- *My doctor run* (run 5): `\"hooks\": {\"status\": \"pass\", \"config_present\": true, \"binary_installed\": true}`, while no hook is installed (F6).\n- *The `gov` entry:* `ok: true`, with `found_version` empty and no location. Nothing says that `gov` is an editable install, or which tree it imports.\n- *The planned check is for product repositories only.* W2-18's measure is \"`gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock`\" (WBS:439).\n- *Gates rely on doctor:*\n  - W2-22 is \"`gov doctor` green\" (WBS:116);\n  - exit criterion 3 is \"`gov doctor` is green (exit 0) on this repository and on EXAMIN\" (WBS:957);\n  - W2-24 needs \"`gov doctor` and `gov check` are green there\" (WBS:658).\n\n  With today's hooks check, doctor could be green here with no git hook at all.\n\n",
      "chunk_id": "4d4bdffd40584bcf6cb52366",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "4c02646746b554aeb6cb5699",
      "sha256": "d4cd5d8c0857fb404e2d3ff7793de480d3e54f857383ffd956a7873f4321863c",
      "path": "docs/releases/0.1.7/TOOL-STATUS.md",
      "start_line": 31,
      "end_line": 32,
      "text": "| TL11 | W2 | `gov memory-use` | amber | A typed log; helpers log no role (A-35; TOOL-MAP row 9). | \u2014 | Nothing depends on it; count memory use from the findings if the owner asks. |\n| TL12 | W3 | Refresh after each commit (the `reference-transaction` git hook) | amber | C3: 0.1.7 holds Phase 0 (the kit's hook, written by `gov adapters` and `gov update`, with a retry; the store behind HEAD named; landing record `phase0-memory-20261124`, 24 new tests green), not proven on the scratch repository (TL-4; I-9). | \u2014 | Keep the cron line `30 3 * * * cd <repo> && $HOME/.local/bin/gov rebuild >> .gov-runtime/refresh.log 2>&1` (not tried on a product), run `gov rebuild` after each merge batch, and rebuild when the first line of `gov retrieve` shows a store behind HEAD. The hook does nothing without `integration_refresh` in `governance/project/rebuild.yaml` (its `branch`; `--when-due` also needs `integration_store`, `after_nightly.latest` and `second`), and the 0.1.7 kit ships no such file. |\n",
      "chunk_id": "4c02646746b554aeb6cb5699",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "69225e84725cebdeaf8fdb13",
      "sha256": "639d31862a90a6b12bd13a7ff734dd0ec68ab65329dfd18f43d7643c73af5c39",
      "path": "docs/releases/0.1.6/manifest.json",
      "start_line": 82,
      "end_line": 91,
      "text": "    \"- DAEO-ma4q: KPI lines FM-1 to FM-4 for the fresh 80's writer loop (I-23 with EF-9, I-18, I-19)\",\n    \"- The memaudit fix lead's brief (I-23 with EXAMIN's EF-9, I-18, I-19; FM-1 to FM-4)\",\n    \"- Merge e2/fix-w2-209-s3: I-21 fixed, W2-209 S3 checks the authority file as the owner set it (on, DEC-1223, bake 4 h, committed with Decided-by: owner)\",\n    \"- The usage-per-repository lead's brief (DEC-1246 (3)(c), plan item 3-10: UR-1 to UR-4)\",\n    \"- Merge w2/integrate into e2/phase0-memory\",\n    \"- test-map: the kit's git hook file maps to its installers' and its own suites\",\n    \"- P0-3: the kit carries the git hook; adapters generate and update install it\",\n    \"- I-23 logged (memaudit's round-2 writer never sees the pre-flight-1 refusals; EXAMIN's EF-8); the CTO's ruling on re-rolling writer round 1 recorded beside it\",\n    \"- W2-209 S3: the repository-state test states the authority file as the owner decided it now (on, DEC-1223, bake_hours 4, committed, last commit Decided-by: owner)\",\n    \"- I-21 (W2-209 S3 red on the base since the authority file went on; a selection miss) and I-22 (W1-35's conftest shadowed in a one-process run) logged\",\n",
      "chunk_id": "69225e84725cebdeaf8fdb13",
      "routes": [
        "semantic"
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
    "duplicates": 15,
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
      "chunk_id": "b62919e3e91dd56e83d837f4",
      "parent_id": "443e7f07a0e7650d123d77c1",
      "path": "src/gov/queue/checks.py",
      "start_line": 54,
      "end_line": 73
    },
    {
      "chunk_id": "a2ae0930edfc0592cfa9afe9",
      "parent_id": "0ba027efb6a348b735360cc2",
      "path": "src/gov/adapters/merge.py",
      "start_line": 197,
      "end_line": 230
    },
    {
      "chunk_id": "2389a07214e3705f5992e785",
      "parent_id": "1b6dafc522d69646f492cbc9",
      "path": ".tickets/DAEO-kt8e.md",
      "start_line": 110,
      "end_line": 131
    },
    {
      "chunk_id": "f1f7fd56d3a4ddcdf76c69c5",
      "parent_id": "cc9b8360d19159a490c7d236",
      "path": "template/governance/kernel/githooks/reference-transaction",
      "start_line": 1,
      "end_line": 76
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "997ca87b1460bb676126a6aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-116-evidence.md",
      "chunk_id": "68694e0faf2a9a575c4cd982",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "6d3ccc7b462d6c97542796ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "8ccf40ea09bb2d1bf354bb74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/06-examin.md",
      "chunk_id": "004ac690c186ac2f586c5eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0z8c.md",
      "chunk_id": "0757983126df111da6aa6413",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7r5e.md",
      "chunk_id": "5f99cc13b446b4cf91683f24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "11cb122f0679c21407eb86d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/07-contract-rebaseline.md",
      "chunk_id": "4a5ce147a9069945185411cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "f21d6e5f6d6e61bb459ab858",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "ee411af1ee807099c24235c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "277a021545ebf84094dc51ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "c90418dbe3442582bec891a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "fe055b1b394bb20331369f59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-0.1.4.md",
      "chunk_id": "34a32f35328c42d06d37b346",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "7b0864a484bd65a5e8dd64df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-b.md",
      "chunk_id": "a9f5075b5bbdfefe4f67be7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/briefs/a-im02-tests.md",
      "chunk_id": "76bdcb3d4d70eb7b47a17652",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "fbe667f62d8a7e931052a559",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "72c2a482354cea8c7f9e4a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "782b947b64a7438dcfd36d3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "3ec5706cfba235aa0e658bd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/README.md",
      "chunk_id": "d722410fe0b2dfb277510fc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "aba586efc7b74b371bda5500",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/test_w2_208_p0_3_kit_hook.py",
      "chunk_id": "a1f15b149f554323bf3dd96f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "204b93061ecee222c5408a85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7r5e.md",
      "chunk_id": "2bc36c49a7604ae0972bbcd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-f58b.md",
      "chunk_id": "2f338ff0592e8950444197ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7r5e.md",
      "chunk_id": "1f8272c44962a548e6ff494a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.8/TOOL-STATUS-DRAFT.md",
      "chunk_id": "e19776933ab963e79033709b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.7/TOOL-STATUS.md",
      "chunk_id": "6c8969b7b0aaba53f094af44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/README.md",
      "chunk_id": "2dbe6c6e32aa35e271739046",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0z8c.md",
      "chunk_id": "30e2461244e19454ca529808",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.8/TOOL-STATUS-DRAFT.md",
      "chunk_id": "02eb32ebccd6e2b6057300c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.7/TOOL-STATUS.md",
      "chunk_id": "f8b04fcbf3240e83312d34c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-phase0-reds.md",
      "chunk_id": "b94fb953c4f403213cbf4e0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "chunk_id": "59bf78483e62019261e27199",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0c839e05f83bdbf081961f10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "546472cfba001ebdb5dbf92b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "2d7651d2ad13028b79135a1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/test-map.yaml",
      "chunk_id": "d2c8cc3d05823e23adb9e174",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "d63a0be72711ed7ffaa65a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "5a86009433866934acf7aafe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "4a076a947c179d0ab10e452d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-rerun.md",
      "chunk_id": "a74b7443d7069155935f780e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "d30c8db5539602addd90152f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.8/TOOL-STATUS-DRAFT.md",
      "chunk_id": "00b3b466384f73b85110177f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adapters/test_p0_3_install_hook.py",
      "chunk_id": "d8ba3598dd408c97a66c64d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-rerun.md",
      "chunk_id": "41782ac877b6dc0689ce20e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "65c0b329f8ecdf0e3ce48b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "3dcfd4f28ac6d920d235c851",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/B2.md",
      "chunk_id": "450ba25c76fad05da0c8ee7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.7/TOOL-STATUS.md",
      "chunk_id": "0bb6cc18f90b60003552189c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "8d1232f43b5255a275a0bb5c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adapters/test_p0_3_install_hook.py",
      "chunk_id": "f01a8dc2b190515c55798a08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "07a59df5e00ab8bde96e9bc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "77dad34ce6792d9ee0b7b6f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "e0b98c39438c2d80088babf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b7c9ad859f3ff3f0afe2304c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "b31c24f95ac779bc334510f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/w2_208_p0_support.py",
      "chunk_id": "693b795c74d63222b153e1c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "f89946c5d1d9034b4f361762",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-f58b.md",
      "chunk_id": "2cf686029929b28e84de58f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "a7b70f70efb8a59e0958c326",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "d232f1287ecbe228d8a6ca0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "4e36798cfa2caf8693170906",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "53d7a59f69ae4cba83e70765",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7r5e.md",
      "chunk_id": "30745b9c86c052ef4b27317c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "ce70b5f03645c48bf132ca7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qyt2.md",
      "chunk_id": "7ac12c2f00a523e269a7873f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "e6bc800dd06a5fdb1e943be1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html",
      "chunk_id": "e7f2e945c56097dc223ead0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "4156e3419fcc7a1eb1abcd9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "6c50bcf7b8e319cbf3c73723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "42b9e23dc08acde2a55a07bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "91ef0c942eebf3a5d85a32e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-31.md",
      "chunk_id": "823b419bee3b21bfa85765bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b7da75d422fa0cd258206c8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "4655eaf1721ad48f2b8f0541",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "7d172f182c22517ca7981749",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "d165c06d890a582e394750f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "79a3b3630be3d83065db679a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "5d3948ac79f5c5157250d4ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/README.md",
      "chunk_id": "508aa3a632631dbfc9f236da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "a06d0574dd3bb0341ba39093",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "d152b758e5cf4988fbaec449",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g29a.md",
      "chunk_id": "77a553a54ce9c099a095e16d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "033ed52068df32353f3e7c73",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adapters/test_p0_3_install_hook.py",
      "chunk_id": "ae65c4c9c69d015ec9fc2308",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "fd6e05b2ce3f7fe6fd689b89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "cd80b0f2720a2ad246b12384",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-head.md",
      "chunk_id": "7ef7065015b76c1d37fc4266",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/facts.py",
      "chunk_id": "3d521519ea69dbca12b45fd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "cf6eba057f24a61f3fc1f496",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "4c12e78182f86564a94df5b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adapters/test_p0_3_install_hook.py",
      "chunk_id": "1d2bde2ee21ed17741707764",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/w2_208_p0_support.py",
      "chunk_id": "b7eda75f47b0c864400effaf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-208/README.md",
      "chunk_id": "f096073919bd55428f77f16d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "c26051e96c7e55dcacff72b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "4892c21e003c6b9e20e8dca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "chunk_id": "a5fd1449134632f39f5552c0",
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
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5980
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWt0OGUubWQiLDExMCwxMjEsImI3Y2QzODEyNzE5MjIxMmIwMWQxMTgxOSJdLFsiZG9jcy9hc3Nlc3NtZW50LzIwMjYtMTAvRC10b29sLXN0YWdpbmcubWQiLDUyMiw1MzUsIjRkNGJkZmZkNDA1ODRiY2Y2Y2I1MjM2NiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1waGFzZTAtbWVtb3J5Lm1kIiwxMSwxNSwiNzVhMjMyMTM1MDZkYTJlNzk4ZTQwZGVlIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0RFQ0lTSU9OUy1QQUdFLTIwMjYtMTEtMjIuaHRtbCIsMzE4LDMzMCwiNzY2YjYwOWU1NWQwYzA4MjRmZWIxMDI2Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0dPTERFTi1XT1JLRkxPVy1DT1JSRUNUSU9OUy5tZCIsOTksMTAyLCIyMzRkOWQ2NjNmY2UyZTllZDQzZmRmMjIiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vSU5URUdSQVRJT04tUExBTi5tZCIsNTEsNTEsIjU4MmNhMGVhMzU4MTU4NjA2N2UxZmQzNyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9UT09MLU1BUC5tZCIsMzYsMzcsIjhjMTU0Njk1ZmE1MzZlZmZjMTE1MTU4OSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9UT09MLU1BUC5tZCIsMzcsMzgsIjkyODllYzNhZWQ3OTczZjFhZGNmNTlmZSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9yZWxlYXNlLTAuMS44L1RPT0wtU1RBVFVTLURSQUZULm1kIiwzOSwzOSwiNGE1ZDA0NmE0ODc0NzNlOWZmMjNjZmRlIl0sWyJkb2NzL3JlbGVhc2VzLzAuMS42L21hbmlmZXN0Lmpzb24iLDgyLDkxLCI2OTIyNWU4NDcyNWNlYmRlYWY4ZmRiMTMiXSxbImRvY3MvcmVsZWFzZXMvMC4xLjcvVE9PTC1TVEFUVVMubWQiLDMxLDMyLCI0YzAyNjQ2NzQ2YjU1NGFlYjZjYjU2OTkiXSxbImRvY3MvcmVsZWFzZXMvMC4xLjcvVE9PTC1TVEFUVVMubWQiLDMyLDMzLCJhZDA2ZTRiM2UyZjFhOTNmODc0YzIxYWYiXSxbInNyYy9nb3YvYWRhcHRlcnMvbWVyZ2UucHkiLDE5MSwxOTYsIjIxYjNmN2RhYjRiZTJiMGYyYWY0OGM4MiJdLFsic3JjL2dvdi91cGRhdGUvY29yZS5weSIsNjI0LDYyNywiZjYxODViNTRjYTExYzk1MGZkN2VmZjFhIl0sWyJ0ZW1wbGF0ZS9nb3Zlcm5hbmNlL2tlcm5lbC9naXRob29rcy9yZWZlcmVuY2UtdHJhbnNhY3Rpb24iLDE3LDQ5LCI1YzQ2MmVlMDM2OTBkMGU3ZTViYjM1NDgiXSxbInRlc3RzL2FjY2VwdGFuY2UvVzItMjA4L1JFQURNRS5tZCIsMTQ1LDE1NSwiNDBjNTVhY2FhNThmOGM3OGM1MDFlYmM1Il1dLCJmIjoiL2hvbWUvdXNhaW4vZ292LW9zLXdvcmt0cmVlcy9XMi0wMC1zdG9yZS1iIiwiaSI6W10sIm8iOjIwLCJwIjp7ImIiOiJzZXJ2aWNlIiwiZCI6ImN1ZGE6MCIsImgiOiI4ZWY2NWExNThjMTA1MjkwIiwibyI6WzMsMTEsMSw0LDM1LDUsMiwwLDksMjksMTksMzcsMTAsMTIsMzEsMzksMjIsMTQsMTMsMjMsMTgsNywyNSw2LDIwLDE2LDIxLDgsMjYsMjcsMzAsMzQsMjgsMjQsMzMsMzYsMzIsMzgsMTUsMTddfSwicSI6ImdpdCBob29rcyBpbnN0YWxsZWQgYnkgdGhlIHByb2R1Y3Q6IHJlZmVyZW5jZS10cmFuc2FjdGlvbiBob29rIGluIHRoZSBraXQsIGluc3RhbGxlZCBieSBnb3YgYWRvcHQgYWRhcHRlcnMgdXBkYXRlIChwbGFuIDAtMyksIHRlc3QgYXV0aG9yc2hpcCBjaGVjayB0ZXN0X2F1dGhvcnMgcmVtZXJnZS1kaWZmLCBURVNUX1JPTEVTLCBjb21taXQtbXNnIGhvb2siLCJyIjowLCJzIjoiY2JiMzIyNjY4MDE3ZWQzYWI3ZGExMTFmYzBjZDhlMjEwNmI2MDkwNSIsInQiOm51bGwsIngiOlsiMGJhMDI3ZWZiNmEzNDhiNzM1MzYwY2MyIiwiMWI2ZGFmYzUyMmQ2OTY0NmY0OTJjYmM5IiwiNDQzZTdmMDdhMGU3NjUwZDEyM2Q3N2MxIiwiY2M5YjgzNjBkMTkxNTlhNDkwYzdkMjM2Il19",
  "routing": {
    "code": [
      "b62919e3e91dd56e83d837f4"
    ],
    "named": [],
    "phrasings": [
      "git hooks installed by the product: reference-transaction hook in the kit, installed by gov adopt adapters update (plan 0-3), test authorship check test_authors remerge-diff, TEST_ROLES, commit-msg hook",
      "git hooks installed product reference-transaction hook kit installed gov adopt adapters update plan 0-3 test authorship check test_authors remerge-diff TEST_ROLES commit-msg hook"
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
        "chunk_id": "b7cd38127192212b01d11819",
        "path": ".tickets/DAEO-kt8e.md",
        "start_line": 110,
        "end_line": 121
      },
      {
        "chunk_id": "5c462ee03690d0e7e5bb3548",
        "path": "template/governance/kernel/githooks/reference-transaction",
        "start_line": 17,
        "end_line": 49
      }
    ]
  }
}
