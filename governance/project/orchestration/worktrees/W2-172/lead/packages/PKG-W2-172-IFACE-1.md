# PKG-W2-172-IFACE-1: W2-172's Interface (DEC-1052), proposed by the lead, run 1 (2026-11-12)

task: DAEO-p8tv · decisions_applied: DEC-1052 (the interface check), DEC-1101, DEC-1125, DEC-1097, DEC-1038

**Question.** DAEO-p8tv has no `## Interface` section, though its siblings W2-170 (DAEO-61vm) and W2-171 (DAEO-k1e2) each have one. The KPI lines name the four subcommands. They do not say where the driver's state lives, how it learns the round-2 decision, the USED boundary or the verdict without opening a folder under the sets root (F1's spy), the store stamp and the rebuild marker, the refusal and exit codes, the `due` record, the digest's line forms, the gate command, or the clock seams the tests need. The test designer cannot write S1 to S9 against it, so no worker starts until it is stated.

**Options.**
- (a) Paste the block below into DAEO-p8tv as `## Interface` (the CTO, delegated P2, as PKG-W2-171-IFACE-1 (a)). Cost: one ticket edit, about 10 min. The pair starts at once.
- (b) The CTO writes its own Interface. Cost: about 60 min of the CTO's time; the pair waits.
- (c) Let the pair settle it. Cost: DEC-1052 forbids this, and two independent sessions would build two interfaces.

