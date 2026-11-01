## The specification of W2-55's public behaviour (the lead's interface spec, the same text in both workers' briefs)

The ticket's KPI lines say what must be true; they do not say what the register's tags look like or where the
checks are called. So that the test designer and the engineer, working in parallel and never reading each
other's work, meet on the same behaviour, these public forms are fixed for this run (a P3 choice of the lead,
inside the ticket's paths, reversible). Everything not fixed here is the implementer's choice, and the tests do
not depend on it.

### S1. The register and its entries

- The register is the file the project's path map (`governance/project/path-map.yaml`) names under
  `decision_register`, read from `HEAD`, exactly as the store reads it (`gov.store.load(root)`; W2-03's entry
  grammar: a heading `### DEC-<n> — <title>` or `### DEC-<n>: <title>`, then a line `- **Status:** <WORD> …`).
  A test commits its register in a temporary git repository and loads the store before calling anything.
- An entry's **tags** are one line of the entry, beginning `- **Tags:**`, of the form
  `- **Tags:** domain: <domain> · scope: <scope> · lands in: <places>` with an optional final ` · done`.
  - `<domain>`: one word of the closed list: `guard`, `close`, `retrieval`, `context`, `adopt`, `launch`,
    `checks`, `plan`, `roles`, `records`, `release` (DEC-791 item 1).
  - `<scope>`: `repository` (this repository only) or `kernel` (kernel-wide) (DEC-791 item 1).
  - `<places>`: one or more paths, separated by `, `, of files `HEAD` holds, that state the rule (DEC-825
    item 2, DEC-851): for scope `kernel` at least one under `template/governance/kernel/`; for scope
    `repository` at least one under `governance/project/` (the prompt or the project briefs). `none` is allowed
    only for an entry that is superseded or done.
  - ` · done`: the entry was a one-off whose action is finished; it stays in the register, and it is not in
    force.
- **Superseded:** an entry whose status word is `SUPERSEDED`, or which another entry's status line names after
  `**Supersedes:**`.
- **Changed:** an entry which another entry's status line names after `**Changes:**`, `**Settles:**`,
  `**Corrects:**`, `**Reverses:**` or `**Withdraws:**`, or whose own status line has a `**Changed by:**` note.
  A changed entry is still in force for its other parts.
