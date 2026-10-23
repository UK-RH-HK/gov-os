You are a fresh independent test designer (MR-3). Ticket: DAEO-rmbe (W2-69), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-69` on branch `w2/W2-69`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

You start in the old launch form, without the sandbox: the suites you write need the code-graph tool (its runtime folder `/tmp/gov-cbm-<uid>` is read-only inside the sandbox until W2-56), and the lead watches your work with a tripwire. Write nothing outside this worktree except your temporary folder below.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-rmbe`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-69` and `w2/W2-69`). If anything differs, stop and say so.
- **The code under test (DEC-732), word for word:** In this worktree every test run and every gov command used for verification runs this worktree's own src/: PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src set per command, never in --settings; quote `python3 -c "import gov; print(gov.__file__)"` in your return. Your tests, run from this worktree, must exercise this worktree's code; your README says how, and the lead checks it with that line.
- **Memory first (DEC-836, DEC-860, DEC-859):**
  - Use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random.
  - Never one giant query or context. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget.
  - A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. A whole-graph job reads it in pages, never one query over the tool's row cap.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form. Search named folders instead. Count the refusals you met and report them.
- **Reads are open, with four exceptions (DEC-820):**
  - (a) secrets and keys: never printed;
  - (b) the contents of the held-out qualification material (its file names may be seen);
  - (c) **the counterpart's work on this ticket: never read this ticket's implementation.** That is every file `git diff --name-only w2/integrate...HEAD` names, other than your own tests. Today it names `docs/research/W2-69-secrets-scan.md`, the design note: do not read it. The design it chose is stated below as behaviour. Read the existing code as it stands on the base (`git show w2/integrate:<path>`). Your independence also comes from order: you write the tests before the implementation exists.
  - (d) the hidden half of any evaluation set, by whoever is measured by it.
  Never read or name the qualification oracle. Never print a secret.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. No amend, rebase, push, merge or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json`, in this worktree or anywhere.
