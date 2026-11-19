"""S4 (and F2): gov wait matches no process by name. (The helper watch's cases, `session-watch helper-watch`, retired with
A-2, DEC-1220 (1), TI-2.)"""

from __future__ import annotations

import w2_160_support as support


def test_s4_gov_wait_matches_no_process_by_name():
    assert support.WAIT_SRC.is_dir(), f"{support.WAIT_SRC} does not exist: gov wait is not built"
    sources = sorted(support.WAIT_SRC.rglob("*.py"))
    assert sources, f"{support.WAIT_SRC} holds no Python file"
    hits = [hit for path in sources for hit in support.process_name_hits(path)]
    assert hits == [], f"a process-name match in gov wait: {hits}"
