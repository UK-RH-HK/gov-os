"""Round 15, piece 6 (DEC-616, DEC-620): this repository's rulesync sources equal the kernel template's.

Measured before the round with the portability check's own program, in this repository:
``.rulesync/subagents/orchestrator.md`` differs from ``template/governance/kernel/roles/orchestrator.md``
(``SOURCE_DIFFERS``) and ``.rulesync/skills/orchestration/SKILL.md`` does not exist (``SOURCE_MISSING``).

No case held this before the round: W1-38's suite builds its projects from ``template/.rulesync/`` and never
reads this repository's own ``.rulesync/``. The one case here does: it runs the program the kernel template
declares for ``adapter-portability``, in this repository, and reads its findings. The program only reads. The
case points it at a rulesync that does not exist, so that it compares the sources with the kernel and stops
there: the files rulesync generates, and the version of rulesync installed, are W1-38's cases and not this
one's.
"""

from __future__ import annotations

import json
import subprocess

import w1_30_r15_support as r15

support = r15.support
CHECK = "adapter-portability"
SOURCE_CODES = ("SOURCE_DIFFERS", "SOURCE_MISSING")


def test_this_repository_s_rulesync_sources_equal_the_kernel_template_s(sandbox):
    """Red before the round: one ``SOURCE_DIFFERS`` (the orchestrator's subagent) and one ``SOURCE_MISSING``
    (the orchestration skill)."""
    env = support.sandbox_env(sandbox)
    env["RULESYNC_BIN"] = str(sandbox.bin / "no-rulesync-here")
    done = subprocess.run(["sh", "-c", r15.kernel_declaration(CHECK)["command"]], cwd=str(r15.REPO_ROOT), env=env,
                          capture_output=True, text=True, timeout=r15.cli_support.COMMAND_TIMEOUT_S,
                          stdin=subprocess.DEVNULL)
    assert "Traceback" not in done.stderr and done.stdout.strip(), \
        f"the {CHECK} program printed no result (exit code {done.returncode})\n{done.stderr}"
    result = json.loads(done.stdout)
    compared = (result.get("compared") or {}).get("kernel_files")
    assert isinstance(compared, int) and compared > 0, \
        f"the {CHECK} program compared no file of the kernel with a rulesync source: {result.get('compared')}"
    found = sorted((finding.get("code"), finding.get("file")) for finding in result.get("findings", [])
                   if finding.get("code") in SOURCE_CODES)
    assert not found, f"this repository's rulesync sources are not those of the kernel template: {found}"
