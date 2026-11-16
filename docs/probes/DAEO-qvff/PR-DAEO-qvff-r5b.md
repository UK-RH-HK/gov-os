---
type: probe
task: DAEO-qvff
round: r5b
reviewer_session: 88ec3fa2-d83a-4e86-859f-8a5b42a31ad7
implementer_session: "5726bff3-e184-4928-87e1-362ca9ac237e"
reviewer_wrote_nothing: true
reviewer_model: claude-opus-5-5
reviewer_effort: high
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 006ee890c4e0da913ad8722486921253e63e1ef5
reviewed_commit: 9e1f63d8380c70fea283ed44714f2d0107a4cb70
decisions_applied: [DEC-1154, DEC-1010, DEC-808, DEC-802, DEC-1187, DEC-979, DEC-906, DEC-968, DEC-1184, DEC-1157]
---

# Probe record: W2-111 (DAEO-qvff), r5b: the narrow re-check (DEC-1154) of 9e1f63d83..006ee890c

## The lead's judgement

**PASS.** The re-check found no finding that is in scope, reachable in ordinary work, and fails open or loses work. The
branch is READY by the verdict block's rule. Three rows are recorded (F1 to F3). By the CTO's order, nothing is committed
after this record: F2's one README line goes to the CTO for ACT-GUARD-FIX-7's follow-up list, and F1 and F3 are Wave 3
rows.

**Why there is a re-check.** r5's review (rv-3, `PR-DAEO-qvff-r5.md`) passed at `9e1f63d83` with rows F1 to F3. Three
decisions followed:
- **P-W2-111-R5-ROWS (a)**, the CTO: F2's path case (`tests/acceptance/serial-only.txt`), with F1 and F3 riding along
  (DEC-802).
- **P-W2-111-YAML-REST (a)**, the owner: the same fail-open class closed in the guard's other YAML reads. W2-111 is
  widened by `src/gov/util/role_paths.py`.
- **P-W2-111-YAML-REST-FRONT (a)**, the CTO: unparseable ticket front matter refuses the role-checked call.

The work: td-7, then eng-3, then td-8, then eng-4, with the lead's merges of w2/integrate and of the tests branch.

**The round.**
- **The reviewer:** an independent auditor (Opus, effort high), read-only, launched with `--owner-named DEC-1154`;
  session `88ec3fa2-d83a-4e86-859f-8a5b42a31ad7`.
- **The brief:** `rv-4`, which carried JUDGEMENT.md word for word and asked for the verdict block.
- **The reviewer wrote nothing:** `git status --porcelain` was empty at the start and at the end, at `006ee890c`, and the
  launcher's tripwire was clean.

**Evidence beside the re-check, at 006ee890c.**
- **gov accept W2-111:** pass, 184/0/0, at load 4.2-4.3.
- **lead_verify:** GREEN. Parallel phase 9,107 tests, 0 failed. Serial phase 7 entries, 51 tests, 0 failed; the entries
  include the five W2-111 timing files, so rv-3's F2 is closed.
- **The red before each fix, on the ticket branch:**
  - `test_w2_111_yaml_parity.py`: 16 failed at `4466208f2`;
  - `test_w2_111_yaml_rest.py`: 23 failed at `803a1af1d`.

**The lead's triage.** None of the three blocks.
- **F1** (ordinary work no, other): a Wave 3 row. The next loader change should send `|#`-style block-scalar headers and
  bare `!` tags to the pure loader too, and widen the fuzz alphabet to tags and block-scalar headers.
- **F2** (ordinary work yes, other): one line for ACT-GUARD-FIX-7's follow-up list. 43 live-hook acceptance cases fail by
  design after the apply, not 32, because `test_w2_111_yaml_rest.py`'s 11 live cases are added. The lead hands it to the
  CTO, who builds the ACT.
- **F3** (out of scope, ordinary work no, fails open): a Wave 3 row. It was not introduced here: the reviewed commit and
  the base behave alike.

## The six confirmations (the reviewer's, in short)

1. **F1 (rv-3) is closed for its three named classes, in the product and the diff.**
   - `git apply --check -v` was clean. The patched hashes are `pretooluse.py` `101bee39d5c9` and `role_reads.py`
     `02a782e31145`; `bash_writes.py` is unchanged at `f03f9ac3e431`.
   - A fuzz of 60,343 real-derived texts (56,566 handed to libyaml) and 12,069 named-stream checks gave 0 differences
     across the four loaders.
   - End to end, both copies ran as processes. Every malformed held-out text refuses every call in both copies (14 of 14
     rows), and the clean text is decided alike.
