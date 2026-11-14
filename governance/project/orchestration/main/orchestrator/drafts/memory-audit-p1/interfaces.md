# Interfaces at claim: W2-187 (DAEO-0cd2) and W2-188 (DAEO-zlog)

Drafted 2026-11-14 by a read-only helper of the CTO (DAEO-sdxk). Each section below is pasted as it stands at the end of
its ticket when the CTO claims it. Read: both tickets, MEMORY-AUDIT-P1 §2 and §5, DEC-1179 as recorded, `src/gov/memaudit/`,
`src/gov/adopt/memory_sets.py` (and its caller `src/gov/adopt/fabric.py:716-723`), `gov.retrieval.measure`'s
re-anchoring, the walls' README and `kinds.yaml`, `indep_launch.py`'s AUDITS.log, SEEDS.log and counts.json lines, the
W2-170, W2-171, W2-172 and W2-88a acceptance helpers, the adopt skill, the practice record and the W2-188 CIT-P draft. No
sets root, hidden folder or memory-verdict folder was opened. `~/gov-os-runs/indep/` holds no `memaudit/` and no
`AUDITS.log` today (listed only), so moving the state needs no migration.

---

## Interface (the CTO at claim, DEC-1179 (8), DEC-1157 (3) and (12); listed for the owner's reading)

- **I1, the command line (`src/gov/memaudit/__main__.py`; S1, S2, S8, S9, S10, F2, F3).** The exit map stays as it is
  (`gov.memaudit.EXIT`: 0 ok, 1 refused, 2 stopped, 3 used, 4 usage), `say` stays the only printer, and every subcommand
  keeps `--sets-root` (required, as today). The new and changed subcommands:
  - `standing declare --sets-root R --set <name> [--repo D] [--runs-dir DIR] [--replaces <old>]` (I3);
  - `standing run --sets-root R [--repo D] [--store-link P] [--gov EXE] [--claude EXE] [--gate-cmd CMD]` (I4). It has no
    `--decision`, no `--force` and no data flag, so any of them is argparse's exit 4 (F3);
  - `standing live --sets-root R [--repo D]`: prints `KEY <key>`, then `LIVE <set>` (exit 0) or `LIVE none` (exit 1). It
    writes nothing;
  - `maintain --sets-root R [--repo D] [--store-link P] [--gov EXE]` (I10);
  - `due --fresh` (I8); `status --repair [--residual DEC-<n>]`, with `--since` required only without `--repair` (I8);
  - `pool-import --sets <name>...` (I9);
  - `preflight`, `declare`, `measure`, `judge` and `figures` take `--week <YYYY>-W<ww>`. With it, the step works on the
    standing set's week folder (I2). `--audit` then names the standing set. Without `--week`, every byte of the fresh path
    is as today.
  - Name forms (`layout.py`): `SET_RE = memory-(audit|standing)-[0-9]{8}` (a Wave 0 verdict set keeps its
    `memory-audit-<date>` name; a new standing set is `memory-standing-<date>`) and `WEEK_RE = [0-9]{4}-W[0-9]{2}`, the
    ISO year and week of `schedule.now()` in UTC (the `GOV_MEMAUDIT_NOW` seam).

