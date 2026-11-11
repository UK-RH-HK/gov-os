"""S3: the A8 dependency proof finds every listed citation form.

Interface item 6: "the list of bootstrap.md line 2362: a word character or ``-`` directly before the path or id;
backslashes; URL-encoding; another letter case; a path split across lines; a citation of only the store's folder or a
glob; ``../`` followed by only the tail of the path; an id cited in a record's prose. The planted unlisted form (the
one that must stay "not found") is the test designer's choice, named in the test."

The store is three files of ``legacy/memory/`` (ids LEG-001, LEG-002), retired as a memory store. Each listed form is
planted alone in a file of its own: rule files under ``.rulesync/rules/`` (read by the proof as rules) and one record
whose prose cites LEG-001. "A citation of only the store's folder or a glob" is planted as both, one file each. The
unlisted form, chosen here: **the store's path written in base64** (``.rulesync/rules/cite-base64.md``).

What the proof prints as found is what its refusal names as citers: the message, and the ``citers`` of its details
when it gives them (never its list of what it read).
"""

from __future__ import annotations

import w2_23_support as support


def _adopt_to_a8(project, box):
    adoption = support.Adoption(project, box)
    adoption.through("A6", support.retire_store_proposal())
    return adoption.run("A8")


def test_s3_the_a8_proof_finds_every_listed_form_and_only_the_unlisted_one_is_not_found(tmp_path, box):
    project = support.plant_project(tmp_path / "harbour", extra={**support.store_files(),
                                                                **support.citation_files()})
    done = _adopt_to_a8(project, box)
    assert done.returncode != 0, "A8 retired the store although every planted file cites it: the proof found " \
        f"no citer\n{done.describe()}"
    error = support.refusal(done, "ADOPT_STORE_STILL_CITED")
    said = support.proof_said(error)
    missed = [f"{form} ({rel})" for form, (rel, _) in support.LISTED_FORMS.items() if rel not in said]
    assert not missed, "the A8 proof does not print these planted citations as found: " + ", ".join(missed) \
        + f"\n{done.describe()}"
    form, rel, _ = support.UNLISTED_FORM
    assert rel not in said, f"the planted unlisted form ({form}, {rel}) is printed as found\n{done.describe()}"
    assert support.at_head(project, support.STORE[0]) is not None, "the store left HEAD although it is cited"


def test_s3_with_only_the_unlisted_form_planted_the_proof_finds_no_citer(tmp_path, box):
    """The control: the base64 form alone holds nothing back, so the store is retired."""
    form, rel, text = support.UNLISTED_FORM
    project = support.plant_project(tmp_path / "harbour", extra={**support.store_files(), rel: text})
    done = _adopt_to_a8(project, box)
    support.succeeded(done)
    assert support.at_head(project, support.STORE[0]) is None, f"the store was not retired\n{done.describe()}"
