import pytest
import yaml

from govbridge.core import yamlutil


def test_duplicate_key_is_refused():
    with pytest.raises(yaml.constructor.ConstructorError):
        yamlutil.load_yaml_text("a: 1\na: 2\n")


def test_unique_keys_load_normally():
    assert yamlutil.load_yaml_text("a: 1\nb: 2\n") == {"a": 1, "b": 2}


def test_canonical_json_is_key_sorted_and_compact():
    assert yamlutil.canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_canonical_hash_is_stable_across_key_order():
    h1 = yamlutil.canonical_hash({"a": 1, "b": 2})
    h2 = yamlutil.canonical_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert len(h1) == 64


def test_sha256_file_matches_sha256_text(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("hello world")
    assert yamlutil.sha256_file(str(p)) == yamlutil.sha256_text("hello world")