- **I2, where things live (`layout.py`, `schedule.py`; S2, S4, S9).**
  - `layout.paths(sets_root, name, week=None)` gives today's dict. With `week`, its `run` is
    `<sets root>/runs/<set>/<week>/` (mode 0700, `make_run`), and `preflight`, `declaration`, `used` and `ledger` lie in
    it. `set`, `hidden` and `map` are as today. "Its run folder" in S4 and F1 is `<sets root>/runs/<set>/` and everything
    under it.
  - `schedule.state_dir(runs, repo) -> Path` is `<runs>/indep/memaudit/<key>/`. `<key>` is
    `os.path.basename(real) + "-" + sha256(real.encode()).hexdigest()[:8]`, where `real = os.path.realpath(repo)`.
    `schedule.folder(runs)` is replaced by it everywhere (driver, due, status, baseline, maintain). The folder holds:
    - `HISTORY.jsonl`, `STARTS.log`, `LOCK` and `cron.log`;
    - `STANDING.jsonl` (I3) and `MAINTAIN.jsonl` (I10);
    - `<audit>/` (a fresh run's `COUNTS.json` and `DIGEST.txt`, as today) and `standing/<set>/<week>/` (the same two files
      for a standing run).
  - The driver passes `GOV_INDEP_RUNS_DIR=<key folder>` to every child it starts (it passes `<runs>` today). The launch
    script's `AUDITS.log`, `SEEDS.log` and `<kind>/<run>/counts.json` therefore land in `<key folder>/indep/`.
    `schedule.last_audit_commit`, `driver._refusal`'s `RN-NOBASE`, `baseline` and `preflight` (through its
    `$GOV_INDEP_RUNS_DIR` default) read them there. The launch script is unchanged.
  - Nothing of a standing set's questions is written under `<runs>`. `STANDING.jsonl` holds the set's name, digests,
    counts and commits only.

- **I3, `standing declare` (new module `src/gov/memaudit/standing.py`: the record, the spent check, the week rule, drift
  and repair; it calls the existing modules and copies none; S1, F1).**
  - **The call:** `standing.declare(sets_root, name, *, repo, runs_dir, replaces=None) -> (word, counts)`.
  - **The refusals, checked in this order, with nothing written:**
    - `STANDING_SPENT <k>` (exit 1): some `question` of the set's `hidden/*.yaml` equals the `question` of a line in
      any `<sets root>/runs/**/misses.jsonl`; or `<sets root>/runs/<set>/**/miss-classes.json` exists; or an
      `AUDITS.log` line (in `<key folder>/indep/` and in `<runs-dir>/indep/`) has `audit == <name>`. `<k>` is the count
      of matched questions, never an id.
    - The set's own `runs/<set>/USED` exists: the set is accepted only as the repository's Wave 0 verdict set.
      `runs/<set>/DECLARATION.json` and `runs/<set>/FIGURES.json` (its counts-only result record) must exist, and the
      declaration's `audit_commit` must equal the commit of the first line of the repository's `AUDITS.log` (the
      baseline W2-88 S21 writes at the verdict commit). Otherwise `STANDING_SPENT 0`. The spent check skips only that
      Wave 0 run's own `runs/<set>/misses.jsonl` and `miss-classes.json` (see the unresolved item U1).
    - `STANDING_LIVE <live set>`: `STANDING.jsonl` holds a live set. `--replaces <old>` lifts this only when `<old>` is
      the live set and its last weekly HISTORY line carries `STANDING_THIN` (O5 (a)). `<old>` is then retired with
      reason `thin` in the same write.
    - `STANDING_BRIEFS`: no delivered writer and checker `counts.json` (`status == "delivered"`, `set == <name>`) is
      found under `<runs-dir>/indep/{writer,checker}/*/` or `<key folder>/indep/{writer,checker}/*/`. `--runs-dir`
      defaults as `preflight` defaults: `$GOV_INDEP_RUNS_DIR`, else `~/gov-os-runs`.
    - `STANDING_FORM`: a file fails `preflight.form_ok`, or `hidden/` holds fewer than 36 files.
  - **The write:** one `STANDING.jsonl` line:
    `{"event": "declared", "set", "set_digest" (common.set_digest(hidden)), "n", "n_apart", "writer_brief_sha256",
    "checker_brief_sha256", "written_commit" (the writer counts' commit), "wave0": bool, "at"}`.
  - **The output:** `STANDING DECLARED <set>: n <n> apart <k> digest <12 hex> written at <12 hex>`, exit 0.

