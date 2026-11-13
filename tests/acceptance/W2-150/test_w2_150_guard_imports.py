"""W2-150 S4: the guard's hot path pulls no new module (DAEO-ijf5; DEC-1052 basis (3)).

In a fresh subprocess, ``import gov.guard.decide`` may load only ``gov`` itself, modules of ``gov.guard`` and
``gov.util``, and the standard library: ``sys.modules`` is compared before and after the import.
"""

from __future__ import annotations

import textwrap

from w2_150_run import run_json


def test_s4_import_of_guard_decide_loads_only_guard_util_and_stdlib():
    got = run_json(textwrap.dedent("""
        import json, sys
        before = set(sys.modules)
        import gov.guard.decide
        new = sorted(set(sys.modules) - before)
        def allowed(name):
            if name == "gov" or name.startswith(("gov.guard.", "gov.util.")) or name in ("gov.guard", "gov.util"):
                return True
            return name.split(".")[0] in sys.stdlib_module_names
        print(json.dumps({"new": new, "outside": [n for n in new if not allowed(n)]}))
    """))
    assert "gov.guard.decide" in got["new"]
    assert not got["outside"], (
        "import gov.guard.decide loads modules outside gov.guard, gov.util and the standard library: "
        f"{got['outside']}")
