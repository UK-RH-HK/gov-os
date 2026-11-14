#!/usr/bin/env bash
# Trace the scoped run's 6 reds: each alone on the head (f0cb5284d) and on its parent (80b19dc16, without E's line),
# in clean copies outside the repository, through the heavy slot.
set -u
R=/tmp/w2-182-trace
rm -rf "$R"; mkdir -p "$R/home" "$R/tmp"
OUT=/home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/log/trace
mkdir -p "$OUT"
IDS=(
 "tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py::TestABashCallAfterAChangeOfDirectory::test_an_ordinary_allowed_call_is_not_blocked"
 "tests/acceptance/W1-38/test_w1_38_rulesync.py::TestHookStubs::test_hook_stubs_exist"
 "tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition"
 "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition"
 "tests/unit/gitenv/test_program_env.py::test_this_repository_s_two_hooks_sources_agree"
 "tests/acceptance/W2-05/test_w2_05_hooks_source.py::test_adapter_portability_is_green_over_this_repository_s_two_hooks_sources"
)
for c in f0cb5284d 80b19dc16; do
  mkdir -p "$R/$c"
  git -C /home/usain/gov-os-worktrees/W2-182 archive "$c" | tar -x -C "$R/$c"
  # the copy is a git repository of its own (some cases read git), one commit
  ( cd "$R/$c" && git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm copy )
  cd "$R/$c" || exit 2
  env TMPDIR="$R/tmp" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$R/$c/src" \
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE "${IDS[@]}" > "$OUT/$c.txt" 2>&1
  echo "$c exit $?"; tail -12 "$OUT/$c.txt" | grep -E '^(FAILED|ERROR)|passed|failed'
done
