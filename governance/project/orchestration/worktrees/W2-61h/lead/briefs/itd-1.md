You are a fresh independent test designer (MR-3; DEC-996 (B): evaluation sets are authored by the independent test designer). Ticket: DAEO-h2k3 (W2-61h, "W2-61's enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-61h` on branch `w2/W2-61h`, at head `7940249ecf0b` (a `--no-ff` merge of `w2/integrate` over the ticket's base `f46b96537d74`, which committed the ticket's claim; it changed only 16 files: `git diff --name-only f46b96537d74 7940249ecf0b`). You write an evaluation set's questions, not code and not tests: there is no implementation in this ticket.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-h2k3','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (twelve fields, status saying so). Delete nothing.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-h2k3`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-61h` and `w2/W2-61h`) and `git rev-parse --short=12 HEAD` (expect `7940249ecf0b`) and `git status --short` (expect nothing but untracked files under `.gov-runtime/`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet, so (DEC-963's form for a test designer) retrieve from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h/src python3 -m gov.cli.main retrieve "<question>" --json` (a read only; that store is at an ancestor of `f46b96537d74`, about half a day older). Retrieval only finds candidates: every gold source is then checked in this worktree's own files, at `f46b96537d74`, never in W2-00-store's. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question (callers, callees, definitions) uses the code graph's own traversal (`trace_path`, `search_graph`, `query_graph`) where you have it, small and targeted, never a load of the whole graph; where you do not have it, confirm by Grep in named folders under `src/`. **P-R1:** drop unread any `gov retrieve` result under `fixtures/evaluation/memory-retrieval/hidden/` or `fixtures/evaluation/memory-retrieval/visible/q21.yaml` to `q24.yaml`, and name in your return any such result you were served (DEC-820 (c)).
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket (this ticket has no implementer; you never read another session's work on DAEO-h2k3); (d) the hidden half of any evaluation set, by whoever is measured by it (`fixtures/evaluation/memory-retrieval/hidden/**` is refused from every worktree by the five-rule guard, W2-84).
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give them in your return. Run no glob, search or listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Command forms the guard can read (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Put anything longer in a script file under your temp folder (Write tool, literal absolute path) and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package. On an authentication error (401, 403, "Failed to authenticate"), stop and return status AUTH_REQUIRED.
- **Never copy the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. Never write in `~/gov-os-workbench`. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Install nothing (an install you need is a P1 escalation in your return). No subagents that write. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk and scratch (DEC-898):** your share is 5 GB and 200,000 files and folders, outside the tracked tree. Use the temp folder the sandbox gives you; make no clone or copy; remove what you make as soon as it is no longer needed; give its measure (`du -sh`, `du -s --inodes`) in your evidence line.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.

## What you read

- Your ticket file `.tickets/DAEO-h2k3.md` (read-only): its KPI lines (the success and failure lines below are its), its `allowed_paths` and its sources. Its `role:` line and the card may still name the independent auditor or the old size of 20: DEC-996 (B) and DEC-954 Q9a with DEC-957 hold — you, the test designer, write 28.
- The decisions it cites in `docs/DECISION_REGISTER.md`: DEC-828 (items 3 and 4), DEC-820 (d), DEC-845 (item 2), DEC-833, DEC-866, DEC-873, DEC-941, DEC-950, DEC-954 (Q9a to Q9c), DEC-957, DEC-996.
- **The form:** the module docstring of `src/gov/retrieval/measure.py` (the question form and how a source is matched). The visible half `fixtures/evaluation/memory-retrieval/visible/q01.yaml` to `q20.yaml` shows the form and the category names in use; you may read those 20, and lens B's assessment `docs/assessment/2026-10/B-memory-retrieval.md`, **only to learn the form and to avoid them: you must not copy or paraphrase any of them** (a failure KPI).
- Everything else you need to write good questions: the repository at `f46b96537d74` (governance, the Contract, the register, the kernel template, `src/gov/`, the plan, git history).

## What you write: 28 new questions

**KPI (success), in the ticket's words:** twenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources an answer must cite, in the form W2-61's visible half takes; after writing, a recorded seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half.

**The spread (DEC-954 Q9c), exactly these counts, 28 in all:**
| category | count | note |
|---|---|---|
| decisions and supersession | 5 | at least 2 whose naive answer is superseded (the gold answer is the one in force, DEC-866; the sources include the superseding entry) |
| exact strings and identifiers with file and line | 4 | the source cites the file with the exact heading or `lines` |
| callers, callees and definitions | 4 | about this repository's code under `src/gov/` |
| code facts by paraphrase | 3 | asked in words that do not repeat the code's names |
| the kernel template (roles, skills, hooks) | 3 | `template/governance/kernel/` |
| multi-file stacked | 3 | each needs two or more files: two or more `sources` entries |
| history | 2 | which commit or decision changed something; cite the record that states it |
| failure memory | 2 | a past failure or red and what was learned or done about it, as recorded |
| a plan, ticket or path-map fact | 1 | |
| an id that exists nowhere | 1 | a plausible id no source holds; the gold answer says it does not exist; give it the governing source(s) a correct "no such id" answer would rest on (e.g. the register or index that would hold it) |

Use a `category` field on each file; where the visible 20 already use a category name for the same kind, use the same name; otherwise a short kebab-case name for the row above.

**The form of each file** (measure.py's docstring governs): YAML with `question` (the text passed to `gov retrieve`), `gold_answer` (the answer as the governing source states it), `sources` (a list; each entry a map with `path` and `heading` and/or `lines: [first, last]`, or a list of such maps as alternatives), `category`. Do **not** set `id` (the file name gives it). Optional `commit: f46b96537d74`. A `heading` is the full text of one line of the file, matched exactly after trailing whitespace is removed; a Markdown `#` heading spans to the next heading of the same or a higher level. Prefer the narrowest span that holds the answer. No source under `fixtures/evaluation/` or `docs/assessment/2026-10/B-memory-retrieval.md` (those never count).

**KPI (success): every gold source exists at `f46b96537d74` and holds its answer, cited by path and heading or line (DEC-828 item 4).** Check each source against the file itself (read the cited span and confirm the answer is there), not against the question file. Your worktree is at `7940249ecf0b`; a source must hold its answer at both commits: for a file the merge did not change (`git diff --quiet f46b96537d74 7940249ecf0b -- <path>` exits 0) the worktree's file is the check; for one of the 16 it did change, also read the cited span at `f46b96537d74` (`git show f46b96537d74:<path>`) and confirm the same lines or heading hold the same answer there, or choose another source. Also confirm each source resolves the way the measure resolves it: a small script file under your temp folder that takes a path, a heading and/or lines as command-line arguments (never a question or an answer) and calls the measure's span resolution (`_span` in `gov.retrieval.measure`, with this worktree's `PYTHONPATH`) prints the span it resolves to, or the fault.

**The order (DEC-828 item 3, the brief's rule):**
1. Compose all 28 first, in your own context, numbered n01 to n28, each with its category, every source checked as above. Validate each one's form in memory before it is written (the YAML you will write parses and carries the three required fields and well-formed sources).
2. Then the recorded seeded draw, stratified by category, over the numbers and categories only (no text in the script): seed = `int("f46b96537d74", 16)`, Python's `random.Random(seed)`. Recommended rule: allocate the 4 visible slots across categories in proportion to their counts by largest remainder (count × 4 / 28), ties broken by the seeded generator; within each category that receives a slot, the seeded generator picks which question. A category of 1 thus stays wholly hidden. If you choose another stratified rule, state it.
3. Then write: the 4 drawn to `fixtures/evaluation/memory-retrieval/visible/q21.yaml` to `q24.yaml` (in draw order), and the 24 others to `fixtures/evaluation/memory-retrieval/hidden/h01.yaml` to `h24.yaml`. Nothing changes in any question after the draw.
4. **After writing:** run W2-61's measure's form check on the 4 visible files only: a script file under your temp folder that loads each of `visible/q21.yaml` to `q24.yaml` with the measure's own loader (`_load` in `gov.retrieval.measure`, with this worktree's `PYTHONPATH`, root this worktree), prints only the id, the number of sources and "ok" or the fault. **Never `--part hidden` or `--part all`, and never open, cat, read, grep or load a hidden file after writing it.** If any check of your hidden files is refused by the guard, take it; a validation you could not do after writing is named in your return.

**Allowed paths, and nothing else:** `fixtures/evaluation/memory-retrieval/hidden/**` and `fixtures/evaluation/memory-retrieval/visible/q21.yaml` to `q24.yaml`. No other file in the tree (no README, no tests, no notes).

**KPI (success): nothing quoted anywhere (DEC-820 (d)).** No question or answer, not even in part, in your commit message, your return, a log, a script or any file outside the 28 question files. Your return gives counts only.

**KPIs (failure), each must not happen:** a hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work (write nothing hidden anywhere but `hidden/`); a question copied from or paraphrasing lens B's visible 20; a gold source that does not hold its answer.

Quality: questions a developer or agent on this repository would really ask; unambiguous; one gold answer each, stated as the source states it; spread across the repository (not all from one file or one decision); not answerable from the question's own words; ids and names exact.

## Commit

Commit only the 28 files, in one commit, with the trailers in the final block. The subject names the ticket and the counts only, e.g. "W2-61h: 28 new memory questions, 24 hidden and 4 visible (q21-q24), seeded stratified draw".

    git commit -m "<subject>" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-828,DEC-845,DEC-954,DEC-957" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Stage the files by their exact paths (no `git add -A` or `git add .`). After the commit run `git log --oneline -2` and `git status --short` and give them in your evidence.

## Return

In `evidence`: the sandbox check's result (a) and (b); the `gov.__file__` line; the commit's 12-digit hash and its trailers; the seed, the draw rule and the draw's record as counts only (per category: total, visible, hidden); the visible form check's output (ids and ok/fault only); your scratch measure. In `tests`: the visible form check and the source checks (counts: sources checked, sources resolved). In `discoveries`: whether `gov retrieve` was used and how many queries; read refusals met (count and form, no contents); any P-R1 result served. No question or answer text anywhere in your return.

One message, your last, complete in itself, with no transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so.
