---
type: probe
task: DAEO-g87r
reviewer_session: 3733ec73-56ed-4532-a182-b8fb39d428a0
implementer_session: 8ad38fe1-a1ed-4122-bb7c-2e684744584f
implementer_session_round2: ccf43198-9304-4f8f-a23e-26ed4e54856b
test_designer_session: da4a1f0a-e7a6-4757-b070-fa7d0d63f36e
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: fac8d2026c732e5a2a47e6f2811b0870b53756d4
decisions_applied: [DEC-1180, DEC-1178, DEC-957, DEC-820]
---

# Probe record: W2-94 fix flow (DAEO-g87r), head `fac8d2026c732e5a2a47e6f2811b0870b53756d4`

task: DAEO-g87r
decisions: DEC-1180, DEC-1178, DEC-1112, DEC-820, DEC-801, DEC-808, DEC-1010

### What was probed, and how
- **The code:** the diff `340cd0efb..fac8d2026` of `governance/project/orchestration/tools/indep_launch.py` and the engineer's unit tests, read line by line against S6–S12, F4–F6 and the lead's interface.
- **The cases:** the designer's cases in `tests/acceptance/W2-94/`.
- **The variant and the wall:** the variant fixture, compared with what the wall gives: `tree-exclude.txt`, `CLAUDE.md.tmpl`, the wall hook, and `writer-result.schema.json`.
- **The runs:** the W2-149, W2-173, W2-178 and W2-94 suites on planted stand-ins only. 187 passed as briefed; 300 passed with every row opted in.
- **Not done:** the planted-break runs. The Edit tool was refused on the `$TMPDIR` copies and I did not work around it.

### Found sound, line by line
- **S6.** `indep_launch.py:581-584`:
  - Either flag alone, another kind, round 1 or no round, an id not fully matching `q[0-9]{2}` (`FIX_RX`, line 90) or a code outside `FIX_CODES` (lines 91-92) all refuse 17 "fix".
  - With `--counts-only`, `--fix`/`--reason` refuse 17 (lines 559-561).
  - This happens before any build, so there is no wall, tree, run folder or SEEDS.log line.
  - `allow_abbrev=False` keeps `--re…` from aliasing.
  - Cases: `test_s6_*` (each wrong form, plus the 8 codes and the edge ids), unit `test_fix_argument_refusals_17_build_nothing`.
- **S7 and F4.** `plan_fix` (867-876) and `round1_sample` (823-864) run at stage 10, before B1:
  - The source must be a plain file with no link on its way (`real_inside` and `islink`). Anything else refuses 10.
  - `verdict.txt` is exactly `<id> <code>\n`.
  - The round-1 sample:
    - Only runs whose `counts.json` says `delivered`, round 1 (not a bool) and this set, with a run id that fully matches `<time>-<set>-r1`, are eligible.
    - The latest is `max(found)`, which is chronological because the id starts with its UTC time.
    - From that run's own tar, the only member read is `<rid>/input/selection.json`: regular, size-capped, parsed strictly, with `sample` a list of strings.
    - No other member of the round-1 tar is extracted, so its `out/set/**` is never read.
  - Staging (2528, 2541-2549) writes `selection.json`, the two staged files and the one copy, and nothing else. No `input/set/` and no `notes.md`: `plan_inputs` is not called in a fix run (2418-2420).
  - Logs and counts carry only counts and the argument words: B4 logs "staged 3", and stderr carries only status, code and reason.
  - Cases: `test_s7_*`, `test_f4_no_other_file_of_the_set_reaches_the_wall`, and the leak greps in `test_s9_on_delivery_the_counts_carry_the_fix_and_no_content`.
- **S8 and F5.** `deliver_fix` (1848-1885):
  - `out/` must be exactly `{<id>.yaml, result.json}`. `os.listdir` sees dotfiles, folders and links.
  - The YAML must be a plain file with no link on its way, parsed with `safe_load`, a mapping, with `id == <id>`.
  - The destination is checked to be a regular file, and every check runs before any write.
  - The old file is kept at `<wall>.replaced/` beside the wall, never under `<setdir>`.
  - The replacement is a temp file plus an atomic rename (`deliver_file`, 1633-1647), and the temp file is always removed.
  - `pack` (2199-2200) archives the old file as `<run>/replaced-hidden/<id>.yaml` and then removes the folder.
  - On every refusal path (17/10 before the build; 20/21 in `check_result` or `deliver_fix` before the rename; any exception before the rename) `<setdir>` is not touched.
  - The file to replace comes only from the validated id, and the delivered YAML must carry the same id, so the wrong file cannot be replaced.
  - Cases: `test_s8_*` and `test_s8_f5_*` (17 refusal forms, with sha256 of every set file before and after).
