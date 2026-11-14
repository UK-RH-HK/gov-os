#!/usr/bin/env bash
# Plant the copies ACT's real after-bytes and a Role: owner ACT commit in a throwaway clone; run the two F2 cases.
set -eu
P=$(mktemp -d /tmp/w2-188-plant.XXXXXX)
trap 'rm -rf "$P"' EXIT
git clone -q --no-hardlinks /home/usain/gov-os-worktrees/W2-188 "$P/c"
cd "$P/c"
git checkout -q 7130a29c0
git checkout -q -b plant
python3 - <<'EOF'
import runpy, hashlib, io, contextlib
ns = {}
src = open('/home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/act-bytes.py').read()
src = src.replace('print("base reproduced', 'NEW = new\n_ = ("base reproduced').replace('print("expected', '_ = ("expected')
exec(compile(src, 'act-bytes', 'exec'), ns)
open('.claude/skills/adopt/SKILL.md', 'w').write(ns['NEW'])
print("planted", hashlib.sha256(open('.claude/skills/adopt/SKILL.md', 'rb').read()).hexdigest())
EOF
git -c user.name=plant -c user.email=plant@example.invalid commit -q -m "ACT-CLAUDE-COPIES-12: regenerate the .claude adopt skill" \
  --trailer "Task: DAEO-zlog" --trailer "Role: owner" -- .claude/skills/adopt/SKILL.md
K='test_f2_the_claude_copy_of_the_skill_equals_the_base_or_the_copies_acts_after_bytes or test_f2_no_commit_of_the_ticket_outside_the_test_designer_or_the_copies_act_touches_claude_or_tests'
run() {
  env HOME=/home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$P/c/src" \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    python3 -m pytest tests/acceptance/W2-188/test_w2_188_copies.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -k "$K" 2>&1 | tail -4
}
echo "== A: real ACT bytes + Role: owner ACT-CLAUDE-COPIES-12 commit (expect 2 passed)"; run
git -c user.name=plant -c user.email=plant@example.invalid commit -q --amend -m "ACT-CLAUDE-COPIES-12: regenerate the .claude adopt skill" \
  --trailer "Task: DAEO-zlog" --trailer "Role: product-spec"
echo "== B: same bytes, Role: product-spec (expect case 2 red)"; run
printf '\nextra\n' >> .claude/skills/adopt/SKILL.md
git -c user.name=plant -c user.email=plant@example.invalid commit -q -m "ACT-CLAUDE-COPIES-12: regenerate again" \
  --trailer "Task: DAEO-zlog" --trailer "Role: owner" -- .claude/skills/adopt/SKILL.md
echo "== C: other bytes (expect case 1 red; case 2 red from B's commit)"; run
