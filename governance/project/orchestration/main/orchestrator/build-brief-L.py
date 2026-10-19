"""Assemble the lead brief of the short round on W1-38 (DEC-635, DEC-641)."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
old = open(B + "W1-30-A5-J-head.md", encoding="utf-8").read()
start = old.index("**By the owner's finish line (DEC-584)")
end = old.index("## The round: six small pieces")
rules = old[start:end].replace("DAEO-2lwj", "DAEO-3ef2")
assert "CAP-38.b" in rules

TOP = """You are the ticket lead for one short round on ticket `DAEO-3ef2` (`W1-38`, rulesync adapters), working only in the worktree `/home/usain/gov-os-worktrees/W1-38` on branch `w1/W1-38`. The ticket is reopened for one round that the owner ordered (DEC-635): this repository's generated adapter output cannot be applied, and the adapter check cannot go green, until one step is built. With that check red no ticket can close cleanly, which breaks a Wave 1 exit criterion. You run the ticket loop for it. Its implementer is an engineer (brief A2). **Review: you commission no reviewer. The main orchestrator has a fresh reviewer probe the final code before the merge (the owner's order, DEC-635); your DONE return names the head, and nothing is committed after it.**

"""

PIECES = """## The round: one piece, test designer first (one designer, then one engineer)

Read first, in `docs/DECISION_REGISTER.md`: DEC-162, DEC-218, DEC-471, DEC-584, DEC-631, DEC-634, DEC-635, DEC-641.

### The piece — the adapter check applies the held-out step after its generation (DEC-635)

**How it is now.** The adapter-portability check (`python3 -m gov.adapters.portability`, declared in `template/governance/kernel/checks/adapter-portability.yaml`) generates with rulesync from the project's sources into an empty temporary folder and compares each generated file byte for byte with the project's. A project's settings must also hold one Read deny rule per held-out path (DEC-162). Those rules are never written into a rulesync source (the owner's rule: no source names a held-out path). They are written into a settings file by the existing generator, `python3 -m gov.guard.heldout`, from the project's held-out file under `governance/project/` (key `held_out_paths`); the generator can be given the settings file to write. So today a project that has the held-out rules can never match what rulesync alone generates.

**Built:** inside its temporary generation the check applies the same generator's step to the generated settings before it compares, when and only when the project has a held-out file. So the project's settings are held to exactly what "rulesync generate, then the held-out step" produces. A project without a held-out file is compared as now. A held-out file that cannot be read or is not of its stated shape makes the check not green (it does not fall back to the comparison without the step), and no finding, message or log line of the check carries a held-out path. The generator itself (`src/gov/guard/heldout.py`) is NOT changed: it lies outside this ticket's paths and no guard change is made in Wave 1 (DEC-577). If the comparison cannot be made exact without changing it, return that as a package.

**For the designer** (W1-38's suite; the cases use stand-in projects built in a temporary folder with a stand-in held-out file that names stand-in paths; where the suite's existing cases need the real rulesync binary they say how they find it):
- a project whose settings are "generated, then the step" is green on the settings;
- the same project with the Read deny rule missing from its settings is red on the settings (the rule lost is caught);
- the same project with a Read deny rule that the held-out file does not give is red on the settings;
- a project without a held-out file whose settings are what rulesync generates is green as before, and one that carries a stray Read deny rule is red;
- a project whose held-out file is broken is not green, and nothing the check prints holds one of the stand-in paths;
- running the step twice gives the same settings (the apply procedure may be repeated).

**Never, by anyone in this round:** read, print, search or copy this repository's own held-out file or its settings file, in the worktree or the main repository, or type either path in a command (write "the held-out file", "the settings file"). The module `src/gov/guard/heldout.py` is code and may be read; it names the two locations. The cases never touch the real files: a case that would need them is not written.

### Order and return

- **Order:** designer (one session, one commit), checked red for the stated reasons, checkpoint, engineer, checkpoint. Then you run W1-38's suite, the other suites that run the adapter check or build settings (search `tests/acceptance` for `portability` and for `heldout`: W1-47, W1-26, W1-30, W1-01, W1-15 among them, run each you find), the unit tests, and the whole of `tests/` in the form the close uses (`python3 -m pytest tests -n auto` with the close's plugin keeping the declared cases out, then the entries of `tests/acceptance/serial-only.txt` alone; a case that fails under load and passes alone is named, DEC-372), and the validator (`python3 docs/plan/tools/validate_s1.py | tail -1`). Another lead is running the whole of `tests/` in another worktree at the same time; a case that fails under that load and passes alone is named as such. You read the diff line by line. You return **DONE with the head named and nothing committed after it**, or PACKAGES.
- **In the return:** built / package; the commits with their Task, Role and Implements trailers checked one by one; the residual list; rewritten and added cases counted; learning metrics. Do not run the adapter check against this repository's own tree as a measurement to report in detail: the orchestrator does that after the merge.
- **`allowed_paths` of the ticket (its file lists them):** `src/gov/adapters/**`, `tests/unit/adapters/**`, `.rulesync/**`, `template/.rulesync/**` and the others it names. No rulesync source is changed in this round. A change the engineer needs outside the paths is a package.
- **Decision packages:** anything that would weaken the comparison (a file or a key left out of it), change the generator or the guard, add a command, or write a held-out path anywhere is the owner's and is returned at once.
- Read DEC-413, DEC-416, DEC-420, DEC-436, DEC-449, DEC-454, DEC-460, DEC-462, DEC-476, DEC-491, DEC-498, DEC-511, DEC-527, DEC-549. Nobody lists `~/gov-os-workbench/` or any folder in it, nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/` (word for word in each worker's brief). **A worker never copies or clones this tree.**
"""
text = TOP + rules + PIECES + "\n" + open(B + "LEAD-common.md", encoding="utf-8").read() + "\n" + open(B + "LEAD-steps.md", encoding="utf-8").read()
with open(B + "W1-38-A5-runL.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text), text.count("DAEO-2lwj"), text.count("W1-30"))
