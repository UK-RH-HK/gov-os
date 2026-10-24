"""Builder tests of ``gov.close.evidence`` (W2-66): what a run's JUnit XML states, and the block."""
from __future__ import annotations

from gov.close import evidence

XML = """<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest">
<testcase classname="acceptance.W1-aa.test_aa" name="test_s" file="acceptance/W1-aa/test_aa.py" line="1">
<skipped type="pytest.skip" message="no network">x</skipped></testcase>
<testcase classname="acceptance.W1-aa.test_aa.TestK" name="test_f[1]" file="acceptance/W1-aa/test_aa.py" line="5">
<failure message="AssertionError: the message">E   AssertionError: the message</failure></testcase>
<testcase classname="acceptance.W1-aa.test_aa" name="test_p" file="acceptance/W1-aa/test_aa.py" line="9"/>
</testsuite></testsuites>"""


def test_the_cases_skips_and_failures_are_read_as_project_node_ids(tmp_path):
    (tmp_path / "tests" / "acceptance" / "W1-aa").mkdir(parents=True)
    (tmp_path / "tests" / "acceptance" / "W1-aa" / "test_aa.py").write_text("", encoding="utf-8")
    (tmp_path / "run.xml").write_text(XML, encoding="utf-8")
    found = evidence.read_junit(tmp_path, tmp_path / "run.xml", tmp_path / "tests")
    node = "tests/acceptance/W1-aa/test_aa.py"
    assert found["cases"] == [f"{node}::test_s", f"{node}::TestK::test_f[1]", f"{node}::test_p"]
    assert found["skips"] == [{"test": f"{node}::test_s", "reason": "no network"}]
    assert found["failures"] == [{"test": f"{node}::TestK::test_f[1]", "text": "E   AssertionError: the message"}]


def test_a_missing_file_states_nothing_and_the_block_counts_its_skips(tmp_path):
    assert evidence.read_junit(tmp_path, tmp_path / "none.xml") == {"cases": [], "skips": [], "failures": []}
    plan = {"scope": "scoped", "why_full": [], "base": "b", "head": "h", "tree": "t", "changed": [], "selected": [],
            "left_out": [], "per_test_timeout": 900, "distribution": "load"}
    runs = [{"skips": [{"test": "a", "reason": "r"}], "failures": []},
            {"skips": [{"test": "b", "reason": "s"}], "failures": [{"test": "c", "text": "x"}]}]
    block = evidence.block(plan, runs, ["one.xml", "two.xml"])
    assert block["skip_count"] == 2 and block["failures"] == [{"test": "c", "text": "x"}]
    assert block["junit_xml"] == ["one.xml", "two.xml"] and block["scope"] == "scoped"


def test_the_paths_a_class_is_judged_on_do_not_take_the_evidence_blocks_key():
    from gov.close.command import _judged_by

    judged = _judged_by("research", ["docs/research/W9/EXP-w9.md"], {}, {"state": "ok"})
    assert evidence.KEY not in judged and judged["class_evidence"] == ["docs/research/W9/EXP-w9.md"]
    assert "class_evidence" not in _judged_by("implementation", None, {}, {"state": "ok"})
