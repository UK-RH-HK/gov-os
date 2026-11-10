# W2-149 set-up A wiring: the lead's draft interface (2026-11-10, not yet briefed; waits on the CTO's seed ruling)

By the ticket lead for DAEO-52ku (row 86). Nothing launched, nothing committed from here. The five briefs' bytes do not
change. A fresh lead uses this to write the test designer's brief once the CTO rules on §0.

## 0. The blocker: the seeds (DEC-105, to the CTO)
The declaration §5 says: "Seeds: [both labellers' seeds, the overlap auditor's and the writers' are derived from this
record's commit id, filled at commit]". It was never filled (`bfa700da1`, `383de0ffd`). W2-149's S6 (DEC-1101 (2)-(3):
"a random sample ... from a seed recorded before writing") has the script draw 63 random bits per wall and refuse a
caller's seed. Labeller-2's brief calls its `seed.txt` "the declaration's overlap seed". Options and recommendation:
the lead's return (twelve fields). Every case below with a given seed uses `--dry --seed N`, so the test design does
not depend on the ruling. Only S6's real-run line depends on it.

## 1. Entry criterion (F7), template, scope
- `governance/project/indep-walls/tree-exclude.txt` += `governance/project/indep-briefs/**` (every wall).
- `kinds.yaml`: a `model:` per kind (proposal: `claude-opus-5-5`, DEC-838), and a top-level `briefs:` map keyed by the
  front matter's `brief:` id: `{kind, flow, result_schema, sample, tree_exclude}`; the five entries are `sgx1-labeller`,
  `sgx1-labeller-2`, `sgx1-writer-tuning`, `sgx1-writer-heldout` and `sgx1-overlap-auditor`. `sample: 0` for the
  labellers and the auditor. `tree_exclude` (set-up A only, stricter): `.claude/**`, `src/gov/guard/**`,
  `src/gov/launch/**`, `governance/project/indep-walls/**` (README item 5). Precedence at stage 10: the front matter's
  value, then the brief's entry, then the kind's (the model only); none gives 10 as today. An entry whose `kind`
  differs from the front matter's gives 10.
- Two template hashes change, so the install ACT's list changes two template lines too (the owner's yes covers them;
  the template is the owner's, ACT-INDEP-WALLS-1).
- W2-149's allowed_paths gain `governance/project/indep-walls/kinds.yaml` and `.../tree-exclude.txt`
  [changed, DEC-1112 (3)]. The new schemas sit under `indep-schemas/**` (already in scope).

## 2. Places
- EXP = `<runs>/SANDBOX-GUARD-EXP-1`, where `<runs>` is `GOV_INDEP_RUNS_DIR` or `~/gov-os-runs` (reading 2).
- Half folder H: `tuning` is EXP/tuning; `held-out` is `<root>/fixtures/evaluation/sandbox-guard-exp-1/hidden` (sealed).
  The script derives both in code. `--set` names the half for the sgx1 flows (`tuning` or `held-out`, otherwise 17).
- Inputs: H/corpus/actions.jsonl and H/planted/cases.jsonl. Labels: H/labels/{labels.jsonl, labels-2.jsonl}.
  Round-1 keeps: H/labels/r1-<brief id>/. Audit: H/labels/audit/<run>.{map.json,decisions.jsonl}. Flagged cases:
  H/labels/owner.jsonl. Replaced label files: H/labels/history/.
