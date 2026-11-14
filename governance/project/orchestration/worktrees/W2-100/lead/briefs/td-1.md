# Brief: independent test designer, DAEO-uw5h (W2-100), run 1 — domain skills A (backend, api, data, security)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work
only in the tests worktree `/home/usain/gov-os-worktrees/W2-100-tests` on branch `w2/W2-100-tests` (DEC-963); you never
write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-100`. You write the ticket's acceptance tests in
`tests/acceptance/W2-100/` from its KPI lines, its `## Interface` and the lead's reading below, in parallel with the
product-spec worker who writes the four skills (DEC-959 item 7), and you show them red against the base.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100-tests` and
  `w2/W2-100-tests`), `git rev-parse --short=12 HEAD` (expect `627bcaa19...`) and `git status --short` (expect
  nothing). If anything differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag,
  no stash, no `git worktree`, no `git clone` of the repository.
- **The code under test (DEC-732):** every test run uses `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100-tests/src`
  set per command; quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100-tests/src python3 -c "import gov; print(gov.__file__)"`
  in your return. Your tests find the repository from their own location (the folder the test file sits in, as
  W2-98's `w2_98_support.py` does with `parents[...]`), never from a fixed path, so merged into the ticket's worktree
  they judge that worktree's files and its `src/`.
- **Every pytest through the heavy slot**, with `TMPDIR` your sandbox's own `$TMPDIR` (keep it; never set it, never
  `--basetemp`), `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-100-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-100 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`
  A slot gate's refusal or wait is a wait, not a refusal.
- **Reads (DEC-820):** reads are open, except: (a) secrets and keys, never read or printed; (b) the held-out
  qualification material's contents (never read, search, diff or copy it; its file names may be seen); (c) **the
  counterpart's work on this ticket: you never read the skills being written**: nothing under
  `template/governance/kernel/skills/{backend,api,data,security}/`, `.rulesync/skills/{backend,api,data,security}/` or
  `template/.rulesync/skills/{backend,api,data,security}/` in the ticket's worktree `/home/usain/gov-os-worktrees/W2-100`,
  on branch `w2/W2-100` or any later commit of it, by any tool (on your own base `627bcaa19` those folders do not
  exist); (d) the hidden half of any evaluation set. Never open an evaluation set's root or any hidden or
  memory-verdict folder. You search with the Read and Grep tools, naming the folder a search starts at (never the
  repository root, `governance/project/` or `.claude/`); if the first search does not answer, search once more in
  different words, then answer from what you read or say "not found" (no `gov retrieve`, no `gov context` in the
  sandbox, DEC-1065). Never read `.claude/settings.json`.
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at
  literal absolute paths. Anything longer than one line goes in a script file in your sandbox's `$TMPDIR`.
- **Never a real model call and never a key:** cases that run `gov skilleval` use a stub `claude` executable that the
  case writes in `tmp_path` and puts first on `PATH` (with only `/usr/bin` and `/bin` after it), as W2-104's suite does
  (`tests/acceptance/W2-104/w2_104_support.py`, read it). No case reaches the network.
- Never copy the repository or a folder of it; a case that needs a project or a git history builds a temporary one
  under `tmp_path` (a few named files copied is fine). Install nothing. No subagents that write. Never write
  `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal by another tool or
  form (DEC-1142 (9)); report it.
- Write commit hashes as 12 digits in your return, never the full 40.

## What you read

- The ticket `.tickets/DAEO-uw5h.md` in your tree: its KPI lines (S1-S6, F1-F6; verbatim there), `allowed_paths`,
  sources, and its `## Interface` section.
- The sources in `docs/DECISION_REGISTER.md`, by id: DEC-959 (items 4, 5, 7), DEC-957 (Q5, the P1 rule), DEC-832,
  DEC-616, DEC-645, DEC-315, DEC-1112 (3); CAP-24.b in `docs/contract/`. ROLES-RESEARCH-1 §2.7 and §2.12:
  `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` lines 135-197 (read by name).
- The skill template `template/governance/kernel/templates/skill.md` and an example `scenarios.md`:
  `template/governance/kernel/skills/qa-review/scenarios.md`.
- The precedent suite closest to yours: `tests/acceptance/W2-98/` (the spec-writing skill with its own check
  script `check_spec.py`, its copies cases, KNOWN RED until the copies ACT). Follow its reading rules where this brief
  does not set others. And `tests/acceptance/W2-104/` (the `gov skilleval` harness, its stub model and its exits:
  0 all pass, 3 a scenario failed, 4 not run, 5 unevaluable, 6 adoption refused).
