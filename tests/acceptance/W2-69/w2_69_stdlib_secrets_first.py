"""A pytest plugin of the W2-69 tests, loaded first with ``-p``: it imports the standard library's ``secrets`` before
any test is collected, as pytest-rerunfailures and pytest-randomly do (W2-L373). Neither is installed on this machine,
and nothing may be installed, so this plugin stands in for them."""

import secrets

STDLIB_SECRETS = secrets.__file__


def pytest_report_collectionfinish(config, start_path, items):
    return [f"w2-69 plugin: the standard library's secrets was imported first ({STDLIB_SECRETS})"]
