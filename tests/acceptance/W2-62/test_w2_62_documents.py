"""W2-62 -- the checkpoint skill's resume rule and the research record, read as documents.

KPI success 5: "The checkpoint skill states the resume rule: RESUME HERE holds the full
session state (what is happening, what was decided, what is next, where things are),
repository knowledge comes from retrieval and the context packets, and a checkpoint is
written at every handover (a worker's return, a merge, a package, a compaction) [DEC-837
items 2 and 3]". With it, DEC-792's 8,000-character limit on RESUME HERE is lifted.

KPI success 2, first half: "Research first, recorded in docs/changes/W2-62-CIT-P.md: whether
Claude Code 2.1.292 caps or moves a SessionStart hook's additionalContext above a size,
measured in a headless session."

The checks look for key terms inside the part of the document that speaks of the matter
(the Markdown section that names RESUME HERE, or the handover), so a faithful rewording
passes and no one exact sentence is demanded.
"""

from __future__ import annotations

import re

import pytest

import w2_62_support as support


def _text(path):
    if not path.is_file():
        pytest.fail(f"{path.relative_to(support.REPO_ROOT)} does not exist", pytrace=False)
    return path.read_text(encoding="utf-8")


def _flat(text):
    return re.sub(r"\s+", " ", text).lower()


def _sections(text, pattern):
    """The Markdown sections (a heading to the next heading of any level; fenced lines are not headings) whose
    text matches ``pattern``, joined and flattened."""
    sections, current, fenced = [], [], False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        if not fenced and re.match(r"#{1,6}\s", line) and current:
            sections.append("\n".join(current))
            current = []
        current.append(line)
    sections.append("\n".join(current))
    return _flat("\n".join(section for section in sections if re.search(pattern, section, re.I)))


def _missing(text, terms):
    return [name for name, pattern in terms.items() if not re.search(pattern, text)]


# --------------------------------------------------------------------------
# The checkpoint skill (success 5, DEC-837 items 2 and 3)
# --------------------------------------------------------------------------

def test_the_skill_says_resume_here_holds_the_full_session_state():
    """Success 5: the full session state: what is happening, what was decided, what is next, where things are."""
    part = _sections(_text(support.SKILL), r"RESUME HERE")
    assert part, "the checkpoint skill does not speak of the RESUME HERE section"
    missing = _missing(part, {
        "the session state": r"session(?:'s)? state|state of the session",
        "full": r"\bfull\b|\bwhole\b|\bcomplete\b|\bentire\b|\ball of\b",
        "what is happening": r"happening|under ?way|in progress|going on",
        "what was decided": r"decided|decisions?\b",
        "what is next": r"\bnext\b",
        "where things are": r"\bwhere\b",
    })
    assert not missing, f"where the checkpoint skill speaks of RESUME HERE, it does not say {missing}"


def test_the_skill_says_repository_knowledge_comes_from_retrieval_and_the_context_packets():
    """Success 5: repository knowledge comes from retrieval and the context packets, not from the resume."""
    part = _sections(_text(support.SKILL), r"RESUME HERE")
    missing = _missing(part, {
        "knowledge of the repository": r"knowledge|what the repository (?:holds|says)",
        "retrieval": r"retriev",
        "the context packets": r"context packets?",
    })
    assert not missing, f"where the checkpoint skill speaks of RESUME HERE, it does not name {missing}"


def test_the_skill_says_a_checkpoint_is_written_at_every_handover():
    """Success 5: at every handover: a worker's return, a merge, a package, a compaction (DEC-837 item 3)."""
    part = _sections(_text(support.SKILL), r"hand-?overs?\b|hand(?:ing)? over")
    assert part, "the checkpoint skill does not speak of a handover"
    missing = _missing(part, {
        "every handover": r"(?:every|each|any)\b[^.]{0,40}hand-?over|hand-?overs?\b[^.]{0,20}\b(?:every|each|always)",
        "a worker's return": r"worker[^.]{0,30}return|return[^.]{0,30}worker",
        "a merge": r"\bmerg",
        "a package": r"\bpackage",
        "a compaction": r"\bcompact",
    })
    assert not missing, f"where the checkpoint skill speaks of the handover, it does not name {missing}"


def test_the_skill_does_not_limit_resume_here_to_8000_characters():
    """DEC-837 item 2: DEC-792's limit is lifted. A mention of 8,000 is allowed only to say it no longer holds."""
    text = _flat(_text(support.SKILL))
    limits = [sentence for sentence in re.split(r"(?<=[.;:])\s", text)
              if re.search(r"\b8(?:,|\s|\.)?000\b|\b8k\b", sentence)
              and not re.search(r"lifted|no longer|removed|not limited|no limit|without (?:a|any) limit", sentence)]
    assert not limits, f"the checkpoint skill still limits RESUME HERE to 8,000 characters: {limits[0][:300]!r}"


# --------------------------------------------------------------------------
# The research record (success 2, first half)
# --------------------------------------------------------------------------

def test_the_research_record_exists_and_names_the_measured_harness():
    """Success 2: Claude Code 2.1.292, a headless session, SessionStart's additionalContext."""
    text = _flat(_text(support.CIT_P))
    missing = _missing(text, {
        "the version 2.1.292": r"2\.1\.292",
        "a headless session": r"headless|claude -p\b|`-p`|--print",
        "the SessionStart hook": r"sessionstart|session-start|session start",
        "additionalContext": r"additionalcontext|additional context",
    })
    assert not missing, f"{support.CIT_P.name} does not record {missing}"


def test_the_research_record_gives_the_measured_sizes_and_what_happened():
    """Success 2: 9,500 whole; 12,000 and 60,000 not injected, saved to a file with a preview."""
    text = _flat(_text(support.CIT_P))
    missing = _missing(text, {
        "9,500": r"9[,.\s]?500|9\.5 ?k",
        "12,000": r"12[,.\s]?000|12 ?k",
        "60,000": r"60[,.\s]?000|60 ?k",
        "arrived whole": r"whole|in full|complete|intact|exactly|verbatim",
        "saved to a file": r"saved to (?:a )?file|full output saved|to a file|written to (?:a )?file",
        "a preview": r"preview",
    })
    assert not missing, f"{support.CIT_P.name} does not record {missing} of the measurement"


def test_the_research_record_gives_the_conclusion_the_bound_and_the_route():
    """Success 2: the bound of about 10,000 characters; the route by instruction, file, line range and size."""
    text = _flat(_text(support.CIT_P))
    missing = _missing(text, {
        "the bound of about 10,000": r"10[,.\s]?000|10 ?k\b",
        "the instruction to read": r"instruction|\bread\b",
        "the file": r"checkpoint|\bfile\b",
        "the line range": r"line range|range of lines|\blines \d|lines? numbers?",
        "the size": r"\bsize\b|characters",
    })
    assert not missing, f"{support.CIT_P.name} does not record {missing} in its conclusion"
