# W1-34 — Decision-package template: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-egm9` (W1-34), the Contract
v4.1 items its KPI lines name (CAP-34.a, CAP-34.b, CAP-34.c, CAP-34.d), Charter v5 §MR-6, and DEC-065, DEC-093,
DEC-220, DEC-221, DEC-308 and DEC-328. Profile LITE: one test per KPI line, no parametrised cases. No earlier
ticket's test was rewritten, and no test of this suite was changed or removed.

- **Batch 1:** seven tests, written before implementation.
- **Batch 2:** one test, added after implementation, reason "delegated decision". DEC-328 decides DP-1, and the
  test pins what it decides. Success 4 now has two tests: the first as far as DP-1 left it, the second for DEC-328.

No decision package is open: DP-1 is decided by DEC-328 (below).

## Run

```sh
python3 -m pytest tests/acceptance/W1-34 -q -p no:cacheprovider
```

Standard library, `pytest` and PyYAML. No network, nothing installed, nothing written. Well under a second.

The tests read only what the template publishes: the files named `decision-package*` and `decision-record*` under
`template/governance/kernel/templates/`. Those two patterns are the implementer's `allowed_paths`; every test can be
satisfied by them alone, with no change to a schema or to Python code.

## KPI lines, tests and red reasons

All in `test_w1_34_decision_package.py`. Run on `w1/W1-34` at `168397f6`: **7 failed**.

| KPI line | Covers | Test | Red today because |
|---|---|---|---|
| Success 1: the ten fields plus rank P1-P3 | CAP-34.b | `test_the_template_has_the_ten_fields_and_a_rank` | `decision-package.md: no heading for ['current state', 'exact permitted next actions']`; the frontmatter also has no `rank` |
| Success 2: at most five open packages, P1 may bypass (DEC-093) | CAP-34.c | `test_batching_allows_at_most_five_open_packages_and_p1_may_bypass` | `the template states no cap of five packages at a time` |
| Success 3: an answer maps to a decision record appended with ACCEPTED (owner, date) | (none) | `test_an_answer_maps_to_a_decision_record_with_accepted_and_who` | `the Answer section names no decision record (an ADR-… or DEC-… id) for the answer`; the section is empty |
| Success 4: the gate record carries a state and its CIT | CAP-34.d | `test_the_gate_record_carries_a_state_and_its_cit` | `the frontmatter has no constrains list for the tickets that wait on the package`; also no state but `PROPOSED` is named and no key holds a CIT |
| Success 5: the routing rule classes a contradiction | CAP-34.a | `test_the_routing_rule_classes_a_contradiction` | `the template has no routing rule: it never says agent-resolvable` |
| Failure 1: a package can be rendered without a recommendation or confidence | (none) | `test_a_package_cannot_be_rendered_without_a_recommendation_or_confidence` | `the recommendation section is blank, so a package renders without one` |
| Failure 2: an answer can be recorded without a date | (none) | `test_an_answer_cannot_be_recorded_without_a_date` | ``Answer section: no `ACCEPTED (who, date)` form, so nothing asks for the date of an answer`` |

The suite was also run against a throwaway reference template outside the tracked tree: 7 passed.

### Batch 2 (added after implementation, reason "delegated decision")

Run on `w1/W1-34` at `e4f04019`, with the template as implemented: **7 passed, 1 failed**.

| KPI line | Covers | Test | Red today because |
|---|---|---|---|
| Success 4: the gate record carries a state and its CIT, as DEC-328 decides it | CAP-34.d | `test_the_gate_state_lives_in_status_alone_and_the_cit_key_is_cit` | ``the template does not state which gate state each `status` value stands for; no paragraph puts these side by side: ['ACCEPTED with answered', 'DECLINED with declined', 'REVOKED with revoked', 'STALE with stale']``; the template says only that open is `status: PROPOSED` |

The frontmatter half of the test already holds on the template as implemented: no second state key, and the CIT
key is `cit`. The pairing was checked on sample wordings held in memory, with nothing written: a sentence, the
reverse order and a table pass; swapped pairs, two separate lists and the values alone fail.

