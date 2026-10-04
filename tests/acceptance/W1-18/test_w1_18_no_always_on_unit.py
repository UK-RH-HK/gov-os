"""Success 1, second half: "no always-on unit" (DEC-074 Q4; ADR-0002 §3 "Processes").

The daemon runs on demand. With the module delivered, the repository ships no
service, socket or timer unit that would keep Ollama running.
"""

from __future__ import annotations

import w1_18_support as support


def test_the_repository_ships_no_always_on_unit_for_ollama(module):
    units = [path for path in support.unit_files() if support.mentions_ollama(path)]
    shown = ", ".join(str(path.relative_to(support.REPO_ROOT)) for path in units)
    assert not units, f"Ollama runs on demand, with no always-on unit (DEC-074 Q4), but the repository ships: {shown}"