2. **The five reads, and the front matter fails closed.**
   - The product's `role_paths.caller` raises `RolePathsError` for a malformed front, for the engineer and for the test
     designer.
   - `judges` reads the front for every `{ticket_…}` role (`role_paths.py:437`, `role_reads.py:902`) before
     `_links_unless_coordination` can widen.
   - No path turns a refusal into a wider allow: the hook's catch-all refuses; `retrieve.role_filter` maps the error to
     `ROLE_PATHS_UNREADABLE`.
3. **No well-formed decision changed (F4).**
   - The kept corpus replay is green.
   - The live-hook paired case passed 20 of 20 with decisions equal (60-66 ms).
   - Clean held-out texts are decided alike.
4. **F2 and F3 (rv-3).**
   - The five `serial-only.txt` entries follow the file's form, and `entries()` returns all five (73 entries in all).
   - F3's README line is present but counts 32, not 43: this is F2 below.
5. **The integrate merges touch nothing the guard or W2-111's cases depend on.** Nothing under `src/gov/guard/`,
   `src/gov/util/`, `.claude/`, the six revised files, or any conftest or pytest setting. `git show --cc` prints nothing
   for the four merges.
6. **The six revised files are unchanged since `cd5642b2d`.**

## Findings (the reviewer's, with their two lines)

- **F1** (success-9, success-10, failure-4). The rule in `src/gov/util/parts.py:60-74` (`d1d187440`) and its copies in the
  diff (patched `pretooluse.py:316`, `role_reads.py:95-109`, `1e455d6d5`).
  - **What:** a 150,000-text synthetic fuzz (130,113 handed to libyaml) gave 196 texts where libyaml's answer differs
    from the pure loader's:
    - **(A)** a block-scalar header followed straight by `#` (`|#`, `>-#`, `|2#`): libyaml reads it, the pure loader
      refuses it (36 texts);
    - **(B)** a bare `!` tag on an empty node: libyaml gives `''`, the pure loader `None` (160 texts).
  - **End to end:** `note: |#` after the list, or a `|-#` list item. The applied (pure) copy refuses every call; the
    patched copy allows the ordinary Read, and the held-out file stays refused.
  - **Not a regression:** the reviewed commit sent these texts to libyaml too.
  - `Ordinary work: no, because a block-scalar header with no space before its comment, or a bare "!" tag, is not written in held-out.yaml, the role_paths block or a ticket's front matter in ordinary work.`
  - `Consequence: other` (the held-out material stays refused in every form tried; only DEC-218's stop-every-call is
    lost). Scope: in. A row.
- **F2** (success-10). `docs/changes/W2-111-live-hook/README.md:25-27` (`006ee890c`).
  - **What:** the ACT follow-up names three files and 32 cases. td-8's live cases in `test_w2_111_yaml_rest.py` also build
    their copies through `make_copies`, which checks ACT-GUARD-FIX-6's hashes. So 43 cases fail by design after
    ACT-GUARD-FIX-7, and the test README (line 359) still says 25.
  - `Ordinary work: yes, because the ACT is planned.`
  - `Consequence: other` (a planned red the list misses; no decision changes). Scope: in. A row, for the ACT's list.
- **F3** (failure-4). `role_paths.ticket_front` and `role_reads.ticket_front`.
  - **What:** a front with a byte-order mark at the start of the `allowed_paths:` line is read by the pure loader as the
    key `﻿allowed_paths`, so the test designer's `{ticket_impl}` loses its `allowed_paths` part. The reviewed commit
    behaved the same (libyaml's error became `{}`).
  - `Ordinary work: no, because a byte-order mark lands mid-file only when files are concatenated by hand.`
  - `Consequence: fails open` (narrow: only the `allowed_paths` part). Scope: out (not introduced here). A Wave 3 row.

## The verdict block (the reviewer's, copied unchanged)

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, {"kpi": "success-2", "verdict": "pass", "findings": []}, {"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-4", "verdict": "pass", "findings": []}, {"kpi": "success-5", "verdict": "pass", "findings": []}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": []}, {"kpi": "success-8", "verdict": "pass", "findings": []}, {"kpi": "success-9", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "success-10", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "failure-2", "verdict": "pass", "findings": []}, {"kpi": "failure-3", "verdict": "pass", "findings": []}, {"kpi": "failure-4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "failure-5", "verdict": "pass", "findings": []}]}
```
