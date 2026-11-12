# W2-113 acceptance tests: an adopted product's CTO is named at adoption

Ticket: `DAEO-g29a` (W2-113) · Profile: STANDARD · Sources: DEC-971 item 4, DEC-957, DEC-982, DEC-974, DEC-1083
(the quiet-hours hook is lifted, not tested) · Interface: the ticket's `## Interface` I1-I3 (DEC-1052, the owner's
PKG-1 (a), DEC-1156 (4); I2 (iii) is PKG-3 (b), DEC-1157 (15)) · Author: independent test designer (MR-3), run 2 of the
ticket, with the two I2 (iii) cases revised in run 3 (below). Written from the ticket's KPI lines, I1-I3 and the existing
code at the base, in parallel with the engineer, without reading the implementation (DEC-963). The base of run 2 was
`4d2773584a8f`; the base of the run-3 revision (and of the red run below) is `159abfe062c6` (the ticket branch's head when
the tests branch was remade).

**Run 3 (DEC-1157 (15), PKG-3 (b), the owner, 2026-11-12).** The ticket's I2 (iii) was "`tk` missing: A0 refuses and
writes nothing". It is now: "`tk` missing: A0 completes without creating the ticket or the key, and its record says so;
the guard stays closed (every install refused, the refusal naming `GOV_TICKET` and how to set the key)". Exactly two
cases were revised (`test_w2_113_defaults.py`; both carry the trailer `Rewrite-Reason: DEC-1157 (15)`), one helper added
to `w2_113_support.py`; no other case, no other module's behaviour changed:

| Was (run 2) | Now (run 3) |
|---|---|
| `test_a0_refuses_when_tk_is_missing` | `test_a0_completes_without_a_ticket_or_a_key_and_its_record_says_so_when_tk_is_missing` |
| `test_a0_writes_nothing_when_tk_is_missing` | `test_the_guard_stays_closed_when_tk_is_missing` |

The role-file KPI (the `moved:` line, W2-33's) and the quiet-hours hook (the `lifted:` line) are not tested here.

Run it from the root of the worktree the tests sit in (every pytest through the heavy slot, `TMPDIR` outside the repo):

    PYTHONPATH=<that worktree>/src python3 -m pytest tests/acceptance/W2-113 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line

`copier` comes from `~/.local/bin/copier` or `PATH` (W1-39), `rulesync` from `RULESYNC_BIN` or `~/.local/bin/rulesync`
(W1-38), PyYAML is the product's own dependency. Nothing is installed: an install command is only text in the hook's
input.

**74 cases in 5 modules** (about 8 s for the whole run on the base: the product is generated once, in about 3 s).

**Red run on the base (`159abfe062c6`, run 3): 35 failed, 39 passed, 0 skipped, 0 errors, 11.0 s** (run 2's red run on
`4d2773584a8f` had the same counts: the two revised cases stay red, for other reasons). Every red is an assertion that
fails for the ticket's reason, never a collection, import or fixture error:

- **R1, A0 creates no ticket and writes no roster, and its record is silent about `tk` (14 cases).** A0 succeeds on the
  planted repository and ends with `.tickets/` and the roster as it found them: "A0 must create exactly one ticket in
  .tickets/ ... the files it added: []" (11 cases: 6 of the adopted-repository module, the 4 that put a worker on the new
  coordination ticket, and the `other-content` roster's key), "A0 did not add coordination_ticket to the roster" (1),
  "the key's line must be the only line A0 adds; it added []" (1), and for the `tk`-missing record case "A0's record
  governance/adoption/A0-safety-baseline.md must say that no coordination ticket was created because tk is missing" (1:
  on the base A0 *does* complete with `tk` missing, creates nothing and adds no key, which is what (b) asks, but its
  record says nothing about `tk`: it reads `tree: clean`, `set_up: []`, "Written by `gov adopt --lite --stage A0`").
- **R2, the refusal does not name `GOV_TICKET` (11 cases).** The base's refusal names the file and the key and says
  "(set at adoption)", but never `GOV_TICKET`. 10 are the success-2 cases; the 11th is `test_the_guard_stays_closed_when_tk_is_missing`
  (A0 succeeded, every one of the 8 installs is refused, each refusal says how to set the key, none names `GOV_TICKET`).
  **That case is red on the base, not green:** no key means the install is refused already, but the refusal's words
  are the old ones.
