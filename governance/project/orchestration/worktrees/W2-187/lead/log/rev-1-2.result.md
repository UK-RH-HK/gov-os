I've finished my review of W2-187 at `5b82d1d53`. I wrote nothing in the tree: `git status --porcelain` is empty and the head is unchanged. My verdict for the round is **pass**, because nothing in scope both fails open (or loses work) and is reachable in ordinary work. Two findings still need your triage before the standing run is switched on.

- **F-A:** in the cron layout, a standing run searches the repository's own store, not the store it declares. The new store-commit check then stops every week at `STOPPED fault`, so no standing verdict is ever produced.
- **F-B:** a commit that lands while the weekly scan runs gets pushed without being scanned. I treat it as an entry criterion (DEC-803) because no repository declares a push today.

task: DAEO-0cd2 (W2-187), independent review round 1 (FULL, C2), head 5b82d1d53868625c43a5b8b2bb58492bad3f8038
status: DONE
work_completed:
- Read the ticket (S1–S12, F1–F7, I1–I13, gaps, routings, amendments, the I13 note), both packages, the evidence, the acceptance README and the sources by id.
- Read every changed module, the wrapper, `memory_sets.walls_act` and the test helpers.
- Traced each KPI line to its tests and code.
- Checked scope and role separation commit by commit.
- Ran three planted or read-only probes: push with the branch moving during the scan; push under cron's `PATH`; the fingerprint head of the main checkout's store and of the integration store, read with `immutable=1`.

files_changed: none
evidence:
- Probe files are only under `$TMPDIR/probeA`.
- The scanner saw `8b7b712`; the remote received `ede719b`, which holds a planted key.
- Under `PATH=/usr/bin:/bin` the output was `PUSH blocked: scan failed missing`.
- Store heads: main checkout `cf8d928286eb`, integration store link `3866f95f6c44`, 31 commits apart.

tests: I re-ran no suite; your results stand. The three probes above are my only runs.
discoveries:
- F-A (the searched store is not the declared store); the fresh path shares the same root (R6).
- The measure's control is fixed to Gov OS's `memory-retrieval` visible 40 (R2).
- gitleaks is only in `~/.local/bin`, which cron's `PATH` doesn't include (R1).

risks: Fixing F-A only on the standing path would make S7 compare a standing figure from the link with a fresh figure from the repository's store. A false `STANDING_FITTED` would then retire the set, and a retired set can never be declared again.
lessons: A planted `gov` that answers the plan's store commit whatever folder it is called from can't show which store a search reached.
proposed_decisions: none. Triage F-A as an agreed fix, and F-B as an entry criterion (DEC-803) or a ride-along if the ticket resumes (DEC-802).
unresolved:
- Whether you read F-A's consequence as "other" (my reading: it fails closed and the STOP is visible every week) or as "loses work".
- Whether the push counts as switched on with this ticket. If it does, F-B becomes ordinary work yes and blocks.

recommended_next_action: Fix F-A before ACT-MEMORY-AUDIT-CRON-1 installs the cron line. Point the standing and fresh children at the store link's work tree, or route their searches to the link's store. Add a case where the repository's own store sits at another commit. Carry F-B to whatever first declares a push.

decisions: DEC-1179, DEC-1182, DEC-1097, DEC-1098, DEC-1157 (3), DEC-803, DEC-802, DEC-1010, DEC-801, DEC-808

### KPI trace

| KPI | tests | code | traced | could a test pass for the wrong reason |
|---|---|---|---|---|
| S1 | `test_w2_187_s1_declare.py` (28), unit `test_standing.py` | `standing.py:164-221`, `layout.SET_RE`, `__main__._standing` | yes | no |
| S2 | `test_w2_187_s2_week.py` (12), `test_s2_s3_…` | `driver.py:359-424`, `standing.py:226-244`, `declare.py:221-300` | yes | no |
| S3 | `test_w2_187_s3_method.py` (5), `test_prompts.py` unchanged | `judge.py:55-57,165-176,253`, `fault.py:128-145`, `measure.py:133-135` | yes | **yes:** `fake_gov_x.py:103` returns the plan's store commit whatever folder it runs in (F-A) |
| S4 | `test_w2_187_s4_counts_only.py` (5) | `judge.py:263-274`, `digest.standing_*`, `driver._standing_line`, `__main__.main` (exception class name only) | yes | no |
| S5 | `test_w2_187_s5_bar.py` (15), revised W2-170/171/172 cases | `declare.py:26-35` | yes | no |
| S6 | `test_w2_187_s6_stale.py` (8) | `preflight.standing`, `measure.py:148-152`, `judge.asked` | yes | **partly:** the pre-flight-alone cases pass the link as `--repo` (`:91-93`) but the driver passes the repository (`driver.py:177`) |
| S7 | `test_w2_187_s7_drift.py` (10) | `standing.py:277-303`, `driver.py:293-294`, `pool._diagnostic` (untested, as the README says) | yes | no |
| S8 | `test_w2_187_s8_cadence_repair.py` (26) | `schedule.py:209-303`, `standing.py:308-364`, the wrapper's second `maintain` | yes | no |
| S9 | `test_w2_187_s9_state.py` (12) | `schedule.py:55-71,149-175`, `pool._importing_sets` | yes | no |
| S10 | `test_w2_187_s10_maintain.py` (18) | `maintain.py`, `matcher.section*` | yes | G6 rests on a stub (named in the evidence) |
| S11 | `test_w2_187_s11_cron.py` (15) | `memaudit_cron.sh`, `walls_act` | yes | no |
| S12 | `test_w2_187_s12_push.py` (27) | `push.py`, `push_step`, `PUSH_ORDER` | yes | no case moves the branch during the scan (F-B) |
| F1 | `test_f1_…`, S4's grep | `classes.py:21-23`, `pool.py:111-113,260-262`, `is_standing` | yes | no |
| F2 | F2 cases (5), S2's cases | `measure.rescore`, `driver.py:376-378` | yes | no |
| F3 | F3 cases (9) | argparse of `standing run`, `declare.py:228-229,276` | yes | no |
| F4 | F4 cases (2), S3's spy | `prompts.py` unchanged, one `_Judge` | yes | no |
| F5 | `test_f5_…`, W2-170/171 suites | the fresh path without `--week` is unchanged | yes | no |
| F6 | F6 cases (2) | `maintain.py` | yes | no |
| F7 | F7 cases (16) | `push.scan`, the wrapper | yes | no |

