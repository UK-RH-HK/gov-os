# OPERATOR-AGENT-1: an operator agent applies ACTs, so the owner no longer runs them at the terminal (DEC-1103 (4))

- **For:** the owner, to decide §8. **Status:** a draft. Nothing is decided until the owner approves it (DEC-1103 (4)).
- **By:** a product-spec agent for the CTO, 2026-11-09.
- **Sources:** DEC-1103 (4); DEC-1058 and `P-ACT-SPLIT.md` (who runs which ACT today); DEC-1057 (every ACT rehearsed);
  DEC-1101 (2) (fixed hashed briefs that the CTO may not change); ACT-INDEP-WALLS-1 and its `LAUNCH-SPEC.md` (walled
  headless sessions, a canary, hashes checked against an `APPROVED` list); `briefs/JUDGEMENT.md` and `tools/verdict.py`
  (READY worked out by code); the live guard (`.claude/hooks/pretooluse.py`) and `path-map.yaml`; the prompt's rules on
  pushes, tags, ACTs and P1 (`prompts/w2-orchestrator.md` §7, §8); DEC-928 (3) (re-pins run in a plain terminal);
  ADR-0001's threat model (honest mistakes, not a deliberate adversary).

**In short:** a fixed program, run inside a walled headless session, applies an ACT only when every gate passes:
rehearsed, reviewed READY, the hashes match what was reviewed, the class worked out by code, and the owner's one-line
yes for class (b). The CTO can put an ACT in the queue. It cannot start the agent, and it cannot get past any gate.
Today you run every ACT at the terminal. After this, you run none of them: (a) needs nothing from you, (b) needs one
line in the chat, and the rest stays yours as it is now.

## 1. What the operator agent is
- **A walled headless session.** It is `claude -p --restricted` in its own folder, `~/gov-os-operator/`, built on
  ACT-INDEP-WALLS-1's design:
  - restricted mode, so your user settings, plugins and hooks do not load;
  - the wall's own settings and its own wall hook, which refuses anything not on its list (fail closed);
  - a clean environment (`env -i`; no `GOV_*`, no `CLAUDE_PROJECT_DIR`);
  - a canary before each run. Claude Code silently ignores a settings file it cannot read, and the canary catches
    that (LAUNCH-SPEC S9);
  - no network. The only exception is an install ACT, which gets the hosts its reviewed manifest names.
- **Its fixed brief** (`brief.md`) is approved by you once and hashed in `~/gov-os-operator/install/APPROVED`, like
  DEC-1101 (2)'s briefs. The brief tells the session to run one program, `operator_run.py`, step by step, and to report.
  - The session's judgement is used for one thing: it may **stop** a run if a check's output differs from the
    rehearsal's log, even when the code passed it.
  - It can never go past a gate the code refused. All the gates are in code (§4).
- **What it may run:** exactly these forms, which the wall's settings and hook both enforce:
  - `operator_run.py <step> <ACT> <manifest sha>`;
  - the frozen copy of the ACT's own `apply.sh check|apply|undo`;
  - the checks named in the manifest;
  - `git add` and `git commit` of the listed files only, with fixed trailers.
- **What it may never touch:**
  - anything with `sudo`, `git push` or `git tag`;
  - history rewrites; deletions outside the project and its scratch;
  - secrets; the held-out material; the sets root;
  - `tests/acceptance/**` (MR-3);
  - `~/.claude/` beyond reading the CTO session's own transcript, for your yes (§4);
  - its own install, brief, rule table and `APPROVED` list. It never changes itself. An ACT that touches them is
    yours (§5).
- **How it is launched, and by whom:**
  - The CTO writes one request line into `~/gov-os-operator/queue/` (the ACT's id and its manifest's sha256). That is
    the only thing the CTO writes there.
  - The dispatcher's cron line runs `operator_launch.py` from the install every 10 minutes, outside the quiet hours.
    The launcher picks up a request and starts the session.
  - The CTO never starts the session. If it ran the launcher by hand, the same gates would refuse unreviewed or
    altered work, because the gates sit in code the CTO cannot change: the install is copied from a reviewed commit
    and hashed in `APPROVED`, and `APPROVED`'s own hash is printed in every result and in your daily digest.
