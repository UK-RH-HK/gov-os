# RUBRIC-2 in the spawn tools (DEC-1120 (3)): model, class, tier and promotion in the spend line

Done by a helper (Sonnet, high; class C1), 2026-11-10. Nothing committed. The live `log/spend.jsonl` was never written (255 lines before and after).

## What changed

`tools/launch_worker.sh`
- `--class C0|C1|C2|C3` is required. Missing, empty, lower case (`c2`) or anything else: exit 2 with a clear line, nothing written.
- The model must be named: `--model <m>` or `LAUNCH_MODEL`; `--model` wins. There is no default model any more (the old `claude-opus-5-5` default is gone). None named: exit 2.
- `--promoted "<reason>"` is optional; an empty reason is refused (exit 2).
- All three go on to `spend.py from-log` (`--model`, `--class`, `--promoted`) through the detached and the `--fg` run alike. The stderr launch line now ends `; model <m>; class <C>[; promoted: <reason>]`.
- Options must stand before the three positionals (as `--projection-usd` always had to). The usage text printed on a wrong call is now the whole comment header (it was lines 2-30).

`tools/spend.py`
- The one schema grows four top-level keys after `extra`: `model`, `class`, `tier` (opus / sonnet / haiku from the model's name; `other` for any other name; null with no model), `promoted` (null or the reason). `KEYS` has 21 keys; `BASE_KEYS` is the old 17.
- An old 17-key line is still a normal line; `normal()` gives it the four as null. Old lines in the file are never rewritten by an append. `normalise` rewrites a log with the 21 keys, as before.
- `record` and `from-log` take optional `--model`, `--class` (choices C0..C3), `--promoted`; with none given they behave as before (the new keys null).
- New subcommand `add-helper` for the CTO's in-session Agent helpers, kind `agent` (the kind the older helper lines have): `--what --role --model --effort --class` all required; `--ticket --wbs --promoted --cost-usd --projection-usd --note --extra` and the four token fields optional. `effort` goes in `extra`, as for a launched worker. A cost not given stays null, never a guess. Its cost counts toward the ticket's total and brake like any line with that `--wbs`.

## The new launch line

    LAUNCH_MODEL=claude-sonnet-5-5 launch_worker.sh --class C2 --projection-usd 6 independent-test-designer high <brief>
    launch_worker.sh --model claude-opus-5-5 --class C3 --promoted "failed review twice (DEC-1120 (3))" engineer high <brief>

The helper's line:

    python3 tools/spend.py add-helper --what "RUBRIC-2 spend tools" --role product-spec --model claude-sonnet-5-5 \
      --effort high --class C1 --ticket <id> --wbs <W2-n> --cost-usd 1.25 --output-tokens 100 --cache-read-tokens 5000

## Behaviour changed for existing callers

- Any call without `--class`, or with no model named (`LAUNCH_MODEL` unset), is now refused (exit 2). That includes `lead_chain*.sh`, queue or wake scripts and any note that calls `launch_worker.sh` by hand: grep them before the next launch (the helper did not edit them).
- `LAUNCH_MODEL` still works and is the only way a script names the model without a flag.
- spend lines now have 21 keys; a reader that reads `at/what/kind/cost_usd/...` by name is unaffected. Only spend.py reads the log today.
- The summary line (`.summary`) and its wording are unchanged.

## Tests (the CTO's scratch tests; scoped)

- `bash tools/test_launch_worker.sh`: 75 checks, PASS (the 50 existing, `lw` now adds `--class C2` and `LAUNCH_MODEL` is exported; 25 new in section 12: class required, invalid, lower case, misplaced, each of C0..C3 accepted; no model by empty and by unset; `--model` alone and winning over the env; no model name built into the tool; empty `--promoted`; the spend line's model, class, tier, promoted for a promoted launch, an unpromoted one, a haiku one and a detached one; old 17-key and free-form lines mixed into the log still read by `sum` and `check`).
- `python3 -m pytest -q -p no:cacheprovider tools/test_spend.py`: 13 passed (the 7 existing, 6 new: the schema and the old line, `tier_of`, `record` and `from-log` fields, `add-helper`, its refusals, an old and new log summed and normalised).

## Backups (taken before any edit; byte-identical to the pre-change files)

- `tools/launch_worker.sh.pre-rubric2`
- `tools/spend.py.pre-rubric2`
- `tools/test_launch_worker.sh.pre-rubric2`
- `tools/test_spend.py.pre-rubric2`

The new versions were built and tested in a scratch folder, then moved into place (spend.py first, so a worker ending mid-switch found a spend.py that takes both forms).
