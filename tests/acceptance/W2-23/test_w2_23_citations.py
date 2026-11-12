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


def _refused_with_found(tmp_path, box, extra, proposal, planted, absent=(), patterns=support.NAMESPACE_PATHS):
    """Plant ``extra`` (the store and the citing files), drive A8 and check the refusal prints each of ``planted`` (a
    path) and none of ``absent``. Returns the project."""
    project = support.plant_project(tmp_path / "harbour", extra=extra, patterns=patterns)
    adoption = support.Adoption(project, box)
    adoption.through("A6", proposal)
    done = adoption.run("A8")
    assert done.returncode != 0, "A8 retired the store although a planted file cites it: the proof found no " \
        f"citer\n{done.describe()}"
    said = support.proof_said(support.refusal(done, "ADOPT_STORE_STILL_CITED"))
    missed = [rel for rel in planted if rel not in said]
    assert not missed, "the A8 proof does not print these planted citations as found: " + ", ".join(missed) \
        + f"\n{done.describe()}"
    wrongly = [rel for rel in absent if rel in said]
    assert not wrongly, "the A8 proof prints as found a file that cites nothing of the store: " \
        + ", ".join(wrongly) + f"\n{done.describe()}"
    return project


def _sentence_final(tmp_path, box, form):
    rel, text = support.SENTENCE_FINAL[form]
    project = _refused_with_found(tmp_path, box, {**support.store_files(), rel: text},
                                  support.retire_store_proposal(), [rel])
    assert support.at_head(project, support.STORE[0]) is not None, "the store left HEAD although it is cited"


def test_s3_a_citation_of_the_stores_folder_ending_a_sentence_with_a_full_stop_is_found(tmp_path, box):
    """P-W2-23-7 (a): ``... is legacy/memory.`` cites the store's folder; the full stop closes the sentence."""
    _sentence_final(tmp_path, box, "folder_then_dot")


def test_s3_a_citation_of_the_stores_folder_with_its_slash_then_a_full_stop_is_found(tmp_path, box):
    """P-W2-23-7 (a): ``... see legacy/memory/.`` cites the store's folder with its slash, then a full stop."""
    _sentence_final(tmp_path, box, "folder_slash_then_dot")


def test_s3_a_dotdot_tail_of_a_store_file_ending_a_sentence_with_a_full_stop_is_found(tmp_path, box):
    """P-W2-23-7 (a): ``../memory/index.md.`` is the tail of ``legacy/memory/index.md`` (a file with no record id,
    so no id match can stand in for the tail form), closed by the full stop of the sentence."""
    _sentence_final(tmp_path, box, "dotdot_tail_then_dot")


def _nested(tmp_path, box, form):
    rel, text = support.NESTED_CITATIONS[form]
    unrelated, unrelated_text = support.NESTED_UNRELATED
    project = _refused_with_found(tmp_path, box,
                                  {**support.nested_store_files(), rel: text, unrelated: unrelated_text},
                                  support.retire_nested_store_proposal(), [rel], absent=[unrelated],
                                  patterns=support.NESTED_PATTERNS)
    assert support.at_head(project, support.NESTED_STORE[0]) is not None, "the store left HEAD although it is cited"


def test_s3_a_store_with_all_files_in_subfolders_is_found_cited_by_its_own_folder_with_the_slash(tmp_path, box):
    """P-W2-23-7 (a): the store's folder is the deepest folder holding all its files (``notes/memory``, though no
    file sits directly in it); ``notes/memory/`` cites the store."""
    _nested(tmp_path, box, "own_folder_slash")


def test_s3_a_store_with_all_files_in_subfolders_is_found_cited_by_its_own_folder_mid_sentence(tmp_path, box):
    """P-W2-23-7 (a): ``notes/memory and ...`` (no slash, mid-sentence) cites the store whose files all sit in
    subfolders of ``notes/memory``."""
    _nested(tmp_path, box, "own_folder_mid_sentence")


def test_s3_a_store_with_all_files_in_subfolders_is_found_cited_by_a_folder_between_its_folder_and_a_file(
        tmp_path, box):
    """P-W2-23-7 (a): ``notes/memory/2025/`` is a folder between the store's folder and a file (``.../2025/q1/a.md``)."""
    _nested(tmp_path, box, "folder_between")


def test_s3_with_only_a_rule_citing_nothing_of_a_nested_store_planted_the_store_is_retired(tmp_path, box):
    """The control for the nested store (P-W2-23-7 (a)): a rule citing nothing of it holds nothing back."""
    rel, text = support.NESTED_UNRELATED
    project = support.plant_project(tmp_path / "harbour", extra={**support.nested_store_files(), rel: text},
                                    patterns=support.NESTED_PATTERNS)
    adoption = support.Adoption(project, box)
    adoption.through("A6", support.retire_nested_store_proposal())
    done = adoption.run("A8")
    support.succeeded(done)
    assert support.at_head(project, support.NESTED_STORE[0]) is None, f"the store was not retired\n{done.describe()}"


def test_s3_with_only_the_unlisted_form_planted_the_proof_finds_no_citer(tmp_path, box):
    """The control: the base64 form alone holds nothing back, so the store is retired."""
    form, rel, text = support.UNLISTED_FORM
    project = support.plant_project(tmp_path / "harbour", extra={**support.store_files(), rel: text})
    done = _adopt_to_a8(project, box)
    support.succeeded(done)
    assert support.at_head(project, support.STORE[0]) is None, f"the store was not retired\n{done.describe()}"
