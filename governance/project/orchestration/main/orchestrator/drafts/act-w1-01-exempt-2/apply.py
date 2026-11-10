p = 'governance/project/path-map.yaml'
s = open(p).read()
a = '''  - commit: "0568d91baf566b4d8f3ccb448e51af41cbb46d03"
    decision: DEC-1031
'''
m = '    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)\n'
b = a + '''  - commit: "cade65dfe0454bb1b34c6a44bd475a9d67c5e45e"
''' + m + '''  - commit: "04460404ea8a07bfb3f3f0019d3384e30c7f9466"
''' + m + '''  - commit: "8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a"
''' + m + '''  - commit: "ab169d051b82072f0db4350b2066eabf6919ffa0"
''' + m + '''  - commit: "15952bbfa576dcfabb7d36d95912a848077e5c3c"
    decision: DEC-1123  # item (3); the owner's ACT-GUARD-SETS-1 commit deleted W2-84's hidden-half cases (DEC-1061, DEC-1097)
'''
assert s.count(a) == 1
open(p, 'w').write(s.replace(a, b))
