"""W2-121c, RT-8 the launcher states the model and effort it picked from the rubric (success line 10).

Before the session starts ``gov launch`` prints one line naming the model and its source, the effort and its source,
the ticket's criticality class and the rubric file (``governance/project/criticality.yaml``), or "no rubric: the role's
default" when the project has none; the launch record holds the same, with the key ``rubric`` (the file, or null).
W2-184's fixture project: role files with a ``Launch by criticality`` table and a ``criticality.yaml`` (a C2 ticket:
the engineer's C2 entry, Sonnet with effort high, "by criticality"); without the file, the role's default line (Sonnet
with effort medium, "role default").
"""

from __future__ import annotations

import w2_121c_support as s

RUBRIC = "governance/project/criticality.yaml"


def _rubric_lines(result) -> list[str]:
    """The stderr lines that name the rubric file or say there is no rubric."""
    return [line for line in result.run.stderr.splitlines() if RUBRIC in line or "rubric" in line.lower()]


def test_rt8_the_launch_line_names_model_effort_their_sources_the_class_and_the_rubric_file(tmp_path):
    kit = s.LaunchKit(tmp_path, rubric=True)
    model, effort = kit.s.TABLES[kit.s.ENGINEER]["C2"]
    result = kit.launch()
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    lines = _rubric_lines(result)
    assert len(lines) == 1, f"not one stderr line naming the rubric: {lines}\n{result.describe()}"
    line = lines[0]
    for word in (model, effort, "by criticality", "C2", RUBRIC):
        assert word in line, f"the launch line does not name {word!r}: {line!r}"
    record = result.record()
    assert record.get("rubric", "<missing>") is not None and str(record.get("rubric")).endswith(RUBRIC), (
        f"the launch record's rubric is {record.get('rubric', '<missing>')!r}, not the rubric file")
    agreed = {key: record.get(key) for key in ("model", "effort", "model_source", "effort_source", "criticality")}
    assert agreed == {"model": model, "effort": effort, "model_source": "by criticality",
                      "effort_source": "by criticality", "criticality": "C2"}, f"the record disagrees: {agreed}"


def test_rt8_without_criticality_yaml_the_line_says_no_rubric_and_the_record_holds_null(tmp_path):
    kit = s.LaunchKit(tmp_path, rubric=False)
    model, effort = kit.s.DEFAULT
    result = kit.launch()
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    lines = _rubric_lines(result)
    assert len(lines) == 1, f"not one stderr line naming the rubric: {lines}\n{result.describe()}"
    line = lines[0]
    assert "no rubric: the role's default" in line.lower(), f"the launch line: {line!r}"
    assert model in line and effort in line, f"the launch line does not name model {model} and effort {effort}: {line!r}"
    record = result.record()
    assert "rubric" in record and record["rubric"] is None, (
        f"the launch record's rubric is {record.get('rubric', '<missing>')!r}, not null")
    assert (record.get("model"), record.get("effort")) == (model, effort), record
