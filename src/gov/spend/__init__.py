"""The runaway brake in the product (W2-156; EMERGENCY-TOOLS-1 D2; DEC-1091 (2), DEC-1126 (4), DEC-1119 (5)).

``gov spend check | clear <ticket> [--projection-usd N] --note <text> | sum``. A ticket's running cost is the sum of
the measured cost of its session records (W2-60b, ``.gov-runtime/sessions/``) since its first launch or since the
last clear; its projection is the one its latest launch record (W2-60a, ``.gov-runtime/launches/``, key
``projection_usd``, filled by ``gov launch --projection-usd``) or its latest clear gives. Past twice that projection,
``check`` writes one brake record, one marker (``.gov-runtime/spend/braked/<ticket>.json``) and one inbox item, and
``gov launch`` refuses the ticket (``SPEND_BRAKED``) until ``clear``. Usage stays record-only (DEC-1089 (3)): the brake
holds a new launch, stops no running session and sends nothing outside the project's inbox. ``brake`` holds the rule;
``command`` is the command line.
"""
