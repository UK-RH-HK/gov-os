import sys
main = "/home/usain/Dynamic-Agentic-Engineering-OS"
sys.path.insert(0, main + "/.claude/hooks"); sys.path.insert(0, main + "/src")
import bash_writes
from gov.guard.decide import _expand_token, _extract_bash_write_targets
T = "tests/acceptance/X/zz.py"
for c in [f"bash <<'EOF'\n# don't overwrite\necho x > {T}\n# it's done\nEOF",
          f"bash <<'EOF'\necho x > {T}\nEOF"]:
    try:
        j = bash_writes.judge(c, main, _extract_bash_write_targets, _expand_token)
        print(repr(c[:40]), "shell:", j.shell, "findings:", j.findings)
    except bash_writes.Unreadable as e:
        print(repr(c[:40]), "Unreadable (refused)")
