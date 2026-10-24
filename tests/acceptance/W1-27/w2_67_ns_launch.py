"""Pid 1 of a fresh PID namespace for ``test_w2_67_sweep_namespaces.py`` (W2-67, batch 5).

Run as ``unshare --user --map-current-user --pid --fork --mount-proc --kill-child python3 w2_67_ns_launch.py
<pid> -- <command...>``. It starts the command as the pid asked in its namespace, never by chance: it forks children
that end at once until the next one is that pid, and fails (exit 70) if the namespace is not fresh or the pid has
passed. It reaps every process of the namespace and ends with the command's exit code (128 + the signal when the
command was killed). When it ends, the kernel ends every other process of the namespace.

Its name does not start with ``test_``: a run of ``tests`` never collects it.
"""

import os
import sys


def main():
    want = int(sys.argv[1])
    command = sys.argv[sys.argv.index("--") + 1:]
    if os.getpid() != 1 or want < 2:
        print(f"w2_67_ns_launch: not pid 1 of a fresh namespace (pid {os.getpid()}), or pid {want} asked",
              file=sys.stderr)
        return 70
    while True:
        child = os.fork()
        if child == 0:
            if os.getpid() == want:
                os.execvp(command[0], command)
            os._exit(0)
        if child == want:
            break
        os.waitpid(child, 0)
        if child > want:
            print(f"w2_67_ns_launch: pid {want} has passed (the namespace gave {child})", file=sys.stderr)
            return 70
    while True:
        try:
            pid, status = os.wait()
        except ChildProcessError:
            return 70
        if pid == want:
            code = os.waitstatus_to_exitcode(status)
            return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
