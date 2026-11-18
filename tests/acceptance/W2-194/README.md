# W2-194 acceptance tests: absent reds against the base, a short --base, accepted reds when scoped (DAEO-kq8b)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines and verify lines, the lead's
interface (the brief of 2026-11-17) and EXAMIN's exa-g6db close (F-030, F-031), never from the implementation. The
base is `2b365738c`.

## How the suite runs

- **Public interfaces only:** `gov close <ticket> --json [--base <rev>]` in planted projects, as in
  `tests/acceptance/W2-193/README.md` ("How the suite runs"); the planted projects and telling tests are W2-193's
  (`w2_193_support.py`, imported from that folder by name; nothing of this folder shares a module name with another).
- The absent red is W2-193's: a test in `tests/acceptance/W2-bb/whole/` that exists only when its folder is collected
  whole, so its alone runs are `absent` with the change and at the base.
- `accepted_reds` are planted as the strict close's cases plant them (DEC-757, `src/gov/close/ratchet.py`'s
  docstring): the path map names the register (`decision_register: docs/DECISION_REGISTER.md`); the register's entry
  has its own status line and names the test's function and file; the entry is added after the initial commit by one
  commit whose final trailer block is `Task: setup` with `Role: owner` (or `Role: orchestrator` for the entry that
  must not count). The plants were checked with the ratchet's own reader on today's code: the owner's entry counts,
  the other two are refused (`ACCEPTED_RED_REFUSED`).
- `--base` is given in every case (the initial commit, a full id unless the case is about the short hash), so no case
  depends on W2-193's default base.
- One close per case; deterministic, no network, no model. Under a minute for this folder under `-n 6`.

## Interface (as used; the lead's naming where the KPI lines leave it open)

- Refusal codes `RED_CAUSED`, `BASE_UNKNOWN`, `BASE_AMBIGUOUS`; each `--base` refusal names what was given.
- Record keys: `base` (full commit id); `accepted_reds` (list of `{test, decision, reason, fixed_by, result}`);
  `accepted_red_findings` (list of `{code, test, message}`); each `reds` entry gains `accepted` (the decision id or
  null). An accepted red: `caused: false`, `accepted: <DEC-id>`, `repair_ticket: null`.

Readings this suite takes (named to the lead):

1. An ambiguous prefix is planted as two commit objects sharing their first 9 digits, found by a birthday search and
   written with `git hash-object`, each on a branch of its own (`ambiguous-1`, `ambiguous-2`), not on HEAD's line:
   `git rev-parse --verify <prefix>^{commit}` calls it ambiguous.
2. An entry "named in the record" when it does not count: an item of `accepted_red_findings` whose `test` is the
   entry's and which has a `code`. Planted as a decision whose status is `PROPOSED`, for a red that is a plain base
   red, so the close passes and writes its record.

## KPI map

| KPI | Test | Red on the base |
|---|---|---|
| success-1 (S1: an absent red red at the base run with the same failure type is a base red) | `test_w2_194_absent.py::test_an_absent_red_red_at_the_base_run_is_not_the_change_s` | no base run: the absent red never matches and is the change's: `RED_CAUSED` ("the close did not pass") |
| success-2 (S2: a short hash closes as the full hash; unknown `BASE_UNKNOWN`, ambiguous `BASE_AMBIGUOUS`, each naming what was given) | `test_w2_194_base.py::test_a_short_hash_closes_as_the_full_hash_and_the_record_names_the_full_id`, `test_w2_194_base.py::test_an_unknown_prefix_is_refused_base_unknown_naming_it`, `test_w2_194_base.py::test_an_ambiguous_prefix_is_refused_base_ambiguous_naming_it` | only a full 40-digit id is taken: the 9-digit hash and the ambiguous prefix are refused `BASE_UNKNOWN` ("the close did not pass"; "the refusal does not name BASE_AMBIGUOUS"). The unknown prefix's case is **green by design**: today's close already refuses it `BASE_UNKNOWN` naming it; it guards that the short-hash route keeps doing so |
| success-3 (S3: a counted `accepted_reds` entry for a red red at the base: accepted, named in `accepted_reds`, no repair ticket; an entry that does not count covers nothing and is named in the record) | `test_w2_194_accepted.py::test_a_listed_red_red_at_the_base_is_accepted_with_its_decision_and_no_repair_ticket`, `test_w2_194_accepted.py::test_the_same_entry_added_without_role_owner_covers_nothing`, `test_w2_194_accepted.py::test_an_entry_whose_decision_is_not_accepted_is_named_in_the_record_and_covers_nothing` | the scoped close reads no `accepted_reds`: the listed red (another failure type at the base) refuses `RED_CAUSED` ("the close did not pass"); the record has no `accepted_red_findings` ("the record has no accepted_red_findings list"). The non-owner entry's case is **green by design** (today it refuses `RED_CAUSED` because no list is read; after the change, because the entry does not count) |
| failure-1 (F1: a red new with the change accepted; an absent red green or not collected at the base run accepted) | `test_w2_194_accepted.py::test_a_listed_red_green_at_the_base_refuses`, `test_w2_194_absent.py::test_an_absent_red_green_at_the_base_run_refuses`, `test_w2_194_absent.py::test_an_absent_red_with_another_failure_type_at_the_base_run_refuses`, `test_w2_194_absent.py::test_an_absent_red_not_collected_at_the_base_run_refuses`, `test_w2_194_accepted.py::test_the_same_entry_added_without_role_owner_covers_nothing` | the two absent reds that were at the base refuse `RED_CAUSED` today too, but never run at the base ("the absent red did not run at the base ...: []"). **Green by design:** the listed red green at the base, the absent red the base lacks and the non-owner entry (today's close refuses each `RED_CAUSED`; they guard the new routes against excusing them) |
