"""W1-06 — the Superpowers entry's sha256 is a digest of the committed vendor folder.

DEC-199 (DP-5, option (a)): "The Superpowers entry's ``sha256`` is a digest of
the committed vendor folder: the sha256 of the sorted lines
``<sha256 of the file>  <relative path>`` over every file under
``template/governance/kernel/vendor/superpowers/``. A test and ``gov doctor``
recompute it offline."

The rule, as read here (README, readings 29 to 34):

- every file: each file ``HEAD`` holds under the vendor folder, with its
  committed bytes;
- one line per file: the file's sha256 in lowercase hexadecimal, two spaces,
  the path relative to the vendor folder (``/`` between components, no leading
  ``./``), one line feed;
- the lines are encoded as UTF-8, sorted as bytes and concatenated; the digest
  is the sha256 of those bytes, in lowercase hexadecimal.

In a clean checkout it is what this prints::

    cd template/governance/kernel/vendor/superpowers
    git ls-files -z | xargs -0 sha256sum | LC_ALL=C sort | sha256sum

Nothing is installed, downloaded or run but git, which is asked what ``HEAD``
holds. Neither case is ``local_only``.
"""

from __future__ import annotations

import hashlib

import w1_06_support as support

NAMES = ("superpowers",)

# Two files, hashed by hand with sha256sum: `printf 'hello\n'` and an empty file.
SAMPLE = {"b.txt": b"hello\n", "a/c.txt": b""}
SAMPLE_LINES = (
    b"5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03  b.txt\n"
    b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  a/c.txt\n"
)
SAMPLE_DIGEST = "ac145d7010e00fbb8972a663e0c05abbb20592a361fa8169167602cf6125539a"


def test_the_digest_rule_gives_the_value_worked_out_by_hand():
    """The rule on two files, against a value computed with ``sha256sum`` alone.

    The lines are sorted as lines, so by the file's digest first: ``b.txt``
    (``5891…``) comes before ``a/c.txt`` (``e3b0…``). Each line, the last one
    too, ends with a line feed.
    """
    assert hashlib.sha256(SAMPLE_LINES).hexdigest() == SAMPLE_DIGEST
    assert support.folder_digest(SAMPLE) == SAMPLE_DIGEST


def test_the_superpowers_sha256_is_the_digest_of_the_committed_vendor_folder(registry):
    """DEC-199: recomputed from the folder as ``HEAD`` holds it, and compared with the registry's value."""
    files = support.committed_files(support.VENDOR_REL)
    expected = support.folder_digest(files)
    recorded = str(support.one(registry, NAMES).get("sha256", "")).strip().lower()
    assert recorded == expected, (
        f"the registry records sha256 {recorded} for Superpowers; the digest of the {len(files)} committed files "
        f"under {support.VENDOR_REL}/ is {expected} (DEC-199: the sha256 of the sorted lines "
        f"`<sha256 of the file>  <path relative to that folder>`, each ended by a line feed)"
    )
