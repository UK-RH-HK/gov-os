"""Step 3 of the build: the counts schema's `reanchor` key, kinds.yaml's `input_reanchor`, and the one W2-149 pin that
every root key but the optional ones must be required (run in the work clone, from its top folder)."""

def edit(path, old, new):
    s = open(path).read()
    assert s.count(old) == 1, (path, old, s.count(old))
    open(path, "w").write(s.replace(old, new))


def count_prop(name):
    return f'''        "{name}": {{
          "type": [
            "integer",
            "null"
          ],
          "minimum": 0
        }}'''


schema = "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json"
edit(schema, '''      "description": "The one-question fix flow only (W2-94 S13, DEC-1180 (4)): its question id, its reason code and the action the delivered result names; action null until a delivered result names it (dry, refused, stopped)."
    }
  }
}''', '''      "description": "The one-question fix flow only (W2-94 S13, DEC-1180 (4)): its question id, its reason code and the action the delivered result names; action null until a delivered result names it (dry, refused, stopped)."
    },
    "reanchor": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "week",
        "entries",
        "ids",
        "absent",
        "corrected",
        "replaced"
      ],
      "properties": {
        "week": {
          "type": "string",
          "pattern": "^[0-9]{4}-W[0-9]{2}$"
        },
''' + ",\n".join(count_prop(n) for n in ("entries", "ids", "absent", "corrected", "replaced")) + '''
      },
      "description": "The weekly re-anchoring flow only (ACT-WALLS-REANCHOR-1, DEC-1179 (6)): its week and numbers only: the request's rows (entries), the questions staged (ids), the requested ids with no hidden file (absent), and the delivered result's corrected and replaced; each null until known (dry, refused, stopped)."
    }
  }
}''')

kinds = "governance/project/indep-walls/kinds.yaml"
edit(kinds, '''    input_round2: [set, notes]    # its own round-1 set and the checker's notes, copied in read-only
''', '''    input_round2: [set, notes]    # its own round-1 set and the checker's notes, copied in read-only
    # The weekly re-anchoring flow (ACT-WALLS-REANCHOR-1; DEC-1179 (6), DEC-1178 (1)): on the writer's round 2 the launch
    # script stages, from the memory audit's REANCHOR-<week>.json, each listed question's hidden file as a read-only copy
    # and the request itself (question ids and entry numbers only). The script refuses the flow (11) unless this line is
    # in the approved template, so the owner's approval of this file is what opens the input.
    input_reanchor: [questions, reanchor]
''')

edit("tests/unit/orchestration/test_w2_149_indep_launch.py", 'id(whole): {"fix"}}', 'id(whole): {"fix", "reanchor"}}')
print("step 3 ok")
