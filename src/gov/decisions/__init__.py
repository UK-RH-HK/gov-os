# gov.decisions -- the decision checker: decision hazards, owner approval facts and gates that do not authorise (W1-11);
# the register's tags and the propagation of supersession (W2-55), kept out of ``check``'s list
from gov.decisions.checker import check

__all__ = ["check", "check_propagation", "check_tags"]


def check_tags(root):
    """The register checks of ``gov.decisions.tags`` (imported when called, so ``python3 -m`` runs it alone)."""
    from gov.decisions.tags import check_tags as run
    return run(root)


def check_propagation(root):
    """The supersession check of ``gov.decisions.propagation``."""
    from gov.decisions.propagation import check_propagation as run
    return run(root)
