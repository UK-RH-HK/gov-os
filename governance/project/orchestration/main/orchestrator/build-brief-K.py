"""Assemble the lead brief of the round on P-42 and P-43: a new top and pieces, the rules section of the last
round's head brief, the common part and the steps."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
old = open(B + "W1-30-A5-J-head.md", encoding="utf-8").read()
start = old.index("**By the owner's finish line (DEC-584)")
end = old.index("## The round: six small pieces")
rules = old[start:end]
assert "## Rules added since the common part was written" in rules

TOP = """You are the ticket lead for a short fix round on ticket `DAEO-2lwj` (`W1-30`), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-30` on branch `w1/W1-30`. The ticket is reopened for one round that the owner ordered (DEC-627, DEC-628): after this repository's adoption, two checks of `gov check` stay red for reasons that are faults of the product, and a third is red on a stale source of this repository. With them red no ticket can close cleanly, which breaks a Wave 1 exit criterion. You run the ticket loop for it. Its implementer is an engineer (brief A2). **Review (FULL): you commission no reviewer. The main orchestrator has a fresh reviewer probe the final code before the merge (DEC-137, DEC-498); your DONE return names the head, and nothing is committed after it.**

"""

PIECES = """## The round: three small pieces, test designer first (one designer, then one engineer)

Read first, in `docs/DECISION_REGISTER.md`: DEC-584, DEC-612, DEC-613, DEC-620, DEC-622, DEC-627, DEC-628, DEC-633, DEC-634. The check declarations are the twenty files of `template/governance/kernel/checks/`; this repository's `gov check` reads them there (DEC-579). The last round's cases are the files `test_w1_30_r15_*.py` of `tests/acceptance/W1-30/`; read how they build a stand-in project and plant a violation.

### Piece 1 — the authority check declares `human_gate` as well (DEC-627)

**Measured.** No declaration states the policy key `human_gate`, so every project is red on `policy-human_gate`. The hard-block check `core-authority` already holds the gate rule: it reports a record that cites, under `approval`, a decision package that is not accepted, and an open ticket named in the `constrains` of a dead package (the findings come from the decision checker, which the authority check runs).
**Built:** the declaration of `core-authority` states both keys, `authority` and `human_gate`.
For the designer, by DEC-613's rule (a key is declared only by a check that a planted violation of that policy turns red): in a stand-in project a violation of the gate rule is planted (a record that cites under `approval` a decision package whose status is not accepted); `core-authority` is red on it and green without it; with the declaration as decided, `gov check` reports no `policy-human_gate` finding; the case of the last round that holds the exact set of declared pairs is brought to the new set (a rewrite with its `Rewrite-Reason:` trailer). Nothing else gains a key.

### Piece 2 — the context check measures the project's own tickets only (DEC-628)

**Measured.** The kernel's template ticket (`governance/kernel/templates/ticket.md` in an adopted project, `template/governance/kernel/templates/ticket.md` here; id `PROJ-0000`, type `task`) is a record of the store. The context-reproducibility check takes every store record of type `ticket` or `task` for a ticket, tries to build a context for the template ticket, and fails ("ticket 'PROJ-0000' not found"). The check is red in every project that holds the kernel's templates, which is every adopted project.
**Built:** the check measures the tickets of the project's ticket folder (`.tickets/`), whatever name their type has, and no other record of the store.
For the designer: a project that holds the kernel's template ticket and whose own tickets are sound is green; a project ticket with a missing input is still red, and the ticket is named; a project that has no ticket of its own (the template ticket alone, or none) reads unmeasured and is not green; a ticket of the project is measured whether its type is `task` or `ticket`. No case may let a real ticket leave the measurement: a ticket file the check cannot read is named and not green.

### Piece 3 — this repository's hooks source (DEC-634)

**Measured.** `.rulesync/hooks.jsonc` of this repository is an early form: six events, no matcher, no time limit, commands at a path this repository does not have. What it generates is not what this repository registers, so the adapter check is red on the settings and the generated output cannot be applied.
**Built (engineer; a correction of this repository's own source, the template's source is not changed):** the source generates exactly the five entries that `python3 -m gov.guard.hooks` lists in the main repository (run it there by that command, which is the permitted way to see the registered hooks; never read the settings file itself): the events PreToolUse, PostToolUse, PostToolUseFailure, PreCompact and SessionStart, each with the matcher and the command of that listing, each with `"timeout": 60`. **No `stop` and no `subagentStop` entry:** they are switched on at a later step that the owner controls (DEC-444). The template's source `template/.rulesync/hooks.jsonc` shows the form of a matcher and a time limit.
For the designer: only if a case of an existing suite holds this file to another form (search `tests/acceptance` for the file's name); then that case is brought to the decision with its reason. Otherwise the measure is the adapter check, and the lead verifies it: generate into a temporary folder outside the worktree with the adapter check's own call (`rulesync generate --targets claudecode,agentsmd --features rules,hooks,permissions,subagents,commands,skills --input-roots /home/usain/gov-os-worktrees/W1-30/.rulesync`, run with the temporary folder as the working directory) and hold the `hooks` block it writes against the guard's listing: five events, the same matchers and commands, a time limit of 60 on each, no Stop, no SubagentStop. Say in your return what you compared. Nobody runs a writing rulesync command inside the worktree or the main repository.

### Order and return

- **Order:** designer (all pieces in one session, one or two commits), checked red for the stated reasons, checkpoint, engineer, checkpoint. Then you run the suites the pieces touch (W1-24, W1-26, W1-30 and any other suite a rewritten case is in, plus W1-01), the unit tests, and the whole of `tests/` in the form the close uses (`python3 -m pytest tests -n auto` with the close's plugin keeping the declared cases out, then the entries of `tests/acceptance/serial-only.txt` alone; a case that fails under load and passes alone is named, DEC-372), the validator (`python3 docs/plan/tools/validate_s1.py | tail -1`), and `gov check --json` with this worktree's code (name every check whose status or finding count differs from `w1/integrate`'s head, and why; a worktree has no built store, so say which checks you could not measure here). You read the diff line by line. You return **DONE with the head named and nothing committed after it**, or PACKAGES.
- **In the return:** per piece, built / package; the commits with their Task, Role and Implements trailers checked one by one; the residual list; rewritten and added cases counted; learning metrics.
- **`allowed_paths` of the ticket (its file lists them):** among them `src/gov/check/**`, `src/gov/context/**`, `template/governance/kernel/checks/**`, the unit-test folders, and `.rulesync/hooks.jsonc`. A change the engineer needs outside the paths is a package.
- **Decision packages:** anything that would set a policy key to informational, drop or weaken a check, change `governance/project/path-map.yaml`, add a command, switch on a Stop or SubagentStop hook, or make red-for-a-real-reason output green is the owner's and is returned at once.
- Read DEC-413, DEC-416, DEC-420, DEC-436, DEC-449, DEC-454, DEC-460, DEC-462, DEC-476, DEC-491, DEC-498, DEC-511, DEC-527, DEC-549. Nobody lists `~/gov-os-workbench/` or any folder in it, nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/` (word for word in each worker's brief). **A worker never copies or clones this tree.**
"""
text = TOP + rules + PIECES + "\n" + open(B + "LEAD-common.md", encoding="utf-8").read() + "\n" + open(B + "LEAD-steps.md", encoding="utf-8").read()
with open(B + "W1-30-A5-runK.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