- Never list, glob, search or write in `~/gov-os-workbench` (DEC-723). Dev-tier tests use `GOV_DEV_TIERS` by name only, clone into a temporary folder, and are marked `local_only`.
- **Never copy the repository or a folder of it** (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. No clone, copy or programme file goes under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths; the guard refuses here-documents and unresolvable variables in Bash write targets. No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never run `gov rebuild` in this worktree** (your tests run it in their own temporary projects), and never `gov rebuild --no-embeddings` anywhere. Never run `gov close`, `gov adopt` or `gov pause`.
- **Refused twice for the same call: stop and say so; no third try.**
- If the guard refuses something you needed for the ticket, do not work around it: return it as a package.

## Scratch budget (DEC-898, owner, standing)

- **Your share:** 6 GB and 300,000 files and folders, out of the lead's 20 GB and 1,000,000 for the lead and all its workers. It covers your temporary folder and anything untracked you leave in the worktree.
- `TMPDIR` is set for you to `/tmp/gov-os-lead-W2-69/td`; keep it for every test run.
- Keep pytest's own retention of three base folders; never a per-run `--basetemp`. Tests clean up what they make.
- Remove every temporary tree you make as soon as you no longer need it.
- Measure your scratch (`du -s --inodes` and `du -sh` of `/tmp/gov-os-lead-W2-69/td` and of the worktree's untracked files) before each long test run and at the end, and give the figures in your return's `evidence` line.
- If you pass your share, stop the heavy work at once, clean what you can, and return with the measure and its cause.

## What you read

- The ticket file `.tickets/DAEO-rmbe.md` (read-only): its KPI lines, its body and its sources.
- The card: `docs/plan/WAVE_2_WBS.md` §0 (rules for every ticket) and §2, W2-69.
- The package that started it: `governance/project/orchestration/packages/P-W2-62-G1.md`, §2 (the cut test).
- List rows W2-M404, W2-M395 and W2-L373 in `docs/plan/WAVE_2_LIST.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-897, DEC-853, DEC-290, DEC-298, DEC-347, DEC-868, DEC-896, DEC-899, DEC-866, DEC-491, DEC-221, DEC-462.
- The public interfaces, as they stand on `w2/integrate`:
  - the secrets-indexing check: its declaration `template/governance/kernel/checks/secrets-indexing.yaml` and its command `python3 -m gov.secrets`, run in a project's root; it prints one line per file it finds a secret in, naming the file (never the secret), and exits 1 when it finds one and 0 when it finds none; when it cannot decide, it never exits 0;
  - `gov check` (the secrets-indexing family);
  - `gov rebuild --json` (`python3 -m gov.cli.main rebuild --json`), which recreates the derived stores under `.gov-runtime/`;
  - the project's `.gitleaks.toml` (its rules; never print a secret from it).
- The earlier tests of this check, as models and for the revisions below: `tests/acceptance/W1-15/`, `tests/acceptance/W2-50/` (its README, `w2_50_support.py`, `w2_50_scan_support.py`, `test_w2_50_secrets_scan_scale.py`, `test_w2_50_never_indexed.py`, `test_w2_50_last_review.py`), and `tests/acceptance/W1-16/` for how a test builds a code-graph store with the tool. You read no private part of an implementation to learn what a test should expect.

## The behaviour to test

### The problem (W2-M404, P-W2-62-G1)

The secrets-indexing check is a hard-block check. Today it gives each derived store's content to `gitleaks stdin` as one input. gitleaks splits that input into fragments and matches each on its own, so a fragment's start is a text start. When a fragment begins inside a word, a rule's leading word boundary matches there, and a fragment of a longer identifier is taken for a token. Where the fragments begin moves with every rebuild, so any rebuild can turn `gov check` and a close RED by chance.

**Facts about gitleaks 8.30.1 (`~/.local/bin/gitleaks`), measured for this ticket, for building deterministic cases against today's check:**
- A fragment of standard input is one read of whatever the pipe delivers at once (up to 65,536 bytes from a pipe as Python's `subprocess.run(input=…)` writes it; 100,000 from a file), then a byte-by-byte peek until two newlines with only spaces, tabs or carriage returns between them, or until 25,000 more bytes. On text with no blank lines, later fragments are 28,672 bytes each. So where the fragments begin depends on the layout and on how the pipe delivers the bytes.
- gitleaks' fragments do not overlap: a real token cut by a fragment edge is missed by today's check unless the part before the edge is a whole match. **This is a K1 failure of today's check, found by the research:** a real token at a word boundary that straddles a fragment edge, starting 1 to 12 bytes before it, was missed.
- gitleaks skips an input it takes for a binary file (for example one that begins with the SQLite header).
- The project's rules come in two rule sets (DEC-347): the project's file with gitleaks' defaults, and the project's rules alone. 71 rules begin with a word boundary `\b`, the project's four among them (`gov-canary`, `gov-token-digit`, `gov-token-upper`, `gov-token-lower`).

### The design chosen (DEC-897 item 1), as behaviour

The design question was answered with evidence before the code. The check will:
- **read each SQLite store's content as its stored values:** every value of every table, the schema table included, each value judged on its own, so bytes of different values never join into one match (this also settles row W2-M395, the byte join). Text is judged as stored. A blob is judged as its bytes, and also without its zero bytes when it holds any (UTF-16);
- **read each SQLite store's freed space as a backstop** (free pages, freed cell space, the unused space of each page), each freed region on its own; text there that holds a secret is a finding;
- read a file under `.gov-runtime/` that is not a SQLite store as its raw bytes, and also without its zero bytes when it holds any; a SQLite file that cannot be opened or read is judged by its raw bytes, never passed as clean undecided;
- give gitleaks its input so that **no read begins or ends inside a word**, and so that a token across any place where the check splits its input is still seen whole;
- and `gov rebuild` will **compact each SQLite store after its build**, the full-text indexes included, so that deleted text survives in neither rows nor freed space.

### The KPI lines, success (from the ticket)

1. **(K1)** A real token is found at every offset and in every form the derived stores hold it: in a stored value, in a SQLite row read as text, in UTF-16 text, and across every boundary where the check splits or reads its input, at a word boundary as the rule defines it [DEC-897 item 1, W2-M404].
2. **(K2)** An embedded fragment of a longer identifier is not flagged: a token-shaped string inside a word, placed at every offset relative to wherever the check or gitleaks begins a read, is not a finding, for every rule with a leading word boundary [DEC-897 item 1, W2-M404].
3. **(K3)** Deleted text does not survive a rebuild: after a full rebuild, text deleted from a SQLite store is in neither its rows nor its free pages, so a secret removed from the sources leaves no residue the check would find, or miss [DEC-897 item 1]. This covers every SQLite store a rebuild writes: the record store with its lexical and semantic indexes, and the code-graph store the code-graph tool builds.
4. **(K4)** The design question is answered with evidence in `docs/research/W2-69-secrets-scan.md` before the code. (You do not read that note. A test may check, from git history and without your reading it, that the note exists and was committed before any commit of this ticket that changes code.)
5. **(K5)** Every file under `.gov-runtime/` the check scans today is still scanned, with every rule set; a scan that cannot finish still fails closed; the reuse of a clean result keyed on the store's hash (DEC-853) stays, and a finding is never reused [DEC-853, DEC-290].
6. **(K6)** The earlier tests this change affects are revised only where scanning the rows as text or compacting the stores changes what they expect, each with `Rewrite-Reason: DEC-897` (below).
7. **(K7)** `tests/unit/secrets/` is renamed `tests/unit/secrets_check/`, so it no longer shadows the standard library's `secrets` module under plugins that import it first; collection is clean with pytest-rerunfailures and pytest-randomly loaded [W2-L373, DEC-899]. **Those two plugins are not installed on this machine, and nothing may be installed.** Test the behaviour they need instead: with a plugin of your own test, loaded first, that imports the standard library's `secrets`, collecting the unit tests gives no error, `tests/unit/secrets/` is gone, and the check's builder tests are under `tests/unit/secrets_check/`. Say this in the README.

### The KPI lines, failure (each needs a test that would catch it)

- A real token at a word boundary that the check misses, at any offset or in any stored form.
- A word-internal fragment flagged at a read edge (the chance red of W2-62's queue, 2026-10-22). A read edge is where a read begins or where it ends.
- Deleted text left in a store's free pages after a rebuild.
- A store or file the check scanned before and no longer scans; a scan that cannot finish passing as clean.

### Notes for the design of the tests

- **You cannot know where the new check will split its input.** So place strings at every offset across wide windows, and across a range of input sizes and layouts (long lines with no newline, text with blank lines, values longer than one gitleaks read, many small values), not only at today's fragment edges. Each case must still be red on today's check where the KPI says today's check fails; where a case cannot be made red deterministically on today's check, the README says so and why.
- The check names each file it finds a secret in, so one run can judge many files at once (one string per file), and a run over many word-internal strings must name none.
- Cover every form: a plain file under `.gov-runtime/`, a text value in a SQLite table, a value in a full-text index, a blob, UTF-16 text (a UTF-16 store, and UTF-16 bytes in a blob or a plain file), a long value, the schema text, and freed space of a SQLite store (a secret deleted but still on disk in an uncompacted store must still be found).
- K2 for every rule with a leading word boundary, in both rule sets: the project's four rules at every offset across the windows; and every one of gitleaks' default rules with a leading boundary, each with a word-internal string built from the rule itself (at fewer offsets is fine, if the README says why). A rule for which no such string can be built (for example a keyword or entropy gate that a word-internal string cannot pass) is named in the README with the reason.
- K3 through `gov rebuild --json` in a temporary project: a store's free-page count is zero after it, and a word deleted from the sources is in no store's bytes after the next rebuild. A case that needs the code-graph tool skips with a stated reason when the tool is absent, as W1-16's do.
- Planted secrets are built at run time from parts; none stands whole in a test file. Nothing prints a secret.
- Behaviour through public interfaces, never internals. Deterministic, no network. Tests that need a repository build a temporary one.
- The suite must run under `pytest -n auto` (xdist) beside every other suite. If a case can only run alone (for example it needs the code-graph tool's daemon, or it is time-sensitive), name it in the README and in your return; do not edit `tests/acceptance/serial-only.txt`, which is outside your paths.
- Keep the suite's run time reasonable: a FULL suite is thorough, but no combinatorial expansion beyond what a KPI demands (DEC-221). State the suite's run time in the README.

## What you write

- **Your new tests:** only under `tests/acceptance/W2-69/`, with a `README.md` that maps each KPI line (success and failure) to its tests and gives the expected red reason of each, and says how the tests run this worktree's code.
- **The earlier tests named for revision (MR-3, P-IS-5 (a), DEC-899):** you may revise only these, and only where scanning the rows as text or compacting the stores changes what they expect, lowering no other expectation:
  - `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py` and `tests/acceptance/W2-50/w2_50_scan_support.py` (W2-50's secrets-scan scale cases);
  - the secrets cases of `tests/acceptance/W2-50/test_w2_50_never_indexed.py` and `tests/acceptance/W2-50/test_w2_50_last_review.py`.
  For each one you change, say in your return what it expected, what it expects now, and why the design changes it. If none needs a change, change none and say so. A test that enforces a superseded decision (DEC-866) is named in your return, not fixed silently. If another earlier test, not named here, would need a change, do not change it: name it in your return as a package.
- A shared file is touched only on lines of your own. No throwaway implementation is left in the tree.
- **Red first:** run your suite to its end (never `-x`) with
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-69/td PYTHONPATH=/home/usain/gov-os-worktrees/W2-69/src python3 -m pytest tests/acceptance/W2-69 -q -p no:cacheprovider -rs`,
  and the revised W2-50 files the same way; they fail for the reasons your README states. Commit before any run longer than a few minutes.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. After each commit, show `git log --oneline -2` and `git status --short`.

- **Your new tests,** in one commit, with the trailers in the final block:
  `git commit -m "DAEO-rmbe (W2-69): acceptance tests for the secrets check reading what the stores hold (DEC-897)" --trailer "Task: DAEO-rmbe" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-897" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
- **The W2-50 revisions, if any,** in a second commit of their own, with the same trailers and `--trailer "Rewrite-Reason: DEC-897"`.

## Return

One message, your last, complete in itself. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Give, among them: your commits' hashes; the test count; each KPI line (success and failure) with its tests; the red result as you saw it (counts and reasons); every earlier test you rewrote, with its reason; the cases that can only run alone; the `gov.__file__` line; the read refusals you met; whether you used `gov retrieve`; your scratch figures. Refused twice for the same call: stop and say so.

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
