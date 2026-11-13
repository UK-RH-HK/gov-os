---
task: nightly-path-fix-check
decisions: [DEC-1154, DEC-781, DEC-1132, DEC-1159, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1073, DEC-953]
reviewed: uncommitted `git diff -- governance/project/orchestration/nightly/` in the main tree (nightly_cron.sh, nightly_restart.sh, nightly_alone.py); repo HEAD 829282dbd530f66890c9bffb3670eedf1681109d
reviewer: a fresh read-only independent auditor (Opus), 2026-11-13 07:03-07:25 UTC, commissioned by the CTO
intended path: .gov-runtime/scratch/orchestrator/drafts/nightly-path-fix/check.md (the guard refused creating that folder: "a reviewer or auditor writes only its own review or audit record ... (DEC-953 item 2)"; not retried, written to the auditor's scratch instead)
---
# Narrow check: the nightly's Node 22 PATH and nightly_alone.py's class-based ids

**Verdict: PASS.**

## What was checked and found sound
- **The diff does only that.** nightly_cron.sh:21 and nightly_restart.sh:37: in each PATH line only the token `node/v18.20.8/bin` changes to `node/v22.23.3/bin`. Every other entry and its order stay the same. v22 replaces v18 instead of being added after it, as the analysis requires. nightly_alone.py: the old inline id rule is replaced by `node_of`, with nothing else touched. The same prefix as merge_queue.py:53 (`NODE`).
- **openspec runs under the new PATH.** With `env -i HOME=$HOME PATH=<new PATH>`, `openspec --version` printed `1.13.2` from `node/v22.23.3/bin/openspec`, and `node --version` printed v22.23.3. gov, rulesync (24.0.0, an ELF binary), gitleaks and claude still resolve from ~/.local/bin. With the old PATH, `openspec` is "command not found", which confirms the cause.
- **The wrappers' own tests pass.** `test_nightly_restart.sh` (the package's rehearsal) ran against a folder holding the changed nightly_restart.sh, quiet_check.py and nightly_estimate.py, as the DEC-1159 review did, with TMPDIR in scratch: 80 cases, 0 failures. `test_nightly.sh` passed N1-N19, C1-C3, K1-K17, G1-G11, E1-E2, S1-S7 and R1-R3.
- **node_of was checked on every case in tonight's JUnit files** (`/tmp/gov-os-nightly-junit/20261113-0404/{parallel,serial}.xml`, 13,613 cases, none with a `file` attribute), against a clean worktree of w2/integrate at 829282dbd:
  - All 104 failing cases resolve to a file that exists. The W1-36 case now reads `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_alone_does_not_make_gov_check_fail`.
  - The id changes for exactly 519 cases, all of them class-based. Each new id names an existing file. The other 13,094 function cases keep the same id as before.
  - The two accepted reds in path-map.yaml are function ids and still match.
- **Group-A sample in a clean detached worktree of w2/integrate under the new PATH.** The run went through heavy_slot.sh with `-p no:cacheprovider -q`, `env -i`, TMPDIR in the auditor's scratch and PYTHONPATH set to the worktree's src. Result: **4 passed in 53.58 s**. The cases were W2-66 `test_the_distribution_mode_is_one_setting_and_the_runs_follow_it`, W2-115 `test_the_strict_close_gives_the_recorded_verdict[green-close_strict]`, W1-30 `test_close_succeeds_on_green_standard_ticket`, and the W1-36 class-based case under its new id. The worktree was removed afterwards.
- **Nothing else in the nightly puts Node 18 first.** The chain is: cron runs nightly_restart.sh, which exports the new PATH. The `systemd-run --scope` and `env` steps pass that environment on to nightly_cron.sh, which exports the same new PATH. It then flows on to nightly.sh, heavy_slot.sh, pytest and nightly_alone.py. nightly_alone.py's re-run takes `os.environ` and changes only PYTEST_* and PYTHONPATH. nightly.sh, quiet_check.py, nightly_alone.py, heavy_slot.sh and the other nightly scripts set no PATH and name no Node version. A search of the orchestration tools, src, template, .claude and the CTO's scratch tools found `v18.20.8` in only one place, the package copy (F1).

## Findings
| id | behaviour | ordinary work | consequence | scope | reverse if |
|---|---|---|---|---|---|
| F1 | The ACT package's copy of the wrapper, `packages/ACT-NIGHTLY-RESTART-1/nightly_restart.sh`, still names Node 18. It is also older than the live wrapper in other ways (before DEC-1159/1160). Anyone who re-promotes that copy would bring Node 18 back. | yes, because a reader may take the package copy as the reviewed source | other (the nightly would go red again, which fails closed) | out | the package copy is declared a historical record that is never copied over the live file |
| F2 | No test pins the nightly's Node bin to one that can run openspec. Both suites passed with v18 and with v22. A future nvm change, such as removing v22.23.3 or a new version, would leave a dead PATH entry and only show up as a red night. | yes, because nvm upgrades are ordinary maintenance | other (fails closed: a red verdict, never a false green) | out | a case elsewhere checks that the nightly's PATH resolves openspec |
| F3 | Node 22's bin also puts ccusage, pyright, tsc, typescript-language-server and npx (22) on the nightly's PATH. Tests that look for ccusage, such as W1-31's ccusage cases and W1-30 R13, now see it in the nightly, the same way they already do in the merge queue's and lead_verify's closes. | yes | other (the nightly now matches the closes' environment) | out | a nightly case that passes in closes turns red only because ccusage is present |
| F4 | A nightly run by hand outside the wrappers (`bash nightly.sh night` from a shell with Node 18 first, as the CTO's own shell has, per the analysis) inherits that PATH. It would still go red with OPENSPEC_ABSENT/FAILED, because nightly.sh sets no PATH of its own. | yes, because a manual re-run for diagnosis is ordinary | other (fails closed) | out | manual runs always go through nightly_cron.sh or nightly_restart.sh |

Classification: 4 findings. None blocks, because none is in scope, reachable in ordinary work, and failing open or losing work. All four are rows.

## Risks for the CTO
- Both wrappers refuse to run when the nightly folder differs from HEAD, with a P1 NIGHTLY-NOT-RUN. Until this change is committed through its ACT, the 04:00 run will refuse. Uncommitted, it fails closed and nothing is lost.
- With A fixed, the analysis expects about 5 reds (groups B-E). The verdict stays red until those test revisions land.

```verdict
{"kpis": [{"kpi": "nightly-path-fix-check", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
