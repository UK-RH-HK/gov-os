Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-147/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-147 — the independent review (DAEO-zi7s), round 1

You are a fresh, read-only independent reviewer. Review **W2-147** (`.tickets/DAEO-zi7s.md`: read it in full, with its
note on the self-loop): `gov plan` breaks a cycle only at a ticket inside it, and a ticket outside every cycle keeps
all its waits (the owner's DEC-1102).

## What to review
- **The branch:** `w2/W2-147` in `/home/usain/gov-os-worktrees/W2-147`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-147`): `src/gov/plan/derive.py`; the engineer's unit tests
  `tests/unit/plan/test_w2_147_cycles.py`; the designer's cases `tests/acceptance/W2-147/`; `docs/changes/W2-147-evidence.md`.
- **The runs:** the CTO's `gov accept W2-147` outside the sandbox: 25/25. The engineer's: `tests/unit/plan` 69 passed,
  `tests/acceptance/W2-136` 76 passed, `tests/unit/launch/test_w2_136_plan_check.py` 34 passed.

## Check, against each KPI line S1 to S4 and the failure lines
- **S1:** the break ticket is always inside the strongly connected component, chosen by the fixed key; only its waits
  from inside the component are broken.
- **S2:** a ticket outside every cycle keeps all its waits and is batched after what it waits on.
- **S3:** deterministic in any file order; each break named (`CYCLE_TIEBREAK`, ticket, waits broken).
- **S4:** two cycles each broken once inside itself; a self-loop broken and named; no cycle: output byte-identical.
- **The engineer's notes:** `hard_waits(self_loop=True)` passed only by `make_plan`, so `gov launch`'s lead check
  (`plan_check.py`) is unchanged: is that right, or does a lead with a self-wait now pass the plan and the launch check
  differently? Nested cycles broken more than once: can that ever break a wait of a ticket outside the component?
- Can any graph make the new `_order` loop forever, drop a ticket from the batches, or break a wait that is not part
  of a cycle?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree. Run nothing that writes. You may run the tests read-only (with
  `-p no:cacheprovider`) through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`.
  No GPU. Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything under
  `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own, different words;
  then answer from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full (the launcher keeps it in this worktree's log; the CTO
  transcribes it): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per
  line, every finding with its two lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S4"]}`.
