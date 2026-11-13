---
type: probe
task: DAEO-href
reviewer_session: 26fdc72a-0754-4aeb-ac3b-e32f68fe2d15
implementer_session: b1f27b65-a5cf-47c1-aa82-f46022cc2690
reviewer_wrote_nothing: true
commissioned_by: orchestrator (W2-183 ticket lead)
judged_by: orchestrator (W2-183 ticket lead)
judgement: pass
probed_commit: e0c076514c9dbbf84d8fca72a93c37b7fa60847b
---

# Probe record: W2-183 (DAEO-href) gov close's context packet at a project setting; the supplementary cap, STANDARD review

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (claude-opus-5-5, high, class C2; session 26fdc72a-0754-4aeb-ac3b-e32f68fe2d15; log `.gov-runtime/scratch/lead/log/rv-1.json` in the W2-183 tree), STANDARD review round 1 of head `e0c076514c9d` (the engineer's commit, session b1f27b65-a5cf-47c1-aa82-f46022cc2690), its brief carrying JUDGEMENT.md word for word.
- **READY, by code.** The verdict block marks S1, S2, S3 and F1 pass. No finding is in scope, ordinary work yes and fails open or loses work (DEC-1010).
- **Rows, not a round (DEC-801, DEC-808).** F1 (the acceptance folder has no quoted-number case; the engineer's unit test `tests/unit/close/test_w2_183_context_setting.py` catches it): Ordinary work: yes, because an engineer could turn a numeric string into a number. Consequence: other. It rides along with the W2-54 revision the lead returns to the CTO (DEC-802). F2 (a non-mapping `budgets:` gives the default): Ordinary work: no, because `budgets:` is an established mapping other readers depend on. Consequence: other. F3 (a YAML date as the setting may not serialise in `gov close --json`'s refusal; inferred, not reproduced): Ordinary work: no, because nobody writes a date as a token count. Consequence: other. F4 (the close record's packet hash, built at the setting, differs from `gov context`'s at the default; nothing compares them): Ordinary work: yes, because a reader could compare them. Consequence: other; out of scope (`context_check.py` is a non-goal).
- **W2-54.** `tests/acceptance/W2-54/test_w2_54_dropped_order.py:172` (a room-for-all `--budget`, nothing dropped) is green on the base 74d35283b and red on this head: the cap applied as S2 decides (the reviewer agrees). Its revision is the CTO's (package P-W2-183-1 in the lead's return).
- **Judgement: pass.**

## The reviewer's record (as returned)

