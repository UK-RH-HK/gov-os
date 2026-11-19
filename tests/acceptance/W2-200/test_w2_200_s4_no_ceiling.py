"""S4: no size ceiling anywhere in the close.

``s4_world``: a ticket of about 300,000 characters cites DEC-130, whose span of the register is over 1,200,000
characters; no ``budgets.close_context_tokens`` anywhere. The same project with ``budgets.close_context_tokens: "abc"``
in ``governance/project/facts.yaml``. Both closes pass. The code under test names none of the retired codes or the
setting.
"""

from __future__ import annotations

import w2_200_support as s

WORDS = ("CONTEXT_OVER_CEILING", "CONTEXT_FAILED", "CONTEXT_SETTING_INVALID", "close_context_tokens")


def test_s4_a_decision_over_a_million_characters_and_a_long_ticket_close_and_are_recorded(s4_world):
    span = s.spans(s.S4_REGISTER)["DEC-130"]
    assert len(span) > 1_200_000 and len(s.S4_TICKET_BODY) > 300_000, "the fixture is wrong: its texts are short"
    s.closed(s4_world.big_run)
    record = s4_world.big.record()
    assert record.get("decisions_applied") == ["DEC-130"], f"decisions_applied: {record.get('decisions_applied')!r}"
    assert s.input_hashes(record).get("DEC-130") in s.span_hashes(s.S4_REGISTER, ["DEC-130"])["DEC-130"], \
        f"DEC-130's hash is not that of its span: {record.get('inputs')!r}"


def test_s4_an_invalid_close_context_tokens_setting_is_ignored(s4_world):
    s.closed(s4_world.invalid_run)
    assert s4_world.invalid.record().get("decisions_applied") == ["DEC-130"]


def test_s4_no_close_output_names_a_retired_code(s4_world):
    for run in (s4_world.big_run, s4_world.invalid_run):
        found = [code for code in s.RETIRED_CODES if code in run.both]
        assert not found, f"the close's output names {found}\n{run.describe()}"


def test_s4_the_code_names_no_ceiling_code_and_no_setting(tmp_path, env):
    """``grep -rn`` of the four words over the ``src`` folder of the code under test (bytecode left aside)."""
    src = s.package_dir(env, tmp_path).parent
    found = []
    for path in s.source_files(src):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for word in WORDS:
                if word in line:
                    found.append(f"{path.relative_to(src)}:{number}: {word}")
    assert not found, f"{len(found)} lines of src name a retired word:\n" + "\n".join(found[:40])
