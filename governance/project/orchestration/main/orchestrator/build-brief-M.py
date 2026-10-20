"""Assemble the lead brief of the short round on W1-38 that takes the test-folder deny rule out of the template (DEC-664)."""
import sys

B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
base = sys.argv[1]  # the commit of w1/integrate the worktree is cut from
old = open(B + "W1-31b-A5-head.md", encoding="utf-8").read()
start = old.index("**By the owner's finish line (DEC-584)")
end = old.index("## The round: one piece")
rules = old[start:end].replace("DAEO-6mk8", "DAEO-3ef2").replace("CAP-04.b", "CAP-38.b")
assert "DAEO-6mk8" not in rules and "CAP-38.b" in rules

TOP = f"""You are the ticket lead for one short round on ticket `DAEO-3ef2` (`W1-38`, rulesync adapters), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-38` on branch `w1/W1-38`, cut from `w1/integrate` at `{base}`. The ticket is reopened for one round that the owner ordered (DEC-664): the template's permission source denies every edit of the acceptance-test folder, the independent test designer's included, so in a project made from the template no test designer can write acceptance tests and no ticket there can reach a clean close. That breaks a Wave 1 exit criterion. You run the ticket loop for it. Its implementer is an engineer (brief A2). **Review: you commission no reviewer. The main orchestrator has a fresh reviewer probe the final code before the merge (the owner's order, DEC-664); your DONE return names the head, and nothing is committed after it.**

"""

PIECES = """## The round: first a separate designer pass on three cases (DEC-665, DEC-669), then one piece, test designer first (one designer, then one engineer)

Read first, in `docs/DECISION_REGISTER.md`: DEC-069, DEC-162, DEC-312, DEC-315, DEC-471, DEC-491, DEC-584, DEC-635, DEC-636, DEC-662, DEC-664, DEC-665, DEC-669.

### First, on its own: the designer pass on three red cases (DEC-665, DEC-669)

Three acceptance cases fail on `w1/integrate` itself since the owner's apply block of 2026-10-11 (`8bb34efe`), which applied this repository's generated adapter output. The owner decided that one test-designer pass rewrites them to the decided state, as a separate designer session inside this round, with its own commit (DEC-669). It is a session of its own: not the session that writes the piece's cases below, and it runs before that one.

- `tests/acceptance/W1-49/test_w1_49_threshold.py::test_the_settings_set_the_auto_compact_window_as_an_env_key` and `::test_the_auto_compact_window_is_about_300k_tokens`: they expect the project's settings file to set `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in its env block. Decided state: rulesync writes no env block (DEC-636), and since the apply block the window is set in the user-level settings (DEC-635).
- `tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_the_research_definition_is_unchanged`: it expects `.claude/agents/research.md` to be the file the owner committed, by its hash (DEC-312). Decided state: that file is the generated file.

**For that designer.** It reads the three cases, their suites' READMEs and the decisions named, and rewrites each case to hold the decided state, through what a case may read. What each rewritten case asserts is the designer's to state from the decisions. Limits it must keep: no case reads anything under `~/.claude/` or the settings file's protected line, and no worker does; a case that could only be written by reading there is returned as a package with the designer's recommendation, not written and not deleted. No case is weakened to "always passes": a rewritten case still fails when the state it names is absent. Both READMEs get a line for each rewrite. **One commit, only under `tests/acceptance/W1-49/` and `tests/acceptance/W1-33/`, with `Task: DAEO-3ef2`, `Role: independent-test-designer`, `Implements: CAP-38.b` and three `Rewrite-Reason:` trailers, one per case, each naming its case and DEC-665.** Each is counted as a rewrite after implementation, with its reason.

You check the three green (they are rewrites to a state that already holds, so they are green after the pass, not red), run the two suites to their end, write a checkpoint, and go on. If the designer returns a package on a case, go on with the piece below and carry the package in your return.

### The piece — the template's permission source no longer denies edits of the acceptance-test folder (DEC-664)

**How it is now.** `template/.rulesync/permissions.jsonc` holds, under `permission.edit`, the line `"tests/acceptance/**": "deny"` beside `".tickets/**": "deny"`. rulesync turns each into a deny rule of the generated settings of every project made from the template, for every session, whatever its role. This repository's own source (`.rulesync/permissions.jsonc`) has no such line: here the guard has decided who may write acceptance tests since the switch-over, and the launcher leaves the test folder open to the independent test designer alone (DEC-315). The template was left behind.

**Built (the owner's words, DEC-664):** the test-folder line is taken out of the template's permission source. In this repository the guard has decided who may write acceptance tests since the switch-over, and the template follows it. MR-3 is held by the launcher and the guard, not by a deny rule that also stops the test designer.

**What must still hold, and is the point of the designer's cases and of the probe:** taking the line out opens the folder to nobody but the independent test designer. In a project made from the template, a session of any other role (engineer, product-spec, research, independent-auditor, orchestrator) is still refused a write under `tests/acceptance/`, by the guard and by the launcher's rules, and the test designer is allowed it. If that is not so with the line gone, the round does not ship the removal: return it as a package at once.

**For the designer** (W1-38's suite; stand-in projects are built in a temporary folder from the template as the suite's existing cases build them; where a case needs the real rulesync binary it says how it finds it, as the suite does now):
- the template's permission source holds no edit rule on the acceptance-test folder, and the settings generated from the template hold no deny rule on it;
- every other deny rule the template's source gives today is still generated (the ticket-folder edit rule and the install and sudo rules): the removal takes one rule and no other;
- in a stand-in project made from the template, the guard's decision on a write under the acceptance-test folder: allowed for the independent test designer on its ticket, refused for each other role. Where an existing case of another suite already holds one of these (W1-02, W1-46 and W1-47 hold guard and launcher decisions), the designer names it in the README rather than writing it again, and writes only what no suite holds for a project made from the template;
- the adapter check on the template's own sources and committed output, if the suite has such a case today, stays green with the line gone;
- existing cases of the suite that expect the test-folder deny rule in the template's output are rewritten to the decided state, each with a `Rewrite-Reason:` trailer naming DEC-664, and counted as rewrites after implementation.

**The engineer** changes only what the ticket's paths allow: the template's permission source, and whatever of `src/gov/adapters/**` and `tests/unit/adapters/**` the designer's cases need (probably nothing). This repository's own `.rulesync/` source is NOT changed, and no generated file of this repository changes: if one would, return that as a package (applying generated output here is the owner's step). The guard, the launcher and `src/gov/guard/**` are NOT changed: they lie outside this ticket's paths. If MR-3 cannot be shown to hold without changing them, that is a package.

**Never, by anyone in this round:** read, print, search or copy this repository's own held-out file or its settings file, in the worktree or the main repository, or type either path in a command (write "the held-out file", "the settings file"). The cases never touch the real files: a case that would need them is not written.

### Order and return

- **Order:** the separate designer pass on the three cases (one session, one commit, checked green), checkpoint; then the piece: designer (one session, one commit), checked red for the stated reasons, checkpoint, engineer, checkpoint. Then you run W1-38's suite, the other suites that read the template's permission source or build a project from the template (search `tests/acceptance` for `permissions.jsonc` and for `template`: W1-01, W1-15, W1-26, W1-30, W1-47 among them; run each you find), the unit tests, and the whole of `tests/` in the form the close uses (`python3 -m pytest tests -n auto` with the close's plugin keeping the declared cases out, then the entries of `tests/acceptance/serial-only.txt` alone; a case that fails under load and passes alone is named, DEC-372), and the validator (`python3 docs/plan/tools/validate_s1.py | tail -1`). Another lead may be running workers in dev-tier clones at the same time; a case that fails under that load and passes alone is named as such. You read the diff line by line. You return **DONE with the head named and nothing committed after it**, or PACKAGES.
- **A live-model case that varies (DEC-671):** `W1-49/test_w1_49_live_session.py::test_after_the_compaction_the_session_names_the_loop_counts` failed once in the main tree's serial run and passed alone. If it fails for you, run it alone once more and report both results; nobody touches it.
- **In the return:** built / package; the commits with their Task, Role and Implements trailers checked one by one; the residual list; rewritten and added cases counted; learning metrics.
- **`allowed_paths` of the ticket (its file lists them):** `template/.rulesync/**`, `.rulesync/**`, `src/gov/adapters/**`, `tests/unit/adapters/**`, `template/governance/kernel/checks/adapter-portability*`. A change the engineer needs outside the paths is a package.
- **Decision packages:** anything that would open the acceptance-test folder to a role other than the independent test designer, take out another deny rule, change the guard or the launcher, or change this repository's own sources or generated output is the owner's and is returned at once.
- Read DEC-413, DEC-416, DEC-420, DEC-436, DEC-449, DEC-454, DEC-460, DEC-462, DEC-476, DEC-498, DEC-511, DEC-527, DEC-549. Nobody lists `~/gov-os-workbench/` or any folder in it, nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/` (word for word in each worker's brief). **A worker never copies or clones this tree.**
"""
twelve = open(B + "TWELVE-FIELDS.md", encoding="utf-8").read()
text = (
    TOP + rules + PIECES + "\n" + twelve + "\n"
    + open(B + "LEAD-common.md", encoding="utf-8").read() + "\n"
    + open(B + "LEAD-steps.md", encoding="utf-8").read() + "\n"
    + "**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
)
with open(B + "W1-38-A5-runM.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text), text.count("DAEO-6mk8"), text.count("W1-31"))
