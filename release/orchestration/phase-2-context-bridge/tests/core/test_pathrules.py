from govbridge.core import pathrules


def test_glob_match_basic():
    assert pathrules.glob_match("a/b/c.py", "**/*.py")
    assert pathrules.glob_match("c.py", "**/*.py")  # "**/" also matches at the top level
    assert not pathrules.glob_match("c.txt", "**/*.py")


def test_glob_match_rooted_pattern_does_not_match_nested():
    assert pathrules.glob_match("target/foo", "target/**")
    assert not pathrules.glob_match("a/target/foo", "target/**")


def test_any_glob_match_returns_first_hit_or_none():
    assert pathrules.any_glob_match("a/.env", ["**/*.pem", "**/.env"]) == "**/.env"
    assert pathrules.any_glob_match("a/x.txt", ["**/*.pem", "**/.env"]) is None


def test_top_level_dir_match_exact_file_and_directory():
    names = ["runtime", "Cargo.toml"]
    assert pathrules.top_level_dir_match("Cargo.toml", names) == "Cargo.toml"
    assert pathrules.top_level_dir_match("runtime/src/x.rs", names) == "runtime"
    assert pathrules.top_level_dir_match("runtime2/src/x.rs", names) is None  # not a true prefix match
    assert pathrules.top_level_dir_match("docs/x.md", names) is None
