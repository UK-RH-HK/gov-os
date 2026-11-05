"""KPI 4 (and F1): a configured size limit with least-recently-used eviction; a revision change starts a new key
space and never serves another revision's vector."""

from __future__ import annotations

import w2_126_support as S

BOUND = 96 * 1024        # bytes: room for some dozens of the 1 KiB vectors below, far fewer than the case asks
DIMENSIONS = 256         # 1 KiB a vector
FRESH = 240              # questions asked after the old ones: well past the bound
TOUCH_EVERY = 8          # the kept question is asked again this often, so it is always among the most recent


def question(name):
    return f"what does the ledger say about item {name}"


def test_least_recently_used_entries_go_first(box, stand_in, tmp_path):
    stand_in.dimensions = DIMENSIONS
    project = S.plant(tmp_path / "project", corpus={})
    kept, old = question("kept-0"), [question(f"old-{n}") for n in range(1, 10)]
    steps = [S.query(kept), *[S.query(text) for text in old], S.query(kept)]
    for n in range(FRESH):
        steps.append(S.query(question(f"fresh-{n}")))
        if n % TOUCH_EVERY == TOUCH_EVERY - 1:
            steps.append(S.query(kept))
    last = question(f"fresh-{FRESH - 1}")
    steps += [S.query(last), S.query(kept), S.query(old[0])]
    env = box.env(**{S.CACHE_BOUND_SETTING: BOUND})
    answers = box.run(project, steps, env)
    assert all(answer["vector"] for answer in answers), {answer["reason"] for answer in answers}

    assert len(stand_in.sent_with(kept)) == 1, "the most recently used entry was evicted"
    assert len(stand_in.sent_with(last)) == 1, "the newest entry was evicted"
    assert len(stand_in.sent_with(old[0])) == 2, "an entry unused since long before the bound was reached was kept"
    size = sum(path.stat().st_size for path in S.files_under(box.cache_dir))
    assert 0 < size <= BOUND, f"the cache takes {size} bytes, past its bound of {BOUND}"


QUESTION = "when is bronze poured into the sand moulds"


def test_a_revision_change_is_a_new_key_space(box, stand_in, tmp_path):
    first = S.plant(tmp_path / "first")
    box.build(first)
    [one] = box.run(first, [S.query(QUESTION)])
    texts_one = sorted(stand_in.texts())

    stand_in.revision = S.REVISION_2
    stand_in.reset()
    second = S.clone(first, tmp_path / "second")
    # Rewrite-Reason: W2-32's S2 (DEC-1064): a revision that no pin names fails closed, so the second project pins
    # the new revision in its models.yaml (W2-32's interface; untracked, so its corpus is the first's). The first and
    # third stay on the default pin, which REVISION_1 begins with.
    (second / "governance/project/models.yaml").write_text(
        f"embedder:\n  model: {S.MODEL}\n  revision: {S.REVISION_2}\n", encoding="utf-8")
    box.build(second)
    [two] = box.run(second, [S.query(QUESTION)])
    assert sorted(stand_in.texts()) == texts_one, "with a new revision, texts were served from the old one's cache"
    old, new = S.store_vectors(first), S.store_vectors(second)
    assert not set(old.values()) & set(new.values()), "a vector of the old revision was served for the new one"
    assert two["vector"] != one["vector"]

    stand_in.revision = S.REVISION_1
    stand_in.reset()
    third = S.clone(first, tmp_path / "third")
    box.build(third)
    [three] = box.run(third, [S.query(QUESTION)])
    assert stand_in.texts() == [], "the first revision's entries were lost when the revision changed"
    assert S.store_vectors(third) == old and three["vector"] == one["vector"], \
        "the new revision's vector was served for the old one"
