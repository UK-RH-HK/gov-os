# The form of a spec

The reference for the spec-writing skill's [SKILL.md](SKILL.md). It states what `check_spec.py` reads; the check
refuses what this form forbids and nothing more. This file links to no further reference file.

## The nine headings

A spec has these `##` headings, in this order. A heading is matched exactly and without regard to case, so
`## Non-goals` never counts as `## Goals`. A heading with nothing under it counts as missing.

1. Problem: what is wrong or missing, for whom, in a short paragraph.
2. Users and scenarios: who uses it, and the situations they meet, each as a short story.
3. Goals: what the change makes true.
4. Non-goals: what it does not try to do, though a reader might expect it.
5. KPIs: the outcomes, each with its failure line (below).
6. Test data: the data the tests need, and who secures it (below).
7. Out of scope: what is left to other work, each with where it goes.
8. Open questions: each as a package (below).
9. Accepted by: who accepts the spec, by role or name, and on what evidence.

## KPIs

Each KPI is a line `- K<n>: <behaviour>` followed by an indented line `  Fails if: <observable failure>`:

```
- K1: A visitor who gives a valid email address receives a welcome message within one minute.
  Fails if: no message arrives within five minutes, or it arrives twice.
```

The behaviour is something an observer sees or measures, from outside. It is testable without naming code.
A KPI with no `Fails if:` line is refused; a KPI whose behaviour line names code is refused. Both name the KPI's id.

### What "names code" means

The behaviour line names code when it holds any one of:

- a code span: text between backticks;
- `name(`: an identifier directly followed by an opening parenthesis, with no space;
- a path with an extension, such as `src/app/signup.py` or `config.yaml`;
- a dotted identifier, such as `account.create` or `Signup.confirm`;
- a snake_case identifier: a word holding an underscore, such as `send_welcome`.

Ordinary prose names none of these: hyphenated words (sign-up, forty-eight), a parenthesis after a space
(options (with cost)), a full stop followed by a space, numbers such as 1.5, and abbreviations such as e.g. and i.e.
A KPI that needs such a word is reworded as the behaviour an observer sees.

## Test data

A table under `## Test data`, one row per source, with these header words in this order:

`source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured`

- `source`: where the data comes from, or what it is.
- `kind`: `imported` (taken from outside) or `synthetic` (built).
- `owner`: who secures it.
- `licence or recipe`: a licence for an imported row; a recipe (how it is built, with its seed) for a synthetic one.
- `privacy`: what personal data it holds, or `none`.
- `secrets`: whether it holds secrets, and how they are kept out.
- `hidden half`: `yes` where the data measures and a half is held apart, `no` where it measures and none is, `n/a`
  where it does not measure. An empty cell is refused.
- `secured`: `yes`, or `no` where it cannot be secured.

A row with `secured: no` is never passed and never skipped: the check prints `P1 Test data: <source> cannot be
secured`, writes `<spec stem>.P1.md` beside the spec (the source, why as far as the row states, options with their
cost, a recommendation), and exits 2. The lead takes that package up as a P1.

## Open questions

Each question is a package, so the decider has what they need:

```
- Question: <the question>
  - Options: <option A> (cost: <cost>); <option B> (cost: <cost>)
  - Recommendation: <one option, and why>
```

## What the check prints

- `REFUSED <part>: <reason>`: one line per failed item, `<part>` being one of the nine heading names; exit 1. A
  missing part is named once and draws no further refusal about its contents.
- `P1 Test data: <source> cannot be secured`: exit 2 when nothing was refused.
- `PASS`, alone on its line, only when no line above was printed; exit 0.
- A usage error prints one usage line on stderr and exits 64.

## Imports

Text copied from another source is adopted only with its licence checked and recorded (DEC-959 item 5, DEC-1084).
The record is `imports.yaml` in the skill folder: a mapping with an `imports:` list (`imports: []` when nothing is
imported), each entry holding `part`, `source`, `version` and `licence`. Copied text carries the marker
`<!-- imported: <part> -->`, with the part's name in place of `<part>`.

`python3 check_spec.py --imports <folder>` finds every marker in the folder's text files and prints
`REFUSED import <part>: no licence record`, or `REFUSED import <part>: licence <licence> is not in the allowed
list`, for each part that fails, then exits 1; otherwise `PASS`. The allowed licences are MIT, Apache-2.0,
BSD-2-Clause, BSD-3-Clause, ISC, CC0-1.0 and CC-BY-4.0.

## A short clean example

```
## Problem
New visitors cannot tell whether their sign-up worked, so many sign up twice.

## Users and scenarios
- A visitor signs up with a valid email address and wants to know it worked.

## Goals
- A visitor learns at once that the sign-up worked.

## Non-goals
- Changing how passwords are stored.

## KPIs
- K1: A visitor who gives a valid email address receives a welcome message within one minute.
  Fails if: no message arrives within five minutes, or it arrives twice.

## Test data
| source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured |
| --- | --- | --- | --- | --- | --- | --- | --- |
| forty sign-up requests | synthetic | QA engineer | built from a fixed seed, ten per day | none | none | yes | yes |

## Out of scope
- Resending the message on request: a later ticket.

## Open questions
- Question: How long may the message take?
  - Options: one minute (cost: a faster mail queue); five minutes (cost: more repeat sign-ups)
  - Recommendation: one minute, as the queue already meets it.

## Accepted by
The product owner, on the passing check and the passing acceptance tests.
```
