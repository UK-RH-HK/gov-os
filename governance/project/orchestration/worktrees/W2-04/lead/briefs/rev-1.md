# Brief: reviewer (FULL, read-only), DAEO-u4oz (W2-04), review 1 of the declared round

You are a fresh reviewer. Ticket `DAEO-u4oz` (`W2-04`, "gov context bounded and reproducible"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`, at the head `{{HEAD}}`, and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-u4oz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` and `git rev-parse --short=12 HEAD` (expect `/home/usain/gov-os-worktrees/W2-04`, `w2/W2-04` and `{{HEAD12}}`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src python3 -m gov.cli.main retrieve "<question>" --json`, in this worktree, whose store the lead rebuilt at the head) for what you need to know before reading files at random. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph, if your session has it.
- **Reads (DEC-820):** you read everything, tests and code alike, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read, print, search, diff or copy the held-out file under `governance/project/` or type its path, never read or name the qualification oracle; (d) the hidden half of any evaluation set. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put a longer probe in a script file in your session's own temporary folder and run that file. **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Run everything in the foreground, one command after another; your session ends with your last message. You write nothing, so no commit of yours will exist: return when your findings are complete.
- Write no file of the repository and make no commit. No `git checkout` of another commit, no `git reset`, no `git clean`, no stash. No subagents that write. Install nothing. No push, merge, rebase or tag. Never run `gov close`, `gov adopt`, `gov pause` or `gov rebuild` (any form) here.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one from scratch in your temporary folder. Never write in `~/gov-os-workbench`. No file under any `.gov-runtime/` folder.
- **Row W2-L423's rule (DEC-911):** write commit hashes in your return as 12 digits, except the probed head, which you give in full once (the probe gate reads it); never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Disk (DEC-898):** your share is 3 GB and 150,000 files and folders, in the sandbox's own temporary folder; remove what you make when done.
- Inside a launched session `.gov-runtime/freeze` and the untracked dotfiles at the top show as placeholder device files: conclude nothing from them.
- Never ask or notify the owner; a question is a package in your return. Your temporary folder is removed when your session ends: every finding is in your final message.
- **Tests run no more than this (DEC-959 item 1):** do not re-run the acceptance or the scoped suites; the lead ran them (results below). Run the code with your own small probes.

## What you read

- The ticket file `.tickets/DAEO-u4oz.md`: its KPI lines (seven success, one failure) and its `allowed_paths` (`src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`), its `list_rows`; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-04`).
- The sources: CAP-15 and CAP-15.a to CAP-15.g (`docs/contract/CONTRACT_v4.md`); DEC-860 (retrieval in batches, ranked and stacked; never one giant query or context); W2-03's per-decision span and `content_hash`; DEC-768 (the dropped list's one order); DEC-552, DEC-568 (records that no longer stand); DEC-866.
- The specification and its addendum below (the same text both workers had; the CTO's decisions P-W2-04-2 (A) and P-W2-04-3 (b), DEC-1005, delegated: a semantic-free supplementary block; one batch = one of the context's own lookups, shown in `supplementary_batches`; a dependency ticket counted by its front matter). The lead's P3 calls: the same `CONTEXT_OVER_CEILING` refusal in both of the check's computations is reproduced and named (`REFUSED:`), any other error stays red; items left for lack of room are in `dropped` and named in `further_batch`; W2-M133 is a split outside this ticket.
- The change: `git diff w2/integrate...{{HEAD12}}` (code: `src/gov/context/__init__.py`, `src/gov/context/context_check.py`, `src/gov/retrieval/supplementary.py`; builder tests `tests/unit/context/`; acceptance tests `tests/acceptance/W2-04/` and the revised cases in `tests/acceptance/W2-54/` and `tests/acceptance/W1-41/`). Also what calls `gov.context.context`: `src/gov/close/command.py` (`_build_context`, the close turns a context error into `CONTEXT_FAILED`).

{{SPEC}}

## The lead's results at this head

{{RESULTS}}

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:
- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open: here above all a packet returned `ok: true` over its ceiling, an unreadable or missing mandatory record shown as read, a record that no longer stands satisfying a source, a stale store measured as fresh, a context-reproducibility check green where two computations differ, a lookup failure hidden, a non-deterministic packet;
- and whether the revised W2-54 and W1-41 cases lowered any expectation (DEC-491, DEC-866): each still guards what it guarded, observed where the addendum puts it.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

## Judgement rules (carried word for word)

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
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## The structured verdict (DEC-1010 item 1)

Your return ends with one fenced block opened by three backticks and the word `verdict`, holding JSON only, one entry per KPI line of the ticket, with these line ids: `success-1` to `success-7` (the seven success lines in their order in the ticket's front matter) and `failure-1` (the failure line). Each entry: `{"kpi": "<line id>", "verdict": "pass|fail", "findings": [...]}`; each finding listed under the KPI line it bears on, with `id` (F1, F2, …, the same ids as in your text), `scope` (`in`: inside this ticket's KPIs and allowed paths; `out`: anything else), `ordinary_work` (`yes|no`) and `consequence` (`fails open|loses work|other`), exactly these words. A finding that bears on no KPI line goes under the line nearest to it, with `scope: "out"`. Example form: `{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, ...]}`. Before the block, one line `judgement: pass` or `judgement: fail`.

## The embedding server (today)

The shared embedding server (127.0.0.1:11434) is overloaded today. Nothing in this review needs it: the supplementary block is semantic-free by design. Wrap every `gov retrieve` call in `timeout 120`; if it does not answer, read the named files instead and say so. Do not probe live semantic retrieval.

## Return

The head you probed (in full, once), your verdict (`pass` or `fail`, by the rules above), and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`). Say also what you probed and found sound. The lead turns your return into the probe record; you write nothing and repair nothing (MR-4).

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

After the twelve fields: your verdict and the findings as above, ending with the `verdict` block; then a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
