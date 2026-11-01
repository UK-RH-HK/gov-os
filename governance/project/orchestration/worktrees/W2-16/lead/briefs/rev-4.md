# Brief: reviewer of W2-16's round 3 (FULL ticket, read-only, DEC-772, DEC-767)

You are a fresh reviewer. Ticket `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL, is in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`, at the head `df7a2a06e5ff91ac58dbf1691c17043973d17fc2`. The owner ordered one round, DEC-772 item 1, and one review **of that round's change only** (DEC-772, DEC-767). You judge that change and probe it for behaviour the tests miss. You write nothing.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-49o5','w').write('x')"` must fail. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-49o5`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`) and `git rev-parse HEAD` (expect `df7a2a06e5ff91ac58dbf1691c17043973d17fc2`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Reads (DEC-820, Policy 2):** reviewers read everything, except (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never the qualification oracle; (d) the hidden half of any evaluation set.
- **Retrieval (DEC-836, DEC-860, DEC-859):** ask first with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m gov.cli.main retrieve "<question>" --json`, before reading files at random; never one giant query (`--batch-size`, then `--continue <token>`). A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted; if it is not available, search named folders with Grep.
- **Read refusals (DEC-849):** the guard may refuse a search that starts at the repository root, `governance/project/` or `.claude/`. Take it, never another form; count them in your return.
- **Tests run no more than this (DEC-959 item 1):** you re-run no suite; the lead's results are below. You may run small probe scripts of your own.
- **Scratch budget (DEC-898):** your share is 3 GB and 150,000 files and folders, in your session's temporary folder; clean what you make; give `du -sh` and `du -s --inodes` of what you leave.
- **Commit hashes (row W2-L423's rule, DEC-911):** anything you write under `.gov-runtime/` (you write nothing) holds 12-digit hashes only, never the keywords of the gitleaks rule that takes a bare 40-hex string for a token. Your return may give the probed commit in full (the probe record's `probed_commit` is a full id).
- Run everything in the foreground; a single tool call is cut off at 10 minutes. No `git checkout`, `reset`, `clean`, `stash` in this worktree. Never read `.claude/settings*.json` or `~/.claude/`. Never write in `~/gov-os-workbench`. **Never copy the repository or a folder of it**; a probe that needs a repository builds a temporary one from single files, as `tests/acceptance/W2-16/w2_16_support.py` does (you may import its helpers from a probe script in your temporary folder). No clone or copy of a programme under `.gov-runtime/`. `.gov-runtime/freeze` shows as a placeholder device file in a launched session: conclude nothing from it. Write no file of the repository, make no commit, no subagents, install nothing, no push, merge, rebase or tag (tags only in your own temporary repositories, unsigned). Never run `gov release` in this worktree. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`.
- If the guard or the sandbox refuses something you needed, say so in your return. **Refused twice for the same call: stop and say so; no third try** (AR-6). Record each refusal by the guard (time, the command's form in one line, the reason it gave).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

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

## What you read

- DEC-772 (item 1: "`gov release` is owner-only, from a plain terminal, like `gov approve` and the freeze lift: it refuses with a Claude Code process among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal, and asks for a typed one-time code. This replaces DEC-761 item 1's line … It is W2-16's next round, and that round does only this"), DEC-767, DEC-409, DEC-761, DEC-771, DEC-866, DEC-491 in `docs/DECISION_REGISTER.md`; the ticket file `.tickets/DAEO-49o5.md`.
- The lead's specification for the round, given to both workers: `.gov-runtime/scratch/lead/briefs/spec-dec772.md`, and the lead's answer to the test designer's P-R3-A: `.gov-runtime/scratch/lead/briefs/td-4b.md`. Its readings: item 1 governs the build form only, `--lock-from` (the Copier task) keeps its DEC-761 caller rule (a terminal-and-code check there would refuse every install and update, against KPI 4 and W1-39's closed suite, DEC-771 item 1); the test seam is in the freeze lift's form (W1-50's `gov.pause.command._lift_test`).
- **The round's change only:** `git diff 2c8cfc7a..df7a2a06 -- src tests docs/releases copier.yml`. Commits: `bb495230` (engineer: the build form's checks, the seam, unit tests, README), `2fa4a6da` (test designer: 28 cases, the suite's builds through the seam, the role cases' build halves, R3-F5 into a fresh folder), `0226a4ec` (test designer: the 25 build-refusal cases through the seam, P-R3-A), `b023b9c1` (the lead's merge of the tests), `df7a2a06` (engineer: a missing version refused after the code, as the build's own). Earlier rounds' work is not under review except where this change touches it (the earlier probe passed: `docs/probes/DAEO-49o5/PR-DAEO-49o5-last-round.md`).
- The lead's results so far: acceptance W2-16 by the engineer, file by file, at `df7a2a06`: doctor 16, immutability 10, install 17, last_round 29, owner_terminal 28, release 42, all passed; `tests/unit/release` and `tests/unit/lock` 99 passed. The lead's scoped verification of the close's form runs beside you; its results go into the lead's return.

## What you judge and probe (this change only)

Run the code where a claim needs it; do not judge by reading alone. A finding you could not reproduce is marked as such.

1. **The build form refuses in each case DEC-772 names, before anything is read or written:** a Claude Code session among the ancestors (the freeze lift's signs), a chain that cannot be read whole, `GOV_ROLE` set (any value, empty included), `GOV_TICKET` set (any value, empty included), no terminal on input or output, a wrong, empty or missing code. Does any path build a release, or write anything, without every check passing? Does anything that cannot be read or asked refuse (never pass)? Is the code shown only on a terminal, from the system's random source, and only after the other checks?
2. **The real command from your session:** `gov release <version>` in a temporary repository (with `GOV_ROLE` and `GOV_TICKET` as your session has them, and in an environment a probe script builds without them, with and without a pseudo-terminal): refused, nothing written? The prefix forms (`GOV_ROLE=… gov release`, `env -u GOV_ROLE -u GOV_TICKET gov release`): refused now? Say what the command did.
3. **The seam:** can the command (`run`) be made to take a planted chain or terminal by any option, argument or environment variable? The seam itself is importable by any Python, as the freeze lift's is: say so as a known limit in the freeze lift's form, not as a new finding, unless you find a path an honest agent would hit in ordinary work.
4. **`--lock-from` unchanged:** its rules and its caller check as before; `copier copy` and `copier update` still install (spot-check one copy and one update in a temporary folder).
5. **The tests' rewrites keep their purpose and lower no expectation:** the suite's builds through the seam (`build_release`), the role cases' build halves, the 25 build-refusal cases (P-R3-A: each refusal held to be the build's own, the code accepted), R3-F5 (the copy into a fresh folder, `Rewrite-Reason: DEC-767`). Would each still catch what it caught before? Does any new case pass whatever the code does?
6. **The README and the docs:** `docs/releases/README.md`'s owner procedure matches what the command does.

## Return

The head you probed, and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity (BLOCKER, HIGH, MEDIUM, LOW), its two lines (`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`). Say also what you probed and found sound. Then your judgement on this change: `pass` or `fail` by the rules above. You repair nothing (MR-4). The lead writes the probe record from your return.

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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them: there, the probe record's content, as a YAML block with `probed_commit` (full id), `judgement` (`pass` or `fail`) and `findings` (each with `id`, `severity`, `behaviour`, `ordinary_work`, `consequence`, `fail_open` true/false), then the narrative. Refused twice for the same call: stop and say so.
