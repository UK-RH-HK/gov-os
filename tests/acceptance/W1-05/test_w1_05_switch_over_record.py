"""W1-05 — the interim diff check is retired on record, and the switch-over waits for its dependencies.

KPI success 2: "The interim operator diff check is retired and recorded as such".
KPI failure 2: "The switch-over happens before W1-02..04 acceptance tests pass".

The record is ``governance/project/bootstrap.md``, the file W1-01 wrote the
procedure in and the only record file in W1-05's ``allowed_paths``.
"""

from __future__ import annotations

import re
import subprocess
import sys

import w1_05_support as support

ISO_DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def _blocks(text):
    """Paragraphs, table rows and list items: runs of lines separated by blank lines, and each line."""
    blocks = [block for block in re.split(r"\n\s*\n", text) if block.strip()]
    return blocks + [line for line in text.splitlines() if line.strip()]


def test_the_operator_diff_check_is_recorded_as_retired():
    path = support.REPO_ROOT / support.BOOTSTRAP_REL
    assert path.is_file(), f"{support.BOOTSTRAP_REL} does not exist"
    text = path.read_text(encoding="utf-8")
    hits = [
        block for block in _blocks(text)
        if re.search(r"\bdiff\b", block, re.IGNORECASE) and re.search(r"\bretire", block, re.IGNORECASE)
    ]
    assert hits, (
        f"{support.BOOTSTRAP_REL} has no paragraph, list item or table row that says the operator diff check "
        "is retired (the words `diff` and `retired` together)"
    )
    dated = [block for block in hits if ISO_DATE.search(block)]
    assert dated, (
        f"{support.BOOTSTRAP_REL} says the diff check is retired but gives no date (YYYY-MM-DD) with it: "
        f"{hits[0].strip()[:200]!r}"
    )
    assert any("W1-05" in block or "DAEO-m7u4" in block for block in dated), (
        f"{support.BOOTSTRAP_REL} does not tie the retirement to the switch-over ticket (W1-05 or DAEO-m7u4)"
    )


def test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over(switched_over):
    """With the hooks wired, the acceptance tests of W1-02, W1-03 and W1-04 exist and pass.

    This runs the three suites in a child pytest process, so it takes as long as they do.
    """
    directories = []
    for wbs_id in support.DEPENDENCIES:
        directory = support.REPO_ROOT / support.ACCEPTANCE_REL / wbs_id
        assert directory.is_dir() and list(directory.glob("test_*.py")), (
            f"the hooks are wired, but {support.ACCEPTANCE_REL}/{wbs_id}/ holds no acceptance tests"
        )
        directories.append(str(directory))
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *directories, "-q", "-x", "-p", "no:cacheprovider"],
        cwd=str(support.REPO_ROOT), capture_output=True, text=True, timeout=1800, check=False,
    )
    tail = "\n".join(proc.stdout.strip().splitlines()[-15:])
    assert proc.returncode == 0, (
        "the hooks are wired, but the acceptance tests of W1-02, W1-03 and W1-04 do not all pass:\n" + tail
    )