### What I probed and found sound

- **Scope:** every file changed by the engineer's and test designer's own commits is inside `allowed_paths`. Files outside them (the ticket, the register, DND, DECISIONS-IN-FORCE, DAEO-h2k3) come only from orchestrator decision-record commits merged from `w2/integrate`.
- **MR-3 separation:** only the test designer touched `tests/acceptance` (10 commits); only the engineer touched code and unit tests (6 commits).
  - Each revision of a W2-170/171/172 test file carries a `Rewrite-Reason`.
  - Their diffs change only bar values, the `bar` helper, `ROUNDING`, the key-folder path, and the W2-171 ledger case's planted scenario (`five` → `clean`, 3 lines, path case P1 (a)).
- **Counts only (read):** nothing writes a question, id, gold, answer or citation outside `runs/<set>/`.
  - With `--week`, `judge` writes no `misses.jsonl` and prints `SEARCH FAILED` as a count.
  - The CLI's error path prints the exception class name only, so even a crashed child leaves no text in the key folder's `.err` files.
  - The reader runs with `--no-session-persistence`.
- **One judged path:** `prompts.py` and `test_prompts.py` are unchanged; `_Judge`, `figures.build` and `matcher` are shared, and `asked()` only selects the live files.
- **Week rule:** a spent week gives `USED` exit 3 before anything is written. A stop before the reader allows one rename to `<week>.stopped`; a second stop gives `USED`. The digest check comes before any search and doesn't spend the week. `measure --kept` on a standing set gives `USED`.
- **F3:** `standing run` takes no `--decision`, `--force` or data flag; `declare --week --decision` is refused as usage; a nonstandard `retrieval.yaml` is `DC-DECISION` with no way to allow it.
- **Bar:** 38, 76 and 76 for n = 40, 79 and 80; a pass means right ≥ need_right, and the wrong-claims limit follows from it.
- **Keyed state** matches I2, and the children receive the key folder in both variables.
- **`maintain`:** always exits 0; writes only `MAINTAIN.jsonl` and 0600 requests that hold ids and entry numbers; never writes `retrieval.yaml` or the path map; leaves standing sets out.
- **Push fails closed:** findings, an uncountable report, other exits, a timeout or a missing binary all block the push.
  - The report is a 0600 file outside the repository and is deleted afterwards.
  - The probe found no key text in any log; `PUSH.log` is 0600 and holds only git's ref line.
  - A push with no declaration writes nothing.
  - The wrapper runs `push` only after an audit step started, and keeps the audit step's exit code.
- **The engineer's "broken anchor stops the measure" risk:** the writer brief (R6, R10) requires `heading`, `lines` and `commit`, so `_span` resolves to "unresolved" instead of raising. The risk can't come from a set written to the brief.
- **Early-stop answers:** `UNRESOLVED_IDS` answers also carry `result.store`, so the nonexistent-id question doesn't make every attempt fault.

### Findings

**F-A: the standing run searches the repository's own store, not the declared store**
- **What was done:** I traced the cron layout: `memaudit_cron.sh --repo <repository>`, with the store link taken from `rebuild.yaml`. I then read both stores' fingerprint heads, read-only.
- **What happened:**
  - `standing run` hands its pre-flight, measure and judge children the repository as their root (`driver.py:177,184,186`).
  - The measure runs `gov retrieve` from that folder with `GOV_STORE` removed (`runner.py:25,46-48`; `retrieval/measure.py:320-323`). So the searches answer from the repository's own `.gov-runtime/store.db` (`cli/main.py:242`; `retrieve/command.py:102-129`).
  - The declaration names and checks the link's store (`driver.py:183`; `declare.py:259-261`).
  - On Gov OS the two are now 31 commits apart (`cf8d928286eb` against `3866f95f6c44`). The new check (`fault.py:143`, `measure.py:133-135`) faults attempt 1, then attempt 2, then writes `STOPPED fault`. The week is spent, and every following week goes the same way.
  - Judge's later searches would also fail as `store` (`judge.py:55-57`).
  - I6 says the pre-flight's root is the store link's work tree; the evidence's reading 4 chose the repository instead.
