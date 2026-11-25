"""The W2-112 case that asserts a time bound and runs alone (fix TT-1; D-03 (b), I-32).

``test_with_both_slots_held_before_any_service_...`` (``test_w2_112_slots.py``) bounds one search at the service's
slot wait plus ``NO_WAIT_S``. It went red in the release suite's parallel run (``python3 -m gov.close.nightly``),
which runs ``gov.close.command``'s test run: that reads ``tests/acceptance/serial-only.txt``, leaves every entry out
of its parallel run and runs each ``serial:`` entry afterwards, alone.

The first case reads this repository's list. The second (a guard) runs the release runner's test run itself on a
planted project with a planted list: small stand-in tests that tell in which worker, and how often, they ran.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import w2_112_support as support

REPO_ROOT = Path(__file__).resolve().parents[3]
LIST_REL = "tests/acceptance/serial-only.txt"
SLOTS_REL = "tests/acceptance/W2-112/test_w2_112_slots.py"
CASE = "test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded"
ENTRY = f"{SLOTS_REL}::{CASE}"
SIBLING = f"{CASE}_and_more"  # a name that merely begins with the listed one: not named by the entry
OTHER = "test_another_case_of_the_file"

# The release runner's own test run, on the project given; what it found, counted and ran is printed.
RUNNER = """
import json, sys
from pathlib import Path
from gov.close import command

root, stated = Path(sys.argv[1]), []
findings, counts = command._run_tests(root, root / "tests", 300, stated=stated, workers=2)
print("\\n" + json.dumps({"findings": findings, "counts": counts, "runs": stated, "gov": command.__file__}))
"""


def _lines():
    """``[(entry, comment)]`` of this repository's list, as its readers take them (the text before `` #``)."""
    found = []
    for line in (REPO_ROOT / LIST_REL).read_text(encoding="utf-8").splitlines():
        entry, _, comment = (" " + line).partition(" #")
        if entry.strip():
            found.append((entry.strip(), comment.strip()))
    return found


def test_the_list_names_the_both_slots_held_case_on_the_serial_route_as_a_latency_case():
    named = [(entry, comment) for entry, comment in _lines() if entry == ENTRY]
    assert len(named) == 1, f"{LIST_REL} holds {len(named)} entries for {ENTRY}: one is expected"
    parts = [part.strip() for part in named[0][1].split(":", 2)]
    assert len(parts) == 3 and parts[:2] == ["serial", "latency"] and len(parts[2].split()) >= 3, \
        f"the entry's comment is to read `serial: latency: <reason in words>`: {named[0][1]!r}"
    assert f"\ndef {CASE}(" in (REPO_ROOT / SLOTS_REL).read_text(encoding="utf-8"), \
        f"{SLOTS_REL} defines no {CASE}"


def _stand_in(name: str, told: Path) -> str:
    """A planted test that adds one line to ``told/<name>``: its xdist worker (empty when none) and the time."""
    return (f"def {name}():\n"
            f"    with open({str(told / name)!r}, 'a', encoding='utf-8') as out:\n"
            "        out.write(f\"{os.environ.get('PYTEST_XDIST_WORKER', '')} {time.monotonic_ns()}\\n\")\n\n\n")


def test_the_release_runner_leaves_the_listed_case_out_of_its_parallel_run_and_runs_it_once_alone(tmp_path):
    """Guard: green on the base. The planted entry is the line's own node id."""
    root, told = tmp_path / "project", tmp_path / "told"
    (root / SLOTS_REL).parent.mkdir(parents=True)
    told.mkdir()
    (root / SLOTS_REL).write_text(
        "import os\nimport time\n\n\n" + "".join(_stand_in(name, told) for name in (CASE, SIBLING, OTHER)),
        encoding="utf-8")
    (root / LIST_REL).write_text(f"# planted\n{ENTRY}  # serial: latency: planted by this case\n", encoding="utf-8")
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "GOV_CLOSE_"))}
    env["PYTHONPATH"] = str(support.gov_src())

    done = subprocess.run([sys.executable, "-c", RUNNER, str(root)], env=env, cwd=str(tmp_path),
                          capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)

    assert done.returncode == 0, f"the release runner's test run failed:\n{done.stdout[-2000:]}\n{done.stderr[-3000:]}"
    out = json.loads(done.stdout.strip().splitlines()[-1])
    assert Path(out["gov"]).is_relative_to(Path(support.gov_src())), f"another gov ran: {out['gov']}"
    assert out["findings"] == [], out["findings"]
    ran = {name: [line.split(" ") for line in (told / name).read_text(encoding="utf-8").splitlines()]
           if (told / name).exists() else [] for name in (CASE, SIBLING, OTHER)}
    assert {name: len(runs) for name, runs in ran.items()} == {CASE: 1, SIBLING: 1, OTHER: 1}, \
        f"each planted case is to run exactly once: {ran}"
    worker, at = ran[CASE][0]
    assert worker == "", f"the listed case ran in the worker {worker!r} of the parallel run"
    for name in (SIBLING, OTHER):
        assert ran[name][0][0], f"the unlisted case {name} did not run in a worker of the parallel run: {ran[name]}"
        assert int(at) > int(ran[name][0][1]), f"the listed case did not run after the parallel run: {ran}"
    forms = {run["form"]: run for run in out["runs"]}
    assert list(forms) == ["parallel", "serial-afterwards"], out["runs"]
    assert forms["parallel"]["passed"] == 2, out["runs"]
    assert forms["serial-afterwards"]["cases"] == [ENTRY] and forms["serial-afterwards"]["passed"] == 1, out["runs"]
