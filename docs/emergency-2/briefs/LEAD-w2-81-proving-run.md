# Lead brief: W2-81's proving run on release 0.1.4, on Sonnet (W2-81, `DAEO-l78m`; release acceptance item 2; the owner, DEC-1221 (1), DEC-1223 (9))

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (the machine rule, memory first, trailers, models).
Name: `w2-81-proving-run`; worktree `/home/usain/gov-os-worktrees/E2-w2-81-proving-run`, branch
`e2/w2-81-proving-run` from `w2/integrate` (it holds W2-81's end-to-end revision, merged today). Every commit
`Task: DAEO-l78m`. **Do not merge**; the CTO lands your branch.

**What this is:** the real proving run S-RERUN of `.tickets/DAEO-l78m.md` (read its success lines, its failure lines
and its amendment notes of 2026-11-19), on **release 0.1.4** (tag `v0.1.4`, C `961db6546`; the live pin
`~/.local/share/gov-os/pin-961db6546490/bin/gov`, which `~/.local/bin/gov` names). The procedure is the README's
section "The runner: one command" (`tests/acceptance/W2-81/README.md`, read it whole, and "The hidden half's form").

## Do it in this order
1. **Learn how the last run was set up** before you start: `~/gov-os-runs/W2-81/run-0.1.1/` (`setup.json`, `run.json`,
   `run.log`), `docs/emergency-2/archive/CHECKPOINT.md` (search it for W2-81 and the re-run on 0.1.1: the adopter
   brief, how each adopting session was launched, the hidden half's place) and `docs/emergency-2/HANDOVER.md`. Use
   memory first. The evaluation sets root is under `~/gov-os-eval/fixtures/evaluation` (find W2-81's hidden half there;
   if there is none, stop and say so in your return: a hidden half is written by an independent writer, not by you).
2. **Build** a fresh run folder `~/gov-os-runs/W2-81/run-0.1.4/` with a fresh seed, `--manifests` in a folder outside
   the run folder and outside every adopting session's reach (the README's "A risk for the real run").
3. **Adopt** each repository with one launched session on **Sonnet** (`claude-sonnet-5-5`), with the adopter brief
   current on 0.1.4 (refresh the 0.1.1 brief for what 0.1.4 changed: `gov queue` in place of `gov close`, the stage
   forms; no word of the planted problems), started in that repository, leaving its logs and reports in
   `<run>/outputs/<repository>/`. At most two at a time, each start under the resource gate (`gov resources --check`;
   load under the gate, `-n auto` runs through the slot); the GPU never spills (rebuilds through the slot).
4. **Read** with the README's real-run command: `--gov` and `--pinned-gov` the 0.1.4 pin, `--adopter-model
   claude-sonnet-5-5`, `--queue-ticket` as the README says, `--sets-root` the evaluation root. The reader and grader
   sessions run on Sonnet (the runner forces it; DEC-1221 (1)).
5. **Record** under `docs/plan/wave-2/w2-81-proving-run/` on your branch: `report.md` and `report.json` copied from the
   run folder (they hold no question or answer text, by the runner's rule), the verdict line, the seed, the models and
   release, and per repository `gov doctor`'s exit code and the governance share with the command that measured it (the
   CTO's ruling of 2026-11-19 in the ticket: the run record carries them, not the runner). Then the transcript scan:
   no session you launched read the hidden half (EMERGENCY-2 2.7; A-12's window and targets): say how you checked.

## Return
The verdict line (`READY (seed N; ...)` or `NOT_READY`), each repository's end-to-end figure and its `gov queue`
result, every NOT_READY reason, the run's time and model spend, the transcript scan's result, your branch and head.
A NOT_READY is a finding, not a failure of yours: report it plainly with its evidence; do not change the judge, the
scorer or any test to make it READY (the test code is the test designer's; a defect in Gov OS is a fix for its owning
ticket, the CTO's to start).
