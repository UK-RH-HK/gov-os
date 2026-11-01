#!/bin/bash
# Re-run the four W2-59 failures alone, on the tree given as $1 (its own src), writing nothing in tests/acceptance.
T="$1"
OUT="$2"
cd "$T" || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-95
export PYTHONDONTWRITEBYTECODE=1
PYTHONPATH="$T/src" python3 -B -c "import gov; print(gov.__file__)" > "$OUT" 2>&1
PYTHONPATH="$T/src" timeout 500 python3 -B -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  "tests/acceptance/W2-59/test_w2_59_hook_lines.py::test_the_line_s_program_imports_the_pin_s_package_not_the_project_s_src" \
  "tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py::test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path" \
  "tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py::test_a_command_that_sets_pythonpath_itself_is_let_through_and_runs_the_tree_s_code" \
  >> "$OUT" 2>&1
echo "pytest exit=$?" >> "$OUT"
