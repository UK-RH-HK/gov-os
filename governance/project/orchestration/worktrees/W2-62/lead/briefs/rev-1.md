You are a fresh reviewer. Ticket DAEO-juee (W2-62, "Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force"), profile STANDARD, is a kernel hook and skill change through CIT-P (CAP-33), so it gets one independent review after green although its profile is STANDARD. It is implemented in the worktree `/home/usain/gov-os-worktrees/W2-62` on branch `w2/W2-62`, at the head `7d8e49d84aff` (tests `87cad875`, implementation `7d8e49d8`), and its acceptance tests pass. You probe that head, the code and the change record `docs/changes/W2-62-CIT-P.md`, for behaviour the tests miss. You write nothing.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-juee','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-juee`) and `git rev-parse --show-toplevel --abbrev-ref HEAD HEAD` (expect `/home/usain/gov-os-worktrees/W2-62`, `w2/W2-62` and `7d8e49d8…`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return.
- **Memory (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m gov.cli.main retrieve "<question>" --json`.
- **Reads (DEC-820, Policy 2):** you read everything, tests and code alike. Only these are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work applies to the engineer and the test designer, not to you; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.rulesync/hooks.jsonc`.
- Refused twice for the same call: stop and say so; no third try (AR-6).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- Write no file of the repository and make no commit. No `git checkout` of another commit, no `git reset`, no `git clean`. No subagents that write. Install nothing. No push, merge, rebase or tag.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it). A probe that needs a repository builds a temporary one in your temporary folder, copying single named files (for example the two hook files) and never `governance/project/`.
- Never write in `~/gov-os-workbench`; never list, glob or search it.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Nobody runs `gov close`, `gov adopt`, `gov pause`, `gov rebuild` or `docs/plan/tools/validate_s1.py`. On ESCALATION_BLOCKED from any command, stop and return it.
- Never ask the owner a question and never use a question box (DEC-850).
- Use your model's full window; you are never asked to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Your sandbox has no network, so you cannot start a live Claude Code session; the lead's live results are given below.

## What you read

- The ticket file `.tickets/DAEO-juee.md`: its KPI lines and its `allowed_paths` (`template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**` (the resume rule only), `tests/unit/hooks/**`, `docs/changes/W2-62-CIT-P.md`).
- The list rows W2-M372 and W2-M373 in `docs/plan/WAVE_2_LIST.md`.
- The decisions: DEC-792 in this worktree's `docs/DECISION_REGISTER.md`; DEC-837, DEC-838 and DEC-851 in the main tree's register (`/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`, committed by the owner after this branch was cut). In short, DEC-837: (1) the session-start hook loads the RESUME HERE block in full, never a first-9,000-characters cut (W2-M372), and names the prompt in force, not Wave 1's (W2-M373); (2) once it does, DEC-792's 8,000-character limit is lifted; the resume holds the full session state, and repository knowledge comes from retrieval and the context packets; (3) a checkpoint at every handover; (4) a kernel hook change through CIT-P, scope approved by the owner.
- The ticket's acceptance tests (`tests/acceptance/W2-62/`, and the revised `tests/acceptance/W1-49/` fixture and two tests in `87cad875`) and the code at the head: `git diff 162f17ea..7d8e49d8`.
- This hook runs live in every session of the main tree once merged (`.rulesync/hooks.jsonc` calls `template/governance/kernel/hooks/sessionstart.py` directly).

## Facts you are given (do not re-measure; you have no network)

- The orchestrator's research, 2026-10-19 (recorded in the CIT-P): Claude Code 2.1.292, a headless Haiku 4.5 session, one SessionStart hook printing N characters ending in a random token: N = 9,500 arrived whole; N = 12,000 and N = 60,000 were not injected (saved to a file under `~/.claude/projects/…/tool-results/`, a preview shown; the token never reached the session).
- The lead's own probe, same version, 2026-10-19: exactly 10,000 ASCII characters arrived whole; 9,000 em-dashes (26,964 UTF-8 bytes) and 4,000 em-dashes (11,964 bytes) arrived whole; 10,300 ASCII characters were not injected. The bound counts characters, not bytes.
- The lead's live run of `tests/acceptance/W2-62/test_w2_62_live_resume.py` (a real resumed session, `claude-opus-5-5`, a 50,000-character section ending in a random token) is given in the lead's verification; on the base hook it also passed, because the base hook named the file and the session read it.
- The lead's verification at this head: `tests/acceptance/W2-62` 58 passed (the live case included); `W1-29` 45 passed; `W1-49` 103 passed and 2 failed, both on the retired 300k auto-compact window (DEC-838), not this ticket; `tests/unit` 2187 passed, 1 skipped. `W1-38` 36 failed: every failure is the copies of the checkpoint skill (`.rulesync/skills/checkpoint/SKILL.md`, `template/.rulesync/skills/checkpoint/SKILL.md`, the generated `.claude/skills/checkpoint/SKILL.md`) no longer matching the changed kernel skill; they are outside the ticket's paths and are returned to the orchestrator as a package, so do not report that red again unless you find something more in it. `gov check` is red on the same copies (adapter/model portability) and on DEC-837 not yet being in this branch's store (context reproducibility; the branch was cut before the owner's commit of DEC-837).
- This repository's `governance/project/roster.yaml` does not yet carry `roles: orchestrator: prompt:`; that line is outside the ticket's paths and is returned to the orchestrator as a package. Until it is added the hook names no prompt here, by the KPI's design.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work (here: a resumed session that silently misses part of its RESUME HERE state, believes it has the whole section when it has not, or is sent to wrong lines or a wrong file);
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open (here: the hook failing with a non-zero exit, hanging, or blocking a session; a non-orchestrator role receiving the orchestrator's injection).

Suggested probes, as described behaviours: checkpoints as an honest orchestrator writes them in ordinary work (Markdown with em-dashes and other non-ASCII text, CRLF line ends, a RESUME HERE heading with trailing text, nested headings, fenced blocks, the generated state block that `precompact.py` appends, a section near the 10,000-character edge, a staleness warning); the line range and size against what the Read tool returns for those lines; the roster in ordinary forms (the key present, absent, empty, not a string, the roster with comments) and in a linked worktree; the optional parts under load (a long ready list, the context packet); and whether the CIT-P records the research faithfully and is complete for CAP-33. Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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

## Return

Your last message, complete in itself. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and the probe record's content after them as the payload. Put in the fields: the sandbox check's result; the head you probed; the `gov.__file__` line; the tests you ran with their counts; the guard read refusals you met (a count, with what was refused); whether you used `gov retrieve`; your judgement, `pass` or `fail` (fail only for a finding with "yes" to ordinary work and "fails open" or "loses work").

The payload is the probe record's body in Markdown, under a heading `# Probe record: W2-62 (DAEO-juee), the CIT-P review`, with three bullets: **What was probed** (the head, your session's role, what you ran, how many probes), **What it found** (each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; then what you probed and found sound), **Judgement** (`pass` or `fail`, and why). You repair nothing (MR-4).

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
