"""pytest plugin (-p lead_plant8): batch 8's nested runs get the shim folder first on their PYTHONPATH."""
import os
import subprocess

SHIM = "/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/lead/plant8/shim"
_run = subprocess.run


def _planted(*args, **kwargs):
    env = kwargs.get("env")
    if env and "W2_67_CODEGRAPH_SEEN" in env:
        env = dict(env)
        env["PYTHONPATH"] = SHIM + os.pathsep + env.get("PYTHONPATH", "")
        env["LEAD_PLANT8_MARKER"] = os.environ.get("LEAD_PLANT8_MARKER", "")
        kwargs["env"] = env
    return _run(*args, **kwargs)


subprocess.run = _planted
