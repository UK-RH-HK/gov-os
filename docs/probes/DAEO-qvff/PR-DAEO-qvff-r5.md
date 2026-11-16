---
type: probe
task: DAEO-qvff
round: r5
reviewer_session: f9465b72-b90a-4666-a289-600c88aa88bd
implementer_session: "aa9cb9e6-3e2c-4dfb-afea-59092d232731"
reviewer_wrote_nothing: true
reviewer_model: claude-opus-5-5
reviewer_effort: high
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9e1f63d8380c70fea283ed44714f2d0107a4cb70
decisions_applied: [DEC-1187, DEC-979, DEC-906, DEC-968, DEC-1184, DEC-1157, DEC-1010, DEC-808, DEC-802, DEC-1154]
---

# Probe record: W2-111 (DAEO-qvff), r5: review round 1 of the DEC-1187 reopen, at 9e1f63d83

## The lead's judgement

**PASS.** The reviewer found no finding that is in scope, reachable in ordinary work and fails open or loses work, so
the branch is READY by the verdict block's rule. Three rows are recorded (F1 to F3). F2 needs the CTO's disposition
before the land, because lead_verify at this head is RED on that case alone (DEC-968). The lead has put the rows to
the CTO as P-W2-111-R5-ROWS.

**The round.**
- **The reviewer:** an independent auditor (Opus, effort high), read-only, session `f9465b72-b90a-4666-a289-600c88aa88bd`.
- **The brief:** `rv-3`, which carried JUDGEMENT.md word for word and asked for the verdict block.
- **The launch:** the first launch (`rv-3`, 21:50Z) was refused by `gov launch` before any session started: "review
  round 3 of DAEO-qvff is refused: at most two review rounds (DEC-1010); its setting … repeats the review of session
  21e927ea…; a third or later needs --owner-named". The CTO had named that case beforehand, so the lead relaunched with
  `--owner-named DEC-1187` (the reopen's decision) as `rv-3-2`. This is round 1 of r5; r4 and r4c judged the earlier
  change.

**The reviewer wrote nothing.**
- `git status --porcelain` was empty at the start and at the end, at `9e1f63d83`.
- The launcher's tripwire changes are all other sessions' work: the CTO's record commit on the main tree and the store
  trees (`ff24400cb` to `9fa839cba`), W2-174's lead and test designer, and W2-88's trees reappearing.

**What was reviewed** (first-parent commits `cd5642b2d..9e1f63d83`):
- **The engineer, eng-2:**
  - `5532c6f80`: the product. YAML through libyaml with SafeLoader as the fallback; the held-out and evaluation-sets
    parse-once caches; `bash_writes` imported lazily in `reads.py`.
  - `828d72040` and `565b25723`: `docs/changes/W2-111-live-hook/live-hook.diff` and its README.
- **The test designer:**
  - td-4 `8e7d98a48`: the YAML count pins, the paired live-hook timing case and its planted 150 ms case.
  - td-5 `5078ee22e`: the 30 ms clause dropped (P-W2-111-S9-DROP (a)).
  - td-6 `00cef4225`: the live-hook case renamed (P-W2-111-TD5-NAME (a)).
- **The lead's merges:** w2/integrate (ticket text and other tickets' landings) and the tests branch.

**Evidence beside the review.**
- **gov accept W2-111** at this head: pass, 111/0/0, at load 1.5-5.2.
- **lead_verify:** RED. Parallel run: 8,797 tests, 5 failed. Serial run: 5/5.
  - The 5 failures are the live-hook timing case, at load 10-20, with decisions equal in every round.
  - Re-run alone once at load 5.6: 5/5 pass, 57.7-78.8 ms.
- **The lead's own S10 check:** 20/20 within 100 ms on a clean patched copy against the live repository.
- **The reviewer's run:** 25/25 pass at load 1.3-2.9 (after 47.9-64.2 ms); the planted 150 ms hook fails every round
  (198.9-234.9 ms).

**The lead's triage.** None of the three blocks; each is a row.
- **F1** (ordinary work no, fails open): a Wave 3 row by the rule. Its fix is cheap, and the fast loader goes into the
  live hook by ACT-GUARD-FIX-7, so the lead proposes it ride along with F2's resume (DEC-802). It starts with a
  test-design batch given F1 as a described behaviour (DEC-136): "a held-out or path-map text the pure SafeLoader
  refuses (a tab inside or after a plain value, `? ` in a flow item, a BOM after the start) still refuses every call".
- **F2** (ordinary work yes, other): the established route is `tests/acceptance/serial-only.txt` ("serial: latency": run
  alone after the parallel phase), where W1-02's, W1-05's and W2-57's timing cases already are. W2-111's timing files are
  not listed, and that file is outside the ticket's paths, so it is a path case for the CTO (DEC-1156 (7)).
- **F3** (ordinary work yes, other): one line in the live-hook README's ACT follow-ups: the 25 live-hook cases fail by
  design once ACT-GUARD-FIX-7 is applied, so they are retired or re-pointed then.

