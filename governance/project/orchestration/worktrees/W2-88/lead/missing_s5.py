import sys, inspect
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-88/src")
from pathlib import Path
from gov.accept import runner
text = Path("/home/usain/gov-os-worktrees/W2-88/tests/acceptance/W2-88/README.md").read_text()
fn = [n for n, f in vars(runner).items() if inspect.isfunction(f) and "mapping: dict[str, list[str]] = {}" in inspect.getsource(f)][0]
mapping = getattr(runner, fn)(text)
for item in mapping.get("success-5", []):
    print("item:", item, "names_a_test:", runner.names_a_test(item))
