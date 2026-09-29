"""``govbridge.compile`` -- the bounded context compiler (ARCHITECTURE.md section 7), the independent validator
(section 5.3), the receipt checker, checkpoint/renewal and the canonical worker bootstrap (node B6, BR-HO-0008).

This is where the hard authority invariant becomes observable: ``packet.py`` fills section A with nothing but the
resolver's own ``MandatoryItem``s, and ``validate.py`` -- a SEPARATE module, imported by ``packet.py``, ``receipt.py``
and any grader, never the reverse -- recomputes the resolver from scratch and refuses a packet whose section A, or
whose section ordering, disagrees.
"""
