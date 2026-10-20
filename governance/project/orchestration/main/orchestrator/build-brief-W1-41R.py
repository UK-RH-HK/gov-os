"""Assemble the lead brief of the round on W1-41: adoption names and enforces the two embedding policies, doctor and rebuild say when no namespace is embedded (DEC-694, DEC-700). python3 build-brief-W1-41R.py <base commit>"""
import sys

B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
base = sys.argv[1]
old = open(B + "W1-31b-A5-head.md", encoding="utf-8").read()
start = old.index("**By the owner's finish line (DEC-584)")
end = old.index("## The round: one piece")
rules = old[start:end].replace("DAEO-6mk8", "DAEO-cdoi").replace("CAP-04.b", "CAP-44.b")
assert "DAEO-6mk8" not in rules and "CAP-44.b" in rules

TOP = f"""You are the ticket lead for one round on ticket `DAEO-cdoi` (`W1-41`, `gov adopt --lite` and the legacy importer), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-41` on branch `w1/W1-41`, cut from `w1/integrate` at `{base}`. The ticket is reopened for one round that the owner ordered (DEC-694): an adopted project can end with a path map in which no namespace is embedded, so its semantic index stays empty after every rebuild, and nothing says why. You run the ticket loop for it. Its implementer is an engineer (brief A2). **Review: you commission no reviewer. The main orchestrator has a fresh reviewer probe the final code before the merge (DEC-694); your DONE return names the head, and nothing is committed after it.**

**The guard in this worktree refuses a tool it does not know (DEC-685), `Monitor` and every `mcp__` tool among them. Wait for background work with Bash (`until [ -s <file> ]; do sleep 20; done`), as the common part says. A foreground command that outlives the tool's limit is killed: start every long run in the background and wait for its exit-code file.**

"""

