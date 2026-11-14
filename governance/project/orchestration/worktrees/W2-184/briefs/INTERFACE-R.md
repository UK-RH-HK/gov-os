## 10. R1-R3 (reopened 2026-11-14 by the CTO, DEC-1180 (4); the narrow check's F1-F3, `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`) [stated by the ticket lead before the pair starts, DEC-1052]

These amend 7.2a, 8 and 5.1a. Nothing refused before becomes allowed. Every other rule of sections 1-9 stands.

10.1 **R1: a lead takes none of the three options (amends 7.2a's last sentence).** `gov launch <lead role> <ticket>`
(a lead role is `orchestrator` or `lead`, `gov.launch.launcher.LEAD_ROLES`) given any of `--reason`, `--trial` or
`--owner-named` before `--` (each alone, or several; an empty value counts as given) is refused by the CLI with **exit
2**, before the launcher is called: nothing starts, no launch record is written, the resource gate is not consulted
and no plan-override line is logged. The message goes to stderr, names each option given, and says that a lead launch
takes none of `--reason`, `--trial` and `--owner-named` (the words "a lead" and the option names appear in it). A lead
launch without them is unchanged. A worker launch with them is unchanged (7.2a). The same three written after `--`
are CLI arguments, not these options: a lead launch with them after `--` is judged by the existing passthrough checks,
as before. `--plan` is unchanged. Also, `gov.launch.launcher.launch(...)` called directly with a lead role and any of
`reason`, `trial`, `owner_named` not `None` refuses with LAUNCH_REFUSED (exit 1) before anything starts (a second
fence; the CLI case is the KPI's).

10.2 **R2: the launch record is written atomically (amends 8; `gov.launch.record.write(records, record)`).** The
record's bytes are written, flushed and fsynced to a temporary file in the same folder whose name begins with `.` and
ends with `.tmp` (form: `.<session_id>.<unique part>.tmp`), so that no reader of `*.json` takes it as a record; then
it is hard-linked to the final name `<session_id>.json`, which fails if a file of that name exists (no overwrite);
then the temporary file is removed. So at no moment is there a final-name file that is empty or partial: a launch
killed at any point leaves either no `<session_id>.json` or a whole one (a leftover `.tmp` file at most). If the final
name exists, `write` refuses as today (LAUNCH_REFUSED, "a launch record of the session <id> is already there") and
removes its temporary file. Any `OSError` (the create, the write, the fsync, the link other than "exists") refuses as
today ("the launch record cannot be written in <folder>") and leaves no final-name file and no temporary file. Readers:
a file in the record folder that does not match `*.json` (a leftover temporary file included) is not a record and is
never read or refused on. A final-name `*.json` record that is not JSON still refuses a launch that reads the folder,
naming the file (5.1a, 6.1, P-td5-1 unchanged). Two writers of the same session id: exactly one final record (the
winner's whole bytes); the other is refused as already there.

10.3 **R3: every root's copy is read (revises 5.1a's P-td5-2).** The probe records are still found under the launch
root and every root the ticket's launch records name (5.1a). For one root-relative path (`docs/probes/<name>/...`)
found under several roots: copies with identical bytes are one copy; copies with different bytes are each read. Each
copy that refuses (front matter not YAML, a verdict block not of the form) refuses the launch, naming the file as
today. The path is still **one review** for 5.2: (a) it holds a fail-open finding if **any** of its copies does; (b)
it counts as one failed record if **any** of its copies has `judgement` fail or failed (never more than one per path,
so two differing copies of one failed record are not two failed reviews). The promotion's `record` is the
root-relative path as in 5.2, in sorted path order over the set of paths. So a stale launch-root copy without the
fail-open finding and a newer copy under the ticket worktree with it: promoted, `promotion.reason` `a fail-open
finding`, `promotion.record` the root-relative path. With one copy, or identical copies, the result is as before.
