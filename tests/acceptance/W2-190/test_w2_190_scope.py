"""W2-190 F2: what is not a reference. One case each, all accepted and recorded: guards (green on the code before the
change, required to stay green after it) against a refusal that counts too much.

- a mention inside the deleted file itself;
- a mention only in a file under ``governance/adoption/`` (the adoption's own records; A1's and A2's records already list
  every path, and a note committed there after A2 names the file again);
- a mention only in a file the same proposal also deletes (two files naming each other, both deleted);
- a path that only shares a suffix with the deleted one: ``x.md`` at the root, while another file names only ``docs/a/x.md``.
"""

from __future__ import annotations

import w2_190_support as support
from w2_190_support import base


def delete(path, batch):
    return base.entry(path, support.DELETE, batch=batch)


def assert_recorded_deleted(adoption, path, batch):
    held = support.recorded(adoption.root, path)
    assert held["action"] == support.DELETE and held["batch"] == batch, held


def test_f2_a_mention_inside_the_file_itself_is_not_a_reference(adoption):
    support.accepted(support.propose(adoption, [delete(support.SELF, 1)]))
    assert_recorded_deleted(adoption, support.SELF, 1)


def test_f2_a_mention_inside_the_adoptions_own_folder_is_not_a_reference(adoption):
    base.write(adoption.root, support.NOTE_IN_ADOPTION,
               f"# Adoption note\n\nThe page {support.ADOPTION_ONLY} is a candidate for deletion.\n")
    base.commit_all(adoption.root, "a note of the adopter's, kept with the adoption's records")
    support.accepted(support.propose(adoption, [delete(support.ADOPTION_ONLY, 1)]))
    assert_recorded_deleted(adoption, support.ADOPTION_ONLY, 1)


def test_f2_a_mention_in_a_file_the_same_proposal_also_deletes_is_not_a_reference(adoption):
    support.accepted(support.propose(adoption, [delete(support.MUTUAL_A, 1), delete(support.MUTUAL_B, 2)]))
    assert_recorded_deleted(adoption, support.MUTUAL_A, 1)
    assert_recorded_deleted(adoption, support.MUTUAL_B, 2)


def test_f2_a_path_that_only_shares_a_suffix_is_not_a_reference(adoption):
    support.accepted(support.propose(adoption, [delete(support.ROOT_X, 1)]))
    assert_recorded_deleted(adoption, support.ROOT_X, 1)
    assert support.recorded(adoption.root, support.DEEP_X)["action"] == "KEEP"
