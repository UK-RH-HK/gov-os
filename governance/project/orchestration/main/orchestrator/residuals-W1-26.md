
## W1-26 residuals (gov check G0-G2, 2026-10-06)

- **`gov check` on this repository exits 3.** Red from real findings: schema/invariants (legacy records without
  `state_class`), graph integrity (dangling `depends_on` references). Red because nothing is measured or built
  here: index freshness (no lexical index in this tree), retrieval regression (unmeasured, no dev tiers
  configured), context reproducibility (no loaded store), and the policy keys change, human_gate, security, test
  and tool (no check registered for them yet). Yellow with "no registered check" (DEC-438): adapter/model
  portability, recovery/rebuild (W1-27), audit reproducibility.
- **The fresh-agent-reconstruction check is red here because `gov` is not on the `PATH` of the check's shell**
  (exit 127). Its declaration is W1-25's.
- **The result lists 24 families:** the Contract's seventeen and the seven policy keys, each as its own entry.
- **The schema check validates the presence of fields,** not their types, enumerations or patterns (reviewer R1).
- **A check's command that exits 0 is green whatever it prints** (DEC-285); a non-JSON output is not a finding.
- **A hard-block check whose tool is absent (`openspec`) is YELLOW, not RED** (reviewer F10).
- **Check commands are run through a shell from their YAML declaration,** with the caller's write access to the
  working directory, and are not validated (F11, F12).
- **Policy coverage matches a key to a check by substring** (F13); the skill-version check accepts any `ACTIVE`
  decision (F14).
- **The provenance `inputs_hash` is the hash of the check's id and the commit,** not of the input files.
- **Four lists remain constants in the code** because the Contract fixes them (the families, the reserved
  commands, the non-authoritative types, the implementer roles); record paths and schema types are derived, and
  an unknown record type is a finding (DEC-436).
- **`wbs_to_id` in `claims.py` is built and never used.**
- **History:** the second round's merge of the integration branch was made without committing in the same
  command and lost other tickets' tests; it was never merged, and the branch was rebuilt (DEC-436). The rebuilt
  branch's merge `b7e75958` was flagged once by the containment check for the shared W1-07 support file,
  byte-identical to the branch's aligned version: a record.
- **Review rounds:** two (the limit). After them, fixed test-first without a further review: an unknown family
  never green, derived record paths, the readiness result (DEC-436); a family with no registered check never
  green (DEC-438, found by the orchestrator's own run).
- **Learning metrics:** 0 KPI disputes; 4 acceptance cases revised after implementation began (2 for DEC-425
  "unmeasured is never green", 2 that named uncovered families by a fixed list); 27 cases added after it;
  source 1,245 lines against an estimate of 290. Every module maps to a KPI line; the estimate was wrong, not
  the scope.
- **Interface:** `gov check [--json] [--list]`; exit 0 all green, 3 `CHECK_FAILED` on any hard-block red;
  `gov.check.runner.run_checks(root)` returns the result and whether a hard-block is red; each family entry has
  `status`, `check_count` and, where it applies, `reason`; each check has `id`, `family`, `severity`, `status`,
  `findings`, `provenance`. Family names are compared normalised (DEC-436).
- **Regression at `6d1848cd`:** every suite green, no latency occurrence.
