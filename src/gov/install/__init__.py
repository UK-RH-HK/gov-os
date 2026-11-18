"""The pinned install (W2-18, DAEO-057v; CAP-43): a repository runs a fixed, hash-verified release of gov.

The pin lives in the repository's git common dir, ``<common>/gov/``, shared by every worktree and never tracked:
``envs/<version>/`` (a virtual environment with the system's packages, the release's wheel installed with
``pip --no-deps --no-index``), ``bin/gov`` (a link to the environment's ``gov``, switched by an atomic rename) and
``pin.json`` (the version, the wheel's name and sha256, the manifest's sha256, the source, the release commit, the
environment and the hash check).

- ``locate``: the git common dir, found by walking up from a folder, without a subprocess;
- ``dispatch``: a ``gov`` started inside a repository with a pin re-runs the pin's gov (``GOV_PIN=off`` aside);
- ``pin``: ``gov install`` itself;
- ``probe``: what doctor's section ``install`` reads of an environment and of an imported package.

This package's top level imports nothing: ``gov.cli.main`` imports ``dispatch`` on every start.
"""