**Recommendation:** (a), with open points O1 to O4 answered (each has a default the block already uses). **Confidence:** medium-high: each item follows the launch script's code (`indep_launch.py` at `1d0d8da0d`), W2-170's and W2-171's Interfaces, `rebuild/integration.py` and MEMORY-AUDIT-1 §3.3 and §4. **Blocks:** W2-172's tests run (and so W2-88, W2-174 and W2-27 on EXAMIN's critical path).

**Also for the CTO (not part of the Interface):** the probe record `docs/probes/DAEO-p8tv/PR-DAEO-p8tv.md` is not under DAEO-p8tv's `allowed_paths`; FULL needs it there before the review round.

**Open points (each with the default used below):**
- **O1, the 24-hour age (S2):** the KPI reads "that commit is more than 24 hours old". Default: the commit's committer time, as written. The cost: a day with no merge to `w2/integrate` before Monday 21:00 refuses that week's audit (`RN-STALE`, in the digest), and the next start is a week later unless `--force`. The alternative is the store's build time (`stores.json` `written_at` of the ready half).
- **O2, the gate (S9):** "the gate's own check" for "the dispatcher holds a full run or a rebuild". Default: `python3 <tools>/gate_check.py --full-run` (the check a full run already makes on itself before it starts, DEC-961), plus the integration store's `<link>.lock` held. The command is a flag, so the CTO can name another.
- **O3, the first audit without a baseline:** default `run` refuses `RN-NOBASE` while `AUDITS.log` has no line. Without that refusal, W2-170's selection lists "cannot be had" and every `drawn:` question is refused.
- **O4, the pinned interpreter (S9):** default `GOV_MEMAUDIT_PYTHON`, else `/usr/bin/python3`.

---

## Interface

Stated by the CTO before the pair starts (DEC-1052; PKG-W2-172-IFACE-1, option (a)). The test designer writes tests to this block and the engineer conforms to it; neither changes it. A gap or a clash goes back to the CTO as a package. W2-170's Interface (DAEO-61vm) and W2-171's (DAEO-k1e2) hold and are called, never copied or changed: their subcommands, exit codes, layout and `say`. The launch script (`governance/project/orchestration/tools/indep_launch.py`, W2-149, W2-173, W2-178) is called and never changed. The three approved briefs are not changed (DEC-1129 (2)). Bracketed lines name the KPI lines each item serves.

### 1 The command line [S1, S4-S8, F1]
Four subcommands join `python3 -m gov.memaudit`: `run`, `due`, `baseline` and `status` (`--help`: exit 0). They print through `say` only (W2-170 §1). Flags:

| flag | used by | meaning and default |
|---|---|---|
| `--sets-root <root>` | all, required | as W2-170 §1. The only flag that names the sets root; the driver never builds, opens, lists or stats a path under it (F1) |
| `--repo <dir>` | all | the repository (the launch script's cwd). Default: the top level of the working directory |
| `--store-link <path>` | `run`, `due` | the integration store's link. Default: `integration_store` of `governance/project/rebuild.yaml`, read with `git show <main line>:governance/project/rebuild.yaml` in `--repo` |
| `--launch <file>` | `run` | the launch script. Default: `<repo>/governance/project/orchestration/tools/indep_launch.py`. The test seam for the stub launch script (W2-149's stub `claude` runs under the real script) |
| `--gov <exe>`, `--claude <exe>` | `run` | passed on unchanged to W2-171's `measure`, `judge` and `pool` (W2-171 §6) |
| `--gate-cmd <exe>` | `run` | §8; default none (no gate) when run by hand |
| `--force` | `run` | the owner's word: lifts the 5-day refusal only (S4); recorded in the counts and the digest |
| `--commit <rev>` | `baseline`, required | resolved with `git rev-parse --verify <rev>^{commit}` in `--repo` |
| `--since <rev>` | `status`, required | as `--commit` |

- **The runs folder is never a flag.** It is `$GOV_INDEP_RUNS_DIR`, else `~/gov-os-runs` (the launch script's own rule and W2-170 `preflight`'s default), and it is passed to every child in the environment. Every printed command line then holds no `runs/` (`gov-os-runs/` would match the KPI's grep).
- **Clock seam:** `GOV_MEMAUDIT_NOW` (ISO 8601 UTC), when set, is "now" for every age and date (S2, S4, S5, S8, S9's wait). Nothing else reads the clock.

### 2 The cycle [S1, S3, F1]
`run` runs the steps below, in this order and no other, each as a child process with cwd `--repo`. Its environment is the driver's own plus `GOV_INDEP_RUNS_DIR`. Its standard error goes to `<R>/<A>/<step>.err` (§4), never printed, and its standard output is kept in `<R>/<A>/<step>.out`. `<py>` is `sys.executable`; `<A>` is the audit's name (§3); `<C>` is the audit commit (§3).

| # | step | command line |
|---|---|---|
| 1 | `writer-1` | `<py> <launch> --sets-root <root> --kind writer --brief governance/project/indep-briefs/memory-audit/writer.md --brief-sha256 <h> --commit <C> --set <A> --round 1` |
| 2 | `preflight` | `<py> -m gov.memaudit preflight --sets-root <root> --audit <A> --repo <repo> --commit <C>` |
| 3 | `checker-1` | launch, `--kind checker`, `checker.md`, `--round 1` |
| 4 | `writer-2` | launch, `--kind writer`, `--round 2`: only when §2a says so |
| 5 | `checker-2` | launch, `--kind checker`, `--round 2`: only when §2a says so |
| 6 | `void` | `<py> -m gov.memaudit void --sets-root <root> --audit <A>` |
| 7 | `measure` | `<py> -m gov.memaudit measure --sets-root <root> --audit <A> --repo <repo> --commit <C> --store <link>/.gov-runtime/store.db [--gov <exe>]` (W2-171's declaration, use-once marker, control and attempts) |
| 8 | `judge` | `<py> -m gov.memaudit judge --sets-root <root> --audit <A> --repo <repo> [--gov] [--claude]` (writes `misses.jsonl`, empty when there is no miss) |
| 9 | `auditor` | launch, `--kind auditor`, `auditor.md`, `--set <A> --audit <A>`: always, also with an empty misses file. The launch script appends the `AUDITS.log` line on delivery |
| 10 | `classes` | `<py> -m gov.memaudit classes --sets-root <root> --audit <A>` |
| 11 | `pool` | `<py> -m gov.memaudit pool --sets-root <root> --audit <A> --repo <repo> [--gov]` |
| 12 | `figures` | `<py> -m gov.memaudit figures --sets-root <root> --audit <A>` (§6; reads, writes nothing) |

- `<h>` is the sha256 of the bytes `git show <C>:<brief path>` returns. The driver never opens `indep-walls/APPROVED`; the launch script checks it.
- **2a, the second round.** The launch script's standard output ends with its counts object (`indep-counts.schema.json`). The driver parses only that last line, keeps it as `<R>/<A>/<step>.counts.json`, and runs steps 4 and 5 exactly when `checker-1`'s `out.revise + out.rejected > 0`. A clean first pass goes from step 3 to step 6.
- Printed per step, before it starts, is one line: `STEP <name> <the command line>`. That is the KPI's "printed command lines" and the call ledger the tests read. It holds no `fixtures/`, `runs/` or `indep-walls/`.

### 3 The audit commit and the refusals before anything starts [S2, S4, F3]
- **The audit commit** `<C>` is `git -C <store-link> rev-parse HEAD`: the ready half's head, which is its build (`rebuild/integration.py`: the link points at the half built at that head). The measure's `--store` is that half's `store.db`, so nothing is rebuilt.
- **The audit's name** `<A>` is `memory-audit-<yyyymmdd>`: the UTC date of now. It names both the set and the audit folder.
- **The checks, in order.** The first one that fails refuses: it prints `REFUSED <code>`, writes `<R>/<A>/COUNTS.json` with `refused: <code>` where `<R>/<A>/` does not yet exist (otherwise it writes nothing there), starts no child and exits 1. A refusal is not a started audit.

| code | refuses when |
|---|---|
| `RN-LOCK` | `<R>/LOCK` is held (an exclusive `flock`, non-blocking, held by `run` until it exits) |
| `RN-NOBASE` | `<runs>/indep/AUDITS.log` is missing or holds no line (O3) |
| `RN-RECENT` | the last line of `<R>/STARTS.log` is under 5 × 24 h before now and `--force` is not given |
| `RN-REBUILD` | `<store-link>.lock` is held (a non-blocking `flock` try on it fails; when the try succeeds the lock is released at once) |
| `RN-SIDE` | `<C>` is not an ancestor of `refs/heads/w2/integrate`, else of `refs/heads/main` (the launch script's main-line rule) |
| `RN-STALE` | `<C>`'s committer time is more than 24 h before now (O1) |
| `RN-NAME` | `<R>/<A>/` already exists: a second start on the same date, so a set is never run twice |

- After the checks pass, `run` appends `{"audit","commit","at","force"}` to `<R>/STARTS.log` before step 1. S4's "last started audit" is that file's last line.

### 4 The driver's own folder `<R>` = `<runs>/indep/memaudit/` [S3, S4, S5, S7, S8, F2]
```
LOCK                 the one-at-a-time lock (flock)
STARTS.log           one JSON line per started audit
HISTORY.jsonl        one JSON line per audit that reached step 12 or stopped after USED (§5); the due rule and status read it
cron.log             the wrapper's one line per run (§8)
<A>/COUNTS.json      the run's counts: audit, commit, force, mode, steps [{step, exit, retried}], stop {step, exit, used} | null, refused, cost {<step>: usd}
<A>/DIGEST.txt       §7
<A>/<step>.out .err .counts.json
```
- Everything here holds counts, codes, ids, hashes and repository paths only (F2).
- `HISTORY.jsonl` line: `{"audit","commit","at","mode","churn","retrieval_28d","passes","pool_regression","measured","used"}`. `churn` is a fraction to 4 places; `retrieval_28d` and `pool_regression` are booleans; `passes` is a boolean, or null when not measured; `measured` is true only when step 12 ran.

### 5 Stops [S3, F3]
- **Any child exit other than 0 stops the cycle.** The one exception is a launch step that exits **16** (the canary): it runs once more with the same command line, and a second 16 stops. A stop prints `STOPPED <step> <exit>`, writes `COUNTS.json` and the digest, appends nothing to `HISTORY.jsonl` before USED, and exits 2. `void`'s exit 2 (a void audit) is a stop like any other.
- **The USED boundary, known without opening the run folder.** Steps 1 to 6 are before USED. Step 7 is before USED when `measure` exits 1 or 4 (W2-170's `DC-` refusals come before `declare` writes `USED`) and after it when `measure` exits 0, 2 or 3 (W2-171 §2). Steps 8 to 12 are after USED.
- **A stop before USED:** the set stays unmeasured, and the next audit has a new date and so a new set (`RN-NAME`).
- **A stop after USED:** the digest gains the owner line (§7). `HISTORY.jsonl` gains the line with `measured: false, used: true`. Nothing in the driver runs that audit's steps again: no resume and no second `measure`.

### 6 The figures, read by W2-170's and W2-171's files only through a child [S7, F1, F2]
- `python3 -m gov.memaudit figures --sets-root <root> --audit <A>` (this ticket's) prints one JSON line built from `runs/<A>/FIGURES.json` (W2-171 §10: `verdict`, `beside.hit5`, `beside.in_bundle`, `n_gold`, `bar`, `misses.by_rank`, `misses.by_namespace`, `classes`, `pool`, `spend.usd`) and from `DROPS.json` (W2-170: kept, dropped, counts by code).
- That line holds numbers and fixed words only. A missing file gives `null` for its keys, and the command exits 0.
- The driver's own process opens no path under the sets root. Every figure it uses comes from a child's standard output: the launch counts line, the `figures` line, and judge's `BESIDE ... spent <usd> USD` for the judge's cost.

### 7 The digest block [S7, S3, F2]
Written whole by rename to `<R>/<A>/DIGEST.txt`, then printed line by line, after every audit, every stop and every `RN-` refusal that has an `<A>`. There are exactly these 12 lines in this order. A figure not reached prints its word followed by `not reached`.
```
AUDIT <A> commit <12 hex>
MODE weekly|monthly reason <code>
VERDICT right <r> of <n>; wrong <w>; exact <lo> to <hi> %; bar <need> right, <max> wrong: passes|misses
HIT5 <a> of <ng>; first bundle <b>
MISSES class gold_wrong <n> question_ambiguous <n> out_of_scope <n> retrieval_miss <n> answer_wrong <n>; rank 1-5 <n> 6-20 <n> none <n>; namespace embedded <n> keyword_only <n>
POOL hit5 <a> of <n> last <a'|none>; full <c> last <c'|none>; regression yes|no
RETRIEVAL changed <k>[: <path> <path> ...]      the six globs (§9) against git diff --name-only <last audit commit> <C>
QUESTIONS kept <k> dropped <d>[; <CODE> <n> ...]
COST <step> <usd:.2f> ... total <usd:.2f>
NEXT due <yyyy-mm-dd> <mode>
STOP none | STOP <step> exit <code> | REFUSED <code>
OWNER none | OWNER stopped after USED at <step> exit <code>: the set is not run again
```
- The schema is one regular expression per line, in this order; the test writes its own from this block.
- The retrieval paths are repository paths of the six globs, not a question's gold source (F2). S7's planted gold path is not one of them.

### 8 The cron wrapper `memaudit_cron.sh` [S9, F4]
- **Set-up:** bash. `PY="${GOV_MEMAUDIT_PYTHON:-/usr/bin/python3}"` (O4); `ROOT="${GOV_MEMAUDIT_SETS_ROOT:-$HOME/gov-os-eval}"`; cwd is the repository.
- **Not due:** it runs `$PY -m gov.memaudit due --sets-root "$ROOT"`; exit 1 (not due) appends the log line and exits 0.
- **Due:** it runs `run --sets-root "$ROOT" --gate-cmd "${GOV_MEMAUDIT_GATE:-<the gate's check, O2>}"` and exits with run's code.
- **The gate:** before each of steps 7, 8 and 11 (the steps that search the store), `run` calls `--gate-cmd` with no arguments: exit 0 is open, anything else is busy. It polls every `GOV_MEMAUDIT_GATE_POLL_S` seconds (default 60) for at most `GOV_MEMAUDIT_GATE_MAX_S` (default 3600, measured by the clock seam). When the wait runs out it stops with `STOPPED <step> gate busy`, which is a §5 stop at that step, and run exits 2.
- **The log line:** one JSON line per run appended to `<R>/cron.log`: `{"at","due","mode","reason","started","exit"}`.
- **What it never holds:** the word `crontab` (`grep -c crontab` is 0). It writes nothing but `cron.log` and what `run` writes.

### 9 `due`, the active and stable rule [S5]
- **Retrieval globs:** `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/store/**`, `src/gov/codeintel/**`, `governance/project/retrieval.yaml`, `governance/project/path-map.yaml`.
- **Churn at a commit X:** the paths tracked at X (`git ls-tree -r --name-only X`), less those matched by `governance/project/indep-walls/tree-exclude.txt` at X (fnmatch, as the launch script matches it), is the denominator. The numerator is those of them that appear in `git log --name-only --format= --since=<X's committer time − 28 d> --until=<X's committer time> X`. The result is a fraction to 4 places.
- **`retrieval_28d` at X:** some path in that same log matches the retrieval globs.
- **Mode.** Weekly while `HISTORY.jsonl` has fewer than 3 measured lines. Monthly when the last 3 measured lines each have `churn < 0.05`, `retrieval_28d` false, `passes` true and `pool_regression` false, and no back-to-weekly trigger holds. The triggers are computed now at the store link's head H: `churn(H) >= 0.10`; a retrieval-glob path in `git diff --name-only <last audit commit> H`; the last measured line's `passes` false; its `pool_regression` true.
- **Due.** Weekly mode is due when 6 days or more have passed since the last line of `STARTS.log` (5 days: not due). Monthly mode is due at 28 days or more (27: not due). No `STARTS.log` line means due.
- **Output and exit codes:** three lines, `MODE weekly|monthly`, `DUE yes|no next <yyyy-mm-dd>` and `REASON <code>`. Reason codes: `start`, `stable`, `churn`, `retrieval`, `verdict`, `pool`, `active`. Exit 0 when due, 1 when not due, 4 on usage.
- `run` records the mode and reason of its own `due` computation in `COUNTS.json`, `HISTORY.jsonl` and the digest.

### 10 `baseline` [S6]
- It appends `{"time","commit","run":"baseline","audit":"baseline"}` to `<runs>/indep/AUDITS.log`. That is the launch script's line form; its `last_audit` reads the last line's `commit`, and W2-170's selection lists do the same. It prints `BASELINE <12 hex>` and exits 0.
- **Refusals (exit 1, nothing written):** `BL-COMMIT` when the commit does not resolve in `--repo`; `BL-EXISTS` when `AUDITS.log` holds any line.

### 11 `status` [S8]
- **The last retrieval change** is L = `git log -1 --format=%H <since>..<main line> -- <the six globs>` in `--repo`.
- **No L:** it prints `audited` and exits 0.
- **Audited:** some `HISTORY.jsonl` line with `measured: true` has a commit A with `git merge-base --is-ancestor L A`. It prints `audited` and exits 0.
- **Otherwise:** it prints `not audited, next due <yyyy-mm-dd>` (§9's date) and exits 1.

### 12 Exit codes of `run`
| exit | when |
|---|---|
| 0 | the audit ran to step 12 |
| 1 | refused (§3) |
| 2 | stopped (§5, §8) |
| 4 | usage, as W2-170 |

Nothing `run` writes lies outside `<R>`. The children write what their own Interfaces say. The driver writes nothing to the path map, the guard, `.claude/`, the walls' template or the crontab (F4).
