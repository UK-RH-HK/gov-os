"""W2-121c, RT-8 the launcher states the model and effort it picked from the rubric in the launch log (success line
10, amended at 486467ec5: the stderr line is gone, a successful launch stays quiet as W2-60a and W1-32 require).

Every ``gov launch`` record holds the model and its source, the effort and its source, the ticket's criticality class,
and ``rubric``: the rubric file (``governance/project/criticality.yaml``), or null when the project has none and the
role's default applied; a successful launch writes nothing to its stdout or stderr. W2-184's fixture project: role files
with a ``Launch by criticality`` table and a ``criticality.yaml`` (a C2 ticket: the engineer's C2 entry, Sonnet with
effort high, ``by criticality``); without the file, the role's default line (Sonnet with effort medium, ``role
default``).
"""

from __future__ import annotations

import w2_121c_support as s

RUBRIC = "governance/project/criticality.yaml"


def _quiet(result):
    assert result.run.stdout == "" and result.run.stderr == "", (
        f"a successful launch wrote to its stdout or stderr\n{result.describe()}")


def test_rt8_with_a_rubric_the_record_names_model_effort_both_sources_the_class_and_the_rubric_file(tmp_path):
    kit = s.LaunchKit(tmp_path, rubric=True)
    model, effort = kit.s.TABLES[kit.s.ENGINEER]["C2"]
    result = kit.launch()
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    record = result.record()
    assert "rubric" in record, f"the launch record has no rubric key: {sorted(record)}"
    assert isinstance(record["rubric"], str) and record["rubric"].endswith(RUBRIC), (
        f"the launch record's rubric is {record['rubric']!r}, not the rubric file {RUBRIC}")
    stated = {key: record.get(key) for key in ("model", "effort", "model_source", "effort_source", "criticality")}
    assert stated == {"model": model, "effort": effort, "model_source": "by criticality",
                      "effort_source": "by criticality", "criticality": "C2"}, f"the record states {stated}"
    _quiet(result)


def test_rt8_without_criticality_yaml_the_sources_are_role_default_and_rubric_is_null(tmp_path):
    kit = s.LaunchKit(tmp_path, rubric=False)
    model, effort = kit.s.DEFAULT
    result = kit.launch()
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    record = result.record()
    assert "rubric" in record, f"the launch record has no rubric key: {sorted(record)}"
    assert record["rubric"] is None, f"the launch record's rubric is {record['rubric']!r}, not null"
    stated = {key: record.get(key) for key in ("model", "effort", "model_source", "effort_source")}
    assert stated == {"model": model, "effort": effort, "model_source": "role default",
                      "effort_source": "role default"}, f"the record states {stated}"
    _quiet(result)