## What each test asks of the template

- **The form.** Exactly one `decision-package*` file has the frontmatter `type: decision-package`; a package is
  written from it. The ten fields, the rank, `status`, `constrains` and the Answer section are read from that file.
  The batching rule, the routing rule and the gate states may stand in the form or in another `decision-package*`
  file beside it.
- **Success 1.** A markdown heading for each of the ten fields: question, why now, current state, options, impact,
  reversibility, cost, recommendation, confidence, permitted next actions (any letter case; the heading may say
  more, as in "Cost of rework" or "Exact permitted next actions"). The frontmatter has `rank`, set to `P1`, `P2` or
  `P3`, and the file names all three.
- **Success 2.** A paragraph says "at most five" (or "no more than", "maximum of", "up to"; "five" or "5") and
  "open"; a paragraph names `P1` and says "bypass".
- **Success 3.** The form has an Answer section. It names the decision record of the answer by an id of the decision
  grammar (`ADR-0000`, `DEC-000`), and shows the form `ACCEPTED (who, …)`. The decision-record template shows the
  same form.
- **Success 4.** The form keeps `status: PROPOSED` and a `constrains` list (DEC-308). The template names the five
  states open, answered, declined, revoked and stale. The frontmatter of a `decision-package*` file of type `gate`
  or `decision-package` has a key for the CIT: a key with the word `cit` in it (`cit`, `cit_id`, …).
- **Success 4, as DEC-328 decides it (batch 2).** Three things.
  - The mapping. For each of the five pairs (`PROPOSED` open, `ACCEPTED` answered, `DECLINED` declined, `REVOKED`
    revoked, `STALE` stale), some paragraph of a `decision-package*` file puts the value and its state word side
    by side, with no other value or state word between them. The value is in upper case; the state word is in
    lower case or capitalised. The wording is the implementer's. One line is enough: "`PROPOSED` is open,
    `ACCEPTED` is answered, `DECLINED` is declined, `REVOKED` is revoked and `STALE` is stale." A table with one
    row per pair also passes. Two separate lists ("PROPOSED, ACCEPTED, … are open, answered, …") do not.
  - `status` alone. In the frontmatter of every `decision-package*` file of type `gate` or `decision-package`,
    `status` is one of the five values, and no other key holds a state: no key with the word `state` or `status`
    in its name, and no key whose value is one of the five state words or the five values. `state_class` is the
    shared record frontmatter of W1-08 and is not counted.
  - The CIT key. The form has a non-empty `cit`, and no such frontmatter has another key with the word `cit` in
    it (`cit_id`, `gate_cit`, …).
- **Success 5.** One paragraph says "agent-resolvable" with "precedence" and "record…"; one says "human-resolvable"
  with "package"; one of them says "contradiction".
- **Failure 1.** The Recommendation and Confidence sections are not blank and each says it is required ("required",
  "must", "mandatory" or "never empty/blank/omitted"). The Confidence section names low, medium and high.
- **Failure 2.** Every `ACCEPTED (…)` form in the Answer section and in the decision-record template has a date
  slot (`YYYY-MM-DD` or a date in that form); each has at least one. A paragraph of the Answer section says the
  date is required.

## Readings

1. **Template only.** The implementer may touch templates and nothing else, so "can be rendered without" and "can
   be recorded without" are read as what the template lets through: a blank or optional slot fails, a slot marked
   required passes. No test renders a package or writes an answer; W1-35 (the skills) and W1-11 (the checker) own
   that behaviour.
