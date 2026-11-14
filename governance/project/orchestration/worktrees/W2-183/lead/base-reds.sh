cd /home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/base-wt
env TMPDIR=/tmp/w2-183-lead PATH=/home/usain/.local/bin:$PATH PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-183/.gov-runtime/scratch/base-wt/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
 "tests/acceptance/W2-128/test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56" \
 "tests/acceptance/W2-54/test_w2_54_dropped_order.py::test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing" \
 "tests/acceptance/W2-152/test_w2_152_facts.py::test_s10_gov_accept_w2_128_still_passes" \
 "tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition" \
 "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition"
