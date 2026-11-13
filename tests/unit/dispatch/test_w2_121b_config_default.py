"""W2-121b S5: the template's default working size is 0.75 GiB per live session (DEC-1149, ACT-P95-1)."""
from gov.resources import config


def test_template_working_size_default_is_0_75_gib_dated_with_dec_1149():
    entry = config.template()["working_size_bytes"]
    assert entry["value"] == 805306368
    assert entry["date"] == "2026-11-12"
    assert "DEC-1149" in entry["source"]
