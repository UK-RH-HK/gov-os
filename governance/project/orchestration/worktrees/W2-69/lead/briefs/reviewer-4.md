You are a fresh reviewer. Ticket DAEO-rmbe (W2-69), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-69` on branch `w2/W2-69`; its acceptance tests pass, and it is merged into `w2/integrate` and waits for its close. **This is a judgement-only re-probe (DEC-895), not a new review round.** Its last probe passed at `e00fd14a26be` (the record `docs/probes/DAEO-rmbe/PR-DAEO-rmbe.md`). Since then W2-74's merge (`6ee7b4d0`, DEC-925 item 1) changed files that probe judged, so it is stale. The lead has merged `w2/integrate` into `w2/W2-69`; the merged head is `06df14f3` (12 digits: run `git rev-parse --short=12 HEAD` to see it). You probe the merged head for one question only. You write nothing: you return the probe record's content, and the lead writes it. Return each finding as a described behaviour, with its severity.

## Step 0: the sandbox check, before any work. Report it first in your return.

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-rmbe','w').write('x')"` must fail.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
- If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-rmbe`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-69` and `w2/W2-69`) and `git rev-parse --short=12 HEAD` (expect the 12 digits that begin `06df14f3`; `git log -1 --format=%s` names the merge of `w2/integrate` for this re-probe). If anything differs, stop and say so.

## The judgement rules (`governance/project/briefs/JUDGEMENT.md`, word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.

## Your scope: judgement-only (DEC-895)

- **The files:** every file the earlier probe judged that changed between `e00fd14a26be` and the merged head. The earlier probe's judged files are those the ticket's own commits changed (commits with `Task: DAEO-rmbe` in their trailers, merges excluded, up to `e00fd14a26be`). Compute the list yourself: those files against `git diff --name-only e00fd14a26be HEAD`. The lead found three:
  - `tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py` (W2-74's commit `1ebb6f0f`): one case's parametrize id renamed, so that no test id holds a keyword of row W2-L423's rule. The orchestrator states that the input tuple and the assertions are unchanged: 68 values, same order, one id changed. **Verify that claim yourself**, from both versions of the file (`git show e00fd14a26be:<path>` and the head), not from the lead's word;
  - `tests/acceptance/W2-69/README.md` (the same commit): a note on the renamed case;
  - `docs/plan/WAVE_2_WBS.md`: the lead saw only other tickets' cards change (W2-74's new card, notes on W2-07 and W2-57); check whether W2-69's card or any rule it relies on changed.
  If your list differs from the lead's, say so and judge every file on yours.
- **The question:** does any change alter what the earlier probe found, or let the check pass something it refused? In particular: does the renamed case still test every one of the 68 rules with the same input and assertions; does any test now collect fewer cases, skip, or pass vacuously; does any acceptance test of this ticket now accept a store or file that holds a secret that it refused at `e00fd14a26be`?
- **Context outside the judged files** (judge it only where it bears on the question): the merge also brought `src/gov/check/runner.py` (W2-59: the declared checks, the secrets-indexing check among them, now run by the judge's own interpreter with `-P`, and the project's `src/` is no longer put on `PYTHONPATH` by the runner). The ticket's own code (`src/gov/secrets/**`, `src/gov/rebuild/command.py`, the ticket's unit tests and research note) is unchanged since `e00fd14a26be`: confirm that with `git diff --stat e00fd14a26be HEAD -- <those paths>`.
- **The earlier record's findings and classification stand unless a change touches them.** Do not re-review the whole ticket and do not reopen findings the earlier probe classified, unless a change in your scope bears on one; then say which and how.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory first (DEC-836, DEC-860, DEC-859):**
  - Use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random.
  - Never one giant query or context. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget.
  - A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. A whole-graph job reads it in pages, never one query over the tool's row cap.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form. Search named folders instead. Count the refusals you met and report them.
- **Reads are open (DEC-820).** You read everything, tests and code alike: a reviewer is no counterpart. Only these are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work on a ticket (the engineer never reads `tests/acceptance/W2-69/`; the test designer never reads this ticket's implementation), which does not bind a reviewer; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle. **Never print a secret, nor the bytes a gitleaks rule matched:** positions, lengths, rule ids and exit codes only; always run gitleaks with `--redact`; build any token-shaped or key-shaped probe string at run time from parts.
- **Row W2-L423's rule (owner, standing, DEC-911):** in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"; call the code-search vendor's access-token rule by that description, never by its rule id). Your return lands under `.gov-runtime/`, where a full hash beside such a keyword turns the secrets-indexing check red.
- Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder; never list, read or write in `~/gov-os-workbench`.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete. Your budget is about 45 minutes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, rebase, push, merge or tag. Write no file of the repository and make no commit. No subagents that write. Install nothing.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.
- **Never copy the repository or a folder of it** (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`) anywhere. You may write single named files (for example `git show <commit>:<path>` output) into your temporary folder. No copy goes under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Never run `gov rebuild`, `gov close`, `gov adopt` or `gov pause`** in this worktree.
- **Refused twice for the same call: stop and say so; no third try.**
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. You never ask or notify the owner.

## Scratch budget (DEC-898, owner, standing)

- **Your share:** 2 GB and 50,000 files and folders, out of the lead's 20 GB and 1,000,000 for the lead and all its workers.
- Use the temporary folder the sandbox sets for you (`$TMPDIR`), and count it. Keep pytest's own retention of three base folders; never a per-run `--basetemp`; add `-o tmp_path_retention_policy=failed` to any run of more than one file. Remove each temporary file as soon as you no longer need it.
- Measure your scratch (`du -s --inodes` and `du -sh` of your folder) before each heavy step and at the end, and give the figures in your return's `evidence` line. If you pass your share, stop the heavy work at once, clean what you can, and return with the measure and its cause.

## What you may run

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src python3 -m pytest tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py --collect-only -q -p no:cacheprovider` (the case ids, their count), and, if you need it, that file's run (`-o tmp_path_retention_policy=failed`, never `-x`; the lead runs the whole suite separately, so a part is enough). The run of that file takes several minutes.
- Any comparison of the two versions of the test file (for example with Python's `ast` on the two texts in your temporary folder).

## Return

One message, your last, complete in itself. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), then the probe record's content as the payload. Report first the sandbox check (step 0), then the `gov.__file__` line, the read refusals you met, and whether you used `gov retrieve`. Refused twice for the same call: stop and say so.

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

**The payload, the probe record's content:**
- `Verdict: pass` or `Verdict: fail` on its own line (fail only if a finding is "Ordinary work: yes" with "Consequence: fails open" or "loses work", or if a change in your scope lets the check pass something it refused at `e00fd14a26be`);
- the head probed (12 digits) and the earlier probe's head;
- the judged files that changed, as you computed them, and for each what changed and whether it alters what the earlier probe found;
- each finding, if any, as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`;
- what you probed and found sound.
The lead passes findings on; you repair nothing (MR-4).
