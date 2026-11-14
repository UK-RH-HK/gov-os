"""Lead's probe: the deny rules gov launch builds for an engineer in this tree (read only, nothing started)."""
import sys
from pathlib import Path

from gov.launch import launcher

root = Path(sys.argv[1]).resolve()
for rule in launcher.build_settings(root, "engineer", "DAEO-2bdu")["permissions"]["deny"]:
    print(rule)
