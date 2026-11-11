## Round 1

Reviewer: independent-auditor, claude -p session (round 1), started by the CTO (launch_worker.sh, DAEO-r30l); not the author (a1ae8de0f141ec0dc). Brief sha256 e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a, checked. Manifest sha256 computed: e567660a69685d102f3eb860e89d09cb738516e69b5cac6a18d8749db9cf0779. Every file hashes as the manifest lists it. The live `.claude/settings.local.json` is the frozen before (d715292711a2).

### The six checks
1. **Touched list and path rule: pass.** In a clone of `w2/integrate` with HOME planted, `apply.sh apply` changed exactly `.claude/settings.local.json` (before d71529…, after acb46a…, mode 644). Nothing else in the clone changed (git status and a newer-than scan), HOME holds 0 files, and `crontab -l` is unchanged. The before/after diff is the eight entries and two commas, and the parsed rest is identical. apply.sh is cwd-relative and reaches the bundle through `dirname "${BASH_SOURCE[0]}"`. The operator's `path_rule` and `validate_manifest` both return None.
2. **Undo tested: pass.** `undo` restored the file byte for byte (cmp against before/), and a second undo is harmless. The log shows the same (A10, A10b, A11).
3. **Rehearsal real: fail (F1).** The log is a run of this apply.sh: the drafts copy it names hashes f89091…, the same as the bundle's. Its checks match my replay. It does not end with `failures: 0`.
4. **Checks right: pass.** Both checks exit 0 after apply, as the manifest says (count null). Check 0 exits 1 on the before file, so it tests the change.
5. **Class: (b).** The `settings` row allows only added `permissions.deny` as (a). Allow rules alter a control. `act_class.classify` agrees: b, row settings, no hits. F2 is filed here.
6. **Guard replay: pass.** The ACT adds CLI permission rules, not guard path-map or deny-list entries. The six CLI deny rules turn no allowed call into a refused one: every form-A call before the ACT was an ask (queue: 23 Write and 4 Read rows under `/tmp/gov-os-emg-*`), and no queue row ever names a key, pem or env file there. `replay_refused` is [].

### The CTO's four questions
**(1) Wider than the form?**
- `//tmp/…` is Claude Code's absolute form; the existing `//home/…` deny rules show it resolves. This session's sandbox read-deny list carries `/home/usain/gov-os-eval/…/memory-retrieval/hidden` and the other two from exactly that form.
- The `*` sits inside one folder name. Rehearsal B2a shows another `/tmp` folder still asks.
- The sets root (`~/gov-os-eval`), held-out material and the hidden halves are not under `/tmp`, and none of the eight existing `gov-os-emg-*` folders links there. The one link, in gov-os-emg-sweep, is pytest's `current` link inside its own folder.
- But every `gov-os-emg-*` folder is by construction another session's work (the CTO's helpers'). For the CTO's session that is the form. For launched workers it is not: see F2.

**(2) Reaching launched workers: a fail-open path?**
- Not for the read walls of DEC-1082 (3) and DEC-1097. The guard judges every Read and Bash call by path (rule 2b), and the three hidden folders also carry CLI deny rules.
- Not new for reads in general. A worker's Bash can already read `/tmp`: the sandbox's read list is deny-only and the user-level `Bash(*)` allows it.
- **Yes for DEC-820's write wall** (writes stay inside the ticket's paths): F2.

**(3) Decided by sha256 alone?** Yes. The state is before, applied or other, by the file's sha256 alone. Other (drift, missing or a link) is refused with exit 3 and nothing is touched; I re-ran the one-byte drift in the clone. The frozen copies are hash-checked before use (exit 4), apply is atomic, and undo runs only from the after hash.

**(4) Do the six denies hold against the allow?** Yes, as rehearsed in B2k with headless sessions: Write and Read of `.key`, a sub-folder `.pem`, `.env` and `.env.local` are all denied, while an ordinary file in the same folder writes. Claude Code ranks deny above allow. Names outside the six (for example `id_rsa` or `*.p12`) are not covered by the CLI; the guard's rule 3 still refuses reads of secrets and keys by name.

### Findings
**F1. The rehearsal log does not end with `failures: 0`.**
- KPI: check 3. Scope: in. ordinary_work: yes. Consequence: other. The operator refuses at G3; nothing fails open.
- Evidence: the last line of rehearsal.log is `REHEARSAL PASS` (62 `ok` lines, 0 failures). `operator_run.py:430-434` matches `^failures:\s*(\d+)$` on the last non-blank line and otherwise raises `Refused("G3", "the rehearsal log does not end with 'failures: <n>'")`. The rehearsal's A16 ran `validate_manifest` and the path rule, not G3.
- Fix: rehearse.py ends the log with `failures: 0` (the count of failed checks). Then re-seal with `build.py --seal`, which gives a new rehearsal sha, a new manifest sha and a new owner line.

