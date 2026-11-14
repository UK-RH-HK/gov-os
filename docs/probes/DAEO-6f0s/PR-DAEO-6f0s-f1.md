---
type: probe
task: DAEO-6f0s
check: "narrow independent check after review round 2 (DEC-1154: the owner's DEC-1177 (1) and the CTO's P-W2-184-2 (a)); not a review round (DEC-1010)"
reviewer_session: e0e76090-d60a-43ab-9f61-d8749106f10b
implementer_session: 06690070-6c47-4c6d-9496-4b59a88390b0, b8148380-9e1a-43ae-9b7c-f9ebcc2f6bb5
reviewer_wrote_nothing: true
commissioned_by: orchestrator (the W2-184 ticket lead)
judged_by: orchestrator (the W2-184 ticket lead)
judgement: pass
probed_commit: fb2ea8460857c9410e4dcaf63353e07ec75a606f
---

# Narrow check of DAEO-6f0s (W2-184) after review round 2: judgement pass

- **Head checked:** fb2ea8460857c9410e4dcaf63353e07ec75a606f (`w2/W2-184`, /home/usain/gov-os-worktrees/W2-184).
- **Session:** `independent-auditor` (GOV_TICKET=DAEO-6f0s), model claude-opus-5-5, effort high. This is a narrow check under DEC-1154, not a third round.
- **What I ran:** everything below ran on `git archive` copies of the head under the session's `$TMPDIR`. Each run set `HOME` to an empty scratch folder and `PYTHONPATH` to the copy's own `src`, with `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. I re-ran no whole suite. The heavy slot could not write its log here (read-only), so I ran without it and kept the runs small.
  1. **The new and rewritten case files as they stand:** `test_w2_184_f1_tests_worktree.py`, `test_w2_184_cli_options.py` and `test_w2_184_s4_reviews.py`. 88 passed, 0 failed.
  2. **Eleven mutants, each in a fresh copy, against those three files:**

     | Mutant | What it breaks | Cases failed |
     |---|---|---|
     | Launch root only | the pre-fix behaviour | 16 |
     | No dedup by root-relative path | a path under two roots counts twice | 14 |
     | Roots of any ticket's records | the ticket filter dropped | 1 |
     | Launch root sorted last | P-td5-2's launch root first | 1 |
     | Non-JSON launch record skipped | P-td5-1 / 6.1 fail closed | 4 |
     | Probe record with bad YAML under another root skipped | 5.1a "nothing that refuses stops refusing" | 1 |
     | CLI drops `reason` | 7.2a | 7 |
     | CLI drops `owner_named` | 7.2a | 9 |
     | CLI drops `trial` | 7.2a | 12 |
     | CLI treats an empty value as absent | forms checked through the CLI | 3 |
     | CLI keeps the old usage line | 7.2a usage | 2 |

     Every mutant was caught.
  3. **My own fixture probes:** a test file placed only in a `$TMPDIR` copy, using the cases' support module and a stand-in CLI. 4 passed.
     - **Round 2's p2, re-run on this head:** a FULL ticket with two linked worktrees. The round-1 auditor is launched from the ticket worktree. A fail-open probe record is then committed on the ticket branch only. The test designer launched from the tests worktree gets Opus, `model_source: promotion`, and its `promotion` names the root-relative record. Round 2 launched from the tests worktree gives `review_round: 2`, effort max, `effort_source: probe`. Round 3 is refused, naming DEC-1010.
     - **Symlinked root:** a launch record names the ticket worktree through a symlink and another names it with a trailing slash. One failed record is still one, not two.
     - **Review count:** records of the same ticket with another role, with `resumes` set, or under another ticket leave the count at 1.
     - **Odd `root` values:** a record whose `root` is relative, null or an integer is skipped, not refused.
  4. **CLI to launcher:** `command.run` with `launcher.launch` replaced by a recorder, for `gov launch orchestrator DAEO-6f0s --reason x --owner-named garbage --trial ../t`.
  5. **Concurrency of the shared read:** five seconds of `_launch_records` reading while another process ran `record.write` in a loop with 3 KB records. 442 reads against 3,229 writes, 0 refusals.
  6. **Reading:** `git show` of 94b48c130, 42d0867d3 and fb2ea8460, and the test designer's a4ad2e380 and 3e3d275a0. I checked the commit roles: the engineer wrote only `src/`, `tests/unit/` and `docs/changes/`. The acceptance tests are the test designer's, and the S4 rewrite carries `Rewrite-Reason: DEC-1010, P-W2-184-1 (a)`. I also read the ticket's `allowed_paths` (`command.py` is now among them), DEC-1177, DEC-1154 and the ticket's last two paragraphs.

## Findings

**F1 (change 2, KPI S4/S1): a lead launch now takes the three options silently and checks none of them.**
`argparse` in `src/gov/launch/command.py:41-45` accepts `--reason`, `--trial` and `--owner-named` for every role, and `run` passes them on to `launcher.launch`. Probe 4 showed a lead launch receiving `{'reason': 'x', 'trial': '../t', 'owner_named': 'garbage'}`. The lead branch of `launcher.launch` (`launcher.py:938-950`) never reads them and does not run `_check_options`. So `gov launch orchestrator <tk> --owner-named garbage` starts the lead, where before fb2ea8460 the same line ended with argparse exit 2.

Interface 7.2a says a lead launch is "unchanged (7.1: a lead takes none of them)". A lead launch without the options is unchanged. With them, they are dropped without a word rather than refused. A lead has no RUBRIC-2 setting, writes no launch record and opens nothing by the dropped word.

What would reverse this: a lead path that refuses or reports the options, or a decision that silent ignoring is what "takes none" means.
- Ordinary work: yes, because a lead launched by a script that also launches workers could carry `--reason` or `--owner-named` by habit.
- Consequence: other (the option has no effect on a lead; nothing opens and no work is lost; at worst a reader of the command line thinks a decision id was checked).
- Scope: in

**F2 (change 1, KPI S4/S5): the cost of P-td5-1. In a project with a `criticality.yaml`, every worker launch now reads the whole shared record folder, and one record that is not JSON refuses every launch.**
`launcher.py:671` calls `_launch_records(root)` on every worker launch when the file exists. `launcher.py:494-500` refuses on the first file it cannot parse. Before the change, only a FULL ticket's auditor launch read the folder.

Two paths to a record that is not JSON:
- **A concurrent reader:** `record.write` (`record.py:91-110`) creates the file with `O_EXCL`, then writes and fsyncs. `_rubric` reads the folder before the start lock is taken, so a launch could meet a record in the moment between its creation and its write. My stress probe hit this 0 times in 442 full reads against 3,229 concurrent writes.
- **A killed launch:** a launch killed inside that window leaves an empty file. `write` removes a partial file only on `OSError`. Every worker launch of the project would then be refused, naming the file, until someone deletes it.

The live record folder holds 82 files today and all parse. This is the lead's settled P-td5-1, written into interface 5.1a and argued as fail closed. Judged by the rules, it is a row.

What would reverse this: a reproduction of a partial or empty record arising in ordinary launches.
- Ordinary work: no, because the window lies between the record's create and its single write of a few KB (0 hits in the stress probe), and a leftover needs a kill inside that window.
- Consequence: other (fails closed: launches are refused naming the file; no promotion is hidden and no work is lost).
- Scope: in

**F3 (change 1, KPI S5/F1): a stale copy of the same probe-record path in the launch root wins over a newer copy under another root.**
This is P-td5-2 as settled: `_probe_files` takes the first root's copy (`launcher.py:521-534`), and `test_f1_a_path_under_both_roots_is_read_from_the_launch_root_s_copy` checks it. The risk case runs like this:
1. The stop-gap (c) merges a record into the tests branch.
2. Later, that same file is edited in place on the ticket branch to add a fail-open finding.
3. A launch from the tests worktree then reads its old copy, and no promotion is applied.

What would reverse this: a probe record that is legitimately rewritten in place after being merged into a tests branch.
- Ordinary work: no, because probe records are committed once per round under their own names (this ticket's are `PR-DAEO-6f0s-round-1.md` and `PR-DAEO-6f0s.md`, each in a single commit), and a lead never writes over a reviewer's verdict (DEC-1010).
- Consequence: fails open (in that constructed case only, a promotion not applied).
- Scope: in

**Probed and found sound:**
- **The fix reaches the tests worktree:** round 2's p2 now promotes the test designer launched from the tests worktree, on both a fail-open finding and two failed reviews.
- **Roots that are gone:** a deleted worktree, a missing folder or a file named as a root is skipped without a refusal.
- **No probe record anywhere:** the launch is as before.
- **Refusals kept:** bad YAML in a probe record, a verdict block that is not JSON, or a launch record that is not JSON still refuses under another root.
- **Counting:** each root-relative path counts once. Roots are compared after `realpath`, so a symlinked root is not double-counted.
- **Other tickets:** only records of this ticket's names (the id given, `id`, `wbs_id`) add roots.
- **Review count (6.1):** unchanged. 42d0867d3 restores the comparison of the record's own `session_id` with `--resume`, and the file stem stands in only for the displayed id, as before. Resumes, other roles and other tickets are not counted, and the count spans every root as before.
- **No `criticality.yaml`:** nothing is read (1.4; the rewritten S4 case).
- **`record.folder` side effects:** it was already called on every worker launch (`launcher.py:764`), so it adds no new refusal.
- **The CLI options:** each gives the keyword case's result. Forms are refused with exit 1 before any record or session, empty values included. An option after `--` stays a CLI argument and admits nothing. The usage line names all three before `[-- …]`. `--plan` ignores them.

## Per KPI line

**S1 (effort: the floor, max and `--reason`): pass.** Through the CLI, `--reason` admits a max the launch chose itself and records `effort_reason`. An empty or blank `--reason` is refused with exit 1 and no record. `--reason` after `--` admits nothing. Change 1 does not touch effort. F1, a lead dropping `--reason` silently, is a row.

**S2 (the model, tier and `--trial`): pass.** Through the CLI, `--trial` sets the trial's model and effort with source `trial` and records its id. A missing trial file or one that does not fit is refused, naming the file and the field. Malformed ids are refused even when a trial sits at the path the id names. `--trial` after `--` admits nothing.

**S3 (the record): pass.** CLI launches record `trial`, `effort_reason` and `owner_named` as the keyword launches do, and null when absent. Promotion records from another root name the root-relative path (`docs/probes/<id>/…`), per 5.1a.

**S4 (a FULL ticket's two reviews): pass.** `--owner-named` through the CLI admits a repeated setting and a third round, and records it. Without it, a third round is refused naming DEC-1010. The shared read leaves the count unchanged (my probe 3; the S4 cases). F2, the folder read on every launch, is a row (ordinary work no, fails closed).

**S5 (promotion from the probe records): pass.** Probe records are read under the launch root and every root this ticket's launch records name. A test designer launched from the tests worktree is promoted on a fail-open finding or two failed reviews kept on the ticket branch. Paths count once, refusals stay refusals, and other tickets' roots are not read. F3, P-td5-2's stale copy, is a row (ordinary work no).

**F1 (failure line: a model below its tier with no trial, a promotion not applied, an effort below the floor): pass.** Round 2's F1, a promotion not applied from the tests worktree, no longer reproduces at this head (my p2 re-run and the 16 cases the launch-root-only mutant fails). An Opus-less model after `--` is still refused on a promoted ticket from the tests worktree.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```

judgement: pass

## The lead's triage (DEC-1010 item 1)

- No finding blocks: none is in scope, ordinary work yes and fails open or loses work.
- F1 (a lead launch takes `--reason`, `--trial` and `--owner-named` silently; ordinary work yes, consequence other),
  F2 (one empty or partial launch record stops every worker launch; ordinary work no, fails closed) and F3 (P-td5-2's
  stale-copy case; ordinary work no): Wave 3 hardening rows, for the CTO.
- The launch of this check: review_round 3, owner_named DEC-1177, model_source promotion, effort high (`after --`).
