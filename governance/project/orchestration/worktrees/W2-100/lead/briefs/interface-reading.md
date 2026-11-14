## The interface both workers build to (the ticket's `## Interface`, P-W2-100-IF-1 (a), and the lead's reading of it)

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