- **What should have happened:** the searches reach the declared store (the link at the audit commit), and anchors are read at that commit. The fresh path has the same root (R6) and should move with it, or S7 would compare two different stores.
- Ordinary work: yes, because this is the default layout: the cron line names the repository and the link comes from `rebuild.yaml`; no deliberate step is involved.
- Consequence: other. It fails closed: there is no verdict and the STOP shows in each week's digest; nothing passes that shouldn't and nothing is deleted.
- Scope: in (S3, S6/I6).
- Reversed by: evidence that the repository's own store is refreshed to the integration head before each standing run, or that `gov retrieve` reaches the link with `GOV_STORE` unset.

**F-B: a commit that lands during the scan is pushed unscanned**
- **What was done:** I planted a repository and a bare remote, with `GOV_MEMAUDIT_PUSH="origin main"`. A planted scanner wrote a clean report, and while it ran, a commit holding a planted key landed on `main`, standing in for a merge from another worktree.
- **What happened:** `PUSH pushed origin main ede719b54a8c`, exit 0. The remote's `main` holds the late commit; the scanner had seen `8b7b712`. `git push` reads the branch name again after the scan (`push.py:127,206-216`).
- **What should have happened:** push only the commit the branch named when the scan began, or block with a named reason if the branch moved.
- Ordinary work: no today, because no repository declares a push: Gov OS declares none (DEC-1182 (1)) and EXAMIN's remote stays removed until it is hosted (DEC-1182 (2)). Once a push is declared, a merge during the scan needs no deliberate step, so under DEC-803 this becomes an entry criterion for the first push declaration.
- Consequence: fails open.
- Scope: in (S12, F7).
- Reversed by: a reading that the push is switched on with this ticket (then the round fails), or a guarantee that the declared branch can't move while the cycle runs.

### Rows

| id | behaviour | ordinary work | consequence | scope |
|---|---|---|---|---|
| R1 | ACT step 6's cron line (`memory_sets.py:180-181`) doesn't name `GOV_MEMAUDIT_GITLEAKS`. gitleaks is only in `~/.local/bin`, so under cron's `PATH` a declared push is blocked every week as `scan failed missing` (probe). Reversed by a cron `PATH` that holds gitleaks. | yes, once a push is declared | other: fails closed, named | in |
| R2 | The control is fixed to Gov OS's `memory-retrieval` visible 40 with E0's 34 (`measure.py:22,99-102`, from W2-171). On an adopted repository's sets root a standing or fresh run stops `notready` after USED. Reversed by a control set in that root. | yes | other: fails closed | out |
| R3 | `maintain` items 4–6 have no timeout, though I10 says each item is bounded (`maintain.py:101-205`). I found no path that hangs. | no | other | in |
| R4 | RN-STALE refuses a Monday run after a weekend with no commits. This follows I4 and the engineer flagged it. | yes | other: fails closed | in |
| R5 | The standing digest's OWNER line says "the set is not run again" (`digest.py:167`); for a standing set only the week is spent. | yes | other: wording | in |
| R6 | The fresh path (W2-172, unchanged) also searches the repository's store while declaring the link's, with no store-commit check. | yes | other | out |

### Verdict
**pass.** No finding is in scope, reachable in ordinary work, and fails open or loses work. F-A should be fixed before the standing run is switched on, and F-B should be carried as an entry criterion.

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, {"kpi": "success-2", "verdict": "pass", "findings": [{"id": "R4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-3", "verdict": "pass", "findings": [{"id": "F-A", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-4", "verdict": "pass", "findings": []}, {"kpi": "success-5", "verdict": "pass", "findings": []}, {"kpi": "success-6", "verdict": "pass", "findings": [{"id": "F-A", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "R6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-8", "verdict": "pass", "findings": []}, {"kpi": "success-9", "verdict": "pass", "findings": []}, {"kpi": "success-10", "verdict": "pass", "findings": [{"id": "R3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "success-11", "verdict": "pass", "findings": []}, {"kpi": "success-12", "verdict": "pass", "findings": [{"id": "F-B", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "failure-2", "verdict": "pass", "findings": []}, {"kpi": "failure-3", "verdict": "pass", "findings": []}, {"kpi": "failure-4", "verdict": "pass", "findings": []}, {"kpi": "failure-5", "verdict": "pass", "findings": []}, {"kpi": "failure-6", "verdict": "pass", "findings": []}, {"kpi": "failure-7", "verdict": "pass", "findings": [{"id": "F-B", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```

guard_refusals: none