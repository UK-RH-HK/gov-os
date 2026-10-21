"""Assemble the lead brief of the short round on W1-02: the guard refuses a tool it does not know (DEC-685). python3 build-brief-W1-02R9.py <base commit>"""
import sys

B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
base = sys.argv[1]
old = open(B + "W1-31b-A5-head.md", encoding="utf-8").read()
start = old.index("**By the owner's finish line (DEC-584)")
end = old.index("## The round: one piece")
rules = old[start:end].replace("DAEO-6mk8", "DAEO-emkd").replace("CAP-04.b", "CAP-58.a")
assert "DAEO-6mk8" not in rules and "CAP-58.a" in rules

TOP = f"""You are the ticket lead for one short round on ticket `DAEO-emkd` (`W1-02`, the PreToolUse default-deny guard), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-02` on branch `w1/W1-02`, cut from `w1/integrate` at `{base}`. The ticket is reopened for one round that the owner ordered (DEC-685): the guard answers allow for any tool whose name it does not know, a file-writing tool included, which breaks its default-deny design. Under the finish line that is a fail-open hole in ordinary work. You run the ticket loop for it. Its implementer is an engineer (brief A2). **Review: you commission no reviewer. The main orchestrator has a fresh reviewer probe the final code before the merge (the owner's order, DEC-685); your DONE return names the head, and nothing is committed after it.**

"""

PIECE = """## The round: one piece, test designer first (one designer, then one engineer)

Read first, in `docs/DECISION_REGISTER.md`: DEC-069, DEC-113, DEC-117, DEC-124, DEC-125, DEC-163, DEC-315, DEC-434, DEC-584, DEC-664, DEC-685. Read `tests/acceptance/W1-02/README.md` and how the suite's cases ask the guard.

### How it is now

`src/gov/guard/decide.py`: the decision knows the read tools `Read`, `Grep`, `Glob`, the write tools `Edit`, `Write`, `NotebookEdit` (judged by their path field), and `Bash` (judged by the write targets it can read). **Every other tool name ends in `return "allow"`.** The project's hook source registers the PreToolUse command with no matcher, so every tool call of a session reaches the guard. The probe of the W1-38 round asked the guard about `MultiEdit` on a path under the acceptance-test folder and got allow for every role, an engineer and a session with no role included.

### Built (the owner's words, DEC-685)

1. **`MultiEdit` is judged exactly like `Edit`, by its file path, for every role**: allowed paths, the acceptance-test folder rule, the freeze, a missing path, long paths, the read rule and the held-out rule as they apply to `Edit` today, and the containment's count of allowed writes where `Edit` is counted.
2. **Any tool the guard does not know is refused (default-deny), unless it is a known read-only tool.** The refusal names the tool and says it is not known to the guard.

**What "known" has to mean, so that ordinary work goes on (yours to settle with evidence, inside the owner's rule):**

- The guard holds one explicit list of the tool names it lets through without a path judgement. A name is on it only if the tool cannot itself write a file of the project or run a shell command: the three read tools, and the harness's own tools that do neither (for example the tool that starts a subagent, whose own calls reach the guard themselves; the tools that fetch or search the web; the ones that list, stop or message tasks and agents; the question, plan, to-do, skill and tool-search tools). **Each entry has a one-line reason beside it, in the code or the suite's README.**
- **Get the real tool names from the installed CLI, not from memory:** start one harmless headless session (`/home/usain/.local/bin/claude -p --output-format json`, in this worktree, in the background, waited for) that is asked only to list the exact names of every tool it has, deferred ones included, and to use none. Report that list in your return. **It also answers the owner's question: does the installed CLI offer `MultiEdit` at all, and can a launched worker (through `gov launch`, with the `--allowedTools` it is started with) or a lead (started with `--allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" "Agent" "Monitor" "TaskStop"`) call it today? Answer both from what you ran and from `src/gov/launch/launcher.py`, and say which it was.**
- **A tool that runs a shell command or writes a file by a path and is not `Bash`, `Edit`, `Write`, `NotebookEdit` or `MultiEdit`** (look at `Monitor`, and at anything else the list shows) is not put on the list by default. Either it is judged like its like (a command field read as `Bash`'s is, a path field as `Edit`'s is), if that is a few lines inside `src/gov/guard/**`, or it is refused. **Leads are started with `Monitor` allowed and the common part of this brief tells you to wait in the foreground with Bash, so a refused `Monitor` is acceptable; say in your return which you chose and what it stops.**
- **Tools whose names begin `mcp__`** are not known: refused. Say so in the residuals.
- **If a tool that the leads, the launched workers or the main orchestrator's own session need in ordinary work can neither be listed with an honest reason nor judged, return that as a package at once**, with the tool, what needs it, and your recommendation. Do not list a tool just to keep it working.
- A session with no role, or an unknown role, stays read-only: the known read-only tools pass for it as the three read tools do today, a write tool or an unknown tool does not.
- The freeze: an unknown tool is refused whether frozen or not; the listed tools pass as the read tools do today.

**For the designer** (W1-02's suite; the cases ask the guard as the suite's existing cases do, on stand-in projects in a temporary folder):
- `MultiEdit` gets the answer `Edit` gets, case by case, for each role and for no role: inside and outside the allowed paths, under the acceptance-test folder (the test designer alone allowed), frozen, with no path, on a protected path;
- a made-up tool name, an empty name, a name that differs from a known one by case or by a trailing space, and an `mcp__` name are refused, for every role, the orchestrator included, with a reason that names the tool;
- each tool on the known list passes, and the three read tools and `Bash`, `Edit`, `Write`, `NotebookEdit` answer as before the round (the existing cases hold most of this: name them in the README rather than writing them again);
- a tool with a command or a path that is not on the list is refused or judged as the round decides (the designer states the behaviour; the lead gives it the decided behaviour once you have settled it from the tool list above, before the designer starts);
- a guard that fails or times out on an unknown tool still does not let the call through (the suite's existing failure cases show the form).
The designer's brief states behaviour and sources only. Existing cases that expect allow for an unknown tool, if any, are rewritten with a `Rewrite-Reason:` trailer naming DEC-685 and counted.

**The engineer** changes only what the ticket's paths allow: `src/gov/guard/**`, `template/governance/kernel/hooks/pretooluse*`, `tests/unit/guard/**`. The hook sources under `.rulesync/` and `template/.rulesync/`, the launcher and every generated file are NOT changed: if the piece seems to need one, that is a package. The guard's deadline and its answer on its own failure are not changed.

**The danger of this piece, which the probe will look for:** a file-writing or command-running tool left on the known list; a spelling of a tool name that slips past the list; ordinary work stopped (a lead that cannot start a subagent, a worker that cannot read); the guard slower than its limit.

**Mind your own session:** the guard that judges your calls and your workers' calls in this worktree is this worktree's code. Once the engineer's commit exists, a tool the new list does not know is refused to you too. That is the behaviour working; note it, do not work round it.

**Never, by anyone in this round:** read, print, search or copy this repository's own held-out file or its settings file, in the worktree or the main repository, or type either path in a command (write "the held-out file", "the settings file"). The cases never touch the real files.

### Order and return

- **Order:** the tool list from the installed CLI and the decided known list first (written into the designer's brief as behaviour); the designer (one session, one commit), checked red for the stated reasons, checkpoint; the engineer, checkpoint. Then you run W1-02's suite, `tests/unit/guard`, every other suite that asks the guard (search `tests/acceptance` for the hook's file name and for `decide`; W1-28, W1-38, W1-46, W1-47 among them), and the whole of `tests/` in the form the close uses (`python3 -m pytest tests -n auto` with the close's plugin keeping the declared cases out, then the entries of `tests/acceptance/serial-only.txt` alone; a case that fails under load and passes alone is named, DEC-372), and the validator (`python3 docs/plan/tools/validate_s1.py | tail -1`). Another lead is running workers in dev-tier clones at the same time; a case that fails under that load and passes alone is named as such. You read the diff line by line. You return **DONE with the head named and nothing committed after it**, or PACKAGES.
- **A live-model case that varies (DEC-676):** `W1-49/test_w1_49_live_session.py::test_after_the_compaction_the_session_names_the_loop_counts` is flaky. If it fails for you, run it alone once more and report both results; nobody touches it.
- **In the return:** built / package; the full tool list the CLI gave; the known list with its reasons; the answer on `MultiEdit` for workers and leads today; what `Monitor` and `mcp__` tools get; the commits with their Task, Role and Implements trailers checked one by one; the residual list; rewritten and added cases counted; source lines against 60; learning metrics.
- **Decision packages:** anything that would change the hook registration, the launcher, a generated file, the guard's deadline or its failure answer, or that would list a tool without an honest reason, is the owner's and is returned at once.
- Read DEC-413, DEC-416, DEC-420, DEC-436, DEC-449, DEC-454, DEC-460, DEC-462, DEC-476, DEC-498, DEC-511, DEC-527, DEC-549. Nobody lists `~/gov-os-workbench/` or any folder in it, nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/` (word for word in each worker's brief). **A worker never copies or clones this tree. Nobody reads under `~/.claude/`.**
"""
twelve = open(B + "TWELVE-FIELDS.md", encoding="utf-8").read()
text = (
    TOP + rules + PIECE + "\n" + twelve + "\n"
    + open(B + "LEAD-common.md", encoding="utf-8").read() + "\n"
    + open(B + "LEAD-steps.md", encoding="utf-8").read() + "\n"
    + "**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
)
with open(B + "W1-02-A5-run9.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text), text.count("DAEO-6mk8"), text.count("W1-31"))
