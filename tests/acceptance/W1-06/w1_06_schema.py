"""A small JSON Schema validator for the W1-06 acceptance tests (standard library only).

A copy of W1-04's ``w1_04_schema.py``, kept here so that this suite does not
depend on another ticket's test helpers.

The tests may install nothing, so they cannot use a validator package. This one
knows the part of JSON Schema draft 2020-12 that the repository's schemas use
(``schemas/records/``) and a little more:

``type``, ``enum``, ``const``, ``required``, ``properties``,
``additionalProperties``, ``patternProperties``, ``propertyNames``,
``minProperties``, ``maxProperties``, ``dependentRequired``, ``items``,
``prefixItems``, ``minItems``, ``maxItems``, ``uniqueItems``, ``minLength``,
``maxLength``, ``pattern``, ``minimum``, ``maximum``, ``exclusiveMinimum``,
``exclusiveMaximum``, ``allOf``, ``anyOf``, ``oneOf``, ``not``,
``if``/``then``/``else``, and ``$ref`` to a place inside the same file.

Annotations are ignored: ``$schema``, ``$id``, ``$comment``, ``$anchor``,
``title``, ``description``, ``examples``, ``default``, ``deprecated``,
``readOnly``, ``writeOnly``, ``format``, ``$defs``, ``definitions`` and every
key that starts with ``x-``.

Any other keyword raises ``UnsupportedKeyword``: a rule this validator cannot
check must not pass in silence.
"""

from __future__ import annotations

import re

ANNOTATIONS = frozenset({
    "$schema", "$id", "$comment", "$anchor", "title", "description", "examples", "default", "deprecated",
    "readOnly", "writeOnly", "format", "$defs", "definitions",
})


class UnsupportedKeyword(AssertionError):
    """The schema uses a keyword this validator does not know."""


def _is_type(value, name):
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise UnsupportedKeyword(f"type {name!r}")


def _resolve(ref, root):
    if not ref.startswith("#"):
        raise UnsupportedKeyword(f"$ref to another file: {ref!r}")
    node = root
    for part in ref[1:].split("/"):
        if part == "":
            continue
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def errors(instance, schema, root=None, where="$"):
    """Every way ``instance`` breaks ``schema``; an empty list when it is valid."""
    root = schema if root is None else root
    if schema is True:
        return []
    if schema is False:
        return [f"{where}: nothing is allowed here"]
    if not isinstance(schema, dict):
        raise UnsupportedKeyword(f"a schema that is neither an object nor a boolean at {where}")
    found = []

    def sub(value, subschema, at=where):
        return errors(value, subschema, root, at)

    for key, rule in schema.items():
        if key in ANNOTATIONS or key.startswith("x-") or key in ("then", "else"):
            continue
        if key == "$ref":
            found += sub(instance, _resolve(rule, root))
        elif key == "type":
            names = rule if isinstance(rule, list) else [rule]
            if not any(_is_type(instance, name) for name in names):
                found.append(f"{where}: is not of type {rule}")
        elif key == "enum":
            if instance not in rule:
                found.append(f"{where}: is not one of {rule}")
        elif key == "const":
            if instance != rule:
                found.append(f"{where}: is not {rule!r}")
        elif key == "allOf":
            for part in rule:
                found += sub(instance, part)
        elif key == "anyOf":
            if all(sub(instance, part) for part in rule):
                found.append(f"{where}: matches none of anyOf")
        elif key == "oneOf":
            if sum(1 for part in rule if not sub(instance, part)) != 1:
                found.append(f"{where}: does not match exactly one of oneOf")
        elif key == "not":
            if not sub(instance, rule):
                found.append(f"{where}: matches what `not` forbids")
        elif key == "if":
            branch = "then" if not sub(instance, rule) else "else"
            if branch in schema:
                found += sub(instance, schema[branch])
        elif key in ("required", "properties", "additionalProperties", "patternProperties", "propertyNames",
                     "minProperties", "maxProperties", "dependentRequired"):
            if not isinstance(instance, dict):
                continue
            if key == "required":
                found += [f"{where}: lacks {name!r}" for name in rule if name not in instance]
            elif key == "properties":
                for name, part in rule.items():
                    if name in instance:
                        found += sub(instance[name], part, f"{where}.{name}")
            elif key == "patternProperties":
                for pattern, part in rule.items():
                    for name, value in instance.items():
                        if re.search(pattern, name):
                            found += sub(value, part, f"{where}.{name}")
            elif key == "additionalProperties":
                known = set(schema.get("properties", {}))
                patterns = list(schema.get("patternProperties", {}))
                for name, value in instance.items():
                    if name in known or any(re.search(p, name) for p in patterns):
                        continue
                    found += sub(value, rule, f"{where}.{name}")
            elif key == "propertyNames":
                for name in instance:
                    found += sub(name, rule, f"{where} (key {name!r})")
            elif key == "minProperties":
                if len(instance) < rule:
                    found.append(f"{where}: has fewer than {rule} keys")
            elif key == "maxProperties":
                if len(instance) > rule:
                    found.append(f"{where}: has more than {rule} keys")
            else:
                for name, needed in rule.items():
                    if name in instance:
                        found += [f"{where}: {name!r} needs {n!r}" for n in needed if n not in instance]
        elif key in ("items", "prefixItems", "minItems", "maxItems", "uniqueItems"):
            if not isinstance(instance, list):
                continue
            if key == "prefixItems":
                for index, part in enumerate(rule[:len(instance)]):
                    found += sub(instance[index], part, f"{where}[{index}]")
            elif key == "items":
                start = len(schema.get("prefixItems", []))
                for index in range(start, len(instance)):
                    found += sub(instance[index], rule, f"{where}[{index}]")
            elif key == "minItems":
                if len(instance) < rule:
                    found.append(f"{where}: has fewer than {rule} items")
            elif key == "maxItems":
                if len(instance) > rule:
                    found.append(f"{where}: has more than {rule} items")
            elif rule:
                seen = []
                for item in instance:
                    if item in seen:
                        found.append(f"{where}: holds {item!r} twice")
                    seen.append(item)
        elif key in ("minLength", "maxLength", "pattern"):
            if not isinstance(instance, str):
                continue
            if key == "minLength" and len(instance) < rule:
                found.append(f"{where}: is shorter than {rule}")
            elif key == "maxLength" and len(instance) > rule:
                found.append(f"{where}: is longer than {rule}")
            elif key == "pattern" and not re.search(rule, instance):
                found.append(f"{where}: does not match {rule!r}")
        elif key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
            if not _is_type(instance, "number"):
                continue
            if ((key == "minimum" and instance < rule) or (key == "maximum" and instance > rule)
                    or (key == "exclusiveMinimum" and instance <= rule)
                    or (key == "exclusiveMaximum" and instance >= rule)):
                found.append(f"{where}: breaks {key} {rule}")
        else:
            raise UnsupportedKeyword(
                f"the schema uses {key!r} at {where}, which the acceptance tests' validator cannot check"
            )
    return found
