"""KPI success 7, re-baselined by DEC-1048 (P-W2-112-F9 (c)): the GPU-slot stopgap stays as the machine-wide guard.

The research record ``docs/research/W2-112-shared-reranker.md`` ends with a section (§5) on the stopgap that caps
private rerankers on the GPU: ACT-RERANK-GPU-SLOTS-1's module and its ``gov-reranker-gpu-slot.pth`` in the reranker
environment. That section was the owner's ACT retiring them. The second review found (F9) that no precondition of
such an ACT stays true: ordinary work brings old trees back after it (a removed worktree re-created from an old
branch, an older base checked out for a red check or a bisect, an old pin kept for rollback), and an old tree's
reranker, without the module, loads on the GPU beside two held slots (DEC-1031's crash state). The owner chose (c):

1. the section records that the module is not to be retired by an ACT now: it stays in place as the machine-wide
   guard that caps every reranker, whatever its tree's commit;
2. it records that the module is retired only when old code fails closed by construction, in a later ticket
   (P-W2-112-F9 (b); for example the reranker environment moving to a path only W2-112-or-later code knows);
3. it gives the operator no step that removes the module or its ``.pth`` now;
4. it still never removes, and never tells the operator to remove, the slot lock files
   (``/tmp/gov-os-rerank-gpu-<i>.lock``): removed while two rerankers hold them, a new reranker takes a fresh lock
   file and loads, three on two slots (review round 1, F1; unchanged).

DEC-1048 supersedes the earlier cases that the ACT's precondition names the installed ``gov``'s re-pin and every
other tree (there is no retirement precondition now).

A document test, read loosely; wording may vary. The section is the top-level section that holds the last heading
naming the stopgap, the module or its retirement (else the record's last top-level section); lines in code blocks
are never headings.

- Item 1 is a sentence that says the module (or "it", or an ACT) is not retired, removed or applied now (now, today,
  at present, for now, at this point, in this ticket), and a sentence, alone or with the next, that says it stays
  (is kept, remains, stays in place) and covers the whole machine (machine-wide, every reranker, whatever its tree's
  commit).
- Item 2 is a sentence that ties its retirement to old code failing closed (or "by construction"), and the section
  naming a later ticket (later, future, follow-up, separate) or P-W2-112-F9's option (b).
- A step that removes the module or its ``.pth`` is a command in a code block (rm, unlink, uninstall, a move that is
  not a restore; comment lines aside) naming the module, its ``.pth`` or a variable holding that path, or a sentence
  that removes it (inline command or words) and neither forbids it (never, not, no, nothing), defers it to the later
  ticket (later, only when, until, fails closed, by construction, (b)), nor speaks of it as a condition or as
  history (if, would, could, was, earlier, superseded, "once removed"); an explanation such as "removing the module
  lets an old tree's reranker load" or "removed, it would let" is not a step.
- A step that removes the lock files is read as before: a command (in a code block, or in inline code outside a
  sentence that forbids it) that removes them or a variable holding their path, or a sentence that removes or lets
  the operator remove them without forbidding it (never, not, do not, must not); an explanation of why they stay is
  to carry its "never" or "not" in the same sentence.
"""

from __future__ import annotations

import re

import w2_112_support as support

RECORD_REL = "docs/research/W2-112-shared-reranker.md"

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NAMES_THE_SECTION = re.compile(
    r"stopgap|gpu[ _-]?slot|\.pth\b|retir|\bguard\b|interim module|(?:slot|stopgap|guard)\s+module|module\s+stays"
    r"|slot (?:rule|cap)|ACT-RERANK-GPU-SLOTS", re.IGNORECASE)
NAMES_THE_STOPGAP = re.compile(r"gpu[_-]slot|stopgap|\.pth\b|slot (?:rule|module)|machine[- ]wide guard"
                               r"|interim module|ACT-RERANK-GPU-SLOTS", re.IGNORECASE)

# Item 1: not retired by an ACT now; stays as the machine-wide guard.
NEGATION = re.compile(r"\bnot\b|\bno\b|\bnever\b|n't\b|\bnor\b", re.IGNORECASE)
RETIRE_WORD = re.compile(r"retir\w*|remov\w*|uninstall\w*|delet\w*|\bACT\b|\bappl(?:y|ied|ies|ying)\b",
                         re.IGNORECASE)
