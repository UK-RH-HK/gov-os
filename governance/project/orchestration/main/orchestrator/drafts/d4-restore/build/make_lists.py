"""ACT-D4-RESTORE-1 (DEC-1103 (2)): build the three edited opt-in lists from the tree's own lists, by hand-checked line
edits (no regeneration). Each of the ten cases is taken out of its opt-in list; a whole-folder or whole-file entry that
held one is commented out and replaced by its other parts, each still lifted, so nothing else changes.

    python3 make_lists.py <tree> <out-folder> [A|B]     A: the ten (DEC-1103 (2)); B: the seven green today
"""
import ast
import sys
from pathlib import Path

TAG = "DEC-1103 (2)"
tree, out = Path(sys.argv[1]), Path(sys.argv[2])


def functions(path):
    mod = ast.parse(path.read_text(encoding="utf-8"))
    return [n.name for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test")]


def drop(lines, entry, why):
    """Comment out the one line whose entry is exactly `entry`."""
    hits = [i for i, raw in enumerate(lines) if raw.split("#", 1)[0].strip() == entry]
    assert len(hits) == 1, (entry, hits)
    i = hits[0]
    lines[i] = f"# {TAG}: back in the gates ({why}); was: {lines[i]}"
    return i


def split(lines, entry, keep_out, why, parts_why):
    """Comment out a whole-path entry and put its other parts (each still lifted) under it."""
    i = drop(lines, entry, why)
    lines[i + 1:i + 1] = [f"{p}  # {parts_why}" for p in keep_out]


# --- tests/optin-lifted-breadth.txt: the three capped cases (D-4's tier-2 cap) ---
b = (tree / "tests/optin-lifted-breadth.txt").read_text(encoding="utf-8").splitlines()
for entry, k in (
        ("tests/acceptance/W1-06/test_w1_06_install_approvals.py::test_every_entry_outside_the_stack_cites_a_decision_that_names_the_tool", "K18c"),
        ("tests/acceptance/W1-08/test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records", "K8"),
        ("tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime", "K9")):
    drop(b, entry, f"the cap lifted for this case: {k} of the P-SELECT-GRAPH trial reded it")

# --- tests/optin-lifted-guard.txt: four of the seven lifted cases ---
g = (tree / "tests/optin-lifted-guard.txt").read_text(encoding="utf-8").splitlines()
# Variant B (the CTO's option, not decided): only the K2 case that is green today; the three red by the guard's
# switched-off features (DEC-1061 (3a), DEC-953 item 2) stay lifted until their features return.
K2_RED_BY_DESIGN = (
        "tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py::test_the_auditor_writes_only_the_report_path_of_its_own_ticket",
        "tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through",
        "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner")
VARIANT = sys.argv[3] if len(sys.argv) > 3 else "A"
for entry in (
        "tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py::test_the_orchestrator_may_write_anywhere_else_in_the_repository",
        "tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py::test_the_auditor_writes_only_the_report_path_of_its_own_ticket",
        "tests/acceptance/W1-46/test_w1_46_research_installs.py::test_a_research_install_inside_the_experiment_folder_is_let_through",
        "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner"):
    if VARIANT == "B" and entry in K2_RED_BY_DESIGN:
        continue
    drop(g, entry, "un-lifted: K2 of the P-SELECT-GRAPH trial reded it")

# --- tests/optin-lifted.txt: W2-71's premise case (K1) and W1-26's two probe-record cases (K8) ---
l = (tree / "tests/optin-lifted.txt").read_text(encoding="utf-8").splitlines()
w271 = tree / "tests/acceptance/W2-71"
own = "tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py"
k1 = "test_premise_the_list_holds_this_suites_own_files"
parts = [f"tests/acceptance/W2-71/{p.name}" for p in sorted(w271.glob("test_*.py")) if p.name != Path(own).name]
parts += [f"{own}::{n}" for n in functions(tree / own) if n != k1]
split(l, "tests/acceptance/W2-71/", parts, f"un-lifted for {own}::{k1} alone: K1 of the P-SELECT-GRAPH trial reded it; "
      "the suite's other parts stay lifted, one line each below",
      f"row W2-L423's rule on gitleaks findings (DEC-1045; was nightly_only.txt); split from the suite's line, {TAG}")
w126 = "tests/acceptance/W1-26/test_w1_26_probe_records.py"
k8 = ("test_this_repository_s_probe_records_are_well_formed", "test_no_finding_of_the_check_on_this_repository_names_a_probe_record")
split(l, w126, [f"{w126}::{n}" for n in functions(tree / w126) if n not in k8],
      f"un-lifted for ::{k8[0]} and ::{k8[1]} alone: K8 of the P-SELECT-GRAPH trial reded them; the file's other cases "
      "stay lifted, one line each below",
      f"a lifted family (S6 skill version, S9 citations, the probe-record form); split from the file's line, {TAG}")

out.mkdir(parents=True, exist_ok=True)
for name, lines in (("optin-lifted-breadth.txt", b), ("optin-lifted-guard.txt", g), ("optin-lifted.txt", l)):
    (out / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(name, len(lines), "lines")