**F2. The `Edit` allow reaches every launched worker's file tools, and nothing then refuses a worker's write into the CTO helpers' scratch folders. Package §8 item 1 says the opposite.**
- KPI: check 5 (the loosened control that the owner approves). Scope: in (CTO question 2). ordinary_work: yes. Consequence: fails open.
- Evidence, link by link:
  - (a) A session in a worktree reads the main tree's untracked settings.local.json. The package measured this (explore4.py, CLI 2.1.322). This session (a launched worker in W2-20) corroborates it: its sandbox read-deny list holds that file's three `Read(//home/usain/gov-os-eval/…)` deny rules.
  - (b) `Edit(//tmp/gov-os-emg-*/**)` lets the Write and Edit tools write there headless with no prompt (rehearsal B1).
  - (c) A worker's `--settings` (`launcher.py` `build_settings`) has no rule for `/tmp`. Its sandbox `allowWrite` binds Bash only, not the file tools.
  - (d) The wired guard (`.claude/hooks/pretooluse.py`) keeps rules 1, 2/2b/2c/2d, 3, 4 and 5. None refuses an engineer's, test designer's or researcher's file-tool write into `/tmp/gov-os-emg-*`, and rule 5 explicitly lets reviewers write `/tmp`.
  - (e) Those folders hold scripts the CTO's helpers run: `/tmp/gov-os-emg-checks/run_check.sh`, `/tmp/gov-os-emg-closes/run_accept.sh` and `/tmp/gov-os-emg-repin5/chain.sh`. The queue's form-A rows are exactly such writes.
  - (f) Launched workers are told to read EMG-common.md, whose line 22 names `TMPDIR=/tmp/gov-os-emg-<your short name>`, so ordinary worker work can reach these folders.
- Consequence: before the ACT, such a write asked and was refused headless. After it, a sandboxed worker's Write tool can rewrite a script that the CTO's unsandboxed session later runs, with no prompt and no guard rule.
- Not measured: whether the CLI also merges this `Edit` allow into a worker's bubblewrap write list. The launcher's own docstrings note that a pattern in an `Edit` rule is unmeasured (P-W2-58-1 measured `Read` rules). That merge would open the folders to the worker's Bash as well.
- The `Read` rule adds no new reach for workers (see question 2).
- Fix, any one, then correct §8 item 1 and measure in a launched worker against stand-in folders:
  - (i) The launcher adds `Edit(//tmp/gov-os-emg-*/**)` to every worker's `--settings` `permissions.deny`. Deny wins over the main file's allow. This is a ticket on `src/gov/launch/launcher.py`.
  - (ii) A guard rule refuses non-orchestrator file-tool writes under `/tmp/gov-os-emg-*`. This is a class (b) ACT on `.claude/hooks/`.
  - (iii) Ship only the `Read` rule now, and have helpers write in their session scratchpad (package §8 item 6) until (i) or (ii) lands.

**F3. Monitor loops over helper folders now run unprompted, and the guard never reads Monitor commands.**
- KPI: check 5. Scope: out (disclosed in package §8 item 2). ordinary_work: no. Consequence: other.
- Evidence: rehearsal B3, information line. The guard judges the command of a Bash call only (package §1 C, `pretooluse.py`).
- Fix: none in this ACT. Package §9 item 1 (the waiting line) and item 2 (LEAD-w2-common line 103) carry it.

**F4. The launcher's worker-settings check reads only the worktree's settings, not the main tree's settings.local.json that worker sessions also load.**
- KPI: check 5. Scope: out (already there before this ACT; package §9 item 4). ordinary_work: no. Consequence: other.
- Evidence: `launcher.py` `_check_repo_settings` (around lines 286-305) loops over `REPO_SETTINGS` under the worktree `root`. Its refusals (a sandbox key, additionalDirectories, bypass mode) never see the main tree's file, which today carries two `additionalDirectories`.
- Fix: an engineer ticket that checks the main tree's settings.local.json as well, and measures what the CLI merges from it.

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []},
          {"kpi": "2", "verdict": "pass", "findings": []},
          {"kpi": "3", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
          {"kpi": "4", "verdict": "pass", "findings": []},
          {"kpi": "5", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
                                                     {"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "other"},
                                                     {"id": "F4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
          {"kpi": "6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "e567660a69685d102f3eb860e89d09cb738516e69b5cac6a18d8749db9cf0779",
 "class": "b",
 "reviewer": "independent-auditor, claude -p session (round 1) started by the CTO (launch_worker.sh, DAEO-r30l); not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-11T14:09:32+00:00",
 "replay_refused": []}
```
