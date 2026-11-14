# Brief: product-spec, DAEO-uw5h (W2-100), batch 1 — domain skills A: backend, api, data, security

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. You write four kernel skills, each the
engineer's skill for its area, with their scenarios, their own check script and their two `.rulesync` copies. An
independent test designer writes the acceptance tests in parallel from the same interface text; you never read them.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `627bcaa19...`) and `git status --short` (expect nothing). If anything
  differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commits exist.
- **Your paths, and only these:** `template/governance/kernel/skills/{backend,api,data,security}/**`,
  `.rulesync/skills/{backend,api,data,security}/**`, `template/.rulesync/skills/{backend,api,data,security}/**`.
  Never `.claude/skills/` (the CTO's copies ACT generates it, DEC-315, DEC-1112 (3)), never `src/`, never
  `governance/project/`, never `tests/`. No product code changes.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag,
  no stash, no `git worktree`.
- **Reads (DEC-820):** reads are open, except: (a) secrets and keys, never read or printed; (b) the held-out
  qualification material's contents (its file names may be seen); (c) **the counterpart's work: never read
  `tests/acceptance/W2-100/`** in any tree or branch (`/home/usain/gov-os-worktrees/W2-100-tests`, `w2/W2-100-tests`);
  (d) the hidden half of any evaluation set. Never open an evaluation set's root or any hidden or memory-verdict
  folder. Search with the Read and Grep tools, naming the folder a search starts at (never the repository root,
  `governance/project/` or `.claude/`); if the first search does not answer, search once more in different words,
  then answer from what you read or say "not found" (no `gov retrieve`, no `gov context` in the sandbox, DEC-1065).
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no backticks,
  no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal
  absolute paths. Anything longer than one line goes in a script file in your sandbox's `$TMPDIR`. Copies: `cp` of a
  named file to a named literal path is fine.
- **Every pytest through the heavy slot**, `TMPDIR` your sandbox's own, `PYTHONUSERBASE=/home/usain/.local`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (you may write a small throw-away test of your own for `check_domain_skill.py` in `$TMPDIR`, never in the repository).
  A slot gate's refusal or wait is a wait, not a refusal.
- **No model call:** never run `gov skilleval` and never start `claude`; the lead runs the real scenarios after you.
- **No import:** write the skills' text yourself. Copy nothing from another collection (no licence record can be made
  inside your paths: `governance/project/skill-imports.yaml` is not yours). NIST SSDF's four group names and OWASP's
  practice names are cited as sources, not copied text.
- Install nothing. No subagents that write. Never write `.gov-runtime/**` outside your sandbox's `$TMPDIR`. Never ask or
  notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal by another tool or
  form (DEC-1142 (9)); report it.
- Write commit hashes as 12 digits in your return, never the full 40.

## What you read

- The ticket `.tickets/DAEO-uw5h.md`: its KPI lines (S1-S6, F1-F6), `allowed_paths`, sources and `## Interface`.
- The sources in `docs/DECISION_REGISTER.md`, by id: DEC-959 (items 4, 5), DEC-957 (Q5 and the P1 rule for security
  and secrets), DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112 (3); CAP-24.b in `docs/contract/`.