- The skill validator `src/gov/check/skill_validator.py` (its docstring), the adapter check
  `src/gov/adapters/portability.py` (its docstring), and the guard's decision interface as an earlier suite tests it
  (search `tests/acceptance/` for how a case asks the guard `.claude/hooks/pretooluse.py` for a decision by role).

## The behaviour to test: the KPI lines (verbatim in the ticket) as the interface reads them

The ticket's `## Interface` section (in `.tickets/DAEO-uw5h.md` in your tree) is the contract; read it first. The
test designer and the product-spec worker get this same text, word for word, and work in parallel without reading
each other's work. Where this text leaves something open, it is not tested and not relied on.

**The four skills.** `template/governance/kernel/skills/<skill>/` for `<skill>` in `backend`, `api`, `data`,
`security`. Each folder holds at least: `SKILL.md`, `scenarios.md`, `check_domain_skill.py`. After the lead's real
runs it also holds `scenario-records.yaml` (written by `gov skilleval`) and `scenario-summaries.md` (hand-written).
Reference files, if any, sit directly in the skill folder (one level below the skill folder, never deeper), each
linked from `SKILL.md`; a reference file links to no further reference file. Each skill folder is copied byte for byte
to `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` (every file; `SKILL.md` with the same front
matter and body). `.claude/skills/<skill>/` is NOT written by this ticket: the CTO's copies ACT generates it after the
owner's yes (DEC-315, DEC-1112 (3)); any case that needs it is KNOWN RED until that ACT, not skipped, not xfail (as
W2-98's `test_w2_98_copies.py`).

**SKILL.md.** The skill template `template/governance/kernel/templates/skill.md` (W2-11 r1), with its HTML comment
removed:
- front matter: `name: <skill>` (exactly the folder's name), `version: "1.0.0"`, a third-person `description` (what it
  does and when to use it; no first or second person, does not open with a command verb; under 60 tokens),
  `output: none` (a domain skill's method writes no path class of its own), `metadata: {version: "1.0.0"}` repeating
  `version`. No other key; no permission key.
- after a `# <Title>` and one paragraph, the eight level-2 headings, each exactly (case-insensitive, a trailing colon
  ignored): `## When / not when`, `## Inputs`, `## Steps`, `## Done when`, `## Output and handover`, `## Escalation`,
  `## Never`, `## Sources`, in that order; other level-2 headings may stand between them but none after `## Sources`.
  Steps holds at least three checklist items (`- [ ]`). Output and handover names the twelve fields. Escalation names
  P3, P2, P1 and Emergency.
- the body (after the front matter) is at most about 150 lines (the cases allow 165).

**The five labelled parts.** Each of `Conventions`, `Pre-commit checklist`, `Unit-test focus`, `Common mistakes`,
`When to escalate` stands in the body as either a heading of level 2, 3 or 4 whose text is the part's name, or a line
that starts (after optional indentation, a `-`/`*` list marker and `**`/`*`/`_` emphasis) with the part's name
followed by a colon (for example `**Pre-commit checklist:**` or `- **Unit-test focus:** ...`). Matching is
case-insensitive.

**The area's named points (I1's list, fixed here).** Each point is found when its phrase stands anywhere in the body,
case-insensitive, with runs of whitespace folded to one space and a hyphen read as a space (so `contract-first` and
`contract first` both match). The phrase is also the name I1 prints when it is missing:
- backend: `error handling`, `idempotence`, `migration`
- api: `contract-first`, `versioning`, `backward compatibility`
- data: `schema change`, `migration`, `rollback`, `data quality`
- security: `input check`, `secrets never in code`, `least privilege`, `Prepare the Organization`,
  `Protect the Software`, `Produce Well-Secured Software`, `Respond to Vulnerabilities`, `any security finding is a P1`
  (for `Prepare the Organization`, `Organisation` is accepted too). These are NIST SSDF's four groups by their names.
(A phrase is a substring match: `migrations` holds `migration`, `idempotence` is not found in `idempotent`.)

