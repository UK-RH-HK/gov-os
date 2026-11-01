"""Run 6: run argv[1:] in the environment a close's test run now gets (DEC-970, package I (b)).

gov.util.gitenv.runner_env (this worktree's src, from PYTHONPATH): no GIT_* variable of the caller, the system
configuration unread, GIT_CONFIG_GLOBAL a file made for the run with only the person's user.name, user.email and
init.defaultBranch. Everything else of this process's environment is kept. Exits with the command's code.
"""
import os
import subprocess
import sys

from gov.util.gitenv import runner_env

base = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
with runner_env(base=base) as env:
    code = subprocess.run(sys.argv[1:], env=env).returncode
sys.exit(code)
