"""Builder regression tests for docs/plan/tools/validate_w2.py (W2-51). The acceptance tests are in tests/acceptance/W2-51/."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "docs" / "plan" / "tools" / "validate_w2.py"


@pytest.fixture
def v(tmp_path):
    spec = importlib.util.spec_from_file_location("validate_w2", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = tmp_path
    return mod


def _w(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_cit_p_lines_read_w2_49s_form(v, tmp_path):
    """A commented `- id:` with a folded item is a line; a `# unchanged` entry and a non-yaml fence are not."""
    _w(tmp_path, "docs/changes/W2-49-CIT-P.md", "\n".join([
        "```yaml", "  covers:", "  - id: CAP-44.h            # written with the recommended answers",
        "    item: 'Adoption verdict, lite: ADOPTED_HEALTHY from a fresh",
        "      Independent Auditor'", "    wave: W2", "  - id: CAP-43.c            # unchanged, W3", "```",
        "```text", "  - id: CAP-43.d", "    wave: W3", "```", ""]))
    assert v.cit_p_lines() == [("W2-49-CIT-P.md", "CAP-44.h", "W2")]


def test_wbs_id_wins_over_external_ref(v, tmp_path):
    """DEC-730: external-ref is read only when there is no wbs_id; a W1 wbs_id is not a Wave 2 ticket."""
    _w(tmp_path, ".tickets/a.md", "---\nwbs_id: W1-07\nexternal-ref: W2-07\n---\n# a\n")
    _w(tmp_path, ".tickets/b.md", "---\nexternal-ref: W2-15a\n---\n# b\n")
    assert [w2 for w2, _, _ in v.tickets()] == ["W2-15a"]


def test_a_ticket_with_no_frontmatter_is_a_named_failure(v, tmp_path):
    _w(tmp_path, ".tickets/c.md", "# no frontmatter\n")
    with pytest.raises(v.Unreadable, match=r"\.tickets/c\.md"):
        v.tickets()
