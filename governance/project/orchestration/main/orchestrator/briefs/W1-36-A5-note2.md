**Resume note (second start of W1-36; read it before the rest, and where it differs from the rest, it holds).** Keep `.gov-runtime/scratch/lead/CHECKPOINT.md` current.

## The first start's result (`e0572d12`) is accepted except for its two check declarations and one addition to the audit skill

The four skills and the 57 cases stand and are not redone. The two declarations (`skill-regression-b1.yaml`, `audit-reproducibility.yaml`) call modules that did not exist and fall back to exit 0 when the module is absent. A check that can succeed without measuring is not merged (DEC-439, DEC-425). The validators now exist on `w1/integrate` (merge `54b8a404`):

- `python3 -m gov.check.skill_validator (folders or files)`: a folder is searched at every depth for `SKILL.md`; exit 0 only when at least one file was validated and none has a finding.
- `python3 -m gov.check.audit_validator (files or folders)`: validates audit reports in the form of **DEC-441** (read it in `docs/DECISION_REGISTER.md` after the merge-back: frontmatter `milestone`, `commit` as a hexadecimal commit id, `pack_sha256`; one table `item | class | evidence`; the six classes of DEC-070; an `OK` row cites at least one path; "none" is `-`; every cited path exists at the cited commit). A folder with no report, no argument, an unreadable file: "unmeasured", exit 1, never green.

In this order:

1. **Merge-back.** Merge `w1/integrate` in one committing command with the trailers `Task: DAEO-skiy` and `Role: orchestrator` (never `--no-commit`, DEC-436). Before it, the overlap check of the steps below (DEC-412 alignment by a launched designer if a shared test file is changed on both sides). After it, `git diff --stat w1/integrate HEAD -- tests/acceptance` lists only this ticket's own files and its own lines in shared W1-07 files.
2. **Test designer** (fresh, launched): cases, red now, that
   (a) each declaration's command runs the generic validator of W1-26 and is nothing that can succeed without it (no `||`, no fallback, no test for the module's presence);
   (b) through `gov check` on a temporary project built from the template: the skill-regression family is green with this ticket's four skills as they are and red when one is broken or missing;
   (c) the audit-reproducibility family: green on a project holding a valid report in DEC-441's form; red on a report with a commit that does not resolve, a row with an unknown class, an `OK` row without evidence, an evidence path absent at the cited commit; and **for a project with no audit report yet** the check is not green (the validator says "unmeasured" and exits 1, which `gov check` shows as red for a hard-block check). The designer settles from the sources (CAP-38 item b with its cover, CAP-47, DEC-088, DEC-285, W1-26's README on tiers and severities) **in which folder a project's audit reports live** (W1-43 will write this wave's under `docs/audit/wave-1/`), **and which tier and severity the declaration carries**, given that a new project has no report before its first milestone: if the sources make a project with no audit yet red at every `gov check`, say so plainly in the return with the lines read; if they leave it open, return it as a package, early, with a recommendation, and do not guess;
   (d) the audit skill's text states the report's form of DEC-441 (the three frontmatter fields, the table's three columns, the six classes, how "no evidence" is written), within the skill's size limits.
   The designer also settles where the paths in the two commands point in an installed project (the skills do not live under `template/` there; read how W1-26's and W1-25's declarations name project paths and where W1-04's installer puts the kernel's skills); if one declaration cannot work both here and in an installed project, that is a package.
3. **Product-spec worker** (fresh, launched): changes the two declarations and the audit skill only (its version rises with the change, DEC-linked as W1-26's `skill-version` check demands: read that check's rule first).
4. **Verify:** this ticket's suite, `tests/acceptance/W1-26`, `W1-07`, `tests/unit` to their ends; the first start's latency failures (W1-05 hook p95, W1-19 warm query) each alone, and say each occurrence (DEC-372). Run the skill validator and `gov check --json` in this worktree and give the two families' entries.
5. No review round (STANDARD). Return as the steps below say; repeat the first start's residuals and metrics in full. Name again what belongs in W1-42's brief (the live audit scenario).

W1-35 runs the same repair for `skill-regression-a.yaml` on its own branch at the same time; the two branches do not touch each other's files. If the designer finds that both tickets' declarations share one family and one must not shadow the other, say what `gov check` does with two checks in one family (W1-26's README).

---

