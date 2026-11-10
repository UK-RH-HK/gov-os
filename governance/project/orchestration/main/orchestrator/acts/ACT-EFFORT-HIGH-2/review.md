## Round 1

Independent review of ACT-EFFORT-HIGH-2 under the operator's fixed reviewer brief (`reviewer-brief.md`, sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`). The manifest's sha256 is `0be009e84c86c22c8f1e62ff63289912cf16d225f8207b22285d76d0980d0ac8`, computed by the reviewer. The reviewer re-ran the ACT in its own clone of `w2/integrate` as cwd, with planted HOMEs, the agent's clean environment, and the operator's own `validate_manifest`, `path_rule`, `classify` and `check_ok`: 52 checks, 0 failures. The live `~/.claude/settings.json` was only read (`bc0dde042f00`).

**Check 1, the touched list and the path rule: pass.**
- `touched` is exactly `home:.claude/settings.json`, before `bc0dde042f00…` and after `2a1c84693189…`, agreeing with `list.txt` and `files`.
- In the dry-run shape, `apply` changes only that file in HOME, nothing in the clone and no crontab.
- `apply.sh` reaches the file through `${HOME:?}` and the bundle through its own folder. It names neither the live repository nor the real HOME and has no `cd` to either. The two checks use `$HOME` / `os.environ["HOME"]`. The operator's `path_rule` passes against the live paths.

**Check 2, the undo is tested: pass.**
- Undo restores the frozen before byte for byte, and the mode, and only from the ACT's own after.
- It refuses a later change (exit 3), a link, and a tampered before copy (exit 4). A second undo is harmless.
- Rehearsal steps 6 and 11 show this, and the reviewer's run repeats it.

**Check 3, the rehearsal is real: pass (F1).** The log ends `failures: 0`, hashes as the manifest states, and is the run of this `apply.sh`: same messages, script mtime 16:14 before the log's 16:16, tampering on a copy.

**Check 4, the checks are right: pass.** Both checks are `exit 0`, `count null`.
- Check 0 exits 1 on the before copy and 0 on the after copy.
- Check 1 exits 0 on both.
- The rehearsal printed the same, and the reviewer's run from the clone repeats it.

**Check 5, the class: (b).**
- The `settings` row (`home:.claude/settings*.json`) allows only additions to `permissions.deny` as (a). A changed `effortLevel` and a new `modelSettings` entry fall to `else: b`.
- `act_class.classify` gives (b), row `settings`, no hits. The claim is (b).
- It is not (O): the undo is tested, and it touches none of the operator's files, no sudo, push, tag or Windows step.

**Check 6, the guard replay: pass, not applicable.** There is no path-map or deny-list addition, so `replay_refused` is empty.

**Apart from the brief's checks:**
- **apply.sh decides by sha256 alone.**
  - A regular file that hashes as the frozen before is `before`; one that hashes as the frozen after is `applied`; anything else is `other` and refused (exit 3) by `check`, `apply` and `undo`, leaving the file untouched.
  - The reviewer showed this for a one-byte drift with top-level still `xhigh`, CRLF line endings, -1's after, a missing file (never created) and a directory.
  - A link is refused before any hash, and HOME unset is refused (exit 1).
- **Each model under DEC-1119 (4) and DEC-1120,** for a session started without `--effort`, as read from Claude Code 2.1.318:
  - **Opus 5.5:** high, unchanged, from its own `modelSettings` entry.
  - **Sonnet 5.5:** from its model default to high, through the new entry. This reaches DEC-1119 (4).
  - **Haiku 5.5:** untouched, at its model default. It is not on the legacy list, so the top-level key never applied to it. This matches DEC-1120 (Haiku, "effort as needed", set per spawn).
  - **Older models on the legacy list** (Fable 5, Fable 5.1, Opus 5, Sonnet 5, Opus 4.x, Haiku 4.5 and the rest) and unparseable model ids: from `xhigh` to high through the top-level key. All launch pins are unpinned on this install.
  - No other settings layer, and no org override, sets an effort.
  - Residual: the key `claude-sonnet-5-5` is assumed to match Claude Code's normalisation of the model id, which `/effort` also uses to write its keys. It was not shown in a running Sonnet session.

### F1: the rehearsal ran in planted HOMEs with no clone as its cwd
- **KPI:** check 3.
- **Scope:** in.
- **ordinary_work:** no.
- **Consequence:** other. `apply.sh` never reads its cwd or any repository path, so a clone as cwd cannot change the result. The reviewer's re-run with its own clone as cwd gave the same results, and the agent's G8 clones the repository itself.
- **Evidence:**
  - The log's header names only planted HOMEs and invokes `apply.sh` by its bundle path.
  - The log does not record apply.sh's sha256 or the cwd.
  - The reviewer's run (cwd = clone of `w2/integrate` at `3ebaa78b`): same outputs, and the clone's `git status --porcelain --ignored` is unchanged.
- **Fix:** none needed for this bundle. For later ACTs, rehearse with a clone as cwd and log the cwd and apply.sh's sha256.

### F2: the hand run's optional backup is a file not on the touched list
- **KPI:** check 1.
- **Scope:** out. The agent route cannot set the variable: `clean_env` passes only PATH, LANG, LC_ALL, USER, LOGNAME, TMPDIR, TZ and HOME, and the reviewer checked that.
- **ordinary_work:** no (on the agent route).
- **Consequence:** other. It adds a copy of the original beside the file; it changes no existing file and loses nothing.
- **Evidence:** with `ACT_BACKUP_BESIDE=1`, `apply` creates `settings.json.bak-<UTC stamp>-ACT-EFFORT-HIGH-2` in `~/.claude/`. The package's by-hand message sets it on purpose and says the backup is the operator's to remove.
- **Fix:** none needed. A by-hand operator removes the backup after the check.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": [{"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": []}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}], "manifest_sha256": "0be009e84c86c22c8f1e62ff63289912cf16d225f8207b22285d76d0980d0ac8", "class": "b", "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author", "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a", "time": "2026-11-10T16:59:44+00:00", "replay_refused": []}
```
