# Review of E3 (ACT-GUARD-FIX-4), DAEO-sdxk — the independent reviewer's record, transcribed by the CTO

The reviewer (independent-auditor, Sonnet, read-only; record returned, not written) reviewed
`drafts/act-guard-fix-4/` (the candidate `pretooluse.py` and `bash_writes.py`, `test_guard_fix_4.py`, the new
`guard4_check.py`, `settings_rm_ask.py`, `ACT-GUARD-FIX-4.md`) on 2026-11-03, judged by
`governance/project/briefs/JUDGEMENT.md`. Transcribed in substance; nothing added.

Evidence (the reviewer's): the ACT's hashes and the live blobs `52ab9bc647b1`, `ceb6fdefbb5f` match; the diff applies
to today's blobs and gives byte-identical files; rules 2, 3 and 4 untouched. `test_guard_fix_4.py` 451 passed;
`guard4_check.py` PASS. Rules 1 and 5, resolving targets (Write, Edit, MultiEdit, redirects, `>>`, `cp`, `mv`, `tee`,
`sed -i`, `touch`, `install`, `dd`, `ln -s`, `rsync`, `truncate`, `git checkout`, `cd tests/acceptance && …`): all
refused; the designer's write passed. Reviews: records under `reviews/` (and `mkdir -p reviews && …`) passed; escapes
(`reviews/../briefs/`, `../tools/land.py`, `src`, `docs`, `.claude`, `.tickets`, `rm -rf reviews`, `mv reviews`)
refused. `rm`: the root, `.`, `*`, `.git`, tracked files, `~`, `$HOME`, `/`, `/etc`, `/tmp`, wrappers (`\rm`, `/bin/rm`,
`command rm`, `sudo rm`, `bash -c`, heredocs) and the worktrees' and runs' folders refused with a reason; scratch,
`/tmp/x`, `/dev/shm` locks, a worktree's own files, `mktemp` folders, untracked main-tree files, caches passed. Each
decision 0.05-0.10 s; malformed input fails closed. `settings_rm_ask.py`: apply, undo and `cmp` byte-identical on a
file in the owner's format; apply removed only the three entries.

## Findings
- **F1** (out of scope, low, pre-existing): a literal write to ANOTHER tree's `tests/acceptance/` is allowed. Ordinary
  work: no, because a session in one tree rarely writes another tree's acceptance tests by literal path. Consequence:
  fails open, backstopped at landing (G-1). A Wave 3 row.
- **F2** (in scope, low to medium): rare `rm` holes (`xargs rm`, `git clean -fdx`, `git rm -rf .`, `unlink`, `mv`,
  `rm "$(echo ~)"`, loops, `rm -rf -- "$@"`); children of the fenced folders pass; an unset variable inside a longer
  path judged only against the holder folders. Ordinary work: no, because the forms need pipes or loops over `rm` or a
  deliberate wipe. Consequence: fails open on rare forms; loses only untracked scratch. A Wave 3 row.
- **F3** (in scope, by design): honest deletes outside the project (`/var/tmp/x`, `~/.cache/x`) are refused with a
  reason. Ordinary work: yes, rarely. Consequence: other.
- **F4** (in scope, low): `settings_rm_ask.py` rewrites the whole file with `json.dumps(indent=2)`; a compact file
  would be reformatted (the owner's real file measured as a 3-line diff). Ordinary work: no. Consequence: other.
- **F5** (in scope, low): `undo` overwrites with the backup, losing settings added since the apply; a stale backup
  blocks a re-apply. Ordinary work: yes, rarely. Consequence: other.
- **F6** (in scope, low): the hooks are copied before the check, not swapped atomically; removing the `ask` entries
  stops the prompt only if `rm` is otherwise permitted. Ordinary work: no. Consequence: other.
- **F7** (in scope): an unreadable glob makes the hook exit 2 (fails closed). Ordinary work: no. Consequence: other.

```verdict
{"kpis": [{"kpi": "rules-1-5", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "rm", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "reviews-records", "verdict": "pass", "findings": []}, {"kpi": "ACT", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
