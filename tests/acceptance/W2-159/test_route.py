"""The hyphenated route (P-W2-159-1 (a)): ``gov session-watch`` is a known command whose module is the folder
``src/gov/session_watch/``. One case: ``gov session-watch --help`` exits 0 (today: ``invalid choice: 'session-watch'``).
Not a KPI line of its own; the route is what lets every other case reach the command.
"""

import os
import subprocess
import sys

import w2_159_support as support


def test_route_gov_session_watch_help_exits_0(tmp_path):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GOV_"))}
    env.update(HOME=str(tmp_path), PYTHONPATH=str(support.SRC), PYTHONDONTWRITEBYTECODE="1")
    done = subprocess.run([sys.executable, "-B", "-m", "gov.cli.main", "session-watch", "--help"], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, f"exit {done.returncode}\n--- stdout ---\n{done.stdout}\n--- stderr ---\n{done.stderr}"
    assert done.stdout.strip(), "the help text is printed"