NOW = re.compile(r"\bnow\b|\btoday\b|\bat present\b|\bpresently\b|\bfor the time being\b"
                 r"|\bat this (?:time|stage|point)\b|\b(?:in|with|by|under|for) (?:this|the present) ticket\b",
                 re.IGNORECASE)
MODULE_NAME = re.compile(r"gov[-_]reranker[-_]gpu[-_]slot|\.pth\b|\bmodule\b|\bstopgap\b|\bguard\b|gpu[- ]slot"
                         r"|ACT-RERANK-GPU-SLOTS", re.IGNORECASE)
SUBJECT = re.compile(MODULE_NAME.pattern + r"|\bit\b|\bACT\b|\bthis section\b|§\s?5", re.IGNORECASE)
LOCK_WORDS = re.compile(r"lock[ -]?files?|\.lock\b|slot[ -]?locks?|gov-os-rerank-gpu", re.IGNORECASE)
STAYS = re.compile(r"\bstay(?:s|ed|ing)?\b|\bremain(?:s|ed|ing)?\b|\bkept\b|\bkeep(?:s|ing)?\b|\bin place\b"
                   r"|\bretain(?:s|ed|ing)?\b", re.IGNORECASE)
WHOLE_MACHINE = re.compile(
    r"machine[- ]wide|whole machine|\b(?:every|all|any|each) rerankers?\b"
    r"|\bwhatever (?:its|the|a|their) (?:tree|commit|checkout|worktree)|\bwhatever commit"
    r"|\b(?:every|any|each|all) (?:trees?|commits?|checkouts?|worktrees?)\b"
    r"|\bregardless of (?:its |the |a |their )?(?:tree|commit|checkout|worktree)"
    r"|\bwhichever (?:tree|commit|checkout|worktree)", re.IGNORECASE)

# Item 2: retired only when old code fails closed by construction, in a later ticket.
FAILS_CLOSED = re.compile(r"\bfail(?:s|ed|ing)?[ -]closed\b|\bby construction\b", re.IGNORECASE)
RETIREMENT_OR_OLD_CODE = re.compile(
    r"retir\w*|remov\w*|\bold(?:er)? (?:code|trees?|workers?|commits?|checkouts?|branch(?:es)?|pins?|wheels?"
    r"|rerankers?)\b|pre-W2-112|W2-112-or-later|before W2-112", re.IGNORECASE)
LATER_TICKET = re.compile(
    r"\b(?:later|future|follow[- ]?(?:up|on)|separate|another|subsequent|new|its own)\b[^.\n]{0,30}\bticket\b"
    r"|\bticket\b[^.\n]{0,30}\b(?:later|to come|to be filed|after W2-112)\b"
    r"|P-W2-112-F9\W{0,3}\(b\)|\boption \(b\)|\bunder \(b\)", re.IGNORECASE)

# Item 3: no step removes the module or its .pth now.
MODULE_PATH = re.compile(r"gov[-_]reranker[-_]gpu[-_]slot|\.pth\b", re.IGNORECASE)
MODULE_TARGET = (r"(?:\S*gov[-_]reranker[-_]gpu[-_]slot\S*|\S*\.pth\b|(?:gpu[- ]slot |interim |stopgap |slot )?module\b"
                 r"|stopgap\b|(?:machine[- ]wide )?guard\b)")
REMOVAL_VERB = (r"(?:remove|delete|unlink|uninstall|disable|strip)(?:s|d|ed)?\b|stripped\b|take out\b|takes out\b"
                r"|took out\b")
REMOVES_MODULE = re.compile(
    r"\b(?:" + REMOVAL_VERB + r")\s+(?:\S+\s+){0,4}?" + MODULE_TARGET
    + r"|" + MODULE_TARGET + r"\s+(?:\S+\s+){0,4}?(?:be|are|get|gets|is)?\s*(?:" + REMOVAL_VERB + r")",
    re.IGNORECASE)
