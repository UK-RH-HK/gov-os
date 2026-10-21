You are a fresh reviewer. Ticket DAEO-5j8b (W2-58, "Policy 2 in the guard and the launcher: reads open, four refusals"), profile STANDARD, a guard and launcher change the owner approved (DEC-821, DEC-873; CAP-33 asks an independent review of it), is implemented in the worktree `/home/usain/gov-os-worktrees/W2-58` on branch `w2/W2-58`, at the head `8caf47db5ac86f1109becaf0c9e2c312165ff3de`, and its acceptance tests pass. You probe that head for behaviour the tests miss: cases that could lose work, let a role write outside its scope, change acceptance tests, or make the guard fail open. You write nothing: you return the probe record's content in your final message, and the lead writes it.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-5j8b`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-58` and `w2/W2-58`), and `git rev-parse HEAD` (expect `8caf47db5ac86f1109becaf0c9e2c312165ff3de`). If anything differs, stop and say so.
- **Step 0, the sandbox check, reported first in your return:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-5j8b','w').write('x')"` must FAIL; (b) `git update-index --refresh` must WORK (you write no object, so skip `git hash-object -w`). If (a) wrote the file or (b) failed, stop there and return, naming what happened.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820):** reviewers and auditors read everything, tests and code alike (DEC-820 item 3). Only these stay refused to you too: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); (d) the hidden half of an evaluation set, if one lists you as measured (none does). (c), the counterpart's work on this ticket, binds the engineer and the test designer, not you. Never read or name the qualification oracle. Never list, read or write anything in `~/gov-os-workbench`.
- **Read refusals until W2-58 lands (DEC-849):** your session's guard runs this worktree's code, which opens the searches from the repository root, `governance/project/` and `.claude/`; if any read is still refused, take the refusal, never look for another spelling, and **count every refusal in your return**.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no commit, no merge in this worktree. Write no file of the repository. No subagents that write. Install nothing. No push, rebase or tag.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch, or with the acceptance suite's own support modules (as `tests/acceptance/W2-58/w2_58_support.py` does).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Your sandbox refuses the network to the model's API: the suite's `local_only` live cases (`test_w2_58_launched_sessions.py`) cannot run inside it; the lead ran them unsandboxed.
- Nobody runs `gov close`, `gov adopt`, `gov pause`, `gov rebuild`, or `docs/plan/tools/validate_s1.py`.
- You never ask or notify the owner (no question box, no `owner-ping`).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.

## What you read

- The ticket file `.tickets/DAEO-5j8b.md`: its KPI lines and its `allowed_paths` (src/gov/guard/protected.py, src/gov/guard/heldout.py, src/gov/guard/decide.py (the read rules only), src/gov/guard/reads.py, src/gov/launch/** (the sandbox's read rules only), governance/project/path-map.yaml (the evaluation_sets block only), template/governance/kernel/schemas/path-map.schema.json (the same block), tests/unit/guard/**, tests/unit/launch/**, docs/changes/W2-58-CIT-E.md).
- The sources, in `docs/DECISION_REGISTER.md`: DEC-820, DEC-821 (its status line marks the words DEC-873 changed), DEC-849, DEC-857, DEC-873; and DEC-826 (Q2), DEC-845, DEC-162, DEC-215, DEC-218, DEC-508, DEC-548, DEC-553, DEC-562, DEC-570, DEC-778, DEC-801.
- The package behind DEC-873: `governance/project/orchestration/packages/P-W2-58-1.md`.
- The change record `docs/changes/W2-58-CIT-E.md`, which you review with the code.
- The ticket's change: `git diff w2/integrate...HEAD` (the guard's read rules in `src/gov/guard/`, the launcher, the path map's `evaluation_sets` block and its schema, the unit tests), the acceptance tests `tests/acceptance/W2-58/` (its README and `EARLIER_CASES.md` name the earlier cases rewritten in `tests/acceptance/W1-02/`, `W1-50/` and `W2-50/`).

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope (no write rule may widen);
- let an implementer change the acceptance tests;
- make the guard or a gate fail open: each of (a) secrets, (b) the held-out contents, (c) the counterpart's work (the engineer and T's acceptance folder; the test designer and T's changed files), (d) an evaluation set's hidden part must still refuse by every read route an honest agent takes in ordinary work; a guard error, an unparseable ticket file or path map, or a failing git command must refuse, never allow; a malformed `evaluation_sets` block must refuse the launch.

And, from DEC-873: a session launched by this head's `gov launch` must be able to run its own tests (engineer), import the code it tests (test designer) and run a scorer (measured session), with no phantom deletion in `git status`; the held-out `Read` rules must stay in every role's launch settings. You can see what the launcher hands the CLI by running `gov launch` with a stand-in CLI as the suite does.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such.

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

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and its two lines (`Ordinary work: …`, `Consequence: …`). Say also what you probed and found sound, and your judgement: **pass** (no finding with "yes" and "fails open" or "loses work") or **fail**. You repair nothing (MR-4).

After the twelve fields, give the probe record's content as a payload, between the lines `--- PROBE RECORD ---` and `--- END PROBE RECORD ---`, in this form (the lead fills the two session ids it knows):

    ---
    type: probe
    task: DAEO-5j8b
    reviewer_session: <the lead fills it>
    implementer_session: <the lead fills it>
    reviewer_wrote_nothing: true
    commissioned_by: orchestrator
    judged_by: orchestrator
    judgement: <pass|fail>
    probed_commit: <the full 40-character hash of the head you probed>
    ---

    # Probe record: W2-58 (DAEO-5j8b), <one line>

    - **What was probed.** ...
    - **What was found.** ... (each finding with its two lines)
    - **Judgement.** ...

Your return is one message. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