## Findings (the reviewer's, with their two lines)

- **F1** (failure-4; success-9, success-10). `src/gov/util/parts.py:72-80` (commit `5532c6f80`) and the hook-local
  `load_yaml_unique` in `live-hook.diff` (`pretooluse.py` 316-347 after the diff).
  - **What:** libyaml accepts texts the pure SafeLoader refuses: a tab inside or after a plain value or after `key:`,
    `? ` inside a flow item, and a BOM after a line break (both loaders accept the BOM case, with different data). So
    the fallback never runs for them.
  - **The fuzz:** 70,000 mutations of the tree's YAML files gave 84-118 differences per 20,000-25,000 texts.
  - **End to end:** with `held_out_paths:` holding `/x/held<TAB>mat`, or `[/x/held? mat]`, the before copy refuses every
    call (DEC-218) and the after copy allows a read of the held-out material. The plausible slips (a trailing tab, or a
    tab after the key) keep the intended list, and the held-out material stays refused.
  - **The claim:** the README's and docstring's "every refusal and its text are the product's" holds only for refusals
    libyaml also makes.
  - `Ordinary work: no, because the fail-open forms need a tab or "? " inside an absolute path entry; the plausible slips give the intended list and keep the held-out material refused.`
  - `Consequence: fails open` (in the no-ordinary-work forms only; the plausible forms: other). Scope: in. A row.
- **F2** (success-10; failure-3 for the suite). `tests/acceptance/W2-111/w2_111_live_hook.py:305-340` (td-4
  `8e7d98a48`, td-5 `5078ee22e`).
  - **What:** the live-hook timing case's verdict changes with load. lead_verify's parallel run at this head reddened 5
    cases (after 105.9-126.0 ms at load 10.6-20.7, decisions equal); quiet they pass (57.7-78.8 ms at load 5.6; 47.9-64.2
    at load 1.6-2.9).
  - **Why:** CPU time per call rises about 1.8 times under load, and the live copy lacks the product hook's margin.
  - `Ordinary work: yes, because lead_verify and the nightly run it under load, and it reddened at this head.`
  - `Consequence: other` (a red gate under DEC-968; no decision changed). Scope: in. Not blocking under DEC-1010; the
    CTO's disposition is needed before the land.
- **F3** (success-10). `docs/changes/W2-111-live-hook/README.md`, "Follow-ups for the ACT" (commit `828d72040`).
  - **What:** after ACT-GUARD-FIX-7 the tree's hooks no longer hash to ACT-GUARD-FIX-6's, so the 25 live-hook cases fail
    by design. The test README records this (lines 353-355); the engineer's ACT follow-ups name only `test_w2_141`.
  - `Ordinary work: yes, because the ACT is planned.`
  - `Consequence: other`. Scope: in. A row: add the follow-up to the ACT's list.

## What the reviewer checked (in short)

- **The product loader:** fuzzed against the pure loader as above. Every other refusal matched in kind and text, and the
  held-out and path-map refusals keep their fixed wording.
- **The caches,** probed within one process:
  - a changed file is parsed again;
  - a broken file or a duplicate key refuses on every call and is never kept;
  - a relative entry refuses every time;
  - a missing file gives `[]`;
  - a caller's change to a returned value does not change the next answer;
  - nothing is written to disk.
- **The lazy `bash_writes` import:** `reads.py:1467` is its only use.
- **The live-hook diff:** `git apply --check -v` checked both files and `git apply` was clean; the result is
  `pretooluse.py` `665614961cd0` and `role_reads.py` `543cf1b26701`, with `bash_writes.py` unchanged.
  - `TreePart`/`TreeNarrow` give the made part's answers: every tree stays in the parts list, and only the moment a part
    is made changes.
  - `runs_gits` equals `glob`, in order, on the live `~/gov-os-runs` (55 found) and on a planted edge folder.
  - `realpaths` equals `os.path.realpath` on 3,052 paths.
  - The hook-local `has_install` gave 0 differences from the pinned 0.1.0's on 23,828 commands under three PATH lengths.
  - Any error in new code is refused with the same "could not decide" text.
- **The 15 revised cases and their READMEs:** `git diff cd5642b2d 9e1f63d83` on the six files is empty.
- **Not re-run:** the engineer's 4,291 x 4 live-hook and 4,204 x 4 product corpora. Their counts stand on the engineer's
  return, with the reviewer's own checks above as support.

## The verdict block (the reviewer's, copied unchanged)

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": []}, {"kpi": "success-2", "verdict": "pass", "findings": []}, {"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-4", "verdict": "pass", "findings": []}, {"kpi": "success-5", "verdict": "pass", "findings": []}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": []}, {"kpi": "success-8", "verdict": "pass", "findings": []}, {"kpi": "success-9", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "success-10", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "failure-2", "verdict": "pass", "findings": []}, {"kpi": "failure-3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "failure-5", "verdict": "pass", "findings": []}]}
```
