import subprocess, sys
from gov.accept import runner
for label, rev, path in (("W2-90b at its head", "w2/W2-90b", "tests/acceptance/W2-90b/README.md"),
                         ("W2-81 at its head", "w2/W2-81", "tests/acceptance/W2-81/README.md")):
    text = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, check=True).stdout
    try:
        m = runner.parse_map(text)
        print(label, "-> parse_map reads", len(m), "lines:", list(m)[:14])
    except runner.Unlisted as e:
        print(label, "-> Unlisted: README line", e.args[0], repr(runner._masked(e.args[1]))[:160])
    except runner.Unreadable:
        print(label, "-> Unreadable (a row names no KPI line it can read)")
