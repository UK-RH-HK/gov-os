Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the independent test designer's brief: the wiring review's F18 to F23 (DAEO-52ku)

You are a fresh independent test designer for **W2-149** (`.tickets/DAEO-52ku.md`). Set-up A's wiring is merged
(`7f0e71519`), and its review was READY with rows F18 to F30
(`.gov-runtime/scratch/ref/W2-149-sgx-review-r1.md` in your worktree). The CTO decided (DEC-1112 (3)) that **F18 to F23
are fixed now**, before the owner is asked for the install ACT. Read in the ticket:
- the changed lines **S25** and **S27**;
- the new lines **S29, S30 and S31**, each marked `[changed, DEC-1112 (3)]`;
- the ticket's last note.

Your earlier cases are in `tests/acceptance/W2-149/`. Start with the README's "Set-up A's wiring: the interface",
`w2_149_setup_a.py` and the four `test_w2_149_setup_a_*.py` files.

## What the cases must show
Each case must be red today, against the merged script, for the reason your README states.

- **F18 (S25):** at labeller 1's **round-1 delivery**, the script runs the same confined check on the session's
  `out/label_rules.py`, over the half's staged lines. A failing script means `rejected`, 20, and nothing in
  `H/labels/r1-sgx1-labeller/`. Cover:
  - a script that leaves out an id;
  - a script that reads a planted marker file;
  - a good script, which still delivers.

  Round 2's existing 18 cases stay as they are. These are `bwrap` cases (marker and opt-in as now).
- **F19 (S29):** for each flow, a valid `result.json` whose `stopped` is not `none`, with the flow's out/ products
  present, means `rejected`, 20, every destination unchanged (hashed), `out.stopped` carrying the word, and the products
  in the wall's tar only. The flows are writer 1, writer 2, labeller 1 round 1, labeller 2 rounds 1 and 2, labeller 1
  round 2, and the auditor.
- **F20 (S30):** labeller 2's round-2 `labels-2.jsonl` must hold exactly one valid line per staged sample id. Show:
  - a missing id, an extra id, a repeated id, a bad `label`, a bad `how`, a non-list `clauses`: each 20, destination
    unchanged;
  - a good file lands with `rule_class` as an integer.
- **F21 (S27):** in `input/disputes.jsonl`, when either side's `reason` is empty (labeller 1's script labels carry `""`),
  both sides' `reason` are `""`. Show a case where the side is labeller 1's script label, and one where both have
  reasons (both kept).
- **F22 (S27):** a settled case's `labels.jsonl` line takes the auditor's `label`, `rule_class`, `clauses` (= its
  `basis`), `reason` (= its `reason`) and `how: "audit"`. A flagged case keeps labeller 1's line with `how: "owner"`
  (unchanged rule).
- **F23 (S31):** `rule_class` is accepted as a JSON integer 1–14, or a decimal string `"1"`–`"14"` (no sign, no leading
  zero, no space), in:
  - the rule script's output (else 18);
  - the hand labels (else 20);
  - labeller 2's labels (else 20);
  - the auditor's decisions (else 20).

  Every file the script writes carries it as an integer: `script-labels.jsonl`, `labels.jsonl`, `labels-2.jsonl` and
  the delivered decisions. Refused forms: `true`, `7.0`, `0`, `15`, `"07"`, `" 7"`, `"+7"`, `"seven"`.
- **Existing cases** that assert the old forms (a settled line keeping labeller 1's class; `labels-2.jsonl` delivered
  byte for byte; reasons passed through): revise them only as far as S27, S30 and S31 require. Commits that change an
  existing case carry `--trailer "Rewrite-Reason: DEC-1112 (3) (the wiring review's F18-F23: S25, S27 changed, S29-S31
  added)"`. List each revised case in the README.

Update the README: the interface section (the round-1 check, the stopped rule, labeller 2's check, the reason blanking,
the settled-line form, the `rule_class` forms) and the KPI map.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149-sgx-tests`, branch `w2/W2-149-sgx-tests`, head `944f39165` (`w2/integrate`). Write
  only `tests/acceptance/W2-149/`.
- **Your record:** your whole return is your session's final message, in full.

## Rules
- You never read the implementation: not `governance/project/orchestration/tools/indep_launch.py`, not
  `tests/unit/orchestration/test_w2_149*`, not `docs/changes/W2-149-evidence.md`, and never the engineer's worktree
  (`W2-149-sgx`).
- No GPU, model, network or installs; no real `claude` session. Every case on planted roots; never the real
  `~/gov-os-eval`, `~/gov-os-runs`, `~/gov-os-wall-trees` or `~/.claude`. The hidden-half rule of `EMG-common.md`.
- A nested `bwrap` cannot start in your sandbox. Mark the cases that need it `bwrap`, and the lead runs them outside.
- Run through the heavy slot `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx-tests/src`, your sandbox's TMPDIR, a scratch HOME with `.local`
  linked in, and `PYTHONUSERBASE=/home/usain/.local`. Then run
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx-tests`.
- **DEC-1080:** one simple command per Bash call. Waits and stops by pid only. Scratch budget 20 GB and 1,000,000 files;
  remove your temp trees.
- **Commit** on `w2/W2-149-sgx-tests`, only `tests/acceptance/W2-149/`, with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Report your scratch size.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
  discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), first, as single-line labelled
  fields;
- the new and revised cases: node ids, expectation, red today and why; which carry `bwrap`;
- the commits;
- `gov accept`'s counts;
- `TESTS-READY`.

Refused twice for the same call: stop and say so; no third try.
