"""KPI success 7: the owner's ACT that retires the GPU-slot stopgap keeps the slot rule for every tree (DEC-1033).

A described behaviour (DEC-136), from the FULL review's round 1, finding F1. KPI 7 makes the ACT that retires the
stopgap (ACT-RERANK-GPU-SLOTS-1's module and its ``.pth`` in the reranker environment, updated by
ACT-RERANK-WAIT-1) a deliverable of this ticket; it is the last section of the research record
``docs/research/W2-112-shared-reranker.md``.

- Only W2-112's own private worker carries the slot rule itself. The installed, pinned ``gov``
  (``~/.local/bin/gov``, re-pinned only at ACT 2) and every other checkout and worktree still start private
  rerankers with the old worker, which relies on the module alone. Removed too early, the module lets those load on
  the GPU beside two held slots: a third copy, the crash state of DEC-1031.
- So the ACT's precondition is that the installed ``gov`` and every tree that can start a reranker carry the
  worker's own slot rule (for example after ACT 2's re-pin, and once no worktree runs an older worker), not merely
  that W2-112 has merged; until then the module stays.
- The ACT never removes, and never tells the operator to remove, the slot lock files
  (``/tmp/gov-os-rerank-gpu-<i>.lock``): removed while two rerankers hold them, a new reranker takes a fresh lock
  file and loads, three on two slots.

A document test, read loosely: the ACT is the section whose heading names the ACT, the stopgap or its retirement
(else the record's last top-level section). A step that removes the lock files is a command (in a code block, or
in inline code outside a sentence that forbids it) that removes them or a variable holding their path, or a
sentence that removes or lets the operator remove them without forbidding it (never, not, do not, must not); an
explanation of why they stay is to carry its "never" or "not" in the same sentence.
"""

from __future__ import annotations

import re

import w2_112_support as support

RECORD_REL = "docs/research/W2-112-shared-reranker.md"

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NAMES_THE_ACT = re.compile(r"\bACT\b|retir|stopgap", re.IGNORECASE)
NAMES_THE_STOPGAP = re.compile(r"gpu[_-]slot|stopgap|\.pth\b|slot (?:rule|module)", re.IGNORECASE)
INSTALLED_GOV = re.compile(r"\.local/bin/gov\b|\bACT[ -]?2\b|\bre-?pin|\b(?:installed|pinned)\b[^.\n]{0,40}\bgov\b"
                           r"|\bgov\b[^.\n]{0,40}\b(?:installed|pinned)\b", re.IGNORECASE)
OTHER_TREES = re.compile(r"\bworktrees?\b|\bcheckouts?\b|\bclones?\b|\bevery tree\b|\bother trees?\b|\ball trees\b",
                         re.IGNORECASE)
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
    assert path.is_file(), f"there is no {RECORD_REL}: KPI 7's ACT is its last section"
    return path.read_text(encoding="utf-8")


def act_section(text: str) -> str:
    """The section of the record that is the ACT retiring the stopgap."""
    lines = text.splitlines()
    headings = [(index, len(found.group(1)), found.group(2)) for index, line in enumerate(lines)
                if (found := HEADING.match(line))]
    named = [heading for heading in headings if NAMES_THE_ACT.search(heading[2])]
    if named:
        start, level, _ = named[-1]
    else:
        levels = [level for _, level, _ in headings[1:]] or [level for _, level, _ in headings]
        assert levels, f"{RECORD_REL} has no section headings, so no ACT section"
        top = min(levels)
        start, level, _ = [heading for heading in headings if heading[1] == top][-1]
    end = next((index for index, depth, _ in headings if index > start and depth <= level), len(lines))
    section = "\n".join(lines[start:end])
    assert NAMES_THE_STOPGAP.search(section), \
        (f"{RECORD_REL} has no section for the ACT that retires the GPU-slot stopgap (its module and .pth): the "
         f"section found ({lines[start]!r}) does not name it")
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


def test_the_acts_precondition_names_the_installed_gov_or_its_re_pin_not_the_merge_alone():
    act = act_section(_record())
    assert INSTALLED_GOV.search(act), \
        ("the ACT retiring the GPU-slot stopgap does not make the installed, pinned gov (~/.local/bin/gov, re-pinned "
         "at ACT 2) part of its precondition: W2-112's merge alone leaves every reranker the installed gov starts "
         "relying on the module (review round 1, F1)")


def test_the_acts_precondition_covers_every_other_tree_that_can_start_a_reranker():
    act = act_section(_record())
    assert OTHER_TREES.search(act), \
        ("the ACT retiring the GPU-slot stopgap does not make the other checkouts and worktrees part of its "
         "precondition: one that runs an older worker relies on the module alone (review round 1, F1)")


def test_no_step_of_the_act_removes_the_gpu_slot_lock_files():
    found = lock_removals(act_section(_record()))
    assert found == [], \
        ("the ACT retiring the GPU-slot stopgap removes, or lets the operator remove, the slot lock files "
         f"(/tmp/gov-os-rerank-gpu-<i>.lock): a new reranker would take a fresh one beside two held (F1): {found}")