- **Its commits** carry these trailers:
  - `Role: operator`, `Act: ACT-<id>`, `Act-sha: <manifest sha>`, `Class: a|b`;
  - `Review: <review record sha>`;
  - for (b), `Approved-by: owner (chat, <time>)`.
  - Never `Role: owner`. Records that the close reads only from your commits stay yours (§5).

## 2. The classes, by effect
- **(a) Applied without you:** the ACT only adds checks, tightens a control, or changes nothing that governs agents.
- **(b) Your yes:** the ACT loosens or alters a control (the guard, permissions, settings, hooks, pins, installs,
  crontab, the watchers). It needs your one-line yes in the chat; then the agent runs it.
- **(O) Yours, as today:** sudo, pushes, tags, anything with no tested undo, `Role: owner` records, Windows-side
  steps, the operator's own files, and anything the rule cannot classify.

**The decision table** (every kind of change ACTs have made; 54 ACT files so far):

| Kind of change (example ACTs) | Class | Why |
|---|---|---|
| Guard hook code `.claude/hooks/**` (1-GUARD, GUARD-FIX-1 to 4, G14, G14b, INDEP-WALLS-1's rule 2c) | (b) | code: no rule can prove a code change only tightens |
| Path map: items **only added** to refusal lists (`sets_root_hidden`, `role_paths` denies, a new `evaluation_sets` entry with its hidden globs) (SANDBOX-SEAL-1) | (a) | tightens a control |
| Path map: any other change (a removal, a new role, an allowed path, `permitted_roles`) (GUARD-SETS-1 with its hook) | (b) | alters a control |
| `.claude/settings*.json`, `.rulesync/**`: items **only added** to `permissions.deny` | (a) | tightens |
| The same files: allow rules, hooks blocks, any other key (PERMISSIONS-1/2, QUIET-DENY-1, STOP-WAITER-1, PUSH-INPUT-1) | (b) | alters a control |
| Generated role files and skills, the kernel template (`.claude/agents|skills/**`, `template/governance/kernel/**`) | (b) | they instruct agents (CAP-33) |
| Git hooks `.git/hooks/**` (SELECT-HOOK-1) | (b) | they run code outside every session's guard |
| Test map: items **only added** under `couplings`, `record_reading`, `every_close`, `shared_core` | (a) | more tests run |
| Test map: `record_only` additions, any removal, timeouts, distribution (SELECT-FIXES-1's four `record_only` paths) | (b) | fewer tests run, or the run changes |
| Opt-in lists `tests/optin-*.txt`: lines **only removed** (cases back into the gates: DEC-1103 (2); a `rep:` line dropped) | (a) | more tests run |
| Opt-in lists: lines added or changed | (b) | cases leave the gates |
| Ratchet lists, `acceptance_exemptions`, accepted history for code (W1-01-EXEMPT-1, W2-57-LS-1, P-TRACE-IMPL-1) | (O) | read only from your `Role: owner` commits |
| Machine gate files `~/.gov-os/machine/**`, `~/.config/gov-os*` (DEC-1103 (1)'s `gate.json`) | (b) | they decide what launches |
| `~/.cache/gov-os/**` | (a) | governs nothing |
| The shared servers' committed configs and modules, with their restart (OLLAMA-CAP-1, QUERY-CPUS-1, QUERY-GPU-2, RERANK-GPU-SLOTS-1, RERANK-WAIT-1) | (a), Q3 | governs no agent; today (b) on a ping reply (DEC-1058) |
| Crontab lines (NIGHTLY-1, NIGHTLY-STOP-1, SCHEDULE-STOP-2, DISPATCH-CRON-2, DISPATCHER-1, RUNS-SWEEP-1) | (b) | runs code on a schedule outside the guard; a stop removes a check |
| The sentinel and the dead-man's switch (DEADMAN-1, SENTINEL-1) | (b) | they watch the CTO |
| The pinned gov, re-pins (REPIN-1, 2, EMERGENCY-1, W2 to W4) | (O), Q4 | DEC-928 (3): a plain terminal, not a Claude session |
| Installs and downloads without sudo (RERANK-TRIAL-1/2) | (b) | new code on the machine (DEC-083, DEC-957) |
| Anything with `sudo` (WSL-INTEROP-1); Windows steps (NIGHTLY-0400's wake) | (O) | yours (DEC-1103 (4)) |
| Irreversible deletion, history prunes (D8) | (O) | no undo can be tested |
| The CTO's own scratch tools (`record_checks.sh`) | none | the CTO's to change; never needs an ACT |
| The blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4) | none | walled sessions under DEC-1101, not the operator |
| `src/**`, tests, the register, tickets, or a path no rule names | (O) | not an ACT's business, or unclassifiable: refused |

**Applied to the past 54 (a reading of each ACT's title and files; the trial in §7 computes the exact result):**
- about 8 in (a): the server ACTs and SANDBOX-SEAL-1;
- about 26 in (b);
- about 12 yours;
- 8 for the walled sessions.

So most of the time you save comes from (b): one line in the chat replaces a terminal session.

## 3. Who classifies, and how a misclassification is caught
**Three votes, and the highest one applies.** The class only rises. The CTO alone never decides it.
1. **The rule in code** (`act_class.py` with `class-rules.yaml`, in the install, hashed in `APPROVED`):
   - It reads the ACT's manifest: every touched file with its before and after sha256, and every command.
   - For the list-shaped files it parses before and after, and calls the change (a) only if the only differences are
     items added to a named refusal or coupling list, or lines removed from an opt-in list.
   - It looks through the scripts for `sudo`, `push`, `tag`, installs, network calls and `rm` outside the project. A
     hit raises the class.
   - The ACT's class is the highest class among its files. An unknown path is (O).
2. **The CTO's claim:** the class the ACT file states.
3. **The independent reviewer's confirmation:** a `"class"` field in the verdict block, next to the manifest sha it
   reviewed.

When the votes disagree, the higher class applies and the disagreement is shown in the digest. A change to the rule
table is yours (O).

**How a misclassification is caught:**
- **Before applying,** the agent recomputes the class from its own frozen copy of the patch, not from the CTO's claim.
  If the result differs from the recorded class, it refuses and reports.
- **The touched-file list is hashed** inside the manifest that the reviewer reviewed. The agent's own dry run (§4 G6)
  runs in a clone with a planted HOME. Every file that changed there, in the tree and in the planted HOME, must be on
  the list. An extra file means a refusal.
- **After an (a) ACT is applied, the control files must be unchanged:** the hook folder, the settings, `.claude/**`,
  the git hooks, `crontab -l`, the pin, the sentinel's and dead-man's code, and the operator's install. The path map
  and the settings deny lists may differ only by the computed additions. For path-map or deny-list additions, a replay
  of the guard on the last 48 hours of calls must change no allowed call to refused, apart from the cases the review
  listed. Any other difference means an immediate undo and a P1 push to you.
- **A landing check:** the reference-transaction hook's selection tool flags any commit that touches a (b) or (O)
  path without `Role: owner`, or without `Role: operator` and an `Act:` trailer, as an inbox P1. This catches the CTO
  applying a change itself by mistake.
- **Your digest** lists every ACT applied: its class, the three votes, the touched files, the commit, and the undo
  command.

## 4. The gates, in order; the log and the notice
Each gate is in `operator_run.py` and either passes or refuses. A refusal stops the run.

| # | Gate | (a) | (b) |
|---|---|---|---|
| G1 | **Frozen:** the agent copies the ACT bundle into `acts/<id>-<sha12>/` (read-only), and every file must hash as the manifest says. From here it runs only its own copy, so a later edit in the CTO's scratch changes nothing | yes | yes |
| G2 | **Under a decision:** the manifest names a DEC id that the register holds as ACCEPTED | yes | yes |
| G3 | **Rehearsed** (DEC-1057): the rehearsal log is in the bundle, hashed, and ends with 0 failures | yes | yes |
| G4 | **READY:** the review record's last verdict block names this manifest sha, and the agent's own pinned copy of `verdict.py` computes READY. The reviewer was launched with the fixed reviewer brief (hash in `APPROVED`) and is not the ACT's author. The reviewer's block decides; the moderator's triage does not apply to ACTs. At most two rounds, then you | yes | yes |
| G5 | **Hashes match:** the manifest sha in the request, in the verdict and as recomputed are all the same | yes | yes |
| G6 | **Class:** recomputed (§3); for (a) it must be (a). For (b): your yes, in the fixed form `yes ACT-<id> <sha8>`, typed in the chat after the review. The agent reads it from the CTO session's own transcript (a user turn, not a tool result; the session named in `log/cto-session.txt`), not from a record the CTO wrote. A yes for another sha, or one older than the review, does not count | (a) | your yes |
| G7 | **Live state as stated:** `apply.sh check` passes (the before-hashes) | yes | yes |
| G8 | **Dry run and undo tested:** in the agent's own clone at the live head, with a planted HOME: `check`, `apply`, the checks, then `undo` byte for byte, and the changed set equal to the list | yes | yes |
| G9 | **Holds:** not in the quiet hours (02:00 to 07:30), not during the nightly's window, a close queue or another ACT. It waits on these and does not refuse | yes | yes |
| — | **Apply:** writes `log/act-in-progress.txt` (the commit freeze), runs `apply.sh apply` and the manifest's checks against the rehearsal's stated exit codes and counts, checks that `git diff --cached --name-status` equals the list, commits, then runs the after-checks (§3) | | |

- **The log:** `~/gov-os-operator/log/operator.jsonl`, one line per gate per ACT: the time, the ACT, the manifest
  sha, the three votes, each gate's result, the commit, each check's result, and the undo state. The CTO can read it;
  only the agent writes it.
  - Your (b) yes is also copied verbatim into `log/act-approvals.jsonl`, as DEC-1058 requires today.
  - The CTO adds the "Applied" section to the ACT file afterwards, from this log.
- **The notice:** a push through the dead-man's switch's channels (headless `PushNotification`, a toast, `pings.log`),
  for example "Applied ACT-x (a) 14:02, checks green; to undo, say `undo ACT-x <sha8>`". The digest repeats it. Any
  refusal after G7, any undo, or any red check is pushed at once as a P1.
- **Undo stays ready** for 7 days, or until the next ACT on the same files. It runs automatically when a check fails.
  Otherwise it runs on your line `undo ACT-<id> <sha8>`, read the same way as a yes.

## 5. What stays yours
- `sudo`, `git push`, release tags, merges into `main` (the prompt §8; DEC-722, DEC-848).
- **P1:** every P1 still comes to you. A failed apply, an undo, a refused class, or a disagreement between votes is a
  P1 package, never handled by the agent.
- Anything the rule cannot classify (an unknown path), anything with no tested undo, `Role: owner` records (ratchets,
  exemptions, accepted history for code, until W2-12), Windows steps, secrets and paid services.
- Re-pins, unless you choose otherwise (Q4).
- The operator's own install, brief, rule table, the reviewer's brief and `APPROVED`. Changes to them reach you as a
  package and are applied by your operator by hand, as today.
- **A change to the prompt:** it lists "any ACT" as P1 (§8). Approving this package makes (a) ACTs not P1 and (b) ACTs
  a one-line yes. The decision record says so.

## 6. Failure modes, and how each fails closed
| Failure | What happens |
|---|---|
| The CTO edits the ACT after its review (a stale draft, a fix it forgot to re-review) | G1/G5: a hash mismatch, refused: "changed after review", a new review is needed |
| The review is missing, malformed, or not READY, or the reviewer used a changed brief | G4 refuses (`verdict.py` fails closed on a malformed block) |
| The CTO or the reviewer calls a (b) ACT (a) | G6: the code's vote is higher, so it runs as (b), and the digest shows the disagreement |
| The rule misses a control file (a gap in the table) | an unknown path is (O); a file the dry run changes that is not on the list is refused; the after-check on the control hashes undoes the ACT and sends a P1 |
| The live files moved since the rehearsal | G7 refuses; the CTO rebuilds, rehearses and re-reviews (a new sha) |
| A yes for an older version, a mix-up between two ACTs | G6: the yes names the sha; a mismatch is refused, and the agent asks again through the CTO's ping |
| The apply fails partway | `undo` from the backups, a P1 push; if the undo fails too, the lock is held, nothing else is applied, and you are told |
| A check is red after the apply | immediate undo, a P1 push |
| The session crashes or times out mid-apply | it is stopped by pid (L-0075). The next launch finds the unfinished journal, runs the undo first, and sends a P1 |
| The wall's settings did not load | the canary refuses before the real session |
| The operator's own files change (`APPROVED` mismatch) | every run refuses until you re-approve |
| The push does not reach you | the log and the digest still show it; the digest compares the log with the notices sent |
| A deliberate forgery (a planted transcript line, a rewritten install by hand) | outside ADR-0001's threat model: a Wave 3 hardening row, not machinery now |

## 7. How it is built and proven; the cost and the time
1. **A ticket, tests first.** An independent test designer writes KPI tests from this package, after which an
   engineer builds. The tests cover:
   - each gate refusing on its own;
   - the classifier on every table row;
   - the after-check undoing an (a) ACT that touches a control file;
   - the yes read from a planted transcript (a tool result is not a yes; a wrong sha is refused);
   - the dry run's changed-set check;
   - the canary;
   - waits and stops by pid only.

   The code lives in `governance/project/operator/` (reviewed and tested), with the fixed brief, the reviewer's brief
   and `class-rules.yaml`. One review, READY by `verdict.py`.
2. **Its own ACT, ACT-OPERATOR-1, applied by your operator by hand one last time** (it is (b) and (O)):
   - the install copied into `~/gov-os-operator/install/` with `APPROVED`;
   - a settings deny rule closing that folder to the CTO's writes, except the queue;
   - the dispatcher's cron line;
   - the landing check's trigger extended to `Role: operator`.

   It is rehearsed (DEC-1057). You approve the two briefs with it.
3. **A trial on past ACTs, before the first live run:**
   - the classifier runs on all 54 ACT files. Pass mark: no ACT lower than the table puts it, with every rise listed;
   - 8 applied ACTs are replayed end to end in clones at their commit before the apply: SELECT-FIXES-1 (b),
     SELECT-HOOK-1 (b), GUARD-SETS-1 (b), PERMISSIONS-2 (b), NIGHTLY-STOP-1 (b), OLLAMA-CAP-1 (a), W1-01-EXEMPT-1 (O)
     and D8 (O);
   - 7 planted faults: an edit after review, a wrong class claim, an unlisted file touched, a red check, a failing
     undo, a missing yes, and a yes for an older sha.

   Pass mark: every planted fault refused, every replayed class as expected, and no live file changed.

   The first live (a) run is the next test-map or opt-in ACT. If the agent is ready in time, that is DEC-1103 (2)'s
   ten cases back into the gates.
- **The time:** about 3 working days elapsed in one slot:
  - tests, about half a day;
  - the build, 1 to 1.5 days;
  - the review and one fix round, about half a day;
  - the trial, about half a day;
  - the build ACT's rehearsal, about 2 hours.

  It reuses ACT-INDEP-WALLS-1's wall hook and canary, so it starts after that ACT is applied.
- **The cost:**
  - tokens about the size of one mid-sized ticket;
  - per ACT, one short session (about $0.05 to $0.30; the work is in code), plus a dry run of 2 to 15 minutes of
    machine time (no full suite, no GPU);
  - your time: this package, the two briefs, and one last terminal session. After that, (a) costs you nothing,
    against 5 to 15 minutes at the terminal per ACT today, and (b) costs one line.

**Recommendation:** approve the design and the table, with Q1 to Q7 as recommended. Confidence: medium-high on the
gates and the classifier. Medium on reading the yes from the transcript, which depends on Claude Code's transcript
format and Remote Control turns: the build's tests settle it, and the fallback is Q2's alternative.

## 8. Questions for the owner
1. **The classes and the table (§2),** including tightening-only edits as (a): deny-list additions, path-map refusal
   additions, test-map coupling additions and opt-in removals. Guard code always stays (b). *Recommended: yes.*
2. **Your yes:** typed in the chat as `yes ACT-<id> <sha8>` (the ping carries the line ready to copy), read by the
   agent from the CTO session's transcript. The alternative is the CTO's verbatim record, as DEC-1058 does today:
   simpler but weaker. *Recommended: the transcript.*
3. **The shared servers' settings** (embedders, reranker): today (b) on a ping reply (DEC-1058). By effect they govern
   no agent, so they become (a). *Recommended: yes.*
4. **Re-pins:** stay yours in a plain terminal (DEC-928 (3)), or become (b) once a re-pin has been rehearsed in the
   agent's form? *Recommended: stay yours for now; decide after one rehearsed re-pin.*
5. **The launch:** the dispatcher's cron runs it from the queue, and the CTO only queues. The alternative is that the
   CTO runs the launcher, with the same gates. *Recommended: the cron.*
6. **Notices:** a push for every (a) ACT applied for the first two weeks, then the digest only, with failures always
   pushed. *Recommended: yes.*
7. **When:** build it after ACT-INDEP-WALLS-1 is applied (it reuses the walls), about 3 days, in the next free slot
   after the two DEC-1103 ACTs. *Recommended: yes.*