**Step 0, the sandbox check:** passed. (a) The probe write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-183` was refused (`OSError: [Errno 30] Read-only file system`), and no file was left. (b) `git hash-object -w --stdin` worked (object `1ae28402a109…`) and `git update-index --refresh` exited 0. Step (b) adds one loose object to the shared `.git`, because the brief requires it. **ps check:** no ollama or llama-server process is running.

Identity: `git rev-parse HEAD` = `e0c076514c9dbbf84d8fca72a93c37b7fa60847b`. `git status --porcelain` is empty, at the start and at the end.

task: DAEO-href (W2-183), STANDARD review, round 1, of head e0c076514c9d
status: DONE
work_completed: I read the whole diff (74d35283b..e0c076514c9d), the ticket, the acceptance tests and their README map, and DEC-1165 (ACCEPTED), DEC-1027 and DEC-860 (both ACCEPTED). I checked each KPI line against the code. I also traced where the packet's hash goes after the close (`packet_hash` in the close record, `context_hash` in the refusal, and `gov check`'s context reproducibility in `context_check.py`), and looked for other callers of `gov.context.context` and other readers of `budgets:`. I tried 16 different setting values against `close_budget` in a scratch copy. I ran the W2-183 acceptance tests against three broken copies of the code.
files_changed: none
evidence: The changed code is `src/gov/context/__init__.py:23-26` (the constants), `:43-76` (`close_budget`) and `:388-390` (the supplementary room is now `min(limit - mandatory_tokens, SUPPLEMENTARY_CAP)`), plus `src/gov/close/command.py:508-516`. `close_budget(root)` is evaluated inside the `try`, so `CONTEXT_SETTING_INVALID` becomes `_Finding("CONTEXT_FAILED", …, context_error=…)`. The build matches the interface the CTO stated, and nothing else in `src/` changed.
- **S3 holds by construction.** Whenever `limit ≤ mandatory + 6000`, `min()` returns the same room as before, so the items are the same. The hash is the same too, because `budget.limit` and the rest of the packet are unchanged. The checks on the mandatory part over its ceiling (`:370`) and the total (`:397`) are untouched.
- **Setting values I tried:**

| setting | result |
|---|---|
| `0`, `-5`, `"many"`, `"65536"`, `true`, `2.5`, `65536.0`, `null`, `[1]`, a date | refused with `CONTEXT_SETTING_INVALID`, naming the key, the file and the value |
| facts file not valid YAML, or not a mapping | refused, named |
| `65_536` | read as 65536 |
| empty file, comment-only file, or `budgets:` not a mapping | the default, 6000 |

- **Who else uses the packet:** `context_check.py:113,156` builds two packets at the default and compares them with each other. It never compares with the close record's `packet_hash`, and only `close/command.py` reads that field in `src/`. `sessionstart.py:153` and `gov context` use the default or an explicit `--budget`. The brief builder (`brief/build.py:332`) and W2-128 read only their own keys of `budgets:`.
tests: Every run went through the heavy slot with the brief's `-m`/`-k` exclusions; those exclusions are the real-model cases, which the CTO runs outside the sandbox. I did not re-run the lead's suites. Results on the broken copies, W2-183 acceptance (49 cases):

| broken copy | acceptance result |
|---|---|
| m1: cap loosened to 9000 | 7 red (all the S2 cap cases), caught |
| m3: an invalid setting falls back to the default | the F1 cases red, caught |
| m2: a quoted number such as `"65536"` accepted | **49 green**, not caught by acceptance; the engineer's `tests/unit/close/test_w2_183_context_setting.py` catches it (1 red) |

I stopped a third run (the context unit tests on m2) while it was still waiting for the heavy slot; it is not needed for any verdict.
discoveries:
- **W2-54 `test_w2_54_dropped_order.py:172`:** the cap does what S2 decides there. `room_for_all` (`w2_54_support.py:613`) works out a budget that holds the whole evidence. Under DEC-1165 (2) no `--budget` holds more than 6,000 supplementary tokens, so the test's premise can no longer be reached through `--budget`. The cap is applied correctly; the test needs revising, and that revision is the CTO's. This is not a finding against this branch.
- There is no `docs/changes/W2-183-evidence.md`. The ticket's `allowed_paths` do not admit one, so this is consistent with the ticket.
risks: For almost every ticket, a close record's `packet_hash` (built at 65536, supplementary room 6000) will differ from `gov context <ticket>`'s hash (built at 6000). No code compares the two today (F4).
lessons: none
proposed_decisions: none
unresolved: none
recommended_next_action: Land on this review. Have the test designer add the quoted-number case (`"65536"`) to the F1 acceptance tests (F1 below), riding along with the W2-54 revision. Carry F2 to F4 as recorded rows.

**F1** — `tests/acceptance/W2-183/test_w2_183_f1_invalid_setting.py:18`. The acceptance tests never write a quoted number such as `"65536"`, which the stated interface says must refuse. A build that turns `"65536"` into 65536 passes all 49 cases; only the engineer's unit test catches it. What would reverse this: an acceptance case that goes red on the m2 copy.
Ordinary work: yes, because an engineer could easily turn a numeric string into a number "helpfully".
Consequence: other (a coverage gap; today's code refuses correctly and a unit test guards it). Scope: in (F1).

**F2** — `src/gov/context/__init__.py:70-72`. If `budgets:` in facts.yaml is something other than a mapping (for example a list), the close falls back to 6000 silently instead of refusing by name. What would reverse this: a ruling that a non-mapping `budgets:` counts as "no setting".
Ordinary work: no, because `budgets:` is an established mapping of role budgets that the brief builder and W2-128 depend on, and turning it into a list breaks those first.
Consequence: other (the close falls back to today's ceiling and refuses as before, so it does not let anything through). Scope: in (F1).

**F3** — `src/gov/context/__init__.py:73-74`, together with `src/gov/cli/main.py:185`. The setting's raw value goes into the refusal's details. If someone writes a YAML date or a timestamp as the setting, `gov close --json` would likely crash when it serializes the refusal, instead of printing it. I inferred this from the code and did not reproduce it end to end. What would reverse it: `gov close --json` with `close_context_tokens: 2026-11-13` printing a clean refusal.
Ordinary work: no, because nobody writes a date as a token count.
Consequence: other. Scope: in (F1).

**F4** — `src/gov/close/command.py:271` and `src/gov/context/context_check.py:156`. One ticket now has two packet hashes: the close records the one built at the setting, while `gov context` and `gov check` build at 6000. A reader who compares the close record with `gov context <ticket>` sees two different hashes. No code compares them today, and each side is reproducible on its own terms. What would reverse this: a reader in `src/` that compares `packet_hash` with a packet built at the default.
Ordinary work: yes, because a person reading the close record could compare it with `gov context`.
Consequence: other. Scope: out (the non-goal leaves `context_check.py` unchanged).

Classification: four findings, none blocking. F1 and F4 are ordinary work yes but with consequence other; F2 and F3 are ordinary work no. All four are recorded rows, and no round is needed.

Judgement: **pass**

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```

decisions: DEC-1165, DEC-1027, DEC-860, CAP-15.d, DEC-801, DEC-808, DEC-1010
guard_refusals: none. The only refusal was the mandated sandbox-check write in step 0 (a), which is expected to fail.