- ROLES-RESEARCH-1 §2.7 (the five parts and the four areas' main points) and §2.12 (security):
  `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` lines 135-197, read by name.
- The skill template `template/governance/kernel/templates/skill.md` (follow it section by section; remove its HTML
  comment from each written skill).
- Precedents: `template/governance/kernel/skills/spec-writing/` (a skill with its own standard-library check script
  `check_spec.py`, and how W2-98 made its two `.rulesync` copies) and `template/governance/kernel/skills/qa-review/`
  (`scenarios.md`, the form `gov skilleval` reads). The engineer role file `template/governance/kernel/roles/engineer.md`
  and the vendored skills it loads (`template/governance/kernel/skills/superpowers/`): a domain skill sits beside them
  and refers to them, never restates them.

## The interface you build to

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

## The work, in this order (S4: scenarios before text)

1. **Scenarios first, one commit.** Write `scenarios.md` for each of the four skills (three scenarios each, the form
   above: situations an engineer meets in that area; the pass line judges the reply alone; security's include one with
   a security finding that passes only when the reply routes it P1). Copy each to its two `.rulesync` folders. Commit
   the twelve files in one commit (subject `W2-100 (DAEO-uw5h): the three scenarios of the backend, api, data and
   security skills, before their text (DEC-959 item 5)`).
2. **The check script.** `check_domain_skill.py` (standard library only, Python 3, a module docstring giving usage and
   the output forms; about 100-150 lines), byte-equal in the four folders. Test it yourself on planted good and bad
   copies in `$TMPDIR` (each missing section, part and point, a permission line in the front matter and in the body,
   prose that only mentions `allowed-tools` mid-line, a security finding line with P2 and with P3).
3. **The four SKILL.md files**, each within about 150 body lines, detail (if any) in reference files directly in the
   skill folder, linked from the body. Each holds the five labelled parts, the area's named points, Steps as a
   checklist, Done when as checkable lines, Output and handover naming the twelve fields, Escalation mapped to P3, P2,
   P1 and Emergency (a security finding always P1, a secret exposed an Emergency), Never, Sources last (the ticket's
   sources plus ROLES-RESEARCH-1 §2.7, DEC-957, and for security NIST SSDF SP 800-218 and OWASP by name). The skill is
   a method only and grants nothing: no permission key, no permission-granting line, no step that widens the engineer's
   reads or writes (CAP-24.b). Unit-test focus refers to the engineer's vendored test-driven-development skill rather
   than restating it.
4. **Copies.** Copy every file of each skill folder byte for byte to `.rulesync/skills/<skill>/` and
   `template/.rulesync/skills/<skill>/`.
5. **Checks, each to the end, quoted in your return:**
   - `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md`
     for each of the four: `PASS`, exit 0; and `sha256sum` of the four scripts (one hash).
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.check.skill_validator template/governance/kernel/skills/backend template/governance/kernel/skills/api template/governance/kernel/skills/data template/governance/kernel/skills/security`: exit 0.
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.adapters.portability` (in the worktree): no
     `SOURCE_DIFFERS`, `SOURCE_MISSING` or `SOURCE_WITHOUT_KERNEL` for the four skills. Findings about the four skills'
     `.claude/skills/` copies (generated, absent until the copies ACT) are expected: name them; any other finding that
     was already there on `627bcaa19` is not yours: say so.
   - `diff -r` of each skill folder against each of its two `.rulesync` copies: empty.
   - `wc -l` of each SKILL.md body and `git log --format='%h %s' -- <skill>/scenarios.md <skill>/SKILL.md` showing the
     scenarios' commit older than the text's.
6. **Commit** the script, the four SKILL.md files, any reference files and all copies (one or more commits, after the
   scenarios' commit).

Commit only your paths, every trailer in the one final block; check first that
`/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is, stop and return; never
`--no-verify`):

    git commit -m "<subject>" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Then `git log --oneline -4` and `git status --short` (expect nothing but the sandbox's own `/dev/null` mount points,
if any; name them).

The lead will later run `gov skilleval` on each skill and may resume you (batch 2) with the runs' `--json` output to
write `scenario-summaries.md` and re-copy the records; in this batch you write neither.

## Return

Your last message, complete in itself. **The twelve fields come first, each a labelled line** ("none" where there is
nothing). Include: the sandbox check's result first in `evidence`; each commit's 12-digit hash, subject and trailers;
the checks above with their output; each body's line count; the script's sha256; the read refusals you met; your
scratch figures (`du -s --inodes` and `du -sh` of your `$TMPDIR` at the end); any package (question, options with
cost, recommendation, confidence, what it blocks).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

## Context bundle (`gov context DAEO-uw5h --role product-spec --budget 12000`, built by your lead outside the sandbox)

The ticket's sources, each ACCEPTED: DEC-959, DEC-957, DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112, CAP-24.b; its
dependency DAEO-drhj (W2-104, the skill harness `gov skilleval`) is closed. Bundle hash `2d2c77d0b287`. The ticket text
with its twelve KPI lines and its `## Interface` is `.tickets/DAEO-uw5h.md` in your tree.
