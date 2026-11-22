# W2-22 acceptance tests: `gov doctor` and a patch-only Claude Code CLI/extension gap

Ticket `DAEO-xm6l` (W2-22, `gov doctor green`). **A fix, not a new ticket** (EMERGENCY-2 section 2): the owner's
DEC-1227 D6 (a). Context: `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`, rows P1 and A1. Written by the
independent test designer from the two fix lines below, before the implementation. The ticket's own status and KPIs
are history and are not changed; the lines of this fix are the two here, read by `gov accept` as `success-1` and
`success-2`.

- **A1 (success-1).** In `gov doctor`'s `claude_code` section a difference of the PATCH number only (same major and same
  minor) between the CLI and the VS Code extension is drift: reported, exit 0. With no registry entry for Claude Code
  (`pinned_version` null), a stand-in CLI 2.1.329 and extension 2.1.328: `gov doctor --json` exits 0 (`ok` true,
  `healthy` true), the section still says `status: drift`, `drift: true`, and an `issues` entry of type `drift` names
  both versions. The plain output (no `--json`, which prints the result as indented JSON on standard output when
  doctor is healthy) names both versions on one line and says drift. Both directions and a wide patch gap
  (2.1.329 against 2.1.300); equal versions are no drift (control).
- **A2 (success-2).** A larger gap still fails: exit 3, error code `DOCTOR_UNHEALTHY`, `claude_code` named. The minor
  differs (either way), the major differs (either way); a CLI below the minimum 2.1.285; a CLI whose sha256 differs
  from the registry's record at the CLI's own version. A patch-only gap beside another failure or drift in the same
  section (CLI sha256, extension below the minimum, both binaries newer than the registry's record) still exits 3.
- A3 is documentation only and is not tested.

## Run

    T=$(mktemp -d); TMPDIR=$T PYTHONPATH=<this worktree>/src bash <heavy_slot.sh> \
        python3 -m pytest tests/acceptance/W2-22 -q -p no:cacheprovider -n auto; chmod -R u+w $T; rm -rf $T

or `gov accept W2-22`. Every case builds a small committed git repository under `tmp_path`, a stand-in `claude` (a
shell script echoing a version) first on the `PATH` `gov` runs with, and a stand-in extension (`extensions.json`,
`package.json`, `resources/native-binary/claude`) under the case's own `HOME/.vscode-server/extensions`; it runs this
worktree's code through W1-07's launcher (DEC-732). The machine's own CLI, extension and home are never read or
touched; no network. The support file reuses W1-27's and W1-07's helpers (`w2_22_support.py`).

## Map

| KPI | Tests | Today (base), and why |
|---|---|---|
| success-1 (A1) | `test_w2_22_claude_code_drift.py::test_a_patch_only_gap_is_named_drift_and_doctor_exits_0[2.1.329-2.1.328]`, `[2.1.328-2.1.329]`, `[2.1.329-2.1.300]` | **red**: exit 3, `DOCTOR_UNHEALTHY` (a drift is counted as unhealthy), where exit 0 and `healthy` true are expected; the section itself (`drift` true, the drift issue naming both versions) is already as expected |
| success-1 (A1) | `test_w2_22_claude_code_drift.py::test_a_patch_only_gap_is_named_in_the_plain_output_too` | **red**: exit 3 and nothing on standard output (the plain error goes to standard error without the versions) |
| success-1 (A1), control | `test_w2_22_claude_code_drift.py::test_equal_versions_are_no_drift_and_doctor_exits_0` | green today (a guard: equal versions stay no drift and exit 0) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_gap_beyond_the_patch_number_fails_doctor[2.2.0-2.1.329]`, `[2.1.329-2.2.0]`, `[2.1.329-2.2.5]`, `[3.0.0-2.1.329]`, `[2.1.329-3.0.0]` | green today (guards against over-fixing: any gap is unhealthy today; they go red if the fix exempts more than the patch number) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_cli_below_the_minimum_fails_doctor[extension-also-below]`, `[extension-above]` | green today (guards) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_cli_with_another_sha256_than_the_record_fails_doctor` | green today (guard) |
| success-2 (A2) | `test_w2_22_claude_code_drift.py::test_a_patch_only_gap_does_not_mask_a_cli_sha256_failure`, `test_a_patch_only_gap_does_not_mask_an_extension_below_the_minimum`, `test_a_patch_only_gap_does_not_mask_drift_from_the_record` | green today (guards: a patch-only exemption that masks a real failure or the record's drift turns them red) |

Red run on the base (4 red, 12 green, the green ones being the guards above):
`4 failed, 12 passed`.

## Open points (for the owner or the lead, not guessed)

- **Drift from the registry's record beside a patch-only gap.** `test_a_patch_only_gap_does_not_mask_drift_from_the_record`
  reads D6 (a) as exempting only the CLI-against-extension gap, so a CLI (and extension) newer than the registry's
  record still ends doctor with exit 3 (W1-27's `test_cli_newer_than_registry_is_drift` keeps its `drift` section).
  If the owner meant every drift in the section to stop counting, this one case changes.
- "Named in the plain output" is read as: one line of the output holds both versions, and the word drift appears.