MODULE_EXCUSE = re.compile(
    r"\bnever\b|\bnot\b|n't\b|\bnor\b|\bno\b|\bnothing\b|\bnone\b|\bneither\b|\bwithout\b"
    r"|\blater\b|\bfuture\b|\bfollow[- ]?(?:up|on)\b|\bonly (?:when|once|after|if)\b|\buntil\b|\btill\b"
    r"|\bfail(?:s|ed|ing)?[ -](?:closed|safe)\b|\bby construction\b|\(b\)"
    r"|\bif\b|\bwould\b|\bcould\b|\bwere\b"
    r"|\bwas\b|\bearlier\b|\bprevious(?:ly)?\b|\bformer(?:ly)?\b|\bsupersed\w*|\breplaced\b|\bdraft\b"
    r"|\boriginal(?:ly)?\b|^[\W\d]*(?:removed|deleted|uninstalled|disabled|unlinked)\b[^,.]{0,20},"
    r"|\b(?:once|when) (?:it is |they are |the \S+ is )?(?:removed|deleted|uninstalled|disabled|gone)\b",
    re.IGNORECASE)
REMOVE_MODULE_COMMAND = re.compile(r"(?:^|[\s;&|(])(?:rm|unlink|rmdir|shred)\b|-delete\b|os\.remove|os\.unlink"
                                   r"|\.unlink\(|shutil\.rmtree|\buninstall\b")
MOVE_COMMAND = re.compile(r"(?:^|[\s;&|(])mv\s")

# Item 4 (unchanged): no step removes the slot lock files.
LOCKS = r"(?:gov-os-rerank-gpu\S*|(?:slot[ -]?)?lock[ -]?files?|slot[ -]?locks?|locks\b|\S*\.lock\b)"
REMOVES_LOCKS = re.compile(
    r"\b(?:remov|delet|unlink|clean(?:s|ed|ing)? up|clear|wip)\w*\s+(?:\S+\s+){0,4}?" + LOCKS
    + r"|" + LOCKS + r"\s+(?:\S+\s+){0,4}?(?:be|are|get|is)?\s*(?:remov|delet|unlink|clean|clear|wip)\w*",
    re.IGNORECASE)
FORBIDS = re.compile(r"\bnever\b|\bnot\b|n't\b|\bmust not\b|\bnor\b", re.IGNORECASE)
REMOVE_COMMAND = re.compile(r"(?:^|[\s;&|(])(?:rm|unlink|rmdir|shred)\b|-delete\b|os\.remove|os\.unlink|\.unlink\("
                            r"|shutil\.rmtree")
LOCK_PATH = re.compile(r"gov-os-rerank-gpu", re.IGNORECASE)
ASSIGNED = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def _record() -> str:
    path = support.REPO_ROOT / RECORD_REL
    assert path.is_file(), f"there is no {RECORD_REL}: KPI 7's section on the GPU-slot stopgap is its last section"
    return path.read_text(encoding="utf-8")


def _headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """``(line index, level, text)`` of each heading outside code blocks."""
    found, fenced = [], False
    for index, line in enumerate(lines):
        if line.strip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced and (match := HEADING.match(line)):
            found.append((index, len(match.group(1)), match.group(2)))
    return found


def stopgap_section(text: str) -> str:
    """The section of the record on the GPU-slot stopgap (its module and ``.pth``): §5."""
    lines = text.splitlines()
    headings = _headings(lines)
    levels = [level for _, level, _ in headings[1:]] or [level for _, level, _ in headings]
    assert levels, f"{RECORD_REL} has no section headings, so no section on the GPU-slot stopgap"
    top = min(levels)
    named = [heading for heading in headings if NAMES_THE_SECTION.search(heading[2])]
    if named:
        chosen = named[-1]
        if chosen[1] > top:
            chosen = next((heading for heading in reversed(headings)
                           if heading[0] < chosen[0] and heading[1] <= top), chosen)
    else:
        chosen = [heading for heading in headings if heading[1] == top][-1]
    start, level, _ = chosen
    end = next((index for index, depth, _ in headings if index > start and depth <= level), len(lines))
    section = "\n".join(lines[start:end])
    assert NAMES_THE_STOPGAP.search(section), \
        (f"{RECORD_REL} has no section on the GPU-slot stopgap (its module and .pth): the section found "
         f"({lines[start]!r}) does not name it")
    return section


