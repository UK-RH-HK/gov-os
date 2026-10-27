"""Fills the review 2 brief: the head, the lead's verification and JUDGEMENT.md word for word."""
from pathlib import Path

SRC = Path("/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-57/68c33b27-7fb1-4772-9f93-b61c41f77f9b/scratchpad/rev-2.md")
OUT = Path("/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/briefs/rev-2.md")
JUDGEMENT = Path("/home/usain/gov-os-worktrees/W2-57/governance/project/briefs/JUDGEMENT.md")

VERIFY = """- `gov.__file__`: `/home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py`.
- Full `gov rebuild --json`: exit 0 (lexical, semantic and code-intelligence stores recreated). The keyword warning (row W2-L423's rule): 0 files.
- `gov check --json`: ok; 17 families, 15 GREEN, 2 YELLOW (`core-decision-citations`, history commits citing a decision their tree does not record; `openspec-validate`, nothing to validate), no RED; the same two as at review 1.
- The red check of run 2's tests before the engineer (`red-c/`): 3 failed for the reasons W2-57's README states (the route case: "cases the list routes to the nightly ran in the close"; R1 (a) and (b): `claude_code` "pass" with `cli_version` None), 23 passed (W1-30's r15 file 21 of 21 against the installed rulesync).
- The full parallel run in the close's form (`pytest tests -n auto -p gov_close_serial_only -o tmp_path_retention_policy=failed`, under the lock, 47:16, load 10 at start): 16,430 passed, 31 skipped (the usual 31; none names rulesync), 8 failed: W2-66's known red (DEC-919; it lists `tests/acceptance/W1-38/conftest.py`, `tests/acceptance/W2-57/conftest.py`, `tests/acceptance/serial-only.txt`) and the seven base reds named above (W1-01 x4, W1-47 x2, W1-49 `[not on PATH]`). W2-57's route case and W1-06's approvals case pass.
- The close's serial phase as `gov close` now runs it (the 48 entries the list routes `serial`, given to the plugin, one run, under the lock): 104 passed, 0 failed (11:48; at review 1 the serial phase held every entry: 180 passed in 17:40).
- The 15 entries the list routes `nightly` (W1-46, W1-25, W1-49 live files; W1-50's two freeze cases; W2-58's four launched-session cases; W2-62; W2-54's worker and real-embedder case; W1-19's real-model file with the run 2 revision, on the shared GPU; W1-21's dev-tier file and family check), one run, under the lock, as evidence that they still run: 76 passed, 0 failed (6:52). W1-19's mean hit@5 83.33 (pass line 80); its warm p95 case and memory case passed. 104 + 76 = 180: no case of the list is lost.
- Collection (`pytest tests --collect-only`, one process): `16649/16651 tests collected (2 deselected)`, no error.
- The engineer's runs (sandboxed): W2-57 21 of 21; W1-30 537 passed; W2-66 168 passed, 1 skipped, 1 failed (DEC-919); W1-27 174 passed, 2 failed (the sandbox's read-only code-graph folder); W1-07 223 passed; `tests/unit` 2655 passed, 1 skipped."""

text = SRC.read_text(encoding="utf-8")
text = text.replace("@@HEAD@@", "8f61bda0eb5c").replace("@@VERIFY@@", VERIFY)
text = text.replace("@@JUDGEMENT@@", JUDGEMENT.read_text(encoding="utf-8").rstrip() + "\n")
assert "@@" not in text
OUT.write_text(text, encoding="utf-8")
print(OUT, len(text), text.count("Can an honest agent hit this in ordinary work"))