2. **The ten fields** are the ten the ticket's first success line lists; CAP-34's acceptance text and Charter v5
   give the same ten (MR-6's eight plus current state and exact permitted next actions). The archived originals
   were not read. "Cost of rework" is matched by a heading with the word "cost", since the Charter says "cost".
3. **Rank is a frontmatter key named `rank`.** W1-35 batches by rank, so it is read from the frontmatter and not
   from prose. The key name is this suite's reading; the sources name no key.
4. **Confidence is low, medium or high.** DEC-220 delegates a package when "confidence is medium or higher", which
   fixes the scale.
5. **`ACCEPTED (owner, date)`** is the form the decision register uses (`ACCEPTED (owner, 2026-10-04)`). The first
   place in the brackets is who decided, and it is not pinned to the word "owner": DEC-220 records delegated
   answers as `ACCEPTED (orchestrator, …)`. Where the form stands in the decision-record template (frontmatter,
   body or a comment) is the implementer's.
6. **Success 4 has two tests.** The batch 1 test goes only as far as DP-1 left it: `status` and `constrains` as
   DEC-308 fixes them, the five state words named, and a key for the CIT. It does not say which key holds the
   state or how the five words are spelled as values. The batch 2 test pins both, from DEC-328.
7. **The W1-08 suite stays green.** It validates every templates file with "package", "gate" or "decision" in its
   name. Nothing here asks for a file or a key its schemas refuse: record frontmatter accepts extra keys, `status`
   is any non-empty string, and a new `decision-package*` or `decision-record*` file needs the shared frontmatter.
   Run before and after this suite was written: 209 passed.
8. **The mapping is read as a pairing, not a sentence** (batch 2). DEC-328 says the template states the mapping
   and leaves the wording free. The values are matched in upper case, as DEC-328 and DEC-308 write them, so the
   value `STALE` and the state word "stale" are told apart by case.
9. **A second state key is read from the frontmatter only** (batch 2). The template's prose may speak of a
   "state"; what DEC-328 rules out is a second key. Batch 2 asks for nothing outside the two template patterns
   and no key a schema refuses. The W1-08 and W1-09 suites were run with batch 2 in place: 286 passed.

## Decision package (decided)

### DP-1 — How the gate state sits beside `status`

- **Decided:** DEC-328, ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04): option (a). The state lives
  in `status` alone, and the CIT key is `cit`. The package is closed; the text below is kept as it was raised.
  The batch 2 test is the assertion its last field promised.
- **Rank:** P2.
- **Question:** Where does a gate record hold its state (open, answered, declined, revoked, stale): in `status`
  alone, or in a second key beside `status`?
- **Why now:** Success 4 asks for the state. DEC-308 already fixes that a package is open while its status is
  `PROPOSED`, and W1-11's checker (which depends on W1-34) will read the state to refuse a declined, revoked or
  stale gate. The template is where the two meet.
- **Current state:** The template has `status: PROPOSED` and nothing else. The schema lets `status` be any
  non-empty string and accepts extra keys; W1-34 cannot change it. `gov.tasks` blocks a ticket only while a
  package's status is `PROPOSED`. The W1-09 suite treats `ACCEPTED` as answered. No in-tree source says how the
  five words map to `status` or names a second key. The same holds for the name of the CIT key.
- **Options:**
  - (a) `status` alone carries the state: `PROPOSED` (open), `ACCEPTED` (answered), `DECLINED`, `REVOKED`, `STALE`.
    The template states the mapping. The CIT key is `cit`.
  - (b) A second key (for example `gate_state`) holds the five lower-case words, beside `status`.
  - (c) `status` takes the five lower-case words themselves.
- **Impact:** (a) one field, so the READY rule and W1-11 read the same value, and it matches DEC-308 and the W1-09
  suite as built. (b) two fields that can disagree (`PROPOSED` with `answered`), and no ticket owns the check that
  they agree. (c) contradicts DEC-308 and turns the W1-09 decision tests red.
- **Reversibility:** High until W1-11 reads the state; after that a change touches W1-11's checker and its tests.
- **Cost of rework:** One line of the template and one assertion here now; a W1-11 rewrite later.
- **Recommendation:** (a).
- **Confidence:** Medium.
- **Exact permitted next actions:** The implementer may build the template now: the Success 4 test passes under (a)
  or (b). On the answer, the test designer adds the assertion that pins the state values (and the CIT key name) as
  a later batch. W1-11's test design waits for the answer.