def _blocks(section: str) -> tuple[list[list[str]], list[str]]:
    """``(code blocks, prose lines)`` of the section."""
    blocks, prose, current = [], [], None
    for line in section.splitlines():
        if line.strip().startswith(("```", "~~~")):
            if current is None:
                current = []
            else:
                blocks.append(current)
                current = None
            continue
        (current if current is not None else prose).append(line)
    if current is not None:
        blocks.append(current)
    return blocks, prose


def _sentences(prose: list[str]) -> list[str]:
    text = re.sub(r"\s+", " ", "\n".join(prose))
    return [sentence for sentence in re.split(r"(?<=[.!?])\s+|\s+(?=\d+\.\s)|\s+(?=[-*]\s)", text) if sentence]


def not_retired_now(section: str) -> list[str]:
    """The sentences saying the module (or "it", or an ACT) is not retired, removed or applied now."""
    found = []
    for sentence in _sentences(_blocks(section)[1]):
        plain = re.sub(r"`", "", sentence)
        about_locks_only = LOCK_WORDS.search(plain) and not MODULE_NAME.search(plain)
        if (NOW.search(plain) and NEGATION.search(plain) and RETIRE_WORD.search(plain) and SUBJECT.search(plain)
                and not about_locks_only):
            found.append(sentence.strip()[:300])
    return found


def stays_as_the_machine_wide_guard(section: str) -> list[str]:
    """The sentences (alone or with the next) saying the module stays and covers the whole machine."""
    sentences = [re.sub(r"`", "", sentence) for sentence in _sentences(_blocks(section)[1])]
    found = []
    for index, sentence in enumerate(sentences):
        window = " ".join(sentences[index:index + 2])
        if STAYS.search(sentence) and WHOLE_MACHINE.search(window):
            found.append(window.strip()[:300])
        elif WHOLE_MACHINE.search(sentence) and STAYS.search(window):
            found.append(window.strip()[:300])
    return found


def retirement_condition(section: str) -> tuple[list[str], list[str]]:
    """``(sentences tying its retirement to old code failing closed, mentions of the later ticket)``."""
    sentences = [re.sub(r"`", "", sentence) for sentence in _sentences(_blocks(section)[1])]
    closed = [sentence.strip()[:300] for sentence in sentences
              if FAILS_CLOSED.search(sentence) and RETIREMENT_OR_OLD_CODE.search(sentence)]
    later = [match.group(0) for match in LATER_TICKET.finditer(re.sub(r"\s+", " ", " ".join(sentences)))]
    return closed, later


def _is_restore(line: str) -> bool:
    """A move whose destination is the ``.pth`` or the module itself puts it back; it removes nothing."""
    words = [word.strip("'\";") for word in line.split()]
    return bool(words) and words[-1].endswith((".pth", ".py")) and bool(MODULE_PATH.search(words[-1]))


def module_removals(section: str) -> list[str]:
    """Every command or step of the section that removes the GPU-slot module or its ``.pth`` now."""
    found = []
    blocks, prose = _blocks(section)
    for block in blocks:
        lines = [line for line in block if not line.strip().startswith(("#", "//", "REM "))]
        holders = {match.group(1) for line in lines if (match := ASSIGNED.match(line)) and MODULE_PATH.search(line)}
        for line in lines:
            names_it = MODULE_PATH.search(line) or any(re.search(r"\$\{?" + name + r"\b", line) for name in holders)
            removes = REMOVE_MODULE_COMMAND.search(line) or (MOVE_COMMAND.search(line) and not _is_restore(line))
            if removes and names_it:
                found.append(f"command: {line.strip()}")
    for sentence in _sentences(prose):
        excused = MODULE_EXCUSE.search(sentence)
        for code in re.findall(r"`([^`]+)`", sentence):
            removes = REMOVE_MODULE_COMMAND.search(code) or (MOVE_COMMAND.search(code) and not _is_restore(code))
            if removes and MODULE_PATH.search(code) and not excused:
                found.append(f"command: {code.strip()}")
        if REMOVES_MODULE.search(re.sub(r"`", "", sentence)) and not excused:
            found.append(f"step: {sentence.strip()[:300]}")
    return found


