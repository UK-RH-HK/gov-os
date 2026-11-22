"""W2-184, KPI success 3 -- the launch record holds the RUBRIC-2 keys of interface section 8.

KPI success-3 [DEC-1120 (3)]: the launch record also holds ``tier``, ``criticality``, ``model_source`` (role default, by
criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a
planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them
null.

The nine keys of section 8 are always present: ``tier``, ``criticality``, ``model_source``, ``effort_source``, ``trial``,
``promotion``, ``effort_reason``, ``owner_named``, ``review_round``. ``tier`` is the family word of ``model``.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG = s.ENGINEER
TK = "DAEO-rc01"


def test_s3_a_launch_by_criticality_records_its_fields(project, launch):
    tk = s.ticket(project, ENG, "C1", tk=TK)
    s.assert_session(launch(ENG, tk), s.SONNET, "xhigh", criticality="C1", model_source="by criticality",
                     effort_source="by criticality")


def test_s3_a_launch_with_a_trial_records_the_trial_id(project, launch):
    tk = s.ticket(project, ENG, "C2", tk=TK)
    s.plant_trial(project, "trial-7", tk=tk)
    s.assert_session(launch(ENG, tk, trial="trial-7"), s.TRIAL_MODEL, "high", criticality="C2", model_source="trial",
                     effort_source="trial", trial="trial-7")


def test_s3_a_promoted_launch_records_the_promotion_reason_and_the_record(project, launch):
    tk = s.ticket(project, ENG, "C2", tk=TK)
    # Rewrite-Reason: DEC-1225: a promotion launched on Opus. R2: it keeps its record and the table's effort and
    # launches the table's model (the engineer's C2 entry: Sonnet); the model's source word is left open.
    record = s.promote_two_failed(project, tk)
    s.assert_session(launch(ENG, tk), s.TABLES[ENG]["C2"][0], "high", criticality="C2", model_source=s.ANY,
                     effort_source="by criticality",
                     promotion={"reason": "two failed reviews", "record": record})


def test_s3_a_plain_launch_records_the_keys_null(project, launch):
    """A role with only a ``Launch default`` line, no criticality file, no trial, no promotion."""
    s.write_role(project, ENG, table=None)
    s.drop_criticality(project)
    tk = s.ticket(project, ENG, "C2", tk=TK)
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality=None, model_source="role default",
                     effort_source="role default")


def test_s3_a_default_only_launch_with_a_criticality_file_records_the_criticality_and_the_rest_null(project, launch):
    s.write_role(project, ENG, table=None)
    tk = s.ticket(project, ENG, "C3", tk=TK)
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality="C3", model_source="role default",
                     effort_source="role default")


@pytest.mark.parametrize("model", [s.OPUS, s.SONNET, s.HAIKU5, s.HAIKU_DATED])
def test_s3_the_tier_is_the_family_word_of_the_model(project, launch, model):
    """``claude-haiku-4-5-20251001`` is ``haiku``, as ``claude-haiku-5-5`` is."""
    s.write_role(project, ENG, table=None, default=(model, "medium"))
    tk = s.ticket(project, ENG, "C2", tk=TK)
    record = launch(ENG, tk).record()
    assert record.get("tier") == model.split("-")[1], f"tier of {model}: {record.get('tier', s.MISSING)!r}"


@pytest.mark.parametrize("kind", ["plain", "by-criticality", "trial", "promotion", "after"])
def test_s3_every_record_holds_all_nine_keys(project, launch, kind):
    tk = s.ticket(project, ENG, "C2", tk=TK)
    if kind == "plain":
        s.write_role(project, ENG, table=None)
        s.drop_criticality(project)
    if kind == "trial":
        s.plant_trial(project, "trial-7", tk=tk)
    if kind == "promotion":
        s.promote_two_failed(project, tk)
    result = launch(ENG, tk, *(("--effort", "xhigh") if kind == "after" else ()),
                    **({"trial": "trial-7"} if kind == "trial" else {}))
    s.b.assert_launched(result)
    missing = [key for key in s.NEW_KEYS if key not in result.record()]
    assert not missing, f"the launch record lacks {missing}: {sorted(result.record())}"


# W2-60a's reviewed core: the record's base fields are kept, with their values
BASE_KEYS = ("record", "format", "session_id", "resumes", "started_at", "root", "role", "ticket", "ticket_class",
             "model", "model_source", "effort", "effort_source", "subagent_model", "compaction_threshold",
             "role_text", "appended_sha256", "template", "skills", "kept_out", "cli")


def test_s3_green_on_base_the_record_keeps_its_base_fields(project, launch):
    """Compatibility: nothing of W2-60a's record changes; the new keys are added."""
    tk = s.ticket(project, ENG, "C2", tk=TK)
    result = launch(ENG, tk)
    s.b.assert_launched(result)
    record = result.record()
    assert [key for key in BASE_KEYS if key not in record] == [], sorted(record)
    assert record["record"] == "gov-launch" and record["role"] == ENG and record["ticket"] == tk
    assert record["ticket_class"] == "implementation" and record["compaction_threshold"] == "none"
    assert record["resumes"] is None and record["root"] == str(project.resolve())
