# W1-11 — Decision checker and owner-approval facts: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-be7u` (W1-11), the Contract
items its KPI lines name (CAP-51.a, CAP-01.b, CAP-21.a, CAP-34.d, with the acceptance lines of CAP-51, CAP-21 and
CAP-34 and CAP-21's lite form), ADR-0001 ("Approval facts"), the "Rules for every ticket" of the Wave 1 plan, and
DEC-012, DEC-039, DEC-046, DEC-074, DEC-136, DEC-182, DEC-221, DEC-227, DEC-274 to DEC-278, DEC-308, DEC-312, DEC-322
and DEC-328. Written before implementation. Profile FULL. No earlier ticket's test was rewritten.

**55 cases in 43 test functions.** Four decision packages are open (DP-1 to DP-4, below). 23 cases follow a
package's recommended option and wait on its answer; 32 hold whatever the answers are.

## Run

```sh
python3 -m pytest tests/acceptance/W1-11 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed. About 7 seconds when green.

- **Every call runs in a new Python process**, through a small driver written to a temporary directory, with this
  worktree's `src/` on `PYTHONPATH`.
- **Nothing is written in this worktree.** Every project is a temporary git repository, or a clone of the b-dev tier
  in a temporary directory. The store is built there, never in this repository (DEC-322).
- **Environment, built from scratch:** `PATH`, an empty temporary `HOME`, `TMPDIR`, locale, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX`. The session's `GOV_ROLE` and `GOV_TICKET` are not passed on.
- **Before a check, the project is committed and `gov.store.load` is run**, so the checker may read the record
  graph, git or the working tree: the three agree. One read-only test leaves uncommitted work in the tree on
  purpose and asserts only that nothing is touched.
- **Fixture commits have fixed dates (after 2026-10-03, DEC-182), authors and trailers.** No commit is signed.
- **The five b-dev tests are marked `local_only`** and skip when `GOV_DEV_TIERS` (default
  `~/gov-os-workbench/synthetic`) has no `b-dev`. They clone the tier; the tier itself is never checked or written.

## The public interface

No `gov` command belongs to this ticket: no KPI names one, `src/gov/cli/**` is outside its `allowed_paths`, and
W1-26 runs the checker from `gov check`. So no `NOT_IMPLEMENTED` case of the W1-07 registry changes. The tests call
one function, as `gov.store` and `gov.tasks` are called (DEC-275). The engineer builds to exactly this:

**`gov.decisions.check(root)`** (`src/gov/decisions/`)

- `root` is a `pathlib.Path`: a project that is a git repository.
- It returns a list of findings, plain JSON data. **An empty list passes; any finding fails.** The same tree gives
  the same list twice.
- It only reads. It writes no file under `root`, stages nothing, commits nothing and moves no ref.
- A `root` that is not a git repository raises `gov.cli.errors.GovError` with a non-empty `code` and `details` a
  map. It is never an empty list. The code's name is the engineer's.

**A finding** is a map with four keys:

| Key | Value |
|---|---|
| `code` | One of the codes below. |
| `ids` | A list of strings: the ids of the records the finding is about. |
| `paths` | A list of strings: the files concerned, relative to `root`, with `/`. |
| `message` | A non-empty string for a person. |

A finding may carry more keys. The tests read `ids` and `paths` as sets, and (except for a cycle) ask only that the
ids and paths below are among them.

| Code | Raised when | `ids` hold | `paths` hold |
|---|---|---|---|
| `ACTIVE_SUPERSEDED` | A decision's `status` is `ACTIVE` and another decision's `supersedes` names it, or its own `superseded_by` names a successor. One finding for each such decision. | the ACTIVE decision | its file |
| `DUPLICATE_ID` | Two decision files have the same `id`, in one directory or in two. | the id | both files |
| `OVERLAPPING_ID` | Two decision files in different directories have ids with the same number and different prefixes (`ADR-003`, `DEC-003`). | both ids | both files |
| `SUPERSESSION_CYCLE` | The supersession edges form a cycle; a decision that supersedes itself is one. | exactly the members of the cycle, in one finding | (not asserted) |
| `ACTIVE_UNAPPROVED` | The commit that last set a decision's `status` to `ACTIVE` (added the file with it, or changed the status to it) is not an owner approval fact. One finding for each such decision. | the decision | its file |
| `GATE_NOT_AUTHORISING` | A record cites as its approval a gate that is not answered (`ACCEPTED`) or whose `cit` is not the record's. One finding for each citing record and gate. | the citing record and the gate | the citing record's file |
| `TICKET_WAITS_ON_DEAD_GATE` | A ticket that is not closed is named in the `constrains` of a `DECLINED`, `REVOKED` or `STALE` package. | the ticket and the package | the ticket's file |

**A decision file** is a Markdown file whose frontmatter is a decision: `type: decision`, or an `id` that fits the
`decision_id` grammar of `common.schema.json` (DEC-227). The second half is needed for b-dev, whose decision files
have no `type` and are therefore not records of the store (DEC-274). Supersession is read as the store reads it
(DEC-277): `supersedes` on the successor, `superseded_by` on the predecessor, one edge.

## KPI lines and their tests

Covers ids: CAP-51.a (17 cases), CAP-01.b and CAP-21.a (11), CAP-34.d (19). The read-only KPI has 6 cases; the
remaining 2 are the interface's own (the same findings twice, and the error case).

| KPI line | Covers | Tests | Waits on |
|---|---|---|---|
| Success 1: flags ACTIVE-while-superseded, duplicate or overlapping ids across directories, and supersession cycles on the b-dev fixtures | CAP-51.a | `test_w1_11_b_dev.py`: the first four tests (HZ-B-06 as planted; HZ-B-03, a cycle and a duplicate id written into the clone). `test_w1_11_hazards.py`: 11 functions, 13 cases, for each class in a register the test plants | nothing; DP-1 asks whether more is owed on the tier as planted |
| Success 2: a change that sets a decision ACTIVE without an owner approval fact from git fails | CAP-01.b, CAP-21.a | `test_w1_11_approval.py`: 7 tests that hold for any definition of the fact (an agent's commit adds or sets ACTIVE; no trailer; the file claims its own approval, CAP-01.b; the owner named in the message body; PROPOSED passes; every one flagged), and 4 that need the fact | the last 4: DP-2 |
| Success 3: files stay byte-identical | none | `test_w1_11_read_only.py` (5), `test_the_tier_is_byte_identical_after_the_check` | nothing |
| Success 4: a declined, revoked or stale gate, or a gate answered for another CIT, does not authorise execution | CAP-34.d | `test_w1_11_gates.py`: 6 functions, 13 cases, on a ticket and a change record that cite a gate; 3 functions, 6 cases, on a ticket that waits on a package | 13: DP-3; 6: DP-4 |
| Failure 1: any planted decision hazard is missed | CAP-51.a | `test_every_hazard_planted_together_is_flagged`, `test_every_active_superseded_decision_is_flagged_not_only_the_first`, `test_every_unapproved_active_decision_is_flagged`, the b-dev tests | nothing |
| Failure 2: the checker rewrites a decision file | none | `test_w1_11_read_only.py`, the b-dev read-only test | nothing |

The interface itself: `test_the_same_tree_gives_the_same_findings_twice`,
`test_a_folder_that_is_no_git_repository_is_an_error_not_a_pass`, and the shape of every finding, which
`w1_11_support.findings` checks on every call.

## Red run

Run on `w1/W1-11` at `116e2035`, before implementation: **55 failed**, every one with

```
w1_11_support.CheckerMissing: the decision checker does not exist: No module named 'gov.decisions' under src/
```

No collection error and no other reason. The suite was also run against a throwaway reference checker in a copy of
`src/` outside the tracked tree (the session's scratch directory, deleted with it): 55 passed, the five b-dev tests
included. So each test can go green, and no test is red for a reason of its own.

Expected red reason once the package exists, line by line: success 1 and failure 1, `no <CODE> finding names ids
[...] and paths [...]`; success 2, `no ACTIVE_UNAPPROVED finding names ...` or the findings shown for a decision the
owner approved; success 3 and failure 2, a list such as `docs/adr/ADR-0010.md: rewritten` or `git status changed`;
success 4, `no GATE_NOT_AUTHORISING finding names ...`.

## The six points

1. **The checker's public interface** is settled: `gov.decisions.check(root)`, as above. Sources: DEC-275 (a Python
   interface), the ticket's `allowed_paths`, the conventions of `gov.store` and `gov.tasks` (plain JSON, `GovError`).
   Left out on purpose, because no KPI needs it: a commit range. The approval rule is judged on `HEAD`'s decisions
   over the whole history, so a legacy register (all of b-dev) is reported unapproved until the owner adopts it.
   W1-26 may need a range or a baseline; that is its test design's.
2. **An owner approval fact** is not settled testably: package DP-2.
3. **The MADR schema.** `madr.schema.json` (W1-08) validates the frontmatter of a `type: decision` record: the
   shared frontmatter, `id` by `decision_id`, `depends_on`, `implements`, `constrains`. No KPI line of this ticket
   says what W1-11 adds to it, and DEC-012 leaves the status list open ("ACTIVE/PROVISIONAL/SUPERSEDED/…"), so this
   suite asserts nothing about the schema's content; W1-08's suite keeps what it holds. Noted for the lead, not
   packages: the five gate `status` values (W1-34 residual) belong in `decision-package.schema.json`, which is
   outside this ticket's `madr*` path; `supersedes` and `superseded_by` still have no grammar (W1-08 residual); the
   two committed ADRs lack `state_class`; whether the checker reports schema failures, or `check-jsonschema` does
   beside it in W1-26, is not asked by any KPI line and is not tested.
4. **How a record cites a gate, and what "another CIT" compares** is not settled: package DP-3. DEC-328 fixes the
   gate's side (`status`, `cit`). Nothing fixes the citing side.
5. **What a declined, revoked or stale package does to waiting tickets** is W1-11's to decide (DEC-308): package
   DP-4.
6. **G-04** was not read. One KPI line is touched by it: what the D2 checker was expected to flag on b-dev as
   planted. Package DP-1.

## Decision packages

### DP-1 — What must be flagged on b-dev as planted

- **Question.** KPI success 1 names three classes "on the b-dev fixtures (HZ-B-03, HZ-B-04, HZ-B-06)". As planted,
  the tier's 14 decision files carry `id`, `title`, `status` (all `ACTIVE`), `date`, `author`: no `type`, no
  `supersedes`, no `superseded_by`. HZ-B-03 is the absence of a link ("DEC-003 has no supersedes field"), stated
  only in prose; HZ-B-04 is three records on one subject "with no formal relationship edges"; the tier has no
  cycle. Is the frontmatter rule enough, or must the checker read prose?
- **Why now.** It decides whether the checker is deterministic over frontmatter and git, and how large it is.
- **Options.** (a) Frontmatter and git only. On the tier as planted the checker flags the overlapping ids of the
  two directories (six pairs, which cover HZ-B-06 and the id overlap at ADR-003/DEC-003 and ADR-002/DEC-001);
  ACTIVE-while-superseded, a cycle and a duplicate id are tested on a clone into which the test writes the link
  the hazard describes. (b) The checker also reads decision bodies for supersession and overlap statements
  ("superseded by DEC-003", "Overlaps with ADR-002"). (c) Reword the KPI to name only what the tier plants.
- **Impact.** (a) is what this suite asserts; HZ-B-03's prose and HZ-B-04's subject overlap stay for the audit
  scenarios (AUDIT-B-01, AUDIT-B-02) and retrieval. (b) adds a text heuristic to an enforcement check, with false
  positives on any body that discusses supersession. (c) changes the ticket.
- **Reversibility.** High: (b) can be added later as more tests; nothing in (a) is undone.
- **Cost.** (a) none beyond this suite. (b) about 40 to 80 lines and a rule for what counts as a statement.
- **Recommendation.** (a).
- **Confidence.** Medium. G-04 in the S0b2 output (what the D2 candidate flagged on b-dev in the bake-off) would
  settle it.
- **Blocks.** No test. Under (b), tests are added for the tier as planted.

### DP-2 — What an owner approval fact from git is

- **Question.** Which commit, author, signature or trailer makes one? The sources agree on the words: "the owner's
  git account: an owner commit, a signed tag or a PR approval" (CAP-21 lite form, ADR-0001, DEC-039, DEC-046). They
  do not say how a check tells the owner's commit from an agent's. In this repository agents commit under the
  owner's name and email, no commit is signed (`git log --format=%G?` gives `N` for all), and a PR approval is not
  in git and cannot be read without the network.
- **Why now.** Four tests need a commit that is an approval; the engineer needs the rule.
- **Options.** (a) The commit carries `Role: owner` in its final trailer block (DEC-182); DEC-312 records the one
  owner commit so far in exactly that form. (b) The commit's author or committer email is the owner's, named in
  project configuration; in this repository that is every agent commit too. (c) The commit, or a tag that contains
  it, has a valid signature by a key listed for the owner (`gpg.ssh.allowedSignersFile`); nothing is signed today,
  and the owner would have to sign every approval. (d) Any of a, b, c combined.
- **Impact.** (a) guards against mistakes and drift, which is the threat model (DEC-039): an agent can type the
  trailer, and the guard can refuse that for worker roles later. (b) guards nothing here. (c) is the only one an
  agent cannot produce, and needs a key, a signers file and a signing habit before any decision can be ACTIVE.
- **Reversibility.** High between (a) and (c): the rule is one function, and (c) can be added on top of (a).
- **Cost.** (a) about 15 lines. (c) about 40 lines, test keys generated per run, and owner setup.
- **Recommendation.** (a) for Wave 1, with (c) recorded as the stricter form.
- **Confidence.** Low to medium: it is the owner's trust rule. The archived D-0007 (the trust direction that
  DEC-046 simplifies), Contract v3 Gate E1 and OWNER-CLARIFICATION-P2-0004 would settle the wording; a product-spec
  worker may read them (DEC-222).
- **Also open under it.** Whether a later owner commit or signed tag that does not touch the decision approves an
  earlier agent change. The suite says no only where the agent's change is the last to set ACTIVE; the mixed case is
  not tested.
- **Blocks.** `test_an_owner_commit_that_sets_a_decision_active_passes`,
  `test_a_register_the_owner_approved_passes_the_whole_check`,
  `test_an_agent_edit_that_leaves_an_approved_decision_active_passes`,
  `test_an_agent_that_sets_an_approved_decision_active_again_fails`. They follow (a). The other seven approval tests
  hold under every option: the agent's commits differ from the owner's in author, committer, role, signature and
  tag.

### DP-3 — How a ticket or change cites a gate as its approval, and which CIT is compared

- **Question.** DEC-328 fixes the gate: state in `status`, CIT in `cit`. DEC-308 fixes one edge, from the package to
  its waiting tickets (`constrains`). Nothing names the key by which a ticket or a change says "this gate
  authorises me", nor where a ticket or change holds its own CIT. The ticket schema and template have neither.
- **Why now.** KPI success 4 cannot be tested without both.
- **Options.** (a) The citing record (a ticket, or a change record such as a CIT-E) names the gates in a
  frontmatter list `approval` and its own CIT in `cit`; the gate authorises when its `status` is `ACCEPTED` and its
  `cit` equals the record's. (b) No new key: a ticket cites every package that names it in `constrains`; the CIT is
  not compared until tickets carry one. (c) A commit trailer (`Approval: DP-0001`) cites the gate for a change.
- **Impact.** (a) adds two optional keys to tickets and change records; the ticket schema is outside this ticket's
  paths and accepts extra keys today. (b) cannot express "answered for another CIT". (c) puts the citation where
  DEC-277 says edges are not read.
- **Reversibility.** Medium: the key name is cheap to change until real tickets use it.
- **Cost.** (a) about 25 lines in the checker. A schema line for `approval` and `cit` belongs to a later ticket.
- **Recommendation.** (a). An open (`PROPOSED`) gate does not authorise either, as the W1-34 template says ("Only an
  answered gate of the same CIT permits the next actions").
- **Confidence.** Low to medium. Contract v3 Gate L3 (the source of CAP-34.d) would settle what "cites" meant.
- **Not tested, and to decide with it:** a cited gate that is no record; a citing record with no `cit`.
- **Blocks.** The 13 cases of the first group of `test_w1_11_gates.py`.

### DP-4 — What a declined, revoked or stale package does to the tickets that wait on it

- **Question.** DEC-308: a ticket named in the `constrains` of a `PROPOSED` package is not READY, and "W1-11 decides
  what a declined or stale package does". As built, the READY rule (`gov.tasks`, outside this ticket's paths)
  releases the ticket as soon as the package is no longer `PROPOSED`, so a declined package frees its tickets.
- **Why now.** That release is the case CAP-34.d forbids, and W1-11 is the ticket named to close it.
- **Options.** (a) The checker fails every ticket that is not closed and is named in the `constrains` of a
  `DECLINED`, `REVOKED` or `STALE` package (`TICKET_WAITS_ON_DEAD_GATE`), until the ticket is removed from the
  package or a new package answers the question. The READY rule is unchanged. (b) The READY rule keeps such a ticket
  blocked; that changes `src/gov/tasks/**` and W1-09's suite, in another ticket. (c) Both.
- **Impact.** (a) fits this ticket's paths; a READY queue can still list the ticket until W1-26 runs the checker.
  (b) closes it at the queue.
- **Reversibility.** High.
- **Cost.** (a) about 15 lines. (b) a KPI line and tests on a W1-09 follow-up.
- **Recommendation.** (a) now, (b) as a residual for the ticket that next changes the READY rule.
- **Confidence.** Medium.
- **Blocks.** The 6 cases of the second group of `test_w1_11_gates.py`.

## Residuals the suite leaves

- A decision file that cannot be read (broken or unclosed frontmatter) is in the read-only fixture; what the checker
  reports for it is not asserted.
- Status values in another case, and a superseder that is itself `PROPOSED`, are not tested.
- Overlapping ids are tested only for identical digit strings (`ADR-003`, `DEC-003`); `ADR-0001` beside `DEC-001`
  is not. This repository's own two series (ADR files, DEC headings in the register) are not both files yet.
- Two overlapping ids inside one directory are not tested: the KPI says "across directories".