def lock_removals(section: str) -> list[str]:
    """Every command or step of the section that removes the slot lock files, or lets the operator remove them."""
    found = []
    blocks, prose = _blocks(section)
    for block in blocks:
        holders = {match.group(1) for line in block if (match := ASSIGNED.match(line)) and LOCK_PATH.search(line)}
        for line in block:
            names_them = LOCK_PATH.search(line) or any(re.search(r"\$\{?" + name + r"\b", line) for name in holders)
            if REMOVE_COMMAND.search(line) and names_them:
                found.append(f"command: {line.strip()}")
    text = re.sub(r"\s+", " ", "\n".join(prose))
    for sentence in re.split(r"(?<=[.!?])\s+|\s+(?=\d+\.\s)|\s+(?=[-*]\s)", text):
        forbidden = FORBIDS.search(sentence)
        for code in re.findall(r"`([^`]+)`", sentence):
            if REMOVE_COMMAND.search(code) and LOCK_PATH.search(code) and not forbidden:
                found.append(f"command: {code.strip()}")
        if REMOVES_LOCKS.search(re.sub(r"`", "", sentence)) and not forbidden:
            found.append(f"step: {sentence.strip()[:300]}")
    return found


def check_not_retired_now_and_kept_as_the_machine_wide_guard(text: str) -> None:
    section = stopgap_section(text)
    assert not_retired_now(section), \
        ("§5 (the section on the GPU-slot stopgap) does not record that the module and its .pth are not to be "
         "retired by an ACT now: no sentence says the module is not retired, removed or applied now (DEC-1048, "
         "P-W2-112-F9 (c))")
    assert stays_as_the_machine_wide_guard(section), \
        ("§5 (the section on the GPU-slot stopgap) does not record that the module stays in place as the "
         "machine-wide guard that caps every reranker, whatever its tree's commit (DEC-1048, P-W2-112-F9 (c))")


def check_retired_only_when_old_code_fails_closed_in_a_later_ticket(text: str) -> None:
    closed, later = retirement_condition(stopgap_section(text))
    assert closed, \
        ("§5 (the section on the GPU-slot stopgap) does not record that the module is retired only when old code "
         "fails closed by construction: no sentence ties its retirement to old code failing closed (DEC-1048, "
         "P-W2-112-F9 (b))")
    assert later, \
        ("§5 (the section on the GPU-slot stopgap) does not put the module's retirement in a later ticket "
         "(DEC-1048, P-W2-112-F9 (b)): it names no later, future or follow-up ticket nor option (b)")


def check_no_step_removes_the_module_or_its_pth(text: str) -> None:
    found = module_removals(stopgap_section(text))
    assert found == [], \
        ("§5 (the section on the GPU-slot stopgap) gives the operator a step that removes the module or its .pth "
         "now; DEC-1048 keeps it as the machine-wide guard, since an old tree's reranker without it loads on the GPU "
         f"beside two held slots (F9): {found}")


def check_no_step_removes_the_lock_files(text: str) -> None:
    found = lock_removals(stopgap_section(text))
    assert found == [], \
        ("§5 (the section on the GPU-slot stopgap) removes, or lets the operator remove, the slot lock files "
         f"(/tmp/gov-os-rerank-gpu-<i>.lock): a new reranker would take a fresh one beside two held (F1): {found}")


def test_the_section_records_the_module_is_not_retired_by_an_act_now_and_stays_as_the_machine_wide_guard():
    check_not_retired_now_and_kept_as_the_machine_wide_guard(_record())


def test_the_section_retires_the_module_only_when_old_code_fails_closed_by_construction_in_a_later_ticket():
    check_retired_only_when_old_code_fails_closed_in_a_later_ticket(_record())


def test_no_step_of_the_section_removes_the_gpu_slot_module_or_its_pth_now():
    check_no_step_removes_the_module_or_its_pth(_record())


def test_no_step_of_the_section_removes_the_gpu_slot_lock_files():
    check_no_step_removes_the_lock_files(_record())