- **S9.** `check_result` (2175-2179):
  - The result must have `action ∈ {corrected, replaced}`, `questions == 1`, and `by_kind` and `by_area` each summing to 1.
  - The schema's `integer` excludes bools and floats (`_is_type`, 358), so `true` and `1.0` cannot pass as 1.
  - A stopped word refuses 21 first (2154-2159).
  - Counts: `fix` is set at the argument check with `action: null` (584) and gets its action only after the result passes (2179). Point (d) is sound and matches the interface's item 6.
  - Cases: `test_s9_*` (26 wrong forms; stopped results; a stop with no question file).
- **S10.** `resolve_brief` (715-718): in a fix run a missing `sample:` becomes 0, and a `brief:` entry refuses 10. Without `--fix`, nothing changes: the variant is refused 10, as today. The brief's bytes and APPROVED line are still checked (2384-2388). Cases: `test_s10_*`, with the fixture at sha256 `0703aebf…`.
- **S11 and F6.** `git diff --stat` names only the ticket's paths. No `indep-walls/**`, `indep-briefs/**` or `indep-schemas/**` file changed. Cases: `test_s11_*`.
- **S12.** Every non-fix path is unchanged: `fix=False` in `resolve_brief`, `staged` and `expected` as before, and `check_result`'s new block applies to fix runs only. The W2-149, W2-173 and W2-178 suites pass unchanged, and `test_s12_a_writer_round_two_without_fix_…` passes.
- **Independence.** The engineer's commits touch no acceptance test, and the designer's touch nothing else (MR-3, DEC-430).

### Findings

**P1 (S10, S7): the walled writer cannot read the fixed brief that the variant makes binding on it.**
- **Where:**
  - Variant lines 25-28 apply "the fixed writer brief's … section 3, 4, 5 (R1 to R10, item 5), section 7's question form, and section 9's stop conditions … in full, word for word".
  - The wall's tree leaves out `governance/project/indep-briefs/**` (`tree-exclude.txt:20`; "a wall reads its own brief.md only", DEC-1112 (3), as that file cites).
  - Only the variant is staged as `brief.md`. The wall hook and `CLAUDE.md.tmpl:3` allow reads of the folder and the tree only.
- **Consequences for q02's run:**
  - (i) The R1–R10 rubric and §4's table reach the writer only as the variant's summary.
  - (ii) The question form can be copied from `input/q02.yaml`, so that part is covered.
  - (iii) The words the result must use, `by_kind ∈ {fact, procedure, decision, location, negative}` and `by_area ∈ {…}`, are only in the fixed brief's §8. The variant never names them, and the schema closes both objects (`writer-result.schema.json:11,22`). A writer that guesses, for example `{"code-location": 1}`, is refused 20.
  - (iv) A stop as the fixed brief's §9 describes it (`questions: 0`, no `stopped` word) ends 20 "fix_result", not 21.
- **Can this ticket fix it?** No:
  - Staging the fixed brief would be a fourth input, against S7's "exactly three", and against the walls' rule that a wall reads only its own brief.
  - Changing the variant is against F6 and DEC-1180 (2)'s "byte for byte".
  - This is a residual for the owner. Options:
    - (a) Run as approved. The question form comes from the input. Wrong key words cost a re-run (≤ $4; the `out/` is kept in the tar). `check_gold` checks the sources structurally, but R1/R3 quality is unchecked.
    - (b) Approve a variant version 2 that writes out §4, R1–R10, §7, the §8 words and §9 inside its own text, with no code change. Recommended.
    - (c) Stage the fixed brief: this needs a KPI change and a walls exception. Not recommended.
- Ordinary work: yes, because every run of this variant meets it.
- Consequence: other. It fails closed (refuses 20) or weakens the quality of the question; nothing undelivered reaches the set, and no work is lost because the `out/` is archived.
- Scope: out (the variant's bytes and the walls are the owner's, class O).
- Reversed by: a path through which the walled session can read `EXAMIN-writer.md` (it is in neither the wall nor the tree), or the §8 words being present in the variant or in `CLAUDE.md.tmpl`.

