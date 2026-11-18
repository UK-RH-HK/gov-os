"""The pin dispatch (W2-18): ``gov`` started in a folder of a repository with a pin re-runs the pin's gov.

``<common>/gov/bin/gov`` (``<common>`` the git common dir, found by ``locate`` without a subprocess) is run with the
same arguments and without ``PYTHONPATH``, unless ``GOV_PIN=off`` is set or the running gov is already that
environment's (``sys.prefix`` is the environment the link names). It never loops: the re-run carries
``GOV_PIN_DISPATCHED`` naming the link, and a gov that finds it naming the same link runs itself.
"""

from __future__ import annotations

import os
import sys

from gov.install.locate import common_dir

MARK = "GOV_PIN_DISPATCHED"


def target(cwd: str, environ: dict, prefix: str) -> tuple[str, dict] | None:
    """``(program, environment)`` to re-run, or ``None`` to run the gov that is running."""
    if environ.get("GOV_PIN") == "off":
        return None
    common = common_dir(cwd)
    if common is None:
        return None
    link = os.path.join(str(common), "gov", "bin", "gov")
    if not os.path.exists(link):  # absent, or a link whose environment is gone
        return None
    environment = os.path.dirname(os.path.dirname(os.path.realpath(link)))
    if os.path.realpath(prefix) == environment or environ.get(MARK) == link:
        return None
    child = {key: value for key, value in environ.items() if key != "PYTHONPATH"}
    child[MARK] = link
    return link, child


def run(argv: list[str]) -> None:
    """Re-run the pin's gov with ``argv`` (this process is replaced), or return to run this gov."""
    try:
        cwd = os.getcwd()
    except OSError:
        return
    found = target(cwd, dict(os.environ), sys.prefix)
    if found is None:
        return
    program, environ = found
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        os.execve(program, [program, *argv], environ)
    except OSError as exc:  # never another release in its place: the pin is what this repository runs
        print(f"gov: the pinned gov {program} cannot run ({exc}); run `gov install <version>` again, or set "
              "GOV_PIN=off to run this gov", file=sys.stderr)
        raise SystemExit(1) from None
