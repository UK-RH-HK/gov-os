from lib.core.engine import run


def test_run():
    assert run("Hello World", 42) == "hello-world:10"
