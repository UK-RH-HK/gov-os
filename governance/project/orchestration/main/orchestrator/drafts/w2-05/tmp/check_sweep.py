import sys
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-05/tests/acceptance/W2-05")
sys.dont_write_bytecode = True
import w2_05_support as s
text = (s.REPO_ROOT / s.SWEEP_REL).read_text(encoding="utf-8")
starting = s.files_that_start_git()
unnamed = [r for r in starting if not s.names_file(text, r)]
print("REPO_ROOT", s.REPO_ROOT, "starting", len(starting), "unnamed", unnamed)
