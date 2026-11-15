"""W2-111 failure-4 and success-9: rv-3's F1 as a described behaviour (DEC-136, DEC-802; brief td-7, P-W2-111-R5-ROWS
(a)). The guard's duplicate-key-refusing YAML loader answers every text as the pure-Python ``yaml.SafeLoader`` does:
a text the pure loader refuses is still refused, and a text it reads is read to the same data, whatever faster parser
is used. The classes: a tab inside or after a plain value and after ``key:``, a ``? `` inside a flow item, a byte order
mark after the start of the text. Support: ``w2_111_yaml_parity.py``.
"""

from __future__ import annotations

import pytest

import w2_111_live_hook as live
import w2_111_yaml_parity as parity

TEXTS = parity.TEXTS
IDS = parity.TEXT_IDS


# -- the fixture is sound: the pure loader refuses the class texts and reads the clean one -----------------------------

@pytest.mark.parametrize("text", TEXTS, ids=IDS)
def test_the_pure_safe_loader_refuses_each_class_text_and_reads_the_clean_one(text, tmp_path):
    source = text.text(str(tmp_path / "material"))
    got = parity.pure_answer(source)
    if text.refused:
        assert got[0] == "refused", f"{text.id}: the pure SafeLoader read the text (the fixture is not sound): {got!r}"
    else:
        assert got == ("data", {"held_out_paths": [f"{tmp_path}/material/held"]}), (
            f"{text.id}: the pure SafeLoader did not read the clean text to its one entry: {got!r}")


# -- the product's loader (success-9, failure-4) --------------------------------------------------------------------

def _product_loaders():
    from gov.guard import heldout
    from gov.util import parts
    return {"gov.util.parts.load_yaml_unique": parts.load_yaml_unique,
            "gov.guard.heldout.load_yaml_unique": heldout.load_yaml_unique}


@pytest.mark.parametrize("form", ["text", "file"])
@pytest.mark.parametrize("text", TEXTS, ids=IDS)
def test_the_product_loader_answers_each_text_as_the_pure_safe_loader_does(text, form, tmp_path):
    """The data, or the exception's type and text, equal the pure loader's: given the text itself (as the path map's
    blocks are read), or the file opened as the guard opens held-out.yaml (UTF-8, a mid-text BOM kept)."""
    source_text = text.text(str(tmp_path / "material"))
    path = parity.write_exact(tmp_path / parity.HELD_OUT_REL, source_text)

    def answer(load):
        if form == "text":
            return parity.answer_of(load, source_text)
        with open(path, encoding="utf-8") as f:
            return parity.answer_of(load, f)

    expected = answer(parity.pure_load)
    for name, load in _product_loaders().items():
        got = answer(load)
        if expected[0] == "refused" and got[0] == "data":
            pytest.fail(f"{text.id} ({form}): {name} read the text that the pure SafeLoader refuses: it read "
                        f"{got[1]!r}; the pure loader: {expected[1]}: {expected[2]}", pytrace=False)
        assert got == expected, (
            f"{text.id} ({form}): {name} answered {got!r}; the pure SafeLoader answered {expected!r}")


# -- the live hook's copy (failure-4) ---------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def live_copies(tmp_path_factory):
    """The applied (before) and patched (after) copies and the pinned interpreter; or the reason they cannot be had."""
    try:
        copies, interpreter = parity.make_live(tmp_path_factory.mktemp("w2-111-yaml-live"))
    except live.LiveHookUnavailable as exc:
        return {"error": str(exc)}
    return {"copies": copies, "interpreter": interpreter}


@pytest.mark.parametrize("text", TEXTS, ids=IDS)
def test_the_live_hook_s_patched_copy_decides_each_held_out_text_as_the_applied_copy_does(live_copies, text,
                                                                                          tmp_path):
    if "error" in live_copies:
        pytest.fail(live_copies["error"], pytrace=False)
    copies, interpreter = live_copies["copies"], live_copies["interpreter"]
    planted = parity.plant_project(tmp_path / "world", text)
    reads = {"the planted file the entry names": planted.planted, "an ordinary file of the project": planted.ordinary}
    decided = {}
    for what, target in reads.items():
        b = parity.run_copy(interpreter, copies.before, planted.project, tmp_path / "run-before", target)
        a = parity.run_copy(interpreter, copies.after, planted.project, tmp_path / "run-after", target)
        decided[what] = (b[0], a[0])
        assert a[0] == b[0], (
            f"{text.id}: a Read of {what} was decided {a[0]} by the patched copy and {b[0]} by the applied copy (the "
            f"pure loader's): the patched copy reads a held-out.yaml the pure SafeLoader "
            f"{'refuses' if text.refused else 'reads'} differently; before {b[1]!r}; after {a[1]!r}")
    # The applied copy (the pinned gov's pure loader) as DEC-218 and the held-out rule have it: the harness is sound.
    if text.refused:
        assert decided == {w: ("deny", "deny") for w in reads}, (
            f"{text.id}: the applied copy did not stop both calls on a held-out.yaml the pure loader refuses: "
            f"{decided}")
    else:
        assert decided == {"the planted file the entry names": ("deny", "deny"),
                           "an ordinary file of the project": ("allow", "allow")}, (
            f"{text.id}: the clean text was not decided as the held-out rule has it: {decided}")
