# P-IS-5 (a): three ticket-file corrections before the first re-pin, as they would be committed

Each correction is its own commit, carrying that ticket's `Task:` (DEC-896 item 2), once the owner takes P-IS-5 (a).

## W2-65 (`DAEO-e82f`)

- **allowed_paths gains:**
  - `src/gov/hooks/subagentstop.py`: kept byte-identical to the template's copy, which `TestHookCopiesIdentical` requires;
  - `tests/acceptance/W1-29/test_session_hooks.py`: for its test designer only, with `Rewrite-Reason: DEC-889 item 8`. W1-29's SubagentStop case accepts the undocumented form this ticket removes (I3 F4).
- **A note for its test designer:** the launcher recognises the guard by `hooks/pretooluse.py`, and the new hook line must keep that (I1 §2.3).
- **Riding along (P-IS-7 (a)):** the weak unit hook cases in `tests/unit/hooks/**`, which its engineer already holds. The weak PreCompact case (I3 P9) is one of them.

## W2-69 (`DAEO-rmbe`)

- **Named for its test designer:** W2-50's scale cases in `tests/acceptance/W2-50/` (the large-store and time-limit cases of the secrets scan). Rows-as-text scanning or compaction may change what they expect (I1 P-I1-7).
  - allowed_paths gains, for its test designer only, each change with a `Rewrite-Reason: DEC-897`:
    - `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`;
    - `tests/acceptance/W2-50/w2_50_scan_support.py`;
    - the secrets cases of `test_w2_50_never_indexed.py` and `test_w2_50_last_review.py`.
  - W2-50's contained duplicate can be retired then (P-I1-7; the retirement is the owner's, P-IS-15).
- **W2-L373's rename rides here.** `tests/unit/secrets/` shadows the standard library's `secrets` under some plugins: a collection red in all five tool trials (I2 F8). The folder becomes `tests/unit/secrets_check/`, and allowed_paths gains `tests/unit/secrets_check/**`.

## W2-66 (`DAEO-c1uz`)

- **The file names the test map** (`governance/project/test-map.yaml` and its schema), not the path map (DEC-896 item 2).
- **It is replaced by the draft in this bundle** (`01-W2-66-ticket.md`).
