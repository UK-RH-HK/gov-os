"""W2-107: the cache holds digests, kinds, fingerprints and verdicts only; never content, a path, a name or a secret.

KPI success 5 (the cache holds hashes and verdicts only, never content, a path or a secret's text); failure 4 (content,
a path or a secret's text written into the cache). The cache file and its ``-wal`` and ``-shm`` companions are read as
bytes, while the process that wrote them still runs and again after a process of its own has written and ended.
"""

from __future__ import annotations

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools


def needles(project, contents, names):
    """Every distinctive string the case judged, in the encodings a store could hold it in."""
    texts = [*contents, *names, str(project), support.planted(), *(name.rsplit("/", 1)[-1] for name in names)]
    return {text: [text.encode("utf-8"), text.encode("utf-16-le"), text.encode("utf-16-be")] for text in texts}


def test_the_cache_holds_no_content_no_path_no_name_and_no_secret(project, engine, cache):
    marks = [support.joined("w2107", "content", "mark", str(number), "q") for number in range(3)]
    contents = [f"W2-107 note: {mark} is a distinctive word." for mark in marks]
    rels = support.put(project, {f"docs/page-{number}.md": text + "\n" for number, text in enumerate(contents)})
    secret = support.put(project, {"docs/planted.md": f"The value is {support.planted()} today.\n"})
    names = [f"docs/{support.joined('w2107', 'pathmark', str(number))}/{support.joined('w2107', 'leaf', str(number))}.md"
             for number in range(3)] + [f"docs/{support.planted()}/page.md"]
    for _ in range(2):
        assert secrets.indexable(project, rels + secret) == rels
        assert [secrets.path_holds_secret(project, name) for name in names] == [False, False, False, True]
    env = support.child_env(engine, cache)
    other = support.put(project, {"docs/child.md": f"W2-107 note: {support.joined('w2107', 'childmark')} too.\n"})
    run = support.run_child(project, other + secret, names, env)
    assert run.error is None and run.indexable == other
    found = support.cache_files(cache)
    assert cache in found, "the cache file was made (so there is something to read)"
    words = [*marks, support.joined("w2107", "childmark"), *(support.joined("w2107", kind, str(number))
                                                             for kind in ("pathmark", "leaf") for number in range(3))]
    for path in found:
        data = path.read_bytes()
        for text, forms in needles(project, contents + words, names).items():
            assert not any(form in data for form in forms), \
                f"{path.name} holds a string the filter judged ({'the secret' if support.planted() in text else 'a text or name'})"