**P2 (S8, lead's point a): `out/conflicts.md` beside a good, unstopped result refuses 20.**
- **Where:** `indep_launch.py:1859-1860`.
- **The texts differ:** the KPI lists `conflicts.md` among the files `out/` may hold. The lead's interface and the variant's §5 ("only if you stop") narrow that to a stop.
- **Judgement:** acceptable. It fails closed, and it makes the operator look at a run that recorded a forbidden read before delivering anything. A stopped result never reaches the check (21 comes first).
- Ordinary work: no, because the writer reads only the variant, which says to write it only on a stop (the fixed brief's "even if you go on" is unreadable in the wall, P1).
- Consequence: other (refuses; the `out/` is in the tar).
- Scope: in.
- Reversed by: an owner reading of S8 that a `conflicts.md` beside a delivered fix must land.

**P3 (S11, lead's point b): the `--dry` usage line was folded into prose, and `--fix`/`--reason` are hidden from the option list.**
- **Where:** `indep_launch.py:17` and lines 21-22; `parse_args` 536-538.
- **Why:** W2-149 pins exactly 10 documented `python3 ` lines (`test_w2_149_indep_launch.py:381`) and the exact option set, and S12 requires that suite unchanged. So "gains one line" could only be met by replacing a line.
- **Effect on `--help`:** its epilog still prints the fix usage line (it is built from the docstring), and the `--dry` advice remains in prose and in the epilog. No other file quotes the removed line.
- Ordinary work: yes, because an operator reads `--help`.
- Consequence: other (documentation only).
- Scope: in.
- Reversed by: a runbook or test that needs the `--dry` example as a documented line.

**P4 (S9, lead's point c): a fix run's counts do not validate against the closed counts schema.**
- **Where:**
  - `finish` (477-478) logs "counts schema failed" on every fix run.
  - `counts_only` (2664-2665) refuses 17 on a fix run's `counts.json`, even though the run delivered.
- **Effect:** stdout's last line and `counts.json` still hold the object. An operator who uses `--counts-only`, as documented, could misread the 17 as a failure.
- **Fix:** an optional `fix` object in `indep-counts.schema.json`, by the lead's package. That file is outside the ticket's paths and under S12/F6.
- Ordinary work: yes.
- Consequence: other (fails closed for reading; nothing lost).
- Scope: out.
- Reversed by: the schema gaining `fix`.

**P5 (F5): a fix run that ends 22 (a trace counted) has replaced `hidden/<id>.yaml`.**
- **Where:** `indep_launch.py:2621` and 2651-2652. Its status is "delivered".
- **Why it is not a refusal:** this is W2-149's established meaning of 22 (`test_w2_149…:868-872`).
- **What the operator needs to know:** 22 is not a refusal. If the trace matters, they revert `hidden/<id>.yaml` from the tar's `replaced-hidden/`.
- Ordinary work: yes, because session traces are what the check exists to catch.
- Consequence: other (the delivery passed every check; the trace is reported; the old file is kept).
- Scope: out (existing behaviour).
- Reversed by: a decision that 22 must not deliver.

**P6 (F5): a SIGTERM or SIGHUP between `deliver_file`'s rename and the end of the run leaves q02 replaced while the counts say "rejected".**
- **Where:** `main` 2702-2712.
- **Effect:** the old file is still archived, because `st.replaced` is set before the rename.
- Ordinary work: no, because it needs a signal in a window of microseconds.
- Consequence: other.
- Scope: out.
- Reversed by: an ordinary path that interrupts there.

**P7 (S8): `out/<id>.yaml` is checked only for `id`.**
- **Effect:** a corrected question that changed its `category` or `commit`, or that has no `sources`, is delivered.
- **Why it is acceptable:** this is as the KPI and the interface state. `check_gold` is the bar after the run, and the old file is in the tar.
- Ordinary work: yes.
- Consequence: other (not open against the KPI; the gold check catches structure).
- Scope: out.
- Reversed by: a KPI line requiring a form check at delivery.

**P8 (S10): an audit logged after round 1 makes the fix run refuse 14 "last_audit" before anything is built.**
- **Where:** `last_audit(runs_indep)` (1153-1164) reads the global `<runs>/indep/AUDITS.log`. Stage 14 (2437-2438) refuses 14 "last_audit" if that commit is not in the repository.
- **Why it bites here:** the fix flow must run against the runs dir that holds round 1's records, for `round1_sample`. If an auditor run was logged there after EXAMIN's round 1, its commit is a workbench commit and not in EXAMIN's launch clone.
- **Not new:** this is existing behaviour, common to every flow. The planted cases have no `AUDITS.log`.
- Ordinary work: yes, if any audit ran since round 1.
- Consequence: other (fails closed, 14, nothing built), but it can block "run today".
- Scope: out.
- Reversed by: the last line of the real `AUDITS.log` being absent or naming a commit present in the launch clone. The CTO can check this without opening hidden content.

**Classification:** P1–P8 are all rows. None is in scope with ordinary work yes and fails open or loses work. No round.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": []},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "S7", "verdict": "pass", "findings": [{"id": "P1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S8", "verdict": "pass", "findings": [{"id": "P2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "P7", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S9", "verdict": "pass", "findings": [{"id": "P4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S10", "verdict": "pass", "findings": [{"id": "P1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "P8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S11", "verdict": "pass", "findings": [{"id": "P3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S12", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": []},
 {"kpi": "F5", "verdict": "pass", "findings": [{"id": "P5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "P6", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "F6", "verdict": "pass", "findings": []}
]}
```

**Overall: pass.**