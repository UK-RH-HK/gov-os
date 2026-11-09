"""The machine-wide resource gate (W2-20): ``gov resources``, its configuration, readings, registry and slots."""


def check_disk(env=None) -> dict:
    """The shared disk's reading for ``gov close`` (S4): ``gov.resources.gate.check_disk``."""
    from gov.resources.gate import check_disk as check
    return check(env)
