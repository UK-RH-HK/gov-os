"""KPI success 4 [CAP-34.d], batch 3: a file that cites a gate and that the checker might not take for a record.
Added after implementation, from behaviours a review described (DEC-136).

DEC-331 exempts one thing: "A record with no `approval` is not checked". A file that writes ``approval`` in its
frontmatter claims a gate as its approval, whatever else its frontmatter lacks or repeats:

- **No ``id``.** The file is checked like any citing record. The finding names the cited id and the file; there is
  no citing id to name.
- **Frontmatter that cannot be read.** Whether the file cites a gate cannot be known, so the check does not pass:
  ``FRONTMATTER_UNREADABLE`` names the file (see ``test_w1_11_unreadable.py``).
- **``approval`` written twice.** The first key cites a dead gate and the second is empty. The check does not pass;
  the finding is ``GATE_NOT_AUTHORISING`` or ``FRONTMATTER_UNREADABLE`` and names the file.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import package, package_path, record, ticket, ticket_path

TICKET = "PROJ-aaaa"
CHANGE_PATH = "docs/changes/CIT-0007.md"
GATE = "DP-0001"
CIT = "CIT-0007"


def without_id(text):
    """The record file ``text`` with its frontmatter ``id`` line taken out."""
    lines = text.split("\n")
    kept = [line for line in lines if not line.startswith("id: ")]
    assert len(kept) == len(lines) - 1, "the fixture has no single `id` line"
    return "\n".join(kept)


def with_frontmatter_line(text, line):
    """The record file ``text`` with ``line`` added as the last line of its frontmatter."""
    head, marker, rest = text.partition("\n---\n")
    assert marker, "the fixture has no closed frontmatter"
    return f"{head}\n{line}{marker}{rest}"


CITERS_WITHOUT_ID = {
    "ticket": (ticket_path(TICKET), without_id(ticket(TICKET, approval=[GATE], cit=CIT))),
    "change": (CHANGE_PATH, without_id(record("CIT-0007", "change", "PROPOSED", approval=[GATE], cit=CIT))),
}


def checked(api, project, files):
    project.put({**support.CLEAN, **files})
    return api.check(project.root)


@pytest.mark.parametrize("citer", sorted(CITERS_WITHOUT_ID))
def test_a_citing_file_without_an_id_is_not_authorised_by_a_declined_gate(api, project, citer):
    path, text = CITERS_WITHOUT_ID[citer]
    found = checked(api, project, {path: text, package_path(GATE): package(GATE, "DECLINED", CIT)})
    support.assert_flagged(found, support.GATE_NOT_AUTHORISING, [GATE], [path])


def test_a_citing_file_without_an_id_is_authorised_by_an_answered_gate_of_its_cit(api, project):
    """The control: the missing id is not itself the finding."""
    path, text = CITERS_WITHOUT_ID["ticket"]
    found = checked(api, project, {path: text, package_path(GATE): package(GATE, support.GATE_ANSWERED, CIT)})
    support.assert_not_flagged(found, support.GATE_NOT_AUTHORISING, [GATE])


def test_a_citing_ticket_whose_frontmatter_cannot_be_read_does_not_pass(api, project):
    path = ticket_path(TICKET)
    broken = (f"---\nid: {TICKET}\ntype: task\nstatus: [open\nstate_class: AUTHORITATIVE\n"
              f"approval: [{GATE}]\ncit: {CIT}\n---\n\n# {TICKET}\n\nBody text.\n")
    found = checked(api, project, {path: broken, package_path(GATE): package(GATE, "DECLINED", CIT)})
    support.assert_fails_naming(found, path, {support.FRONTMATTER_UNREADABLE})


def test_a_second_empty_approval_key_does_not_take_the_first_out_of_the_check(api, project):
    path = ticket_path(TICKET)
    twice = with_frontmatter_line(ticket(TICKET, approval=[GATE], cit=CIT), "approval:")
    found = checked(api, project, {path: twice, package_path(GATE): package(GATE, "DECLINED", CIT)})
    support.assert_fails_naming(found, path, {support.GATE_NOT_AUTHORISING, support.FRONTMATTER_UNREADABLE})