- **R3, the refusal says "(set at adoption)" as a fact (10 cases).** The base's text says it in all five planted
  products, of which none was adopted.

## How the cases run the code of the worktree they sit in (DEC-732)

Every path is taken relative to the test files (`REPO_ROOT = Path(__file__).resolve().parents[3]`,
`w2_113_support.py`). Merged into the ticket's worktree, the cases judge that worktree's `src/` and `template/`.

- **A planted repository adopted (I3).** W2-90's `generate_project` (copier copy of an assembled template source, then
  `rulesync generate`) is run once per session (fixture `generated`). Per case it is copied into a folder named
  `harbour/` (the repository's folder is the product's name), the three fixture tickets are written
  (`w2_113_support.plant`) and committed with `commit_all`, and the tree is checked clean. `gov adopt --lite --stage
  A0 --json` then runs as a child process (W2-23's `run_gov`: `python -m gov.cli.main`, this worktree's `src` first on
  `PYTHONPATH`, the repository as the working folder and root, a planted `HOME`, no model reachable). Nothing is edited
  between that run and the guard's calls: the roster and the tickets the guard reads are the ones A0 committed.
- **The guard's decision** is the kernel hook's, through the generated settings, as W2-110's suite puts a call through
  it (`w2_110_support.call`: every PreToolUse line registered for Bash, through `sh -c`, `GOV_ROLE` and `GOV_TICKET` as
  the session declares them, the stand-in home of W1-38 whose `gov` names this worktree's `src`). Two fixtures check
  that the product's hook is this worktree's template hook and that the hook's interpreter imports this worktree's
  `gov` (as W2-110's conftest does).
- **Reused by import, not copied:** `w2_110_support` (the product, sessions, `call`, `says_how_to_set_the_key`) and
  `w2_23_support` (the `gov adopt` child process, git, the envelope).
- **The decision** is W1-05's and W1-04's form: `deny`, `ask`, `allow` (no decision), `error`.

### The fixtures

Every planted repository holds these tickets before adoption (all `in_progress`, W1-04's ticket form, committed):

| Ticket | WBS id | Role | Used as |
|---|---|---|---|
| `DAEO-1ead` | `P-01` | orchestrator | the orchestrator on another ticket (failure 2); the ticket a roster already names (I2 (i)) |
| `DAEO-eng1` | `P-02` | engineer | the engineer's and the test designer's own ticket |
| `DAEO-aud1` | `P-04` | independent-auditor | the auditor's own ticket |

The coordination ticket is not among them: A0 creates it. The roster is planted only where a case says so; the
template ships none.

| Adoption | Planted roster (committed, before A0) | Other change | Used by |
|---|---|---|---|
| `standard` | none | none | I1, failure 1, failure 2 |
| `names-by-id` | `coordination_ticket: DAEO-1ead` at the top, then a `roles:` block | none | I2 (i) |
| `names-by-wbs` | `coordination_ticket: P-01` | none | I2 (i) |
| `other-content` | comments, a `roles:` block, `budget_per_ticket: 12`; no key | none | I2 (ii) |
| `no-tk` | none | `governance/kernel/bin/tk` removed (committed) | I2 (iii): A0 completes, creates no ticket and no key, says so in its record; the guard stays closed (run 3: was "A0 refuses") |

Success 2 uses W2-110's configurations of the same generator (`no-key`, `no-roster`, `as-generated`,
`names-no-ticket-by-id`, `names-no-ticket-by-wbs`), each with the sessions "the orchestrator on `DAEO-c0rd`" and "an
engineer on `DAEO-eng1`". Adoption is not needed there.

Installs: `pip3 install requests` and `npm i left-pad` (one per class of the install rule; W2-110 covers the rest).

## KPI lines, cases and red reasons

| KPI id | tests | expected red reason |
|---|---|---|
| success-1 | `test_w2_113_adopted.py::test_a0_succeeds_on_a_planted_repository`, `test_w2_113_adopted.py::test_a0_creates_exactly_one_ticket_and_the_roster_names_it`, `test_w2_113_adopted.py::test_the_new_ticket_is_the_coordination_ticket_of_the_project`, `test_w2_113_adopted.py::test_a0_s_record_names_the_ticket_and_the_roster`, `test_w2_113_adopted.py::test_the_ticket_and_the_roster_are_in_a0_s_commit_and_the_tree_is_clean`, `test_w2_113_adopted.py::test_the_orchestrator_on_the_new_ticket_is_asked_for_an_install`, `test_w2_113_others_refused.py::test_a_worker_on_its_own_ticket_is_refused`, `test_w2_113_others_refused.py::test_an_orchestrator_on_another_ticket_is_refused`, `test_w2_113_others_refused.py::test_an_orchestrator_on_another_ticket_is_refused_for_every_install`, `test_w2_113_others_refused.py::test_an_orchestrator_with_no_ticket_is_refused`, `test_w2_113_others_refused.py::test_a_worker_on_the_coordination_ticket_is_refused`, `test_w2_113_others_refused.py::test_an_orchestrator_subagent_in_a_worker_s_session_is_refused`, `test_w2_113_defaults.py::test_a_roster_that_names_an_existing_ticket_is_kept_and_no_ticket_is_created`, `test_w2_113_defaults.py::test_the_ticket_a_roster_names_stays_the_ctos`, `test_w2_113_defaults.py::test_a_roster_without_the_key_gets_the_key_of_a_new_ticket`, `test_w2_113_defaults.py::test_a_roster_without_the_key_changes_nothing_else`, `test_w2_113_defaults.py::test_a_roster_without_the_key_keeps_its_text_and_its_comments`, `test_w2_113_defaults.py::test_a0_completes_without_a_ticket_or_a_key_and_its_record_says_so_when_tk_is_missing`, `test_w2_113_defaults.py::test_the_guard_stays_closed_when_tk_is_missing` | R1: A0 creates no ticket and writes no roster (the key is absent), and with `tk` missing its record does not say that no ticket was created because `tk` is missing (the first `tk` case: A0 completes, creates nothing and adds no key on the base already, as (b) asks; only the record's words are red). R2: with `tk` missing the second `tk` case is red on the base too: every install is refused (no key), but no refusal names `GOV_TICKET`. Green on the base, by design: the precondition (A0 runs), the refusals of workers on their own tickets and of an orchestrator on another ticket or none (no key, so every session is refused), and I2 (i) (A0 creates and changes nothing today) |
| success-2 | `test_w2_113_refusal_words.py::test_the_install_stays_refused_when_the_rule_cannot_run`, `test_w2_113_refusal_words.py::test_the_refusal_names_gov_ticket`, `test_w2_113_refusal_words.py::test_the_refusal_says_how_to_set_the_key`, `test_w2_113_refusal_words.py::test_the_refusal_does_not_claim_a_key_was_set`, `test_w2_113_predicates.py::test_the_old_words_claim_a_key_was_set_and_do_not_name_the_variable`, `test_w2_113_predicates.py::test_a_true_text_passes_every_predicate`, `test_w2_113_predicates.py::test_a_text_that_speaks_of_the_value_of_a_key_that_is_not_there_is_caught`, `test_w2_113_predicates.py::test_other_false_claims_are_caught` | R2: the refusal does not name `GOV_TICKET` (10 cases); R3: it says "(set at adoption)" as a fact (10 cases). Green on the base: the refusal's decision (stays closed, 10) and "says how to set the key" (10: W2-110 made it name the file and the key), and the 4 predicate checks of the suite's own helper |
| failure-1 | `test_w2_113_adopted.py::test_the_orchestrator_on_the_new_ticket_is_asked_for_an_install`, `test_w2_113_adopted.py::test_a0_creates_exactly_one_ticket_and_the_roster_names_it` | R1: A0 creates no ticket, so there is no key and no ticket for the CTO's session to stand on: no coordination ticket is named at adoption |
| failure-2 | `test_w2_113_others_refused.py::test_a_worker_on_its_own_ticket_is_refused`, `test_w2_113_others_refused.py::test_an_orchestrator_on_another_ticket_is_refused`, `test_w2_113_others_refused.py::test_an_orchestrator_on_another_ticket_is_refused_for_every_install`, `test_w2_113_others_refused.py::test_an_orchestrator_with_no_ticket_is_refused`, `test_w2_113_others_refused.py::test_a_worker_on_the_coordination_ticket_is_refused`, `test_w2_113_others_refused.py::test_an_orchestrator_subagent_in_a_worker_s_session_is_refused` | R1 for the 4 cases that put a session on the new coordination ticket (A0 creates none). **The other 10 are green on the base**: with no key the guard refuses every session already. They are required all the same: they turn red for an implementation that, once the key is written, asks more than the CTO |

What each module holds (case counts):

| Module | Cases | KPI lines |
|---|---|---|
| `test_w2_113_adopted.py` | 7: A0 succeeds (1); the roster's key names exactly one new ticket (1); the ticket's class and title (1); the record (1); the commit and the clean tree (1); the orchestrator on the new ticket is asked, 2 installs (2) | success 1, failure 1 |
| `test_w2_113_others_refused.py` | 14: a worker (engineer, test designer, auditor) on its own ticket × 2 installs (6); an orchestrator on `DAEO-1ead` by id and by WBS id (1); that orchestrator × 2 installs (2); an orchestrator with no ticket (1); the three workers on the coordination ticket (3); an orchestrator subagent in an engineer's session on it (1) | failure 2, success 1 |
| `test_w2_113_defaults.py` | 9: I2 (i) kept and nothing created × (id, WBS id) (2) and still the CTO's (2); I2 (ii) the key added (1), nothing else changed (1), the text and comments kept (1); I2 (iii) A0 completes without a ticket or a key and its record says so (1), the guard stays closed: 4 sessions × 2 installs in one case (1) | success 1 (I2), and success 2's words for the `tk` case |
| `test_w2_113_refusal_words.py` | 40: 5 planted products × 2 sessions × 4 properties (decision, `GOV_TICKET`, how to set it, no false claim) | success 2 |
| `test_w2_113_predicates.py` | 4: the predicates on sample texts (the old words, a true text, a lying text, edge phrases) | success 2 (the helper) |

## Readings stated, not asked

Each is this suite's reading where I1-I3 do not say; none is a guess at an interface.

1. **"`<project>`" is the repository's folder name (`harbour`).** The template asks no project name (copier has no
   question for it, and no file of `template/governance/project/` holds one), so the only name a product has is its
   folder. The title is read from the ticket as the frontmatter's `title` if it has one, else the first `# ` heading
   (where the vendored `tk create` writes it), and must equal `harbour coordination` exactly (case, spacing and word
   order). **If the implementer reads the name from somewhere else, this case is the one to revisit** (see the return's
   `discoveries`).
2. **`class: coordination` is the ticket's frontmatter key `class`**, equal to the string `coordination`.
3. **"Records both in A0's record" is the record's text** (`governance/adoption/A0-safety-baseline.md`) holding the
   new ticket's id and the roster's path `governance/project/roster.yaml`, anywhere. The record's own keys are not
   named in I1, so none is pinned (a `set_up` list that names both files satisfies it).
4. **"A0's commit" is HEAD after A0**: one commit on the planted head, which holds the ticket file, the roster and the
   record; and the tree is clean. The roster and the ticket are compared with HEAD byte for byte.
5. **Exactly one ticket is created** (the new files in `.tickets/` after A0 number one), and the roster's key is its
   id (not its WBS id; `tk create` gives none).
6. **I2 (i) "names an existing ticket" is read as the guard reads it**: by id or by WBS id (`names-by-id`,
   `names-by-wbs`). "Keeps it" is the roster parsed equal to what was planted and the `.tickets/` file set unchanged. The
   roster's bytes are not required unchanged (A0 may rewrite it with the same content).
7. **I2 (ii) "changes nothing else" has two readings, two cases.** `test_a_roster_without_the_key_changes_nothing_else`
   compares the parsed content less the key: every other key and value, nothing added, nothing dropped. The stricter
   `test_a_roster_without_the_key_keeps_its_text_and_its_comments` requires every non-blank line of the original text,
   comments included, to still be there in order, and the key's line to be the only line added. An implementation that
   re-serialises the roster (a YAML dump) passes the first and fails the second. If the owner reads "nothing else" as
   parsed content only, the second case is the one to drop.
8. **I2 (iii), run 3 (PKG-3 (b), DEC-1157 (15)): "completes without creating the ticket or the key, and its record says
   so; the guard stays closed".** Two cases.
   - *Completes without the ticket or the key, and says so:* A0 ends as W2-23's success does (`succeeded`: exit 0, an
     `ok: true` envelope, no traceback); no ticket file is added to `.tickets/`; the roster's bytes are as planted
     (absent stays absent: "no key" is read as "A0 does not write the roster", the planted repository has none); A0's
     record exists at `governance/adoption/A0-safety-baseline.md` and says so (the predicate below). I2 fixes no field
     name, so no key of the record is pinned.
   - *The guard stays closed:* in that repository, through the kernel hook (`w110.call`), four sessions each attempt both
     installs (`pip3 install requests`, `npm i left-pad`): the orchestrator on an existing ticket (`DAEO-1ead`), the
     orchestrator on a would-be coordination ticket (`DAEO-c0rd`, not in the repository), an orchestrator with no ticket,
     and an engineer on its own ticket. Every one is refused (`deny`: never asked, never let through), and every refusal
     names `GOV_TICKET` and says how to set the key (W2-110's predicate: it names the roster file and the key). The tree is
     clean after A0. The case needs A0 to have succeeded (the precondition `succeeded`): a refusing A0 fails the other
     case with its own message. It reuses success 2's `names_the_variable` and `says_how_to_set_the_key`; the third
     success-2 predicate (no false claim of a set key) is not applied here, I2 (iii) does not name it.

### The record says so

`w2_113_support.says_no_ticket_was_created_because_tk_is_missing(record_text)`, one narrow predicate on A0's record
text, not on a field name. The text, with whitespace collapsed (so a YAML-folded line counts as one), must hold:

1. the word `tk` (not inside a longer word; a path `.../bin/tk` counts as naming it), and
2. within 160 characters of that occurrence, both (a) a word saying a thing was not made: `no`, `not`, `none`, `null`,
   `never`, `without`, `skipped`/`skip`, `nothing`, or `n't`; and (b) the substring `ticket` (so `coordination_ticket`
   counts).

True records pass in any of these shapes: "No coordination ticket was created because tk is missing", `coordination_ticket:
none` with a reason "tk is missing", "the vendored tk was not found, so the ticket and the key were not created", "Skipped:
tk not found, ticket creation skipped". These fail: a record silent about `tk` (the base's), a record that names `tk` and
says nothing negative about a ticket ("The vendored tk is missing."), a record that says no ticket was made but never names
`tk`, a record that says a ticket "was created with tk", a record that lists only the path `governance/kernel/bin/tk`.
Not caught on purpose: a record that names `tk` and a negation that do not relate (it would take a stand-in written to
cheat). Shown on stand-in records in a temporary folder (9 samples, all as stated; scratch, not committed).
9. **"Asked" and "refused" are the hook lines' decisions** (`ask`; `deny`), as W2-110 reads them. No generated settings
   rule may refuse the CTO's call first.
10. **The second orchestrator** is the orchestrator on `DAEO-1ead`, by id and by WBS id, plus one with no ticket. The
    workers are also put on the new coordination ticket: only an orchestrator session on it is the CTO's (W2-110's rule).

### Success 2: the words

Three predicates, in `w2_113_support`:

- **Names `GOV_TICKET`**: the refusal text holds the string `GOV_TICKET`.
- **Says how to set the key**: W2-110's `says_how_to_set_the_key`: the text names `governance/project/roster.yaml` and
  `coordination_ticket`.
- **Claims a key was set** (`claims_a_key_was_set(reason, key_exists)`), a list of the matched phrases, empty for a
  text that makes none. Narrow on purpose. In every case it matches:
  - "set at adoption" as a fact, i.e. not preceded by "to be", "should be", "must be", "will be", "can be" or "shall
    be";
  - "was / were / has been / have been / is / are" + "set / written / added / created" + "at / by / during / in" +
    "[the] [last | earlier] adoption";
  - "already set" or "already written" (not after "not" or "never").

  Where no key exists at all (no roster, or a roster without the key; cases a and b), it also matches "the key names /
  holds / is set / has the value / points ..." (with or without the key's name after "the key"): such a text speaks of
  a key's value that is not there. Where a key exists and names no ticket (case c), "the key names no ticket" is true
  and passes.

  What passes (held in `test_w2_113_predicates.py`): "the key is not set", "no key has been set", "no key was
  written", "adoption writes the key", "set it by hand", "the key should be set at adoption", "it must be set at
  adoption", "the key is not already set". What fails: the base's own "(set at adoption)", "the key was set at the last
  adoption", "the key has been set by adoption", "the key is already set", "the key was written by adoption".

The base's refusal puts "(set at adoption)" after its instruction, and the review's F5 complains of exactly that, so
the narrow predicate holds the old text red. A true text (one that names `GOV_TICKET`, says where and how to set the
key, and says adoption "writes" it) passes.

## Green on the base (39 cases), each by design

- `test_a0_succeeds_on_a_planted_repository`: A0 runs on the planted repository today.
- **failure 2, 10 cases:** the refusals of a worker on its own ticket (6), of the orchestrator on `DAEO-1ead` (3) and of
  the orchestrator with no ticket (1). With no key written the guard refuses every session, so they hold vacuously on
  the base. They guard the other half of the ticket: an implementation that writes the key and then asks too many.
- **I2 (i), 4 cases:** A0 on a roster that names an existing ticket creates nothing and changes nothing today, so the
  case holds; it turns red for an A0 that creates a ticket regardless.
- **success 2, 20 cases:** the decision stays `deny` (10) and the refusal still names the file and the key (10).
- **The 4 predicate checks**, on the suite's own helper.

## Checked against stand-ins (scratch, not committed; stand-ins live in a temporary tree, never in the ticket's paths)

- **A0 stand-in that does what I1/I2 say** (a script that runs the real `gov` with A0 wrapped: it creates the ticket
  through `gov.tasks.tickets.create`, adds `class: coordination`, writes the roster's key, puts both in the commit and
  the record, keeps a roster that names a ticket, refuses without `tk`): the three A0 modules, **30 passed**. (Run 2; its
  "refuses without `tk`" and the flaw "`tk` missing but the record committed (the writes-nothing case)" below are the
  old I2 (iii) and no longer apply: run 3's two `tk` cases are checked on the base, red for the reasons above, and the
  record predicate on stand-in records, as stated under "The record says so".)
- **The same stand-in with one flaw at a time, each caught by the case meant for it:** no `class` and a wrong title (the
  class/title case); no key written (7 cases); a key naming a missing ticket (4); the ticket left uncommitted (the
  commit and clean-tree case); the record not naming the files (the record case); the roster re-serialised (the
  comments case only); an existing key ignored and a new ticket created (4); `tk` missing but the record committed
  (the writes-nothing case).
- **Refusal-text stand-ins** (the hook's real decision, its text replaced): a true text, **40 passed**; no `GOV_TICKET`:
  10 failed (the names case); "set at adoption" as a fact: 10 failed (the claims case); "the key names the coordination
  ticket" added: 6 failed (cases a and b, not c); no file or key: 10 failed (the how-to case); an `ask` instead of a
  refusal: all 40 failed.

## Not tested

- **The role-file lines** (the `moved:` line): W2-33's.
- **The quiet-hours hook** (the `lifted:` line, DEC-1083).
- **A path case** ("the branch changes only the ticket's `allowed_paths`", DEC-1155): not written; no KPI line asks
  for it.
- **A0 without the template** (no `.gitleaks.toml`, no `.gitignore` line): W2-23's.
- **Stages A1 to A8** with the new A0 output ("Note for W2-88 and W2-174: keep it at merge"): those suites run A0
  through W1-41's and W2-23's own planted projects, which stay green or red by themselves; nothing here re-tests them.
- **W2-110's KPIs** (the install rule itself): W2-110's suite.