- An action line is staged projected to the brief's fields (`id role agent ticket wbs tool input cwd executable strata
  source`, plus `rule_class` for planted cases). `session` and call ids are dropped.

## 3. Flows (from the brief entry's `flow`)
- **sgx1-writer-1 / -2:** selection as S5. Writer 2 also gets `input/seal.json` `{"sealed": true|false}`: true when the
  path map at `--commit` holds the `sandbox-guard-exp-1` evaluation set with its hidden glob and `sets_root_hidden`
  covers it. Delivery: `out/cases.jsonl` (each line valid: id pattern `p1-`/`p2-`, source, rule_class 1..14) to
  H/planted/cases.jsonl, writer 1 to tuning and writer 2 to held-out. All or nothing; an existing file refuses 20.
  `aims.jsonl` stays in the tar only. A `--set` that does not match the flow's half refuses 17.
- **sgx1-labeller-1, round 1:** `input/half.json` `{"half","pin"}`, `input/actions.jsonl`, `input/cases.jsonl` (either
  missing gives 10). Delivery: `rulebook.md` and `label_rules.py` to H/labels/r1-sgx1-labeller/, with sha256s in counts.
- **sgx1-labeller-1, round 2:** the round-1 files from H/labels/r1-… (hashes checked against round 1's delivered
  sha256), staged as `input/round1/`. The script runs `label_rules.py` **confined**: `bwrap` (0.9.0 installed) with
  every namespace unshared and no network; read-only binds of the python install only; no HOME, sets root, runs, repo
  or wall; `--die-with-parent`; rlimits on CPU, memory, file size 0 and file count; a wall-clock cap; a stdout cap; the
  pinned python `-I` (`GOV_INDEP_RULES_PYTHON`, else the interpreter on the first line of `~/.local/bin/gov`). Stdin is
  actions then cases. The output must give every id exactly once, with the label in {allow, refuse, ask}, rule_class
  1..14, clauses a list of strings and uncertain a bool. Anything else (bwrap missing, timeout, invalid output) refuses
  with a new code **18 "rules"**, nothing staged. The script stages `input/script-labels.jsonl` and `input/sample.json`
  `{"ids": [...]}`: ids with `int(sha256((SEED + "labeller-sample" + id).encode()).hexdigest(), 16) % 20 == 0`, where
  SEED is the wall's `seed.txt` without the newline. Delivery: `hand-labels.jsonl` validated, and every required id
  (uncertain, class 1-13 by the script's class, the sample) present, else 20. The script merges hand over script into
  H/labels/labels.jsonl (`how` `script`|`hand`); an existing file refuses 20.
- **sgx1-labeller-2, round 1:** `input/half.json` only. Delivery: `rulebook-2.md` to H/labels/r1-sgx1-labeller-2/.
- **sgx1-labeller-2, round 2:** `input/round1/rulebook-2.md` and `input/sample.jsonl`: the projected action and case
  lines with `int(sha256((SEED + "overlap" + id).encode()).hexdigest(), 16) % 10 == 0` (the declaration's rule;
  **S20 [changed, DEC-1112 (3)]**, no random.Random). Delivery: `labels-2.jsonl` with exactly the sample's ids, each
  once, `how: hand`, to H/labels/labels-2.jsonl; an existing file refuses 20.
- **sgx1-overlap-auditor** (kind auditor; `--audit` still required, recorded only; no misses read; **no AUDITS.log
  line**, so the memory writers' `last_audit` is untouched). It needs both label files. The disputes are the ids in
  both whose `label` differs, not yet decided in H/labels/audit/. Each run takes the first 40 by id (the CTO's
  delegated split at 40). For each case, a coin from `random.Random(seed)` decides whether x is labeller 1. The map
  goes to H/labels/audit/<run>.map.json and stays outside the wall. `input/half.json` `{"half","pin","cases"}`;
  `input/disputes.jsonl` per the brief §2, the reason "" for a script label; `input/tickets.jsonl`: for each ticket a
  case names, `{id, role, wbs_id, allowed_paths}` from `.tickets/*.md` at `--commit` (git show), matched on `id` or
  `wbs_id`. Delivery: `decisions.jsonl` validated (one line per case in order, ids equal, the label, rule_class,
  basis, agrees_with x|y|neither, the flag, reason "" iff the flag is none), else 20. It is written mapped back to
  H/labels/audit/<run>.decisions.jsonl. labels.jsonl is rewritten atomically, the old copy kept in labels/history/:
  settled cases take `label` = the auditor's and `how: audit`; flagged cases take `how: owner` and are appended to
  owner.jsonl with both labels and the decision.
- Hidden budget (S18): each flow's expected files counted under the sealed folder.
- Result schemas: new `sgx1-labeller-result`, `sgx1-labeller-2-result`, `sgx1-writer-result` and
  `sgx1-auditor-result` (round 1 and round 2 by `anyOf` and `const`, numbers and fixed words only). The counts schema
  gains the new count keys (numbers only).

## 4. KPI lines to add or change (in the ticket, `[changed, DEC-1112 (3)]` with the reason)
S16 (deliveries per flow), S20 (the declaration's rule), and new lines for: stage 10 with the template's defaults (the
five real briefs pass `--dry` on a planted list), the tree exclusions, each flow's staging and delivery, the confined
rule script (a planted script that tries a file, a socket and a child process: each fails, and the run refuses 18), the
40 split, and x/y mapped back. S6 per the CTO's ruling.
