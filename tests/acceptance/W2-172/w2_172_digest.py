"""The digest block's schema (Interface item 7): one regular expression per line, in order, written from the item.

``match_digest(lines, strict)`` returns the 12 match objects. ``strict`` (an audit that ran to step 12) takes each
figure line in its full form; otherwise (a stop or a refusal) a figure line may be its word followed by ``not reached``
(item 7: "a figure not reached prints its word followed by `not reached`").
"""

from __future__ import annotations

import re

HEX12 = r"[0-9a-f]{12}"
NUM = r"\d+(?:\.\d+)?"
WORDS = ("AUDIT", "MODE", "VERDICT", "HIT5", "MISSES", "POOL", "RETRIEVAL", "QUESTIONS", "COST", "NEXT", "STOP",
         "OWNER")
FIGURE_WORDS = ("VERDICT", "HIT5", "MISSES", "POOL", "RETRIEVAL", "QUESTIONS", "COST")
PATTERNS = {
    "AUDIT": rf"AUDIT (?P<audit>memory-audit-\d{{8}}) commit (?P<commit>{HEX12})",
    "MODE": r"MODE (?P<mode>weekly|monthly) reason (?P<reason>start|stable|churn|retrieval|verdict|pool|active)",
    "VERDICT": rf"VERDICT right (?P<right>\d+) of (?P<n>\d+); wrong (?P<wrong>\d+); exact (?P<lo>{NUM}) to (?P<hi>{NUM}) %; "
               r"bar (?P<need>\d+) right, (?P<max>\d+) wrong: (?P<word>passes|misses)",
    "HIT5": r"HIT5 (?P<a>\d+) of (?P<ng>\d+); first bundle (?P<b>\d+)",
    "MISSES": r"MISSES class gold_wrong (?P<gold_wrong>\d+) question_ambiguous (?P<question_ambiguous>\d+) "
              r"out_of_scope (?P<out_of_scope>\d+) retrieval_miss (?P<retrieval_miss>\d+) answer_wrong "
              r"(?P<answer_wrong>\d+); rank 1-5 (?P<r15>\d+) 6-20 (?P<r620>\d+) none (?P<rnone>\d+); namespace "
              r"embedded (?P<embedded>\d+) keyword_only (?P<keyword_only>\d+)",
    "POOL": r"POOL hit5 (?P<hit5>\d+) of (?P<n>\d+) last (?P<last_hit5>\d+|none); full (?P<full>\d+) last "
            r"(?P<last_full>\d+|none); regression (?P<regression>yes|no)",
    "RETRIEVAL": r"RETRIEVAL changed (?P<k>\d+)(?:: (?P<paths>\S+(?: \S+)*))?",
    "QUESTIONS": r"QUESTIONS kept (?P<kept>\d+) dropped (?P<dropped>\d+)(?P<codes>(?:; [A-Z][A-Z0-9-]* \d+"
                 r"(?: [A-Z][A-Z0-9-]* \d+)*)*)",
    "COST": r"COST(?P<steps>(?: [a-z0-9-]+ \d+\.\d\d)*) total (?P<total>\d+\.\d\d)",
    "NEXT": r"NEXT due (?P<date>\d{4}-\d{2}-\d{2}) (?P<mode>weekly|monthly)",
    "STOP": r"(?P<word>STOP none|STOP (?P<step>[a-z0-9-]+) (?:exit (?P<code>\d+)|gate busy)|REFUSED (?P<refused>RN-[A-Z]+))",
    "OWNER": r"(?P<word>OWNER none|OWNER stopped after USED at (?P<step>[a-z0-9-]+) exit (?P<code>\d+): "
             r"the set is not run again)",
}


def match_digest(lines: list[str], strict: bool = True) -> list[re.Match]:
    assert len(lines) == 12, f"the digest has exactly 12 lines, got {len(lines)}: {lines}"
    found = []
    for word, line in zip(WORDS, lines):
        pattern = PATTERNS[word]
        if not strict and word in FIGURE_WORDS:
            pattern = rf"(?:{pattern}|{word} not reached)"
        m = re.fullmatch(pattern, line)
        assert m, f"digest line {WORDS.index(word) + 1} ({word}) does not fit its form: {line!r}"
        found.append(m)
    return found


def by_word(lines: list[str], strict: bool = True) -> dict[str, re.Match]:
    return dict(zip(WORDS, match_digest(lines, strict)))


def cost_steps(m: re.Match) -> dict[str, float]:
    parts = (m["steps"] or "").split()
    return {parts[i]: float(parts[i + 1]) for i in range(0, len(parts), 2)}
