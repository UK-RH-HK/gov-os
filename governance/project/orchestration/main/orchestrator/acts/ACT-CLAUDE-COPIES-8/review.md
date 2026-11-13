# ACT-CLAUDE-COPIES-8 (default form): the ACT review (OPERATOR-AGENT-1 §3, G4), with the source commit b88a76172

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session, not the ACT's author. Worked under the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`, sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, the hash in the install's `APPROVED`) and `governance/project/briefs/JUDGEMENT.md`.
- Manifest sha256: `e2fc98150aa1d19165d8b0da3e5ec57dc65c69d5de55924ff8f6aefa7f4e0dae` (re-hashed). The with-sources form was not reviewed.
- Reviewed on integrate `02873772c` (it moved from `c0918f144` during the review by one `.tickets/` commit, which touches no bundle path).
- All runs in fresh `--no-hardlinks` clones under `/tmp/claude-1000/rev-copies78-430190/`, HOME planted at an empty folder, every pytest through `heavy_slot.sh` with `-p no:cacheprovider` and TMPDIR outside the repository. Refused reads: 0.

task: ACT-CLAUDE-COPIES-8 (DAEO-sdxk; W2-56 DAEO-wnnz closed)
decisions: DEC-1163 (1), DEC-1052, DEC-315, DEC-1156 (7), DEC-1057, DEC-1104, DEC-861, DEC-801, DEC-808, DEC-1010, DEC-1014, CAP-33

Classification: 0 blocking; F1 to F5 are rows (consequence other). Integrate carries 4 reds after the ACT, none brought by it.

## The source commit b88a76172 (the owner's exception, DEC-1163 (1))
- **Exactly one line deleted in each of the three files, nothing else:** the diff is three one-line deletions of the same line, `- Run \`gov accept\` for a ticket whose suites need the code index outside the sandbox, until W2-56 [DEC-1052].` The after hashes are the owner's: `role-lead.md` `4e8e46b0` to `c731503e`, `role-cto.md` `013d4d85` to `dbcc9d8c`, `template/.rulesync/subagents/orchestrator.md` `ef15ea7d` to `5db8f0cb`. Integrate's head still holds these bytes.
- **W2-56 is closed:** `1c02c490f` sets DAEO-wnnz `status: closed`, with the FULL close review passing 21 of 21 lines.
- **The line's purpose is spent:** W2-56's probe `docs/probes/DAEO-wnnz/PR-DAEO-wnnz.md` S13 (rows 11 and gate (a) evidence 3) records a code-graph suite and `gov check` running inside a real sandboxed session, which makes the old-launch-form fallback unnecessary. `gov rebuild` inside the sandbox stays a Wave 3 row, but `gov accept` does not call it (its runner has no rebuild or index call). Leads still run without a sandbox (DEC-1098 (4), DEC-1112 (1)), so the line had nothing left to tell a lead.
- **No other "until <ticket>" line is left** in `template/governance/kernel/` (templates, roles, skills) or `template/.rulesync/`, searched with `gov brief`'s own pattern. After this ACT, `.claude/templates/`, `.claude/agents/` and `.rulesync/` carry none either (F4 names the one left in a project brief).
- The commit is `Role: orchestrator`, `Task: DAEO-sdxk`, with a `Decided-by: owner (chat, …)` trailer recording the owner's chat decision (DEC-861), and the register's DEC-1163 (1) names it. See F2 for the landing check.