PIECE = """## The round: one piece, test designer first (one designer, then one engineer)

Read first, in `docs/DECISION_REGISTER.md`: DEC-069, DEC-380, DEC-381, DEC-388, DEC-517, DEC-584, DEC-616, DEC-686, DEC-693, DEC-694, DEC-700. Read `tests/acceptance/W1-41/README.md` and how its cases build and adopt a stand-in project; the ticket file `.tickets/DAEO-cdoi.md` (read-only; its allowed paths were widened for this round by DEC-694).

### How it is now (the diagnostic of DEC-693)

- A namespace of `governance/project/path-map.yaml` may carry `embedding_policy`. The semantic index embeds the chunks of a file only when every namespace that holds the file says exactly `embedded` (`src/gov/retrieval/semantic.py`, DEC-381); any other value, a missing field and a file in no namespace are "not embedded" (DEC-380, DEC-388).
- The template's own path map states no `embedding_policy` for any namespace. Nothing in `gov adopt` (`src/gov/adopt/`), the kernel's adopt skill (`template/governance/kernel/skills/adopt/SKILL.md`) or the path-map schema says which values the field takes.
- In the adopted a-dev dev-tier clone the adoption's path map gave 20 namespaces the text "not stated by the programme" and none `embedded`. A full `gov rebuild` answered "semantic: recreated", the index held no vector, every retrieval answered `FACET_UNAVAILABLE`, and the doctor's semantic canary missed: no error and no finding anywhere.

### Built (the owner's words, DEC-694, with DEC-700)

1. **The adopt skill and the path-map stage of adoption name the two valid values**, `embedded` and `not embedded`: the skill says what each means and that every namespace states one; the stage's refusal names them.
2. **Adoption refuses a target path map in which a namespace has another value, or in which no namespace is embedded.** Under DEC-700 a namespace without the field counts as "another value" here: adoption states each namespace's policy explicitly. The refusal is a refusal of the stage, in the form the stage's other refusals take (a code, a message, nothing written), and it names each namespace at fault and the two valid values. Which stage carries it: the stage that records the target path map (A3), and any earlier stage that reads the project's path map only if a case shows that a later refusal would come too late (you settle that from the code with evidence; a choice that changes the order of the stages is a package).
3. **`gov doctor` and `gov rebuild` report "no namespace is embedded"** when the project's path map has no namespace that says `embedded`, instead of leaving an empty semantic index unexplained. The rebuild still recreates its stores and says so; its answer for the semantic store carries the words "no namespace is embedded". The doctor names it in its semantic part, by those words, beside the canary's answer. Exit codes: the rebuild's stays as it is today when its stores are recreated; the doctor treats it as it treats its other states that leave a facet without evidence (you state which, from the code). **Outside adoption nothing is refused for it:** an unknown or missing value is still read as "not embedded" (DEC-380, DEC-388 stay), and the retrieval, the index and the schema are not changed.

**For the designer** (W1-41's suite; stand-in projects in a temporary folder, as the suite builds them; for the doctor and the rebuild, the suites that already ask them show the form, and nothing loads a model: a case that needs vectors is not this round's):
- adoption with a path map whose namespaces all state one of the two values and one or more `embedded`: goes on as before;
- one namespace with another text (a free text, a near spelling such as `Embedded` or `embedded ` with a trailing space, `not_embedded`), one with the field missing, and a map where every namespace says `not embedded`: each refused, nothing written, the refusal naming the namespace(s) and the two values;
- the skill names both values (a case may read the kernel skill's text);
- `gov rebuild` and `gov doctor` on a project whose path map has no embedded namespace: each says "no namespace is embedded"; on a project with one embedded namespace, neither says it;
- outside adoption, an unknown value still reads as "not embedded" (the suites of DEC-380 and DEC-388 hold this: name their cases in the README rather than writing them again).
Existing W1-41 cases whose stand-in path maps state no policy will now be refused at the stage: the designer brings their stand-ins to state the policies, each such rewrite with a `Rewrite-Reason:` trailer naming DEC-694 and counted as "planned: behaviour ordered". **Other suites that adopt a stand-in through these stages** (search `tests/acceptance` for `adopt`): list each that breaks, in your return; the designer rewrites only cases of suites the round's KPIs name (W1-41's), and a break elsewhere is a package with the list.
The designer's brief states behaviour and sources only, never a name of the code to be written (DEC-462).

**The engineer** changes only what the ticket's paths allow: `src/gov/adopt/**`, `tests/unit/adopt/**`, `src/gov/doctor/**`, `tests/unit/doctor/**`, `src/gov/rebuild/**`, `tests/unit/rebuild/**`, `template/governance/kernel/skills/adopt/SKILL.md` (and the ticket's earlier paths, not needed here). **Not changed:** `src/gov/retrieval/**`, `src/gov/config/**`, the path-map schema, the template's path map, the generated copies of the skill (`.claude/skills/`, `.rulesync/`, `template/.rulesync/`: the main orchestrator regenerates them after the merge, DEC-616). If the piece seems to need one of them, that is a package.

**The danger of this piece, which the probe will look for:** an adoption that still records a path map embedding nothing; a refusal that writes part of a record; a near spelling that slips through; the doctor or the rebuild failing a project they served before; a change to how retrieval reads the field.

**Never, by anyone in this round:** read, print, search or copy this repository's own held-out file or its settings file, in the worktree or the main repository, or type either path in a command (write "the held-out file", "the settings file"). The cases never touch the real files. Nobody runs `gov adopt`, `gov rebuild` or `gov close` against this worktree or the main tree: the cases use stand-ins.

### Order and return

- **Order:** the designer (one session, one commit), checked red for the stated reasons, checkpoint; the engineer, checkpoint. Then you run W1-41's suite, `tests/unit/adopt`, `tests/unit/doctor`, `tests/unit/rebuild`, every other suite that adopts, rebuilds or asks the doctor (search `tests/acceptance` for them), and the whole of `tests/` in the form the close uses (`python3 -m pytest tests -n auto` with the close's plugin keeping the declared cases out, then the entries of `tests/acceptance/serial-only.txt` alone; a case that fails under load and passes alone is named, DEC-372), and the validator (`python3 docs/plan/tools/validate_s1.py | tail -1`). Another lead is running workers in dev-tier clones at the same time; a case that fails under that load and passes alone is named as such. You read the diff line by line. You return **DONE with the head named and nothing committed after it**, or PACKAGES.
- **A live-model case that varies (DEC-676):** `W1-49/test_w1_49_live_session.py::test_after_the_compaction_the_session_names_the_loop_counts` is flaky; the W1-46 live-session cases need the network (DEC-689). If one fails for you, run it alone once more and report both results; nobody touches it.
- **In the return:** built / package; which stage refuses and why there; the refusal's code and words; the doctor's and the rebuild's words and exit codes; the commits with their Task, Role and Implements trailers checked one by one; the suites that adopt and whether any broke; the residual list; rewritten and added cases counted; source lines against 80; learning metrics.
- **Decision packages:** anything that would change the retrieval's reading of the field, the schema, the template's path map, a generated file or the order of the stages, or a suite outside W1-41 that the round breaks, is the owner's and is returned at once.
- Read DEC-413, DEC-416, DEC-420, DEC-436, DEC-449, DEC-454, DEC-460, DEC-462, DEC-476, DEC-498, DEC-511, DEC-527, DEC-549. Nobody lists `~/gov-os-workbench/` or any folder in it, nobody reads anything under `~/gov-os-workbench/w1-tests/` or `qualification-oracle/` (word for word in each worker's brief). **A worker never copies or clones this tree. Nobody reads under `~/.claude/`.**
"""
twelve = open(B + "TWELVE-FIELDS.md", encoding="utf-8").read()
text = (
    TOP + rules + PIECE + "\n" + twelve + "\n"
    + open(B + "LEAD-common.md", encoding="utf-8").read() + "\n"
    + open(B + "LEAD-steps.md", encoding="utf-8").read() + "\n"
    + "**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
)
with open(B + "W1-41-A5-round.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text), text.count("DAEO-6mk8"), text.count("DAEO-cdoi"))