**I1: `check_domain_skill.py`.** One standard-library Python 3 script, byte-equal in the four folders (and so in their
copies). Run as `python3 <skill folder>/check_domain_skill.py <path to a SKILL.md>`. The skill (area) is read from the
given file's front matter `name`; the given file may lie anywhere (a planted copy in a temporary folder is judged by
its own `name`). Output on stdout:
- one line per failure found (all failures, not only the first), each starting `REFUSED <skill>: `, then exit 1:
  - `REFUSED <skill>: missing <section>` for an absent level-2 section, with `<section>` as written above (e.g.
    `missing Never`); `REFUSED <skill>: section order: <section>` for a present section out of the template's order,
    or with a level-2 heading after `## Sources`;
  - `REFUSED <skill>: missing <part>` for an absent labelled part (e.g. `missing Common mistakes`);
  - `REFUSED <skill>: missing <point>` for an absent named point, with `<point>` the phrase as listed above (e.g.
    `missing idempotence`, `missing Respond to Vulnerabilities`);
  - `REFUSED <skill>: permission line <n>: <text>` for a permission-granting line, `<n>` its 1-based line number in the
    file (front matter counted), `<text>` the line stripped. A permission-granting line is a line of the file (front
    matter or body) whose first word, after optional indentation, a `-`/`*` list marker, emphasis, a backtick or a
    quote, is `allowed-tools`, `allowed_tools`, `allowedTools`, `permissions`, `permission` or `allow` (case-insensitive),
    followed directly (after an optional closing quote, backtick or emphasis) by a colon. Prose that mentions the words
    elsewhere in a line is not such a line;
  - (security only) `REFUSED security: finding below P1 line <n>: <text>` for a line that holds the word `finding` or
    `findings` (case-insensitive) and the token `P2` or `P3` (a whole word). So the security skill names P3 and P2 in
    its Escalation only on lines without the word "finding", and states `any security finding is a P1`.
- `PASS` and exit 0 when nothing fails.
- A name outside the four, a missing argument or an unreadable file: not tested (the script may print a REFUSED line
  or a usage line and exit non-zero).

**Scenarios (`scenarios.md`, the `gov skilleval` form, W2-104).** Exactly three scenarios, each a heading
`## <n>. <title>` (n = 1, 2, 3) followed by three bullets `- **Situation:** ...`, `- **Expected:** ...`,
`- **Pass line:** ...` (as `template/governance/kernel/skills/qa-review/scenarios.md`). Each scenario is a situation an
engineer meets in that area, and its pass line judges the session's reply alone (the session has the skill and the
situation text, no repository). The security skill's scenarios include one with a security finding, whose pass line
holds only when the reply routes it as P1. `scenarios.md` is committed (with its two copies) in a commit no later
than the first commit of the skill's `SKILL.md` (S4, F4).