## Per check
1. **Touched list, generation and path rule: PASS.**
   - The bundle's file hashes equal the manifest's; `list.txt` equals `touched`; no unnamed file in the bundle. The four `before/` files are integrate's bytes today.
   - Each before/after pair differs by exactly that one line, deleted.
   - The reviewer's own generation from integrate's sources (`compose()` for every root role source, rulesync 24.0.0 with portability's GENERATE arguments into a fresh folder, `--write-templates .claude/templates`) changes exactly the four touched files, byte-equal to `after/`. Rulesync's only other differing output is `.claude/settings.json`, not written, as in COPIES-5 and -6. After that, portability exits 0 with no findings.
   - `apply.sh` reaches its bundle through its own folder and writes under `$PWD`; neither it nor either check names a live repository or HOME path or `cd`s to one.
2. **Undo: PASS.** In the clone, `apply` changes exactly the four files and `undo` restores them byte for byte, leaving a clean tree. The rehearsal log shows the undo, the re-apply, and the commit, undo, commit sequence ending in an empty diff.
3. **Rehearsal: PASS.** A real run of this `apply.sh` in clones with a planted HOME, ending `failures: 0`, including integrate's then-head `4be656e70` (F1).
4. **Checks: PASS.**
   - Check 1 (4 files): exit 1 before the apply, exit 0 after (4 OK lines).
   - Check 2 (36 files: kernel role files, the two kernel templates after the deletion, the template sources, COPIES-6's other copies): exit 0 before and after on today's head (36 OK lines).
   - `apply.sh check` refuses a moved target (exit 3), a wrong working folder (exit 3) and a second apply (exit 3); an unknown step exits 2. The rehearsal's out-of-order trees are refused at G7 or G8.
5. **Class: (b).** The operator's `act_class`, run read-only on the bundle, gives class `b` with no hits. Its rows are `agents-skills-kernel` for `.claude/agents/orchestrator.md`, `claude-rest` for the two `.claude/templates/` copies, and `rulesync-other` for `.rulesync/subagents/orchestrator.md`, all (b).
6. **Guard replay: not applicable.** No path-map or deny entry is added; `replay_refused` is empty.

**The suites on integrate `02873772c` with the bundle applied and committed (reviewer's runs):**
- W2-153: 66 passed.
- `tests/unit/adapters`: 102 passed (40 deselected).
- W1-33: 112 passed.
- W1-38: 42 passed (159 deselected).
- `tests/unit/launch`: 220 passed.
- `tests/unit/brief`: 25 passed.
- **W2-152: 1 failed, 66 passed.**
- **W2-128: 3 failed, 118 passed.**

The four reds, and whose they are:
- `W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead]` and `[role-cto]`: row 8 requires the deleted line in the kernel templates, so these are red from b88a76172, not from the copies. The fix is the decided-behaviour test revision; the CTO routes it (DEC-1156 (7)).
- `W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes`: it runs `gov accept W2-128`, so it is red while W2-128 is.
- **Not named by the builder:** `W2-128/test_w2_128_schemas.py::test_s10_every_existing_ticket_stays_valid`. It is red because `.tickets/DAEO-5y8d.md` (W2-182, filed in `3ec28e859`, after the builder's runs on `4be656e70`) has a non-goal line that YAML reads as a mapping: `- not the 2 timing cases … (W2-112, W2-145 S4): environment, DEC-1159 (1)`. That is integrate's own red and the CTO's to fix, and it keeps W2-152 S10 red even after row 8 is revised (F3).

The bundle makes W2-153's two and the adapters' two reds green; it brings no new red.

## Findings (none blocks)
- **F1** (check 3, scope in): the rehearsal's gated runs and its head run were measured at `4be656e70`. Integrate is now `02873772c`, and the commits between touch none of the 4 targets or 36 checked files; the reviewer's apply on today's head gives the same result.
  - Ordinary work: yes, because integrate moves after a bundle is built.
  - Consequence: other.
  - What would reverse it: any target or check-2 file differing at apply time.
- **F2** (the source commit, scope in): b88a76172 touches the (b) control path `template/governance/kernel/templates/**` as a commit outside a ticket, with `Role: orchestrator` and no `Act:`. The operator's own landing check, run read-only on that one commit, flags it as a P1 (`agents-skills-kernel`, "neither Role: owner nor Role: operator with Act:"). The owner approved exactly these bytes (DEC-1163 (1)), so the flag is expected. Whoever reads the inbox should close it against DEC-1163 (1) and not take it for a stray write.
  - Ordinary work: yes, because the landing selection reads every first-parent commit.
  - Consequence: other (it fails closed: a flag, no write).
  - What would reverse it: the landing check exempting this commit, or an inbox item already closed against DEC-1163 (1).
- **F3** (suites, scope out): integrate has a fourth red that neither the package nor the rehearsal names: W2-128's `test_s10_every_existing_ticket_stays_valid`, caused by `.tickets/DAEO-5y8d.md` line 50. Because W2-152 S10 runs `gov accept W2-128`, it stays red until both row 8 is revised and that line is quoted.
  - Ordinary work: yes, because an unquoted colon in a ticket list item is an ordinary slip.
  - Consequence: other.
  - What would reverse it: the ticket line quoted (or the schema accepting it) and W2-128 S10 green on integrate.
- **F4** (outside the bundle, scope out): `governance/project/briefs/LEAD-w2-common.md:97` still tells a lead to start a code-graph worker "in the old launch form … until W2-56". It is the superseded common-brief form (`release_lead.sh` refuses briefs built from it, and `gov brief` does not scan it), and `launch_worker.sh` starts every worker through `gov launch`.
  - Ordinary work: no, because the brief form that carries it is refused at release.
  - Consequence: other.
  - What would reverse it: a live lead brief still built from LEAD-w2-common.
- **F5** (package text, scope in): the package's §0 gives as its reason that `gov brief` refuses every lead brief while the line stands. `gov brief` scans the kernel templates, which b88a76172 already fixed. What the four copies still affect is the system prompt the launcher gives each lead (`.claude/templates/role-lead.md`) and the orchestrator agent definition. So until this ACT lands, a launched lead still reads the stale line. That is harmless, since leads run without a sandbox, but the reason as written is out of date.
  - Ordinary work: yes.
  - Consequence: other.
  - What would reverse it: `gov brief` reading `.claude/templates/` rather than the kernel.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": [{"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "e2fc98150aa1d19165d8b0da3e5ec57dc65c69d5de55924ff8f6aefa7f4e0dae",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T12:30:00+00:00",
 "replay_refused": []}
```
