#!/usr/bin/env bash
# Fills and launches rev-4 (independent-auditor, Opus high, C2 FULL).
set -u
B=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/briefs
python3 - "$B/rev-4.md" <<'PY'
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
lv = ("- `tests/acceptance/W2-37` + `tests/unit/impact` at `96498443f` (before the skill commit), with the code-graph "
      "tool on PATH (`CODEINTEL_OFF_PATH=` empty): 160 passed, 2 failed (the two skill-routing cases, before the "
      "section). All 21 code-graph cases and the 5 new stated-link cases green.\n"
      "- The skill worker at `68d9a917b`: `test_w2_37_skill_routing.py` `[template]` green, `[claude-copy]` red (the "
      "CTO's copy: known). W1-35: `test_w1_35.py:991` and `test_w1_35.py:845` turn red with `SKILL_UNKNOWN_COMMAND "
      "'impact'` (P-7: `src/gov/check/commands.py` lacks `impact`; named in the CIT-P). Treat these as known; judge "
      "whether the CIT-P states them honestly.\n"
      "- lead_verify at `68d9a917b` is running while you work; the lead adds its result to the record.")
t = t.replace("{SKILL_HEAD}", "68d9a917b").replace("{SKILL_COMMIT}", "68d9a917b").replace("{LEAD_VERIFY}", lv)
open(p, "w", encoding="utf-8").write(t)
PY
grep -nE '\{[A-Z_]+\}' "$B/rev-4.md" && { echo SLOTS LEFT; exit 1; }
cd /home/usain/gov-os-worktrees/W2-37 && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-37 LAUNCH_TICKET=DAEO-6n5k \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh \
  --model claude-opus-5-5 --class C2 independent-auditor high "$B/rev-4.md" 2>&1 | tail -3