- **The status names what superseded or changed it (DEC-791 item 1, DEC-866 item 1):** a `SUPERSEDED` entry's
  status line says `SUPERSEDED by DEC-<n>`, naming an entry of the register; an entry that another entry names
  as superseded or changed (the fields above) carries that entry's id on its own status line (`SUPERSEDED by
  DEC-<n>` or `**Changed by:** DEC-<n>`).

### S2. The decisions validator's register checks

- `gov.decisions.check_tags(root)` returns a list of findings, each a dict with `code`, `ids`, `paths` and
  `message`, as W2-03's `gov.decisions.check(root)` does; an empty list passes. `python3 -m gov.decisions.tags`,
  run in a project root, prints the findings and exits 1 when there are any, 0 when there are none (the form a
  `gov check` family's command takes).
- A finding names the entry (its id in `ids`, the register's path in `paths`) and what is wrong, with these
  codes: `TAG_MISSING` (no tags line, or a tags line without a domain, a scope or a lands-in part; the message
  names which), `TAG_DOMAIN_UNKNOWN` (a domain outside the closed list), `TAG_SCOPE_UNKNOWN`,
  `TAG_LANDS_IN_UNKNOWN` (a place `HEAD` does not hold), `TAG_LANDS_IN_MISPLACED` (no place where its scope
  says), `STATUS_SUCCESSOR_UNNAMED` (a `SUPERSEDED` entry naming no successor, or one the register does not
  hold), `STATUS_RELATION_UNMARKED` (an entry another entry supersedes or changes whose status line does not
  name that entry; `ids` holds both, the old first).
- W2-03's `gov.decisions.check(root)` keeps its own codes and results: the register checks are not added to its
  list (the close and the escalation lift read that list).

### S3. Supersession propagates (DEC-866)

- `gov.decisions.check_propagation(root)` returns findings in the same shape; `python3 -m
  gov.decisions.propagation`, run in a project root, prints them and exits 1 when there are any, 0 when there are
  none.
- **What enforces an old decision:**
  - for a **superseded** entry: any line of a searched place that cites its id (`DEC-<n>` as a whole word), in a
    file that does not also cite the entry that superseded it;
  - for a superseded **or changed** entry: any line of a searched place that holds one of the entry's recorded
    values. The values are on the old entry, one line: `- **Values:** "<text>", "<text>"` (literal strings
    that state the old rule, such as `"300000"` or `"LEAD_CHECKPOINT"`).
  - A changed entry's id alone is no finding (the id does not tell which part is cited).
- **The searched places,** read from `HEAD`: `tests/`, `src/`, `template/`, `governance/project/prompts/`,
  `governance/project/briefs/`, `governance/project/path-map.yaml`, and the ticket files `.tickets/*.md` whose
  frontmatter `status` is not `closed` (a closed ticket is a record). The register itself and other records
  (`docs/`, `governance/project/orchestration/`) are not searched.
- **A recorded reason:** a line of the old entry, or of the entry that superseded or changed it,
  `- **Kept:** <path> — <reason>`, one line per kept file; a kept file gives no finding for that old entry.
- **A finding** has code `ENFORCES_SUPERSEDED`, `ids` `[<old>, <new>]` (the old decision and the one that
  superseded or changed it), `paths` `[<the place>]`, and a message naming both decisions and the place with its
  line number.
- Its first fixture is the sweep of 2026-10-20 (`governance/project/orchestration/packages/SWEEP-2026-10-20.md`):
  W1-49's two window cases (DEC-636 and DEC-665 against DEC-838: tests asserting a 300k window) and W2-59's three
  earlier cases (DEC-605 against DEC-822 and DEC-835: tests where the judge imports the judged project's code)
  are found when the register records those relations and values.

### S4. What agents see: `gov context` and `gov retrieve`

- **`gov retrieve <query> --json`:** evidence from the register whose entry is superseded or done is left out of
  the bundle. When at least one was left out, the bundle (the envelope's `result`) has a key `left_out`:
  `{"count": <n>, "superseded": [<ids>], "done": [<ids>]}` (ids sorted, each id once; `count` the number of
  distinct entries left out). When none was left out the key is absent and the bundle is as before.
- **`gov context <ticket> --json`:** the supplementary context leaves out register evidence of superseded or done
  entries in the same way, and the packet has the same `left_out` key when at least one was left out (absent
  otherwise, so a packet with nothing left out, and its hash, stay as before). The mandatory inputs are as
  before: a superseded mandatory input still refuses (`BLOCKED`); a done entry the ticket declares as a source is
  still read.
- A changed entry (S1) is not left out.
- Lens B's Q05 (a superseded decision served unmarked, `F4`: the superseded filter did nothing for register
  decisions) no longer happens.

### S5. `gov context --in-force`

- `gov context --in-force --json` (no ticket) gives, in the envelope's `result`:
  - `lines`: one string per register entry in force, in the register's order, each beginning with the entry's id,
    then its title; an entry that is changed (S1) names, on its line, the entries that changed it;
  - `left_out`: `{"count": <n>, "superseded": [<ids>], "done": [<ids>]}`, the entries not in force and why;
  - `register`: the register's path.
- In force: every entry that is neither superseded nor done (S1). It is generated from the register at `HEAD`
  (the store's copy), never from a hand-made file such as `governance/project/orchestration/DECISIONS-IN-FORCE.md`.
- A project whose path map names no register gives an empty `lines` and a `left_out` count of 0; a named register
  that cannot be read refuses, never an empty digest.
- `gov context <ticket>` without `--in-force` is unchanged; `gov context` with neither a ticket nor `--in-force`
  is refused by the parser.
- The session-start hook's loading of the digest is not part of this run (the owner's CIT-P question, DEC-952
  item 5).

### S6. The backfill proposal (KPI 4)

- `docs/research/W2-55-backfill.md`, a proposal only: nothing is written to `docs/DECISION_REGISTER.md` (it is
  not in the ticket's paths; the orchestrator applies the accepted backfill).
- Sections, by these headings:
  - `## Proposed tags`: a Markdown table with one row per entry of the register at the ticket's base, in the
    register's order, columns `| id | domain | scope | lands in | status | reason |`: the proposed domain (from
    the closed list), scope (`repository` or `kernel`), lands in (paths, or `none`), status (the proposed status
    note: in force, `done`, `SUPERSEDED by DEC-<n>` or `Changed by: DEC-<n>`) and the reason for the proposal;
  - `## Amends and refines`: every relation DEC-825 item 4 left for this ticket (the entries whose text amends or
    refines an earlier entry, about 120), one line each, `DEC-<new> amends|refines DEC-<old>`, with the status
    note proposed for the old entry;
  - `## Sample for the owner's review`: the entries drawn for the owner, how they were drawn (a stated seed or
    rule, so the draw can be repeated), and what the owner is asked to check.
- How the proposal was made is stated in the file (the script or the rules), so it can be made again.