**The records (after the lead's runs; S4).** `gov skilleval template/governance/kernel/skills/<skill> --json`
appends to `scenario-records.yaml` in the skill folder (a map `records:`, a list of entries with `skill`,
`skill_version`, `scenario`, `title`, `verdict`, `cause`, `cost_usd`, `seconds`, `model`, `effort`, `run_at`).
`scenario-summaries.md` beside it holds one entry per recorded run, in this form:

    ## Scenario <n>: <title>
    - verdict: <pass|fail|not-run>
    - run_at: <the record entry's run_at, exactly>
    - summary:
      <line 1 of a three-line summary of the session's reply>
      <line 2>
      <line 3>

S4 holds when, for each skill, scenarios 1, 2 and 3 each have a last record entry with `verdict: pass`, and the
summaries hold an entry with that scenario number, `verdict: pass` and that entry's `run_at`.

**How the code-bound clauses read (from the ticket).** S1, F1, F3: "named by the skill's own check (I1)"; the skill
validator (`python3 -m gov.check.skill_validator`) keeps its front-matter permission key and size halves. F4: the
commit order by the acceptance test's own reading of `git log` (on a planted history, and on the real tree); the
failing-scenario half is `gov skilleval`'s exit 3 (with a stub model in a case). S2: the grep half (no permission grant
in any of the skill's files) and the guard half (the guard's decision for an engineer the same with and without the
skill present) now; the launch record's `skills` list after the copies ACT, not in this suite. S5: `gov skilleval
--adopt` with `governance/project/skill-imports.yaml` (W2-104's harness), in a temporary project with a stub model.
S6/F6: `DRIFT` reads as the adapter check's (`python3 -m gov.adapters.portability`) `SOURCE_DIFFERS` and
`GENERATED_DIFFERS`. F2: I1's refusal of a P2 or P3 route in the text (in the suite) plus a planted P2 copy through the
real `gov skilleval` (the lead's evidence, outside the suite). No product code (`src/`) changes.

## What you write

- Only inside `tests/acceptance/W2-100/` in the tests worktree. No revision of any earlier suite.
- In proportion (STANDARD): every KPI line's success and failure plus the key edge cases; no combinatorial expansion.
  Parametrize over the four skills where a line holds for each.
- **Planted inputs are yours.** You cannot read the real skills, so every planted SKILL.md (a good one per area, and
  the copies each missing one item, one with a permission line, one routing a finding P2) is built by your own
  helper from the interface above, in `tmp_path`, and judged by the real skill folder's `check_domain_skill.py`
  (run as a subprocess from the repository the test sits in). Your good planted copy must PASS; each bad one must be
  refused naming the item. Also a case that the four check scripts are byte-equal, and one that each real SKILL.md
  passes its own check.
- **Repository-state cases** read the real skill folders (structure, sections, parts, points, the validator exit 0,
  body size, reference-file depth, no permission grant in any file, the `.rulesync` copies equal to the source,
  `scenarios.md` committed no later than `SKILL.md` by `git log` on the repository the test sits in, the records and
  summaries as S4 reads them). They are red on your base (no skill folders) and go green once the skills, and for S4
  the lead's real runs, land. Name in the README which cases need the lead's real `gov skilleval` runs (S4's records
  and summaries) and which are KNOWN RED until the copies ACT (`.claude/skills/` copies, the adapter's generated
  comparison, S2's launch record — S2's launch record is not in this suite at all).
- **F4 planted history:** a temporary git repository in `tmp_path` with a skill whose SKILL.md is committed before its
  scenarios.md; your test's own `git log` reading (the same helper the real-tree case uses) refuses it naming the
  skill. A planted scenario record with a failing scenario: `gov skilleval` with a stub that fails one scenario exits 3.
- **S5/F5:** in a temporary project with a stub model: a planted import entry with a licence record (`licence_verdict:
  allowed`) and three passing scenarios is adopted (`gov skilleval --adopt` exit 0); one with no entry, one with a
  forbidding licence verdict, and one with a failing scenario, are each refused (exit 6) and the output names the part.
- **F2:** a planted security skill copy with a line routing a finding P2 is refused by I1 (`finding below P1`); a
  planted security scenario run with a stub whose reply routes the finding P2 fails (`gov skilleval` exit 3); and the
  real security SKILL.md holds no line with `finding` and `P2`/`P3`.
- **S2 guard half:** the guard's decision for the engineer role on a few representative calls (a write inside and
  outside a planted ticket's paths, a read of a secret-like file) is the same with and without a planted
  `.claude/skills/backend/` copy present. If you cannot find how to ask the guard for a decision by role from an
  existing suite, return it as a package instead of guessing.
- **S6/F6:** the real `.rulesync` copies equal the source (the adapter's rule, as W2-98's `differences()`); a planted
  hand edit in a `.rulesync` copy in a minimal planted tree makes the adapter check print `SOURCE_DIFFERS` naming the
  file; the `.claude` cases as W2-98's (KNOWN RED until the copies ACT, skip only when `rulesync` is not installed).
- A `README.md` in `tests/acceptance/W2-100/` that maps each KPI line (S1-S6, F1-F6) to its cases, gives each case's
  expected red reason on the base, names the cases that wait for the lead's real runs and those KNOWN RED until the
  copies ACT, and says how the cases find the code under test.
- **Bite checks:** for each planted-bad case, show once (in your return) that it would fail on a check that does not
  refuse: e.g. a stand-in `check_domain_skill.py` of yours under `tmp_path` that always prints PASS, pointed at by an
  environment variable your support module reads (unset in a real run), as W2-98's `W2_98_SKILL_DIR`.
- Red first: run the suite to the end, never with `-x`, against your base. Cases fail for the reason the README states
  (no skill folders on the base); the purely planted cases that need no skill folder (F4's planted history, S5/F5 with
  a stub, the adapter's planted hand edit) may already pass: name them.
- A KPI line you find ambiguous, or one you cannot test through the interface, is never a guess: return it as a
  package (question, options with cost, recommendation, confidence, what it blocks).

## Commit

Commit only `tests/acceptance/W2-100/`, in the tests worktree, with every trailer in the one final block. Check first
that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there, stop and
return; never `--no-verify`.

    git commit -m "W2-100 tests: <subject>" --trailer "Task: DAEO-uw5h" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-100

(`Implements:` names only the ticket's `sources:`, DEC-927.) Then `git log --oneline -3` and `git status --short`
(expect nothing but the sandbox's own `/dev/null` mount points, if any; name them).

## Return

Your last message, complete in itself. **The twelve fields come first, each a labelled line** ("none" where there is
nothing). Include: the sandbox check's result first in `evidence`; your commits' 12-digit hashes and trailers; the
case count; the KPI lines with their cases; the red reasons as you saw them; the bite checks; the `gov.__file__` line;
the read refusals you met; your scratch figures (`du -s --inodes` and `du -sh` of your `$TMPDIR` at the end); any
package (question, options with cost, recommendation, confidence, what it blocks).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

## Context bundle (`gov context DAEO-uw5h --role independent-test-designer --budget 12000`, built by your lead outside the sandbox)

The ticket's sources, each ACCEPTED: DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112, CAP-24.b; its
dependency DAEO-drhj (W2-104, the skill harness) is closed. Bundle hash `2d2c77d0b287`. The ticket text with its
twelve KPI lines and its `## Interface` is `.tickets/DAEO-uw5h.md` in your tree.
