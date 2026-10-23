"""Add the path map's acceptance_exemptions block (DEC-906) after accepted_history, in a clone. Usage: add_exemption.py <path map>."""
import sys
from pathlib import Path

pm = Path(sys.argv[1])
text = pm.read_text()
assert "acceptance_exemptions:" not in text
marker = "# The data files this project's tests read"
assert marker in text
block = ('# Commits that W1-01\'s MR-3 history case accepts though they touch tests/acceptance/ without the test designer\'s\n'
         '# role (DEC-906): each by its exact sha, with the owner\'s decision. Only the owner\'s commit adds an entry; any other\n'
         '# commit touching tests/acceptance/ without that role stays red.\n'
         'acceptance_exemptions:\n'
         '  - commit: "c9a08678644485a7528bc875164e110881b63d93"\n'
         '    decision: DEC-900\n')
pm.write_text(text.replace(marker, block + marker, 1))
print("acceptance_exemptions added (1 entry)")
