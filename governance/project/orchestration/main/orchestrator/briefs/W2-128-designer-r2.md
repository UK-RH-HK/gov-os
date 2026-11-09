# W2-128 round 1, revision 2 — the independent test designer's brief (DAEO-t8mp)

You are a fresh independent test designer for **W2-128** (`.tickets/DAEO-t8mp.md`). Your predecessor wrote round 1's
cases (`tests/acceptance/W2-128/`, TESTS-READY `97489c19d283`) and raised D1 and D2. The CTO decided (now in the
ticket's body, "Interface and rounds", the schema bullet, `d1f50e2f`, merged into your branch as `f67e57de`):
- **P1 (b):** a `waits_on` item's object form is `{ref: <id or record path>, reason: <one line>}`; the key is `ref`,
  never `on` (YAML 1.1 reads a bare `on` as `true`).
- **P2 (a):** a `waits_on` item is either a string or that object (DAEO-2bdu's string items stay valid).
- Also stated: a template's `role` front matter is a plain string (`any` for T-0 and T-1); no `{FACT:…}` family.

## The change
- `tests/acceptance/W2-128/test_w2_128_links.py` (about line 156, S19) and `test_w2_128_schemas.py` (about line 71,
  S10): `on` becomes `ref`; S19 accepts a string item or a `{ref, reason}` object in T-1's skeleton, and still fails an
  object without `reason`; S10 checks the schema accepts both forms and refuses an object without `ref`. Anything else
  in your cases that assumed `on`, `{FACT:…}`, or a placeholder `role`: align it with the ticket's interface.
- The README's map and its "On integrate" column updated; the D1/D2 note marked decided.
- Nothing else changes.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-128-tests`, branch `w2/W2-128-tests`; you write only
  `tests/acceptance/W2-128/`. Run only those cases:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-tests/src python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider`
  with an empty `HOME`, then `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-128-tests`.
- Never read this ticket's implementation: never open `/home/usain/gov-os-worktrees/W2-128` or `w2/W2-128`; keep every
  search inside your worktree (DEC-1093 (2)). Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, model, network or installs. DEC-1080: one simple command per
  Bash call. No merge inside the sandbox. Search again once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-128-tests`, only `tests/acceptance/W2-128/`, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1088, DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the cases changed, the run's counts, `gov accept`'s counts, and `TESTS-READY <hash12>`.
