# W2-81's proving run on release 0.1.4 (S-RERUN; DEC-1221 (1), release acceptance item 2): the run record

Written by the lead `w2-81-proving-run` (`Task: DAEO-l78m`), 2026-11-20. Run folder `~/gov-os-runs/W2-81/run-0.1.4/` (not in this repository).

**Verdict line:** `NOT_READY (seed 7429927; hidden half: present and asked in 6 of 6 repositories)`, exit 1 (the runner's real-run read step).

- **Seed:** 7429927 (fresh). 13 hidden variants built by the runner. Manifests in `~/gov-os-runs/W2-81-manifests-0.1.4/`, outside the run folder and outside every session's reach.
- **Release:** 0.1.4, read by the runner from the pinned install (`~/.local/share/gov-os/pin-961db6546490/bin/gov --version`: `gov 0.1.4`); tag `v0.1.4`; `src/` of this branch equals the tag's (`git diff v0.1.4 HEAD -- src` is empty).
- **Models** (from `report.json`, `models`): adopter `claude-sonnet-5-5`, reader `claude-sonnet-5-5`, grader `claude-sonnet-5-5`. The adopters ran at effort high (`claude -p --model claude-sonnet-5-5 --effort high`); each worker an adopter launched (test designer, auditors) was launched by `gov launch`, which chooses the model: `claude-sonnet-5-5`.
- **Command (read step):** `PYTHONPATH=<worktree>/src python3 tests/acceptance/W2-81/w2_81_run.py --folder ~/gov-os-runs/W2-81/run-0.1.4 --mode read --gov <pin> --pinned-gov <pin> --adopter-model claude-sonnet-5-5 --claude claude --queue-ticket python-app=pa-smko --queue-ticket rust-workspace=rw-vyk3 --queue-ticket typescript-monorepo=tm-4kpa --queue-ticket legacy-docs=ld-mj6i --queue-ticket secret-history=sh-e15w --queue-ticket python-app-clean=pac-73p5 --sets-root ~/gov-os-eval --manifests ~/gov-os-runs/W2-81-manifests-0.1.4`.
- **Set-up** (before the adopters; the 0.1.1 re-run's operator step, `tools/setup_0.1.4.py`): kit from tag `v0.1.4` by `copier`, `gov adapters generate`, A0, the coordination, A5, A7, A10 review tickets and the adoption ticket (LITE). Adopter brief: `adopter-brief-0.1.4.md`; driver: `tools/drive.sh` (two at a time, each start under `gov resources --check`).

## Per repository

| Repository | End to end (right of asked) | Adoption ticket | `gov queue <ticket>` (the runner's run) | `gov doctor` exit | Governance share |
|---|---|---|---|---|---|
| python-app | 80.95 % (17 of 21), bar not met | `pa-smko` | exit 3 (acceptance `crash`) | 3 | not measured |
| rust-workspace | 75 % (15 of 20), bar not met | `rw-vyk3` | exit 3 (acceptance `crash`) | 3 | not measured |
| typescript-monorepo | 60 % (12 of 20), bar not met | `tm-4kpa` | exit 3 (acceptance `crash`) | 3 | not measured |
| legacy-docs | 60 % (12 of 20), bar not met | `ld-mj6i` | exit 3 (acceptance `crash`) | 3 | not measured |
| secret-history | 80 % (16 of 20), bar not met | `sh-e15w` | exit 3 (acceptance `crash`) | 3 | not measured |
| python-app-clean | 95 % (19 of 20), bar met | `pac-73p5` | exit 3 (acceptance `crash`) | 3 | not measured |

(Each repository's asked count is its visible questions plus 10 hidden ones.)

- **`gov doctor` command:** `gov doctor` in each repository (the pinned `gov`, a scrubbed environment, no `GOV_*` variable), after the landing step. Exit 3 `DOCTOR_UNHEALTHY` in all six, for one check only: `claude_code`, "CLI 2.1.329 differs from extension 2.1.328" (`pinned_version: null`). Every other check passes or is unmeasured. This is a condition of the machine (the CLI and the extension), the same in every repository; the output is `outputs/<repository>/doctor.out` in the run folder. The adopters met it too.
- **Governance share, command and result:** `gov telemetry <adoption ticket> --ticket-session <adopter session>=orchestrator --ticket-session <test designer session>=independent-test-designer` (the sessions' ids from their `claude -p` logs) answers `CCUSAGE_ABSENT: ccusage is not on PATH: the sessions' tokens were not measured`; `gov status` reports `governance_share: not measured`. The share is not measured in any repository. The tool the measure needs is `ccusage`; it is not installed (an install is the CTO's to approve and record, see "Installs").
- **`gov queue`:** the runner's run answered exit 3 in all six, every one with the acceptance folder's run as `outcome: error, error_kind: crash` and 0 tests run. Cause: the runner starts `gov queue` with `HOME=<run folder>/.home` (`w2_81_run._env`), where `python3 -m pytest` is not found (pytest lives in the owner's user site, `~/.local/lib/python3.12/site-packages`); reproduced by `gov queue <ticket> --dry-run` with that `HOME` (0 passed) and not with the owner's `HOME`. Run read-only (`--dry-run`, nothing moved or committed) with the owner's `HOME`, the landing is red on the ticket's acceptance folder in all six, on the F1 line (`outputs/<repository>/dry-realhome/summary.txt`): python-app 16 passed 1 failed; rust-workspace 2 passed 4 failed; typescript-monorepo 2 passed 1 failed; legacy-docs 15 passed 1 failed; secret-history 3 passed 1 failed; python-app-clean 2 passed 1 failed. F1 is "every commit touching `governance/adoption/` carries `Role: orchestrator`": every stage commit `gov adopt --lite` writes has a subject only, no trailer block (all six adopters' finding 1; the same defect as 0.1.1's W81-9 / F-001). So the ticket cannot close in any repository, with or without the runner's `HOME`. No `gov queue` landed anything.
- **The landing step, not run by the adopters:** the adopters ended at `gov accept` (all six: red on F1 only, except rust-workspace which also lacks the A10 record).

## Every NOT_READY reason (the judge's, from `report.json`)

63 reasons in all (6 of them the landing): the full list is in `report.md`. In groups:

- **End-to-end figure under 95:** python-app 80.95, rust-workspace 75, typescript-monorepo 60, legacy-docs 60, secret-history 80 (python-app-clean met it at 95).
- **`gov queue` ended with exit 3:** all six (above).
- **NOT_BUILT capabilities, named by the judge:** `A2-content-class` (python-app, rust-workspace, typescript-monorepo, legacy-docs, secret-history), `A8-documents` (rust-workspace, legacy-docs), `VERDICT` and `findings` (all six). Each planted problem whose handling needs one is NOT_BUILT: python-app 5 of its 5 planted kinds and hidden variant #1; rust-workspace 3 planted and hidden variants #2 to #4; typescript-monorepo 5 planted (including the secret) and variant #5; legacy-docs 3 planted and variants #7 to #10; secret-history 3 planted (including the secret) and variants #11 to #13.
- **MISSED:** legacy-docs' two large-file problems.
- **Controls FLAGGED:** `current-spec-looks-old` and `live-file-in-legacy-folder` in rust-workspace, legacy-docs and secret-history (6 controls).
- **Stage ABSENT:** rust-workspace's A10 record (its A9 stopped with `FABRIC_INCOMPLETE`, "vectors: 2 file(s) judged and in neither list").
- **Not a reason, for the reader:** python-app-clean has no planted problem and no control flagged; it fails only on the landing and the two not-built stages.

## What the adopters reported (counts; the findings are in the run folder, `outputs/<repository>/FINDINGS.md`)

python-app 16, rust-workspace 14, typescript-monorepo 14, legacy-docs 10, secret-history 16, python-app-clean 12. Common to all or most: stage commits carry no trailers (all six); `gov brief` for the auditor and the test designer leaves slots open (`{W2}`, `{PROFILE}`, `{BRANCH}`, `{REGISTER}`, `{EXIT_FILE}`, `{SUBJECT}`, `{COMMIT_PATHS}`, an empty "Objective:") and refuses the test designer's on `UNSET_WHERE` (all six); AS reports 0 specs and 0 modules where the repository has them (five); MA and A9 treat the kit's own `governance/framework.lock` as an over-limit file with a secret and leave it unindexed (all six); the final `gov rebuild` marks the committed A5, A7 (and A10) verdicts invalid (rust-workspace, python-app-clean); the store lags HEAD after a stage's commit (typescript-monorepo, secret-history, legacy-docs); `gov doctor` unhealthy on `claude_code` drift (all six); no lite verdict stage or command exists (rust-workspace). The adopters stopped cleanly (`ADOPTION STOPPED`, tree clean, store commit = HEAD).

Gaps in **my brief** (not the product's), met by the adopters and recovered from: the brief's order (A1, A2, MA, A3) omitted stage AS, which A3 requires (carried from the 0.1.1 brief); and its A3 `artefacts` form (a batch for every entry, `kind` for a RETIRE) is not the form 0.1.4's A3 takes for KEEP (`KEEP is in no batch of A6`; `RETIRE` takes no target and only the kinds rule-file, memory-store, chat-database). The adopters ended with `artefacts: []` in three repositories, so a superseded or legacy file was never proposed for retirement there. This affects which planted problems were handled; it does not change the NOT_BUILT capabilities above, which no brief could supply.

## The transcript scan (EMERGENCY-2 2.7; A-12)

No session launched here read the hidden half.
- **Window:** from 2026-11-20T14:20Z (before the first adopter started at 14:22Z) to the end of the read step (15:30Z). The hidden half was written 2026-11-12.
- **Sessions:** the transcripts of every session launched in this run: the six adopters and the workers they launched (test designers, auditors), 29 transcripts, in the 12 project folders `~/.claude/projects/-home-usain-gov-os-runs-W2-81-run-0-1-4-repos-<repository>[-tests]/` (copied to a scratch root; the live folder also holds every other session of the machine, whose hits would be this lead's own and the CTO's).
- **Targets and command:** `gov memaudit scan --set ~/gov-os-eval/fixtures/evaluation/adoption-proving-ground/hidden --since 2026-11-20T14:20:00Z --id <repository>-h01 ... <repository>-h30 (180 ids: the ids the hidden half's form gives, `<repository>-h<nn>`, none read from it) --projects <the scratch root>` printed `no transcript in the window names the set: 29 transcripts read, 180 ids`.
- **Also grepped in the same 29 transcripts:** `gov-os-eval`, `adoption-proving-ground`, `W2-81-manifests`, `report.json`, `/hidden`, `e2e/`: 0 files each; `Dynamic-Agentic-Engineering-OS`: 1 file (the kit's `.copier-answers.yml` text, `_src_path`); no transcript names another repository's path.
- **Not scanned, by construction:** the reader and grader sessions (121 questions, 242 sessions) run `claude -p --safe-mode --tools "" --no-session-persistence` (`gov.memaudit.claude.argv_of`): no tools, so none could read a file, and none writes a transcript.
- **The tool's own defect (EXAMIN's F-033, reported to the CTO by the EXAMIN session):** without `--id`, `gov memaudit scan` takes the set's file stems as ids, here the six repository names, and would match every transcript; I passed explicit ids.
- **The hidden half itself:** this session never opened it; the runner (the real-run command) read it, as the README's form says.

## Time and spend

- Adopters: first start 14:22:06Z, last end 15:17:08Z (55 min wall, two at a time); each 13.8 to 18.2 min. Read step 15:17:40Z to 15:30:32Z (13 min).
- Model spend recorded in the sessions' own logs: adopters $12.50 (claude-sonnet-5-5, 78 to 101 turns each), their launched workers $8.25 (27 sessions), $20.75 in all. The 242 reader and grader sessions record no cost (their rows hold none): not measured.

## Installs

`ccusage` (the governance-share counter `gov telemetry` needs; its version, size and registration are the CTO's to name): not installed here.
