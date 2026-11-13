# P-ACT-SPLIT: which ACTs stay with the owner's operator, and which the CTO runs on the owner's approval (P1, short form)

By the CTO (session 33b3628c), 2026-11-03, at the owner's request. **DECIDED: approved as written (owner,
2026-11-03, in the chat); ACT-G14 stays with the operator, as (a).**
Basis: question 4 (less of the owner's time on ACTs) and question 2 (no change runs without its checks, rollback and
rehearsal, so nothing is lost).

## The split
**(a) The operator's ACTs.** Anything that changes how the CTO itself is judged or what its session runs on:
- the guard: `.claude/hooks/**`, `role_paths` and the guard's rules;
- `.claude/` settings (permissions, allow lists, the quiet-hours hook) and the generated role files and skills;
- the pinned gov (`~/.local/bin/gov`, `~/.local/share/gov-os/pin-*`): every re-pin;
- the sentinel and dead-man's switch code (they watch the CTO);
- what the CTO's session runs on: WSL, `.wslconfig`, Windows, the Claude app and its settings.

**(b) The CTO's ACTs, on the owner's approval by ping reply.** A machine-level change that has a tested rollback:
- the crontab: the nightly's and the sweep's lines un-commented at the lift, and the dispatcher's line pointed at its
  committed copy (DEC-1010 item 6);
- the repository's servers' configuration beyond the approved restart classes (the embedders' `OLLAMA_*` settings and
  caps, the reranker service's settings);
- the CTO's watchers and samplers when they change (not only restart);
- `~/.config/gov-os*` and `~/.cache/gov-os` settings files.

**The rule that sorts a new ACT:** it is (b) only if it is outside (a), it has a rollback that the rehearsal ran, and
nothing in it is on the "never" list below. Anything else is (a). When in doubt, (a).

## Never the CTO's, whatever is approved
- `sudo`, `git push`, and anything that changes the CTO's own permissions or the guard (that is (a), or refused).
- Installs of any kind (packages, models, tools, services new to the machine; DEC-083, DEC-957). The CTO asks; the
  owner installs.
- Irreversible deletion: rewriting or pruning git history (as ACT-D8's `gc --prune`), deleting anything outside the
  project and its scratch, or anything with no rollback. These stay (a) even when they are not guard changes.
- Secrets and credentials, paid services, and anything a deny rule keeps sessions out of (e.g. `~/.claude/projects/`).
- Any (b) ACT in the quiet hours (02:00 to 07:30), except an emergency's rollback.

## How a (b) ACT runs and how the approval is recorded
1. The ACT file in `packages/`, as today: exact commands, checks, rollback, and the **rehearsal's log** (run end to end
   in a scratch copy, the owner's standing rule). Its sha256 is stated in the ping.
2. The ping: `APPROVE ACT-<id> (b) | packages/ACT-<id>.md sha <12 digits> | <one line>`.
3. **The approval:** the owner's reply (chat or Remote Control) naming the ACT. The CTO records it verbatim in the
   ACT's "Approval" section (time, channel, words, the file's sha) and in `log/act-approvals.jsonl`. The CTO runs
   exactly that version; any edit after the approval needs a new one. No register entry unless the ACT carries a
   decision (R-8).
4. The CTO runs it. On any check that differs, it rolls back at once and pings.
5. **The report after:** each check's output appended to the ACT ("Applied"), with any difference from the rehearsal,
   in the next digest. A rollback is pinged at once.
6. A command the CTO's permission settings still ask for is a second approval: the owner's click. The CTO never routes
   round it, and the allow list is not widened for (b) (that would be an (a) change).

## Today's and the coming ACTs
| ACT | what | class |
|---|---|---|
| ACT-D8 (done) | the hidden half out of git: worktree, branch, nightly clone, `gc --prune` | (a): irreversible (never the CTO's) |
| ACT-G14 (now) | role separation in the guard's hook and the path map | (a) |
| re-pin window 3 (after measure 3) | the pinned gov | (a) |
| D-5's role files and skills (`.claude/` generated copies) | the guard's inputs | (a) |
| the stand-by file's end in `deadman.py` (O-5, when the sentinel stops reading it) | the sentinel | (a) |
| `.wslconfig` after the RAM upgrade | what the CTO's session runs on | (a) |
| the dispatcher's crontab line to its committed copy (DEC-1010 item 6) | crontab | (b) |
| the nightly's and the sweep's crontab lines back on (at the lift, on the owner's word) | crontab | (b) |
| the embedders' or the reranker's settings changed (if D-4b or W2-32 needs it) | server configuration | (b) |
| the restart classes (approved, D-3 answer 4) | restarts from committed configs | no ACT |
| the integration store refresh, records | the repository's own | no ACT |

**Recommendation:** approve the split as written. Of the eleven, six stay with the operator, three move to the CTO on
a ping reply, and two need no ACT at all.