- **I4, `standing run` (`driver.standing(...)` beside `driver.run`, reusing `_Cycle`, `_refusal`'s RN-LOCK, RN-REBUILD,
  RN-SIDE and RN-STALE, `_history` and `_finish`; S2, S3, S4, S6, F2, F3, F4).**
  - **Its children,** in order, each `python3 -m gov.memaudit <step> --sets-root R --audit <set> --week <week> ...`:
    `preflight` (I6), `measure`, `judge`, `figures`. The gate is asked before `measure` and `judge`, as today (`GATED`).
  - **No `classes`, auditor launch, `pool` or writer launch:** `classes` and `pool` refuse a standing set name
    (`MS-STANDING`, exit 1), and so does `pool-import` (F1).
  - **The week rule** (`standing.week_state(paths)`; S2) is checked before anything is written:
    - The week folder is absent, or present without `USED`: the run goes on (the folder is re-used).
    - `USED` present with `reader/` or `FIGURES.json`, or `USED` present with no `STOPPED`: `USED`, exit 3, nothing
      written (no STARTS line, no digest).
    - `STOPPED` present with no `reader/`, and `<week>.stopped/` absent: the week folder is renamed to `<week>.stopped/`
      and the run starts once more.
    - `STOPPED` present and `<week>.stopped/` present: `USED`, exit 3.
  - **Before any search,** the refusals are `STANDING_NONE`, `STANDING_RETIRED` and `STANDING_DIGEST`. The last is
    `common.set_digest(hidden)` not equal to the record's `set_digest`; then nothing is written and the week is not spent
    (F2).
  - **The one judged path:**
    - `declare.declare(..., week=)` writes `DECLARATION.json`, its ledger line, then `USED`, as today. In standing mode
      `n` is the live count from the week's `PREFLIGHT.json`; `n_set` and `dropped` are recorded beside it.
      `DC-DROPS` is not asked.
    - A nonstandard `retrieval.yaml` is `DC-DECISION` with no way to allow it (F3).
    - `measure.run(..., week=)` measures the whole `hidden` part (wholeness against `n_set`) and scores the live ids.
    - `judge.run(..., week=)` asks only the live questions, by `_Judge.one`, `prompts` and `matcher` unchanged (S3's
      spy).
    - `figures.build` runs as today. In standing mode `figures.write_misses` is not called, and judge's `SEARCH FAILED`
      line prints its count with no ids (S4).
  - **The store commit (S3; W2-138's field `result.store.commit`):** `fault.not_whole(folder, n, families,
    store_commit=None)`. In standing mode it gives the cause `store_commit` when any kept result's `result.store.commit`
    is absent or not the declaration's `store_commit`; that attempt is then a fault under the existing rule (one restart,
    then `STOPPED fault`). A later search in `judge.search` from another commit is a counted search failure with an empty
    bundle (`why` `store`).
  - **After `figures`,** one HISTORY line:
    `{"kind": "standing", "set", "week", "audit": <set>, "commit", "at", "mode", "churn", "retrieval_28d", "passes",
    "pool_regression" (the last fresh line's), "measured": true, "used": true, "n", "right", "wrong", "not_found",
    "dropped", "pct" (100 right / n), "word": "pass"|"miss", "gov_pin", "retrieval_yaml_sha256", "path_map_sha256"}`.
    Then the states of I7 and I8, and the digest (I12).
  - **The last stdout line** is `STANDING <week> right <r> of <n>: passes|misses`.
  - **Exit:** 0 when the run ran (a miss is data, not a failure), 1 refused, 2 stopped, 3 week spent, 4 usage.

- **I5, the bar (`declare.bar`, `declare.ROUNDING`; S5).**
  - `bar(n) = {"need_right": -(-95 * n // 100), "max_wrong": 5 * n // 100, "target_right": -(-95 * n // 100)}`, which
    gives 38, 76 and 76 for n = 40, 79 and 80.
  - `figures.build`'s `passes` stays `right >= need_right and wrong <= max_wrong`; the second half is implied
    (n - ceil(0.95 n) = floor(0.05 n)).
  - `ROUNDING = "need_right = ceil(95 n / 100); max_wrong = floor(5 n / 100); target_right = need_right; integer
    arithmetic; standing and fresh runs alike (DEC-1179 (2))"`.
  - The digest's VERDICT line and `verdict_lines` print it unchanged. The revised W2-170 helper `bar` returns this dict,
    key for key, so W2-88's S15 case passes unedited.

- **I6, the standing pre-flight (`preflight.standing(sets_root, name, *, week, commit, repo) -> (word, counts)`; S6,
  F2).**
  - **Each question is loaded alone** through `matcher.questions(sets_root, set, "hidden", root, only=<stem>)`, a new
    one-file form. `root` is the store link's worktree at the audit commit. A load fault drops that one question, never
    the set.
  - **A question is dropped** when some entry of its `sources` has every alternative unresolved (`q["unresolved"]` names
    `entry n`, or `entry n.m` for every `m`), or when it is a nonexistent-id question and `preflight.id_exists` finds its
    id.
  - **The write:** `PREFLIGHT.json` in the week folder:
    `{"mode": "standing", "ok", "n_set", "n", "dropped", "dropped_ids", "n_apart", "set_digest", "files_sha256"}`. Ids
    stay in the run folder. `declare.preflighted` reads the same `files_sha256`.
  - **The output** is the single line `PRE-FLIGHT standing: n <n> of <n_set>; dropped <k>`, with no id. `ok` is false
    only for `STANDING_DIGEST`. Nothing in the set is edited or moved, so `void` is never called.
  - **Fewer than 70 live questions** puts `STANDING_THIN <live>` in the HISTORY line's `word` list and in the digest
    (O5 (a)).

- **I7, the check against fitting at each fresh run (`standing.drift(state, fresh_fig) -> dict`, called in `driver.run`
  after `figures`; S7).**
  - **The figures:** F is `100 * right / n` of the fresh run; S is the mean `pct` of the live set's last four standing
    measured lines.
  - **Fewer than four lines** gives `drift: not yet (k of 4)`.
  - **S - F >= 5:**
    - a HISTORY line `{"kind": "drift", "word": "STANDING_FITTED", "S", "F", "set"}`;
    - a `STANDING.jsonl` line `{"event": "retired", "reason": "fitted"}`;
    - a later `standing run` on that set is `STANDING_RETIRED`, exit 1.
  - **F - S >= 5:** the word is `STANDING_STALE`; nothing is retired.
  - **The retired set as a diagnostic set (counts only):** `pool.run` re-measures each retired set in place, retrieval
    only, into `<sets root>/runs/<set>/diagnostic-<audit>/`. It prints `POOL DIAGNOSTIC <set> hit5 <k> of <n>; full <k>`
    and never copies its files into `memory-pool/` (S4).
  - **With no live standing set,** `driver.run` writes its lines without `kind`, exactly as today.

- **I8, the two cadences, the miss and the repair (`schedule.py`, `standing.py`; S8).**
  - **The standing cadence:** `due` (its three lines and exit codes unchanged) is `schedule.decide(repo, state, head, at,
    lines)`, unchanged, over the live set's own standing lines. With no live set it reads the lines with no `kind`, which
    is W2-172's unedited S5 case. STARTS.log lines gain `"kind": "standing"|"fresh"` once a set is live.
  - **The fresh cadence:** `due --fresh` prints `MODE fresh`, `DUE yes|no next <yyyy-mm-dd>` and
    `REASON first|28d|miss|wait`.
    - `first`: no fresh start.
    - `miss`: the live set's last standing measured line has `passes: false` and no fresh start in the current ISO week.
    - `28d`: today is on or after the first Monday on or after (last fresh start's date + 28 days).
    - With no live set it answers as `due`.
  - **A miss** is the standing HISTORY line with `"word": "miss"`. The P1 digest line is in I12.
  - **The repair:** after each standing measured line, a HISTORY line
    `{"kind": "repair", "word": "MEMORY_REPAIR open", "set", "week"}` is written when none is open and either:
    - this line and the previous standing line are both misses; or
    - this line is a miss and the last passing `pct` minus this `pct` is 5 or more.

    A later pass writes `MEMORY_REPAIR closed`.
  - **`status --repair`:** prints `REPAIR open since <week>` (exit 1) or `REPAIR none` (exit 0). With
    `--residual DEC-<n>` it appends `{"kind": "repair", "word": "MEMORY_REPAIR residual", "decision": "DEC-<n>"}`,
    prints `REPAIR residual DEC-<n>` and exits 0. A malformed id is exit 4.

- **I9, a retrieval change per repository, and `pool-import --sets` (`schedule.retrieval_changed`, `pool.importing`;
  S9).**
  - `retrieval_changed(repo, since, until, gov=None)` keeps today's diff over the six globs for every repository. In an
    adopted repository the four code globs match nothing it tracks, so only `retrieval.yaml` and the path map count there.
  - It adds `gov-pin` when `declare.gov_pin(gov or ~/.local/bin/gov)` differs from the last HISTORY line's `gov_pin`. A
    line without the field (W2-172's planted lines) is no trigger.
  - `pool-import --sets a b` imports exactly those sets' `hidden` parts (and `visible` where present) from that sets
    root, leaving out nonexistent-id questions as today. It has no 79/138 count check. Each set is imported once
    (`runs/memory-pool/IMPORTED-<set>.json`; `MS-IMPORTED` names it again). A standing set name is `MS-STANDING`. With
    no `--sets`, the import is today's, byte for byte.

- **I10, `maintain` (new module `src/gov/memaudit/maintain.py`; S10, F6).**
  - **Its six items,** each bounded by a timeout (`GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S`, default 1800 for a build, 300
    otherwise):
    1. **The store:** `schedule.head_of(store_link)` against `git rev-parse <mainline>`. When behind, one
       `<gov> rebuild --integration <mainline branch>`. A failure keeps the store in service and is named:
       `kept <12 hex> (refresh exit <c>)`.
    2. **The layout:** `gov.store.layout.found_of` on `<link>/.gov-runtime/store.db`, read-only. When not None, one
       rebuild by the same command, else named `stale kept`.
    3. **The links:** `<gov> links --since <the last MAINTAIN line's commit> --json` in the repository; the count of new
       findings. On a first pass it runs from the mark with no `--since`; a refusal is `none`.
    4. **Unindexed paths:** tracked paths of the link worktree that `gov.retrieval.lexical.kept_out` does not keep out,
       less the distinct `path` values of `lexical_chunk` in its store; the count.
    5. **Not found and second searches:** from the latest standing week folder's and the latest fresh run's
       `reader/*.json`, the rows with `final_verdict == "not_found"` and the rows with a non-empty `searches`; two
       counts.
    6. **The changed cited lines:** for every set the sets root's path map declares, except standing sets (live or
       retired), `matcher.questions(sets_root, set, part, link)`'s `unresolved` entries. This is W2-61h S4's list:
       re-anchoring runs in memory, so a block moved unchanged is not listed. One request per set with at least one
       entry goes to `<sets root>/runs/<set>/REANCHOR-<week>.json` (mode 0600, written whole; the folder made 0700 by
       `layout.make_run`):

       `{"week", "audit_commit", "set", "changed": [{"id", "entry"}], "count"}`

       It holds no question, answer or path. This mirrors the auditor's walled input, which the launch script takes from
       `runs/<audit>/` (kinds.yaml `auditor.input: [set, misses]`). Count: the total.
  - **The write:** one `MAINTAIN.jsonl` line in the key folder: the week, the commit, the six items, and the sha256 of
    `retrieval.yaml` and of the path map before and after (equal, F6).
  - **The output:** one line,
    `MAINTAIN 1 store <word> 2 layout <word> 3 links <k> 4 unindexed <k> 5 not_found <a> second <b> 6 reanchor <k>`.
  - **Exit 0 always,** except 4 for usage. The module imports no crontab writer, applies no ACT and never writes
    `retrieval.yaml` or the path map.

- **I11, the schedule's code (`memaudit_cron.sh`, `memory_sets.walls_act`; S11).**
  - **The wrapper:**
    - It takes `--repo <dir>` (default: the cwd's top level), runs `cd` into it, and keeps its variables
      (`GOV_MEMAUDIT_PYTHON`, `GOV_MEMAUDIT_SETS_ROOT`, `GOV_INDEP_RUNS_DIR`, `GOV_MEMAUDIT_GATE`).
    - It first calls `standing live --repo`. Exit 0 gives the live path: `due` and `due --fresh`; then `maintain` when
      either is due; `standing run --gate-cmd` when `due`; `maintain` once more when that run's last line ends `misses`
      (S8 R4); and `run --gate-cmd` when `due --fresh`, in that order.
    - Any other exit gives today's path, byte for byte (`due`, then `run`). That keeps W2-172 S9's shim cases green:
      the shim passes `standing live` to the real interpreter, which answers `LIVE none`.
    - `cron.log` is `<key folder>/cron.log` (the `KEY` line), else `$RUNS/indep/memaudit/cron.log`. Its line's six keys
      are unchanged. The exit is the last started step's.
  - **The ACT text:** `walls_act(out, *, sets_root, audit, made, blind, repo=None)`. `repo` defaults to the git top level
    of `out`, which A9 writes inside the repository; `fabric.py` stays unchanged. ACT.md gains step 6:

    `6. Install the weekly memory audit's cron line for this repository (Mondays 21:00; never installed by adoption):
    \`0 21 * * 1 GOV_MEMAUDIT_SETS_ROOT=<sets_root> <GOV_OS>/governance/project/orchestration/tools/memaudit_cron.sh
    --repo <repo>\``

    It is text only; no crontab is read or written.

- **I12, the digest lines (`digest.py`; S4, S6, S7, S8, S10).**
  - **A standing run's block** (`standing/<set>/<week>/DIGEST.txt`, and on stdout):
    - `STANDING <set> week <week> commit <12>`;
    - `VERDICT right <r> of <n>; wrong <w>; not found <f>; bar <need> right: passes|misses`;
    - `MISSES outcome wrong <a> incomplete <b> not_found <c>; rank 1-5 <x> 6-20 <y> absent <z>`;
    - `QUESTIONS live <n> of <n_set>; dropped <k>` (and `STANDING_THIN <live>` below 70);
    - `BESIDE hit5 <k> of <n_gold>; first bundle <k>; A1 <a> A2 <b>: <g> gains <l> losses, exact McNemar p <p>`;
    - the I10 `MAINTAIN` line;
    - `P1 memory below 95 %: wrong <a> incomplete <b> not_found <c>` on a miss, else `P1 none`;
    - `REPAIR open|none`;
    - `NEXT standing <date> <mode>; fresh <date>`;
    - `STOP ...` and `OWNER ...` as W2-172's lines.
  - **A fresh run's twelve lines are unchanged.** After them come `DRIFT S <s> F <f>: none|STANDING_FITTED|STANDING_STALE`
    (or `DRIFT not yet (k of 4)`) and the latest `MAINTAIN` line, with a live set only. The revised W2-172 S7 case counts
    them.
  - **No line** holds a question id, question, gold, answer, citation or path of a standing set.

- **How the code-bound clauses read:**
  - **S1's command** is `standing declare` with `--sets-root` required, as every subcommand. "The sha256 of the writer's
    and checker's briefs" is the `brief_sha256` of their delivered `counts.json`. "The commit it was written at" is the
    writer counts' `commit`. "Ever written to a misses.jsonl" is matched by question text.
  - **S2's "writes nothing"** covers the sets root, the key folder and stdout's digest (only the `USED` line is printed).
  - **S4's "AUDITS.log"** is the repository's `<key folder>/indep/AUDITS.log`, which a standing run never touches.
  - **S5's "the revised W2-170, W2-171 and W2-172 cases"** are the six files in `allowed_paths`, plus the two helpers in
    Gap G1.
  - **S9's "keep separate AUDITS.log"** is met with the launch script's AUDITS.log at `<key folder>/indep/AUDITS.log`
    (I2), not `<key folder>/AUDITS.log`, because the launch script fixes `$GOV_INDEP_RUNS_DIR/indep/`. "For Gov OS also its
    six retrieval globs" is the six globs applied to every repository, as I9 says.
  - **S10's "six counts"** are one field per item; items 1 and 2 print a state word, item 5 two numbers. "Cited lines
    changed" is `gov.retrieval.measure`'s `unresolved` (a block not found once at the audit commit).
  - **S10 and S8's "runs at once after the miss"** is the wrapper's second `maintain` in the same cycle.
  - **S11's "within the gate's wait"** is `--gate-cmd` on both `standing run` and `run`.
  - **F2's `measure --kept` on a standing run:** a name with a `STANDING.jsonl` record or a week folder prints `USED`,
    exit 3, nothing written.

- **Gaps (a KPI that cannot be met inside `allowed_paths` as filed):**
  - **G1 (S9 against S5, S8 and W2-172's unedited cases).** Moving the state to `<runs>/indep/memaudit/<key>/` breaks
    W2-172's s1, s2-s4, s6, s8 and s9 cases and the f1-f4 cases. They read it through `self.mem` and `self.audits_log` in
    `tests/acceptance/W2-172/w2_172_world.py` (lines 281-282) and `w2_172_git.py` (lines 43-44). Neither helper is in
    `allowed_paths`, and S8 requires `test_w2_172_s5_due.py` unchanged. The fix keeps every W2-172 test file unchanged:
    add the two helpers to `allowed_paths` for the test designer, about four lines (the key, `mem`, `audits_log`), with a
    `Rewrite-Reason` naming DEC-1179 (5). That is a path case the CTO routes under DEC-1156 (7).
  - **G2 (S10 (6)'s hand-off).** The tool writes the request (I10). Staging it into a writer's wall needs a `reanchor`
    input in `governance/project/indep-walls/kinds.yaml` and the matching staging in
    `governance/project/orchestration/tools/indep_launch.py`, which are walls and control paths (an ACT). Until then the
    owner's operator hands it over in the Monday slot, as the ticket's last paragraph says.

---

## Interface (the CTO at claim, DEC-1179 (8), DEC-1157 (3) and (12); listed for the owner's reading)

- **I1, the skill's three copies and the four places (S1, S2, S4, F1).** `template/governance/kernel/skills/adopt/SKILL.md`
  is edited. `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md` are then byte copies of it,
  all three at base sha256 `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`, 74 lines. Exactly four
  places change:
  - **Line 4:** `version: "1.0.0"` becomes `version: "1.1.0"` (W2-88a is closed and the kernel copy still reads 1.0.0
    at `10c0ca52b`). If the version line reads anything other than 1.0.0 at claim, use the next minor after it (S4).
  - **Line 58, step 6:** replaced in place by one numbered line, `6. Declare ...`.
  - **A new paragraph** after line 59 (step 7), with one blank line before it, before line 61's
    `## Verify clauses for adopted tickets`.
  - **Line 74, the sources line:** adds DEC-1101, DEC-1125 and DEC-1179 in numeric order.

  `git diff <base> -- template/governance/kernel/skills/adopt/SKILL.md` shows those four hunks and no other.
  `.claude/skills/adopt/SKILL.md` is not touched (the copies ACT).

- **I2, step 6's text constraints (S1, F1, F3; W2-88a's `check_steps` at `tests/acceptance/W2-88a/w2_88a_support.py:207`).**
  - **The step-6 anchor:** step 6 opens with `Declare`, and no word starting `declar` stands earlier in steps 1 to 5.
  - **The step-6 checks:** it says `measure`, `the verdict set` and `once`.
  - **The step-7 anchor** (`record\w*` then, within one sentence, `every|each|all` then `method`) must not occur in step 6.
  - **No subcommand:** it names no `gov.memaudit` and no `standing declare`.
  - **No second reranking model:** it never calls the reader one.
  - **The literal phrases step 6 holds:** `standing set`, `every week`, `same questions`, `95 %`, `counts only`,
    `never chooses or judges a fix`, `fresh set` with `month`, `fitted` with `replaced`, and `DEC-1179`. S1's
    statement that a miss is never re-run in the same week and never re-scored is kept in words as well, though the
    S1 Verify list does not test it.

- **I3, the paragraph after step 7 (S2).** One paragraph that holds the literal words `cron`, `ACT`, `operator`,
  `never installs` (or `never installed`) and `95 %`, and points to the practice record's section 9. It names no
  subcommand, and the step-7 anchor rule does not apply after step 7.

- **I4, the practice record `docs/research/W2-88-memory-practice.md` (280 lines at the base; S3, F3).**
  - **The places re-worded as the CIT-P quotes:** §3's bullet at lines 91-92; §5 item 6's two sub-bullets at lines
    190-191; §6 step 6 at line 221.
  - **§6 still passes `check_steps`:** the same anchor rules as I2, and step 6 keeps `Declare`, `measure`,
    `the verdict set` and `once`.
  - **A new `## 9. The standing set (DEC-1179)`,** appended after §8 at the end of the file. It holds:
    - what the set is;
    - the method: the reader ranking the whole bundle and searching again once, A2, with E2's 115 and 128 of 138 and
      E3's 114 against 84;
    - the bar, ceil(0.95 n);
    - the walls, with the literal `counts only`;
    - the literal `never chooses or judges a fix`;
    - the sentence that W2-88 S10's second reranking model stays forbidden;
    - staleness by count;
    - the monthly check with its two 5-point rules;
    - DEC-1179 (4)'s text as recorded, word for word: the bytes of the register's DEC-1179 line `  - (4) ...` after
      `(4) `, from `**Below 95 %:**` to its closing `.`.

- **I5, the checks the session runs and records under `docs/probes/DAEO-zlog/` (S1, S3, S4).**
  - `check_steps` on A9's region of each copy (`a9_regions`) and on the practice record's §6: no problems;
  - `check_pointer` on A9's region: no problems;
  - `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt`: exit 0;
  - `sha256sum` of the three copies: equal;
  - `grep -c 'gov.memaudit\|standing declare'` of the three copies: 0;
  - the I1 `git diff --stat` and hunk count.

  It runs no test suite.

- **I6, the CIT-P record `docs/changes/W2-188-CIT-P.md` (S5).** Built from the draft
  `.gov-runtime/scratch/orchestrator/drafts/memory-audit-p1/W2-188-CIT-P.md`. It holds:
  - the skill's sha256 before (`16fd341f...`) and after; the after equals the kernel copy at the ticket's last commit, so
    the record is the last file changed;
  - the lines added and removed;
  - the old and new text of each changed place;
  - the impact table: W2-11's body case `test_every_copy_carries_the_kernel_skills_body[adopt]` red until the copies ACT;
    W2-88a's cases unchanged;
  - the reviewer's `verdict: PASS` as the last verdict line;
  - in the front matter, `owner_approval: '<sha256 after> approved by the owner, <date>, <reference>'`, written before
    the merge.

- **How the code-bound clauses read:**
  - **S1:** "never chooses a fix" reads as F3's literal `never chooses or judges a fix`. "Fresh set monthly" reads as
    `fresh set` and `month` within step 6. "Fitted replaced" reads as `fitted` and `replaced` within step 6. "Counts only"
    is the literal phrase.
  - **S4:** "the next minor" is 1.1.0. "Those four places" are I1's four hunks.
  - **S3:** "equals DEC-1179 (4)'s as recorded" is I4's verbatim substring.
  - **F2:** the close's diff names no `.claude/` path and no `tests/` path.

- **Gaps:** none inside `allowed_paths`. The draft's text needs four changes to meet these clauses (see discoveries):
  - its step 6 says "with only counts leaving its run" and lacks the literal `counts only`;
  - its §9 lacks the literal `counts only` and `never chooses or judges a fix`;
  - its §9 last bullet must be replaced by DEC-1179 (4)'s recorded text, recorded at `976e53791`.
