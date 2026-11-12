"""The failure line: any change to a skill beyond the two named lines, or W2-138's step-5 line lost (README).

Each skill is compared, whole, with the reference commit's text (``w2_142_support.reference``):
- the retrieval skill with its step 7 paragraph (from the line starting ``7.`` to the blank line after it) taken
  out and its ``version:`` line set aside must equal the reference with its ``version:`` line set aside;
- the discovery skill with line 55 cut back to the reference's text and its ``version:`` line set aside must equal
  the reference with its ``version:`` line set aside (S2 bumps its version, DEC-1097 (8)).
Revised for W2-11 (DEC-866, DEC-981, DEC-1137): a ``metadata:`` block holding only ``version``, equal to the version
line, is set aside too; nothing else is.
"""

from __future__ import annotations

import re

import pytest

import w2_142_support as support

STEP_7 = re.compile(r"^7\.[^\n]*\n(?:[^\n]+\n)*\n", re.M)


# Revised for W2-11 (Rewrite-Reason: DEC-866, DEC-981, DEC-1137; DEC-1112 (3) P-b): every kernel skill carries
# ``metadata.version`` equal to ``version``, the one carried repeat. A front-matter ``metadata:`` block holding only
# ``version`` (the next line not indented) equal to the version line is set aside; a block holding anything else, or
# another version, stays and fails the comparison.
METADATA_VERSION = re.compile(r'^metadata:[ \t]*\n[ \t]+version:[ \t]*"?([^"\n]*?)"?[ \t]*\n(?![ \t])', re.M)


def _metadata_version_set_aside(text: str) -> str:
    end = text.find("\n---", 3)
    if not text.startswith("---") or end < 0:
        return text
    front, rest = text[:end + 1], text[end + 1:]
    found = METADATA_VERSION.findall(front)
    if not found:
        return text
    assert len(found) == 1, "premise: at most one metadata block"
    version = support.VERSION_LINE.search(front)
    assert version and version.group(0) == f'version: "{found[0]}"', (
        f"metadata.version {found[0]!r} is not the skill's version line {version.group(0) if version else None!r}")
    return METADATA_VERSION.sub("", front, count=1) + rest


def _versions_set_aside(text: str) -> str:
    text = _metadata_version_set_aside(text)
    assert len(support.VERSION_LINE.findall(text)) == 1, "premise: exactly one quoted version line"
    return support.VERSION_LINE.sub('version: "<set aside>"', text)


def test_f1_the_retrieval_skill_is_the_reference_but_for_step_7_and_its_version():
    before = support.reference(support.RETRIEVAL)
    now = STEP_7.sub("", support.current(support.RETRIEVAL), count=1)
    assert _versions_set_aside(now) == _versions_set_aside(before), (
        "the retrieval skill changed outside step 7 and its version line")


def test_f1_the_discovery_skill_is_the_reference_but_for_line_55_s_added_sentence_and_its_version():
    before = support.reference(support.DISCOVERY)
    lines = support.current(support.DISCOVERY).split("\n")
    held = [i for i, line in enumerate(lines) if line.startswith(support.LINE_55)]
    assert len(held) == 1, f"line 55's text no longer starts exactly one line ({len(held)})"
    lines[held[0]] = support.LINE_55
    assert _versions_set_aside("\n".join(lines)) == _versions_set_aside(before), (
        "the discovery skill changed outside line 55's added sentence and its version line")


PLANTED_REFERENCE = '---\nname: planted\nversion: "1.0.0"\ndescription: A planted skill.\n---\n\n# Planted\n'
PLANTED_METADATA = {  # W2-11's revision: what the set-aside lets through, and what it still fails
    "metadata.version equal to version": ('metadata:\n  version: "1.1.0"\n', True),
    "metadata.version unquoted, equal to version": ("metadata:\n  version: 1.1.0\n", True),
    "metadata.version unlike version": ('metadata:\n  version: "1.0.0"\n', False),
    "metadata holding another key": ('metadata:\n  version: "1.1.0"\n  allowed-tools: Bash(*)\n', False),
}


@pytest.mark.parametrize("kind", sorted(PLANTED_METADATA))
def test_f1_the_check_sets_aside_only_a_metadata_block_holding_the_version(kind):
    block, passes = PLANTED_METADATA[kind]
    planted = PLANTED_REFERENCE.replace('version: "1.0.0"\n', 'version: "1.1.0"\n' + block)
    try:
        same = _versions_set_aside(planted) == _versions_set_aside(PLANTED_REFERENCE)
    except AssertionError:
        same = False
    assert same == passes, f"the check {'fails' if passes else 'passes'} a skill whose front matter adds {block!r}"
