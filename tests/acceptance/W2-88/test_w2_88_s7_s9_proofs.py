"""S7, S8, S9 (success-7, success-8, success-9) and the largest-proof figure of S1: the proof record
``docs/changes/W2-88-evidence.md`` (the implementer's evidence, DEC-996 (3) A; proofs (b) and (c) are W2-88b's, DEC-1150 (1)).

All of these cases read the record as it stands in the repository the suite sits in (red on the base: the engineer writes it
last). The builders' output (``~/gov-os-runs/W2-88/proving-ground/``) is a string in the record: a test never builds there.
The check for a run of the adoption tools against ``~/gov-os-workbench/examin/`` is a function (``examin_runs``) the real
branch and a planted repository are both judged by (and it judges only the branch ``w2/W2-88``, DEC-1155).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

import w2_88_support as W

EVIDENCE = W.REPO_ROOT / W.EVIDENCE_REL
GROUND = "~/gov-os-runs/W2-88/proving-ground/"
HEX = re.compile(r"\b[0-9a-f]{12,40}\b")
FIVE = {"python": r"python", "rust": r"rust", "typescript": r"typescript", "legacy documents": r"legacy",
        "secret in history": r"secret"}
FIELDS = {"commit": HEX, "size": re.compile(r"\bsize\b|\bfiles\b|\bbytes\b", re.I),
          "assessment": re.compile(r"assessment", re.I), "plan's proposals (count and kinds)": re.compile(r"proposal", re.I),
          "per-store figures": re.compile(r"per-store|stores?\b.*\b(lexical|vectors|codegraph)", re.I | re.S),
          "measure": re.compile(r"measure", re.I)}


def sections(text: str) -> dict:
    """Heading -> body for every markdown heading of the record."""
    found, heading, body = {}, None, []
    for line in text.splitlines():
        if re.match(r"#{1,6} ", line):
            if heading is not None:
                found[heading] = "\n".join(body)
            heading, body = line.lstrip("# ").strip(), []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        found[heading] = "\n".join(body)
    return found


def proof(text: str, letter: str) -> str:
    """The body of the section for proof (``letter``): the heading naming it and everything under its sub-headings."""
    lines, out, inside, level = text.splitlines(), [], False, 0
    for line in lines:
        match = re.match(r"(#{1,6}) (.*)", line)
        if match:
            depth = len(match.group(1))
            if re.search(rf"proof\s*\({letter}\)|\({letter}\)\s*(w2-81|synthetic|examin)|^{letter}\b", match.group(2), re.I) and not inside:
                inside, level = True, depth
                continue
            if inside and depth <= level:
                break
        if inside:
            out.append(line)
    return "\n".join(out)


def record() -> str:
    assert EVIDENCE.is_file(), f"{W.EVIDENCE_REL} is not written: the engineer writes the implementer's evidence last"
    return EVIDENCE.read_text(encoding="utf-8")


# ---- S7 -------------------------------------------------------------------------------------------------------

def test_s7_the_record_holds_a_section_for_proof_a_and_one_for_d():
    text = record()
    assert proof(text, "a").strip(), "no section for proof (a)"
    assert proof(text, "d").strip(), "no section for proof (d)"


@pytest.mark.parametrize("field", sorted(FIELDS))
def test_s7_proof_a_names_each_field(field):
    section = proof(record(), "a")
    assert section.strip(), "no section for proof (a)"
    assert FIELDS[field].search(section), f"proof (a) does not hold the field: {field}"


def test_s7_the_plans_proposals_are_counted_and_their_kinds_named():
    section = proof(record(), "a")
    assert re.search(r"\b\d+\b[^\n]{0,40}proposal|proposals?[^\n]{0,40}\b\d+\b", section, re.I), "proof (a) gives no proposal count"
    assert any(kind in section for kind in W.KINDS), f"proof (a) names none of the proposal kinds {W.KINDS}"


def test_s1_the_largest_proof_repositorys_peak_rss_is_recorded_and_under_the_per_session_figure():
    section = proof(record(), "a")
    figures = [int(m.replace(",", "").replace("_", "")) for m in re.findall(r"peak[ _]rss(?:_bytes)?\D{0,40}?(\d[\d,_]{5,})", section, re.I)]
    assert figures, "proof (a) records no peak RSS figure for the largest proof repository"
    assert max(figures) < W.per_session_figure(), f"the largest recorded peak RSS {max(figures)} is not under the per-session figure"
    assert re.search(r"largest", section, re.I), "proof (a) does not say which repository is the largest"


# ---- S8 -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(FIVE))
def test_s8_proof_a_has_a_section_for_each_synthetic_repository_with_its_commit(name):
    text = record()
    start = proof(text, "a")
    assert start.strip(), "no section for proof (a)"
    parts = re.split(r"\n#{2,6} ", "\n" + start)
    mine = [p for p in parts if re.search(FIVE[name], p.split("\n", 1)[0], re.I)]
    assert mine, f"proof (a) has no section for the {name} repository"
    assert HEX.search(mine[0]), f"the {name} section names no commit"


def test_s8_the_builders_output_path_is_under_the_proving_ground_and_none_of_it_is_in_the_repository():
    assert GROUND in record() or GROUND.replace("~", str(Path.home())) in record(), f"the record does not name {GROUND}"
    status = subprocess.run(["git", "-C", str(W.REPO_ROOT), "status", "--porcelain", "--untracked-files=all"],
                            capture_output=True, text=True, timeout=120).stdout
    assert "proving-ground" not in status and "gov-os-runs" not in status, f"git status shows the builders' output:\n{status[:400]}"


# ---- S9 -------------------------------------------------------------------------------------------------------

def examin_runs(root: Path) -> list[str]:
    """Lines of a file the branch changes (against ``w2/integrate``) that name ``gov-os-workbench/examin`` and an adoption
    tool (``gov adopt``, ``--stage``), or a ``gov adopt`` line whose root is that path: a run of the adoption tools there."""
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=120)

    base = git("merge-base", "HEAD", "w2/integrate")
    names = git("diff", "--name-only", f"{base.stdout.strip()}...HEAD").stdout.splitlines() if base.returncode == 0 else []
    found = []
    for name in names:
        path = Path(root) / name
        if not path.is_file() or name.startswith(("tests/acceptance/W2-88/", "docs/changes/W2-88-evidence")):
            continue          # this suite names the path to look for it; the record names it to say no run was made
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "gov-os-workbench/examin" in line and re.search(r"gov adopt|adopt --lite|--stage\s+A\d", line):
                found.append(f"{name}:{number}")
    return found


def _planted(tmp_path, branch, content):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "PATH": "/usr/bin:/bin"}
    ident = ["-c", "user.name=Planted", "-c", "user.email=planted@example.invalid", "-c", "commit.gpgsign=false"]

    def git(*args):
        subprocess.run(["git", "-C", str(repo), *ident, *args], check=True, capture_output=True, env=env, timeout=60)

    git("init", "-q", "-b", "w2/integrate")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", branch)
    (repo / "tool.sh").write_text(content, encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "a script")
    return repo


def test_s9_a_planted_run_of_the_adoption_tools_against_examins_copy_is_found(tmp_path):
    repo = _planted(tmp_path, "w2/W2-88", "gov adopt --lite --stage A0 --root ~/gov-os-workbench/examin\n")
    assert examin_runs(repo) == ["tool.sh:1"]


def test_s9_a_planted_branch_without_such_a_run_has_none(tmp_path):
    repo = _planted(tmp_path, "w2/W2-88", "gov adopt --lite --stage A0 --root /tmp/some-other-clone\n")
    assert examin_runs(repo) == []


def test_s9_this_branch_holds_no_adoption_run_against_examins_copy():
    head = subprocess.run(["git", "-C", str(W.REPO_ROOT), "symbolic-ref", "-q", "--short", "HEAD"], capture_output=True, text=True)
    branch = head.stdout.strip()
    if branch != "w2/W2-88":
        pytest.skip(f"S9's branch check judges only the branch w2/W2-88; this is {branch or 'a detached HEAD'}: not judged here")
    assert examin_runs(W.REPO_ROOT) == []


def test_s9_the_record_has_no_adoption_run_on_examins_copy_and_names_w2_27_for_it():
    section = proof(record(), "d")
    assert section.strip(), "no section for proof (d)"
    assert "W2-27" in section, "proof (d) does not name W2-27, whose run it is"
    for line in section.splitlines():
        assert not (re.search(r"gov adopt|--stage\s+A\d", line) and "examin" in line.lower() and not re.search(r"\bno\b|never|not", line, re.I)), \
            f"proof (d) records an adoption run on EXAMIN's copy: {line[:100]}"
