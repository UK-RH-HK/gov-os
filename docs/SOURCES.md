# Sources

This tree was rebuilt from the Governance OS v4 line. Nothing was deleted from history.

- Archive tag: `archive/gov-os-v4-final` (annotated), at BASE
- BASE: `1ab6782fa4e8f490c8b97ac6959cdd77a29350f9` (tip of `bridge/p2-context-retrieval` at restructure)
- Pre-restructure bundle: `~/gov-os-inventory/restructure/pre-restructure.bundle`, sha256 `efafe460af693d4159ba4549067309c20c5a2def2aabc0284527aacfc0532434`
- Former branches: kept as `refs/archive/heads/<name>`; list them with `git for-each-ref refs/archive/heads`

To retrieve archived material:

```bash
git show archive/gov-os-v4-final:<path>                 # any file as it was at BASE
git for-each-ref refs/archive/heads     # the former branches
git show refs/archive/heads/<name>:<path>
```

Everything under `docs/source/` is reference only. It is excluded from agents (`.claude/settings.json`) and is superseded by the ADRs in `docs/adr/` where they conflict.

## Carried files (216)

sha256 is of the file content at BASE (for the V8.3 panel, of the copied file).

| New path | Original path | Inventory row | sha256 |
|---|---|---|---|
| `.gitignore` | `.gitignore` | R004 (edited: lines appended) | `bd7f7b235daed86247e4a0830a335ed7928ba8dd29f1aa107e2a5640fbde1f1f` |
| `cli/config/authority-registry.yaml` | `release/orchestration/phase-2-context-bridge/config/authority-registry.yaml` | R079 | `6af2e627661239f834dcd26225866e165efd8812962a1e777d58f63596a31416` |
| `cli/config/canonical-view.yaml` | `release/orchestration/phase-2-context-bridge/config/canonical-view.yaml` | R077 | `3184499a276cd93c81025dbae7c8633d9e6c97a9908f646b276db0232a760b03` |
| `cli/config/corpus-rules.yaml` | `release/orchestration/phase-2-context-bridge/config/corpus-rules.yaml` | R076 | `87fb5010db3018e21c99be60c2072dcb83fcd31bf931b094280771c895430985` |
| `cli/config/embed-profile.yaml` | `release/orchestration/phase-2-context-bridge/config/embed-profile.yaml` | R079 | `aba815ca58612c54e1e76674cff2aa4e5aa8eb905ea61aae51a486d060c3f2a0` |
| `cli/config/facets.yaml` | `release/orchestration/phase-2-context-bridge/config/facets.yaml` | R079 | `4fa6f8bb8edb2ad61a39a9513a9dca83a4068b96390d44b47208464c1ff17549` |
| `cli/config/id-grammar.yaml` | `release/orchestration/phase-2-context-bridge/config/id-grammar.yaml` | R076 | `7a0ad25350e6ea8a926c43f24c0201c57417f8b68ec9767752c08eadd6c0f364` |
| `cli/config/model-pin.yaml` | `release/orchestration/phase-2-context-bridge/config/model-pin.yaml` | R076 | `9fc40e573a18d6f603014eb8ef7fd9ea7bd8c31ed23064b25be22f68686f3222` |
| `cli/config/requirements.lock` | `release/orchestration/phase-2-context-bridge/config/requirements.lock` | R078 | `896aaed6e3f594f9469d3b403dc38a1b25c40803561f5961930dfd5e3e7bf8ef` |
| `cli/config/schemas/authority-registry.yaml` | `release/orchestration/phase-2-context-bridge/ARCHITECTURE/schemas/authority-registry.yaml` | R081 | `245108e4a909116a8166b786325b332a4815b1e947912c2dc0bc10e4a3020aad` |
| `cli/config/state-aliases.yaml` | `release/orchestration/phase-2-context-bridge/config/state-aliases.yaml` | R079 | `6d7af11bdb9804ea3588d1ebbd5a928b859e0ad6c5a5d55a63b721750add0969` |
| `cli/govbridge/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/__init__.py` | R071 | `9815be874dbd2d31b150e80690a79f38224933b457dfa2379a20298e85f3c890` |
| `cli/govbridge/authority/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/__init__.py` | R064 | `5be3738a72b842628d48645cf933faf9c27ac13726ada568d35a62ba555ca274` |
| `cli/govbridge/authority/classes.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/classes.py` | R064 | `7cde2c2f617ea4af752d8d92727c0e9e9c23954d4a69ce34fbf480984d11705f` |
| `cli/govbridge/authority/layer.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/layer.py` | R064 | `7f98df44c3d20cc5ac20e5f3d275aec228b3a8c400ce5dbf7a5491241376064a` |
| `cli/govbridge/authority/lifecycle.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/lifecycle.py` | R064 | `e040cc5c37c763038c901e7750557a3d4a2b99ebfd4c1067552e0acdc2bc2074` |
| `cli/govbridge/authority/records.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/records.py` | R064 | `6958afc4a1b4d7848e6b0aba9bd8239184f25043f8121bbbcd0bbed30bb4bc08` |
| `cli/govbridge/authority/registry.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/registry.py` | R064 | `99c6f5d4066d7e50b489852b0f86c4fcb2b40812f4f41a68274101c56a442d02` |
| `cli/govbridge/authority/resolver.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/resolver.py` | R064 | `31324cc051c8eae93f1aa6eca874bfc3e686fdc0c7411c9b21b890fadcadb057` |
| `cli/govbridge/authority/state.py` | `release/orchestration/phase-2-context-bridge/govbridge/authority/state.py` | R064 | `5ae6d6c3158afefe0d504e35c59b538761346ee394b175e633c6f8d4626f5d3e` |
| `cli/govbridge/compile/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/compile/__init__.py` | R067 | `e33d97455646c43baf91e39a6941c2db1d30968126f957571635a7d25226242a` |
| `cli/govbridge/compile/sectionmap.py` | `release/orchestration/phase-2-context-bridge/govbridge/compile/sectionmap.py` | R066 | `fc4928f36bdec55f4aa4bf95654faaf20ebde813f5c3ee597242036bfea52e0f` |
| `cli/govbridge/core/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/__init__.py` | R065 | `1b76b694c3e38028e59d75d5b50c285fe8c0d132e3437e384d523c3bb913ef1b` |
| `cli/govbridge/core/chunking.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/chunking.py` | R065 | `1d172b6640bea7dc520cc4b6fea932b6b457330852c70653c2ae38beef08a845` |
| `cli/govbridge/core/corpus.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/corpus.py` | R065 | `fc699ce2e81f5c195b1d27b5ac61ebe732c8a55e07c92ff47352d85d00ceba7b` |
| `cli/govbridge/core/freshness.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/freshness.py` | R065 | `0cdf63e9d79100da2c5225c66c239d0d380866924acd99880f4bc325d7e0318c` |
| `cli/govbridge/core/gitobj.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/gitobj.py` | R065 | `af6b03cde0617765505755fe78662085be8aacc146974f002f21f0f1d4888c1e` |
| `cli/govbridge/core/manifest.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/manifest.py` | R065 | `e59c6fcb34a0a9067d26f8813e62755d2d5de176159f4d44ef8832c025d0d8bf` |
| `cli/govbridge/core/pathrules.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/pathrules.py` | R065 | `411b5fae9f3a0d613b80808111b934943f221f86daee74c87f4302d8d85eba37` |
| `cli/govbridge/core/store.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/store.py` | R065 | `424bd9db609dbe9223bc0ebb220ac6afc605a59b03a381a92608450f058d5b22` |
| `cli/govbridge/core/taskctx.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/taskctx.py` | R065 | `2d8b62dc83e597bf755a1d617d08997eeb2191eaa83d725282808d6a65d028e0` |
| `cli/govbridge/core/telemetry.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/telemetry.py` | R065 | `f09ed0e6a82b2059de0d048a3b7e76f941d1327afef1ed6248987c5c8344815e` |
| `cli/govbridge/core/view.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/view.py` | R065 | `894b5b9411e9e50f345714fa4714f9b49c021535123c66a0e713a346a453e1c1` |
| `cli/govbridge/core/yamlutil.py` | `release/orchestration/phase-2-context-bridge/govbridge/core/yamlutil.py` | R065 | `ea4ddab63808572e460ac06b422322fb6bf8f997034871ebcf00d1de76c2fd6e` |
| `cli/govbridge/gather/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/gather/__init__.py` | R063 | `9158a6a352988e65ebd01b2c1e6fbfe652e8940f0dea0242bc4ce4d1cd13dce6` |
| `cli/govbridge/gather/facets.py` | `release/orchestration/phase-2-context-bridge/govbridge/gather/facets.py` | R063 | `7e358dbff1bb950785df9e2bd7f728f47bd434a4ddfc72ee028eb364074d8147` |
| `cli/govbridge/graph/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/graph/__init__.py` | R069 | `f9f0dd255380bc7d6929f80a969a6eaee22ee3d5998f1477ae7273454cbb2d10` |
| `cli/govbridge/graph/edges.py` | `release/orchestration/phase-2-context-bridge/govbridge/graph/edges.py` | R069 | `53dcf9743aa4a0e9ea12b20937b5429c2444dfe58c90d5a0ddc12881a85f1b57` |
| `cli/govbridge/lexical/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/lexical/__init__.py` | R059 | `cc356a4c25e8fc1c342e0ff8b1e7dd03c7ded320f9db0f6852d437f420a99136` |
| `cli/govbridge/lexical/fts.py` | `release/orchestration/phase-2-context-bridge/govbridge/lexical/fts.py` | R059 | `6b9e2b42c23b8d43e890b58cad68b224d1b627aad797f643091126e2be53cf62` |
| `cli/govbridge/lexical/query.py` | `release/orchestration/phase-2-context-bridge/govbridge/lexical/query.py` | R059 | `a14ad99b4edd09f232500e4945b1190e11a4ce285c063af3cdf612fe7c18f7c6` |
| `cli/govbridge/semantic/__init__.py` | `release/orchestration/phase-2-context-bridge/govbridge/semantic/__init__.py` | R061 | `8040a8b341d706ea2c3e4535e44673e52d9fed894a5c0e2dfff51230d08e5e2e` |
| `cli/govbridge/semantic/freshness_layer.py` | `release/orchestration/phase-2-context-bridge/govbridge/semantic/freshness_layer.py` | R061 | `2a59ac1a207c552f39cfec1940138c1b7dd994824120ae612b6513ccfd9af8a4` |
| `cli/govbridge/semantic/modelpin.py` | `release/orchestration/phase-2-context-bridge/govbridge/semantic/modelpin.py` | R060 | `0ea6f07c369e1bbe369abe79458ed372476d593a303265559ab4da714af77fdd` |
| `cli/govbridge/semantic/profile.py` | `release/orchestration/phase-2-context-bridge/govbridge/semantic/profile.py` | R060 | `53c780c7524f745af14edfd250173a6322732cf1c8dc6f57659d2fd60708384a` |
| `cli/govbridge/semantic/runner.py` | `release/orchestration/phase-2-context-bridge/govbridge/semantic/runner.py` | R061 | `527df30c67d14ee37ef619a116b221427cb46106f8ea7ab76ddd9c338ed1521e` |
| `cli/govbridge/semantic/vectors.py` | `release/orchestration/phase-2-context-bridge/govbridge/semantic/vectors.py` | R061 | `438545b63ca9c267956bf8d1a851a0a2fd98c871a37cea245d8afdd7185e631d` |
| `cli/tests/authority/conftest.py` | `release/orchestration/phase-2-context-bridge/tests/authority/conftest.py` | R074 | `870d43e181f1e0a6027637c2d149d4f4e4ad900419ef59fe900a7d9114201d0d` |
| `cli/tests/authority/test_classes.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_classes.py` | R074 | `63baff054753feb79a85ee40aadd6fb45bfce589898b78495fd382aa8e8d7839` |
| `cli/tests/authority/test_import_boundary.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_import_boundary.py` | R074 | `e3575a9e75dc556870dc9203d53cf5c68adb77184fac0bc284dc3f691f412433` |
| `cli/tests/authority/test_layer.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_layer.py` | R074 | `84fd6af84fac2f9dfe5e8518077c8ec1b607e01553ae01f8fa12c15aa6ac9d76` |
| `cli/tests/authority/test_lazy_config.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_lazy_config.py` | R074 | `796743941edeed8e58be31f4e0680fb388ad2879d4c159593b851d0ff88e1c97` |
| `cli/tests/authority/test_lifecycle.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_lifecycle.py` | R074 | `fc1429819734856b7d4e67acf5ed21346c6ec88b77cdf42dd81ea7a760739e18` |
| `cli/tests/authority/test_records.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_records.py` | R074 | `857020a14b34e3c2c1078c1ef40697a76f74f4312dfaf8fff528eff2aec16070` |
| `cli/tests/authority/test_registry.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_registry.py` | R074 | `cecc15611b7e57e1f60480d7f2521d66652e72983ef09d32183de11e6ee99ce2` |
| `cli/tests/authority/test_resolver.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_resolver.py` | R074 | `c5a5d142a1b2cac9e5f4c301b9eaf9751574cd59f36469133c96386b2d4aed3e` |
| `cli/tests/authority/test_state.py` | `release/orchestration/phase-2-context-bridge/tests/authority/test_state.py` | R074 | `a7bb46d87da24d40ba433fba9e0f018afb0a75b0c5f2b6d18f5921deabd69225` |
| `cli/tests/core/conftest.py` | `release/orchestration/phase-2-context-bridge/tests/core/conftest.py` | R074 | `0ae04bf9f0802dfc739f2492cbf823501a0d0c31633d3a2f074e5b5470be39b8` |
| `cli/tests/core/test_chunking.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_chunking.py` | R074 | `44c73cfda6abbe7f3a3053f6e5f204c636f4c0f35f1f8d253ef66e5d3abd3c96` |
| `cli/tests/core/test_corpus.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_corpus.py` | R074 | `e900ccb57f359f6cb0ab844cfd2663c82a320f7857d58a827d68e01664224f56` |
| `cli/tests/core/test_freshness.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_freshness.py` | R074 | `5c33e478085222654da887c12fca0de40de44009a2dd0ef7823ad06671203758` |
| `cli/tests/core/test_freshness_entrypoint.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_freshness_entrypoint.py` | R074 | `a1a6c22e3abb0077e4ace017facf0517afd53e194a70b00aca434d9b93c22005` |
| `cli/tests/core/test_freshness_records_ref_override.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_freshness_records_ref_override.py` | R074 | `ec3b0b114f3007cdf83e95073ee3104ec970bf67c1ee71fed4785ba41312c0dd` |
| `cli/tests/core/test_gitobj.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_gitobj.py` | R074 | `a35ea6d91add113af95b98c41517e6fd4985ee194f7d27630da837e3e5064866` |
| `cli/tests/core/test_gitobj_repo_root.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_gitobj_repo_root.py` | R074 | `e8a71f577f3430dff3d7c7478baf9e1013c93f312e3557ad87474b8807f63c14` |
| `cli/tests/core/test_manifest.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_manifest.py` | R074 | `e82aa31f304bf2ad65a856feec74cf83629dec8f1f796a68cc45178bde3c42a4` |
| `cli/tests/core/test_pathrules.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_pathrules.py` | R074 | `34666828dc4e9fb8f0990983007fce7c08bde8839a65229352146bf86f321d9f` |
| `cli/tests/core/test_store.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_store.py` | R074 | `1f7371a7986d1e0065ace28c134f0aca3d278294d10fe21ba52aaa123c6fb7c8` |
| `cli/tests/core/test_telemetry.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_telemetry.py` | R074 | `a40cec2271a613ae11c5d0fada6afc2d39244d47073209c510da8bb5fc3f23ff` |
| `cli/tests/core/test_view.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_view.py` | R074 | `718bb2269b04f73249b6a818419a295f0ad8504b68294a35586aff6c828472f1` |
| `cli/tests/core/test_view_canonical_fallback.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_view_canonical_fallback.py` | R074 | `58b340211c99635919454783a3885c2902244301a38d130a2849a675d05af804` |
| `cli/tests/core/test_yamlutil.py` | `release/orchestration/phase-2-context-bridge/tests/core/test_yamlutil.py` | R074 | `ceb5b17dd0b1a7ed436088dd7f5213107cade95401bb3e20d9ef046595dc4f2d` |
| `cli/tests/fixtures/answers/answers_repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/answers/answers_repobuilder.py` | R072 | `9197a909ae2bdd381b88f1be9d63902148aae11c5a8856ff0b8a3ed75775dc18` |
| `cli/tests/fixtures/authority/authority_repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/authority/authority_repobuilder.py` | R072 | `e6bc69b3ce57bb9c0ef5563175f96e9b2c82bfc495b16c2f6beee1debd09297c` |
| `cli/tests/fixtures/authority/fixture-authority-registry.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/authority/fixture-authority-registry.yaml` | R072 | `ca68749332e67f9985f2bcf0c190bee76a60c20f0e5f17adf9a00988eef1085a` |
| `cli/tests/fixtures/compile/compile_repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/compile/compile_repobuilder.py` | R072 | `0e0452b1ab5dcf0155b49e32f5aeab5ef6205b58bdcbccf1f33aa9b84ffa56ff` |
| `cli/tests/fixtures/compile/mandatory/repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/compile/mandatory/repobuilder.py` | R072 | `1922216d7e73a414d1accfff6905849b0f0a6201a543c3942ad0151837ead0a4` |
| `cli/tests/fixtures/compile/recorded_view/repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/compile/recorded_view/repobuilder.py` | R072 | `c6a0b97fcabd6d1b1b0f46198bd99b7e9736f11a900d4dd7dbd723bc6e3b71d9` |
| `cli/tests/fixtures/compile/task-spec-d0006-control.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/compile/task-spec-d0006-control.yaml` | R072 | `08e06a34d5b2c09a62cd7006c0eb540d3bba63fb64746688fc21b744fdbd74d9` |
| `cli/tests/fixtures/controls/control-a/SELECTION.md` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/SELECTION.md` | R072 | `700be32c88b36413ecd0ca4d967302dc63e5a7cbf376036dab8a75eb5f54b3fc` |
| `cli/tests/fixtures/controls/control-a/baseline/compile.out` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/compile.out` | R072 | `28000e7b99adee510b4739660d10f632061ad6f6954335b73f68049ecc3af125` |
| `cli/tests/fixtures/controls/control-a/baseline/manifest-summary.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/manifest-summary.yaml` | R072 | `4bcbb60deb86614c9dd8900805425930be9be68b8f2198a2758e2a74ac4e7331` |
| `cli/tests/fixtures/controls/control-a/baseline/packet-verify.out` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/packet-verify.out` | R072 | `2a7e2cf12b69bf3eefefb16de13c51c6ed497a47c9e2b5975604da6f4f0e2df4` |
| `cli/tests/fixtures/controls/control-a/baseline/packet/manifest.json` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/packet/manifest.json` | R072 | `29ba1c3e69dd349bdd09421f1b2c01af2cc63f17ed9790f0828f5d613cb50c9a` |
| `cli/tests/fixtures/controls/control-a/baseline/packet/meta.json` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/packet/meta.json` | R072 | `0dff7b7e78bfa576a9ed28338b3e31dbcdf19a3ac03cb17d7eac59449d8ee762` |
| `cli/tests/fixtures/controls/control-a/baseline/packet/packet.md` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/packet/packet.md` | R072 | `2659c18572441499a391662e50a1418de8c5a8abef4d2056ba3879f79adc9a6b` |
| `cli/tests/fixtures/controls/control-a/baseline/packet/task_spec.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/packet/task_spec.yaml` | R072 | `d209b2d3f7016f026072bf4d059c3259b76528897f35b51e5d60b9a06857f8e7` |
| `cli/tests/fixtures/controls/control-a/baseline/selection-greps.out` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/baseline/selection-greps.out` | R072 | `5ee14210f85ab966fe8ba2bda524b491d63a4813347c2185d777ffd75e37da46` |
| `cli/tests/fixtures/controls/control-a/queries.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/queries.yaml` | R072 | `d6375e23848926835eaa80c2ab338464df5cf4d8ddf69147d88931c372a9a4c5` |
| `cli/tests/fixtures/controls/control-a/task-spec.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/controls/control-a/task-spec.yaml` | R072 | `439b8bf28b86b2ff81330fd0a9231fbf1a3a8e254aeda189a360478a10b24dec` |
| `cli/tests/fixtures/core/fixture-corpus-rules.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/core/fixture-corpus-rules.yaml` | R072 | `1c58faa893d443b6e26b2f32d958789a298936bcbb3aab0051f61c08c2292acc` |
| `cli/tests/fixtures/core/repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/core/repobuilder.py` | R072 | `b1f3d2003aa798ae46bc41a1a8b724908dc8b6387eb064be08572403aad53d25` |
| `cli/tests/fixtures/demo/rubric-gd9.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/demo/rubric-gd9.yaml` | R072 | `78e2820c33252d790aeb0513db160ef70cc870e805dd44c2f0d347dce834237f` |
| `cli/tests/fixtures/demo/transcript-gd6.jsonl` | `release/orchestration/phase-2-context-bridge/tests/fixtures/demo/transcript-gd6.jsonl` | R072 | `aba76a3ca2ccbf4db97159bdafc18cc7b6fa842112cb94f6b8bd27444675db03` |
| `cli/tests/fixtures/gather/fake_routes.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/gather/fake_routes.py` | R072 | `9d5b9809ce3fd69e684f36d585942b8b8768d8d8f1ea281304146546c5741a76` |
| `cli/tests/fixtures/gather/followup/followup_repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/gather/followup/followup_repobuilder.py` | R072 | `3f7aef441abd880f7c96ffe146d7a38a7791368c15db2f56aa11d616f00f353e` |
| `cli/tests/fixtures/gather/followup/hash_seed_probe.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/gather/followup/hash_seed_probe.py` | R072 | `8e5d030e4b5f997ec175c044a12b7fb9c76d47576bb9aea390219cd31e323cf1` |
| `cli/tests/fixtures/gather/gather_repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/gather/gather_repobuilder.py` | R072 | `447bb095a66d275d0631d48f3f2cbc96bc1e27803fb1fb17f37584e650275651` |
| `cli/tests/fixtures/gather/test-facets.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/gather/test-facets.yaml` | R072 | `22b876eec3cae66e772cd1bc4b562117481bf643d66f963125018826ae36d802` |
| `cli/tests/fixtures/integration/answers-g3-fail.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/integration/answers-g3-fail.yaml` | R072 | `71b099dee327d310c76e56a64111c2c8f383a39d5e7b5ae1b610ff885e49e294` |
| `cli/tests/fixtures/integration/answers-passing.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/integration/answers-passing.yaml` | R072 | `0dcf2f2d7abae0e50805b135c28ed0a160849ee5272b3f54f877526163486924` |
| `cli/tests/fixtures/integration/answers-upstream-only.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/integration/answers-upstream-only.yaml` | R072 | `60c4aa4738672cb78ba7c363dc21c92a6040ff676ae4e5e05d2092119884be51` |
| `cli/tests/fixtures/integration/demo-queries-synthetic.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/integration/demo-queries-synthetic.yaml` | R072 | `81adb1c49eeb27e2b74046e6305d2adb773f299e534135c83fe0031675726faf` |
| `cli/tests/fixtures/integration/oracle-synthetic.yaml` | `release/orchestration/phase-2-context-bridge/tests/fixtures/integration/oracle-synthetic.yaml` | R072 | `721b70d46bc51dde5d2dbbbd894112bb93e05254312e689e9dd525b546c37a45` |
| `cli/tests/fixtures/integration/reads-undeclared.json` | `release/orchestration/phase-2-context-bridge/tests/fixtures/integration/reads-undeclared.json` | R072 | `41af7da9d4c96e07c5e2fb1f17eb13fdf2bcea06b305db07e6617f1d619d3d78` |
| `cli/tests/fixtures/route/exclusions/exclusions_repobuilder.py` | `release/orchestration/phase-2-context-bridge/tests/fixtures/route/exclusions/exclusions_repobuilder.py` | R072 | `d2fc6431d072151e691143669a5370071eb832e106b87a37f8036658a74fac78` |
| `cli/tests/lexical/conftest.py` | `release/orchestration/phase-2-context-bridge/tests/lexical/conftest.py` | R072 | `cc2bd909eecb57832df511ede898ed6c997a5f64226d7212caf9c7e13aa7cb5f` |
| `cli/tests/lexical/test_fts.py` | `release/orchestration/phase-2-context-bridge/tests/lexical/test_fts.py` | R072 | `1723fdaea3f87833d455daa428ed2b981388a29c4b1cb82a279e589ddf938bff` |
| `cli/tests/lexical/test_query.py` | `release/orchestration/phase-2-context-bridge/tests/lexical/test_query.py` | R072 | `63225cd407e873968a34627572c1eb82b08e18753d5fd239344697f7e58ee0f1` |
| `cli/tests/semantic/conftest.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/conftest.py` | R074 | `bb089f8366404581eeb0b7e54e1dc1beade13bb93b0a2c90393292a4411cd4a4` |
| `cli/tests/semantic/test_adapter_protocol.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/test_adapter_protocol.py` | R074 | `e577194a22037c9d0977aeda53c36eb9ad80d3fe93244511b2b5c542d2525626` |
| `cli/tests/semantic/test_freshness_layer.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/test_freshness_layer.py` | R074 | `3d3e8ccd19ef56ed3144373ac5e8deca3ffb30b6fed97647e302eafc0adee12a` |
| `cli/tests/semantic/test_modelpin.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/test_modelpin.py` | R072 | `ead15ae5fd33cae27dd68617c458688a9b70fc6cb5e9d3fb2ff596ea8696fb62` |
| `cli/tests/semantic/test_profile.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/test_profile.py` | R072 | `d3eea78234fdbea7c396255ed2b6d576e69e32ac16aaeafe2eda0a32c8a3202b` |
| `cli/tests/semantic/test_vectors.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/test_vectors.py` | R074 | `516e4958dd34130645de6b18a8fba9f3d7fef721c66c1bd7b6872637d315c82b` |
| `cli/tests/semantic/test_vectors_resumability.py` | `release/orchestration/phase-2-context-bridge/tests/semantic/test_vectors_resumability.py` | R074 | `e7c4e70d0484f18f14c561e1843532ecd78a68b468fb2db0afca26e1e353602c` |
| `cli/tests/support/embedder_hashed_ngram.py` | `capabilities/python/govos_capabilities/embedder_hashed_ngram.py` | R039 | `be9ee9cee292d584b66534b180c14e6ec91d62e1477b701c3a5256cb80465820` |
| `docs/interfaces/API-0002.yaml` | `spec/interfaces/API-0002.yaml` | R009 | `62b5c9ef1122c446369c4338d0b85c7a548d73f55fa905e3d5e31d770c1caf8e` |
| `docs/source/control-panel/Governance_OS_Interactive_Stage_Control_Panel_FINAL_AUDITED_v8_2.html` | `release/orchestration/control-panel/Governance_OS_Interactive_Stage_Control_Panel_FINAL_AUDITED_v8_2.html` | R052 | `6fecfb6b2be86031137433a1cf7e960eeb9ca0c23b4890b2eb54c0546158269c` |
| `docs/source/control-panel/Governance_OS_Interactive_Stage_Control_Panel_v8_3_MASTER_DRAFT_v2.html` | `C:\Users\usain\Downloads\Governance_OS_Interactive_Stage_Control_Panel_v8_3_MASTER_DRAFT_v2.html (owner-supplied, outside Git)` | — (V8.3 panel) | `8e7dce78a31cc04d2e247d8eb3fbf34b8b946f8f81918e4162a08a821938fdce` |
| `docs/source/originals/DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md` | `DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md` | R001 | `66bfd86fca1f587000ce2e5c559653cd3d837121e62db5c60dea3b90946af8ca` |
| `docs/source/originals/GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md` | `GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md` | R001 | `de908bc282c78e8c60ea697355a44ef7c3de808c7f3fe2b194ffae35d09c62c5` |
| `docs/source/originals/GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md` | `GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md` | R001 | `4fee2e00359cd2e1cee5e506d9e982fb020e2bb32c2b4c71091b417b20530efc` |
| `docs/source/originals/Governance_OS_Capability_Acceptance_Contract_v3.md` | `Governance_OS_Capability_Acceptance_Contract_v3.md` | R002 | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| `docs/source/owner-records/bridge/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md` | `release/orchestration/phase-2-context-bridge/GATES/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md` | R053 | `44a206eda6d7c8228059115aef4f4bbaef2f8d6cb43eff8b4d4b30deb4154e16` |
| `docs/source/owner-records/bridge/OWNER-DIRECTION-BR-0003-VERIFIER-CHALLENGE-ITEMS.md` | `release/orchestration/phase-2-context-bridge/GATES/OWNER-DIRECTION-BR-0003-VERIFIER-CHALLENGE-ITEMS.md` | R053 | `4afbc78328f6069fb148022dcddf246470a057cac75794efec601d4529ac7c68` |
| `docs/source/owner-records/bridge/OWNER-DIRECTION-BR-0004-CHECKPOINT-DISCIPLINE.md` | `release/orchestration/phase-2-context-bridge/GATES/OWNER-DIRECTION-BR-0004-CHECKPOINT-DISCIPLINE.md` | R053 | `7783efcba342d765250dc0c1083c518e78788ae4bfdfb1f508cdafd93c84e134` |
| `docs/source/owner-records/bridge/OWNER-DIRECTION-BR-0005-MULTI-BATCH-MULTI-HOP-RETRIEVAL.md` | `release/orchestration/phase-2-context-bridge/GATES/OWNER-DIRECTION-BR-0005-MULTI-BATCH-MULTI-HOP-RETRIEVAL.md` | R053 | `7c051a1ffeaf2296ca1a225d19f7a173948b8dd72130f86944e8daa952377941` |
| `docs/source/owner-records/bridge/OWNER-DIRECTION-BR-0006-CONTEXT-RETRIEVAL-AND-CONTINUITY.md` | `release/orchestration/phase-2-context-bridge/GATES/OWNER-DIRECTION-BR-0006-CONTEXT-RETRIEVAL-AND-CONTINUITY.md` | R053 | `21967774a2b8d150ef0afa4badbdbe81346796cb15b4a1616fed2f7fb954003e` |
| `docs/source/owner-records/bridge/OWNER-LAUNCHER-BR-0001-P2X-FAIL-1.md` | `release/orchestration/phase-2-context-bridge/GATES/OWNER-LAUNCHER-BR-0001-P2X-FAIL-1.md` | R053 | `6bbd4141478fd944937deaae82e14cfce6aa2a9372a287c93f32c8e8181446f2` |
| `docs/source/owner-records/phase-1/OWNER-DECISION-0005-R0-REVIEW-ANSWERS.md` | `release/orchestration/phase-1/GATES/OWNER-DECISION-0005-R0-REVIEW-ANSWERS.md` | R054 | `3831cbf51d6f663299a3a338d85bd07bed662fd33e5392502d4f270ce87e36fa` |
| `docs/source/owner-records/phase-1/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md` | `release/orchestration/phase-1/GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md` | R054 | `903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db` |
| `docs/source/owner-records/phase-1/OWNER-DECISION-0007-R1-QUESTIONS.md` | `release/orchestration/phase-1/GATES/OWNER-DECISION-0007-R1-QUESTIONS.md` | R054 | `4a0f61c0b3de4c4c657f5b208cd184a8b4add5cde74b4ae152cba964a6bdba7d` |
| `docs/source/owner-records/phase-1/OWNER-DECISION-0008-CONVERGENCE-OPTION-B.md` | `release/orchestration/phase-1/GATES/OWNER-DECISION-0008-CONVERGENCE-OPTION-B.md` | R054 | `aa541eab86192c3710a76cf3119efdeb7e108891c5f0e9782a88e05a20d06518` |
| `docs/source/owner-records/phase-1/OWNER-DECISION-0009-ADOPT-ARCH-0003.md` | `release/orchestration/phase-1/GATES/OWNER-DECISION-0009-ADOPT-ARCH-0003.md` | R054 | `a0d3325fa8618f1af5089b47370e362cee37ba76516c1bd1ad77acf53ca1fd39` |
| `docs/source/owner-records/phase-1/OWNER-DESIGN-REQUIREMENTS-0001.md` | `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` | R053 | `c85d80c2402b94bfa691a1cdca5aae18ebe6dfd15e867c72b6f75544b391a960` |
| `docs/source/owner-records/phase-1/OWNER-DESIGN-REQUIREMENTS-0001.yaml` | `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.yaml` | R053 | `004669e2980fe728a069b93e250b672a930182bb9b7945320afa8f32e46013b6` |
| `docs/source/owner-records/phase-1/OWNER-DESIGN-REQUIREMENTS-0002.md` | `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0002.md` | R053 | `914720488a63e121146a3b335ecb06282cb7795802aa33da11de223af775918d` |
| `docs/source/owner-records/phase-1/OWNER-DESIGN-REQUIREMENTS-0002.yaml` | `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0002.yaml` | R053 | `9d877f4b4417a4954e2a75990a43984ff750d357c433cad89a422038bca0cd9f` |
| `docs/source/owner-records/phase-1/OWNER-DIRECTIVE-0003-FREEZE-ROT-LOOP.md` | `release/orchestration/phase-1/GATES/OWNER-DIRECTIVE-0003-FREEZE-ROT-LOOP.md` | R053 | `b1b3aa1feace9d796373d2b795954fac79e745a86aab725b4b5ad669254df308` |
| `docs/source/owner-records/phase-1/OWNER-DIRECTIVE-0004-SIGNED-RELEASE-ROOT-REBASE.md` | `release/orchestration/phase-1/GATES/OWNER-DIRECTIVE-0004-SIGNED-RELEASE-ROOT-REBASE.md` | R053 | `26243019d09e07617a63cf575c3e5e59cad307a7ac38100116dbbb3300f2a1ba` |
| `docs/source/owner-records/phase-2/HG-P2-0001-OWNER-DECISIONS.md` | `release/orchestration/phase-2/GATES/HG-P2-0001-OWNER-DECISIONS.md` | R054 | `9db9c0ab341b46f90528560d143b47e3e039a25686ba03a23be19301dd35be95` |
| `docs/source/owner-records/phase-2/OWNER-AMENDMENT-P2-0010-CONTEXT-RETRIEVAL-BRIDGE.md` | `release/orchestration/phase-2/GATES/OWNER-AMENDMENT-P2-0010-CONTEXT-RETRIEVAL-BRIDGE.md` | R054 | `8cc0f3bbf74238f5d0c8b28f00b581c2878154faa69895af35a7f35447c3c7b3` |
| `docs/source/owner-records/phase-2/OWNER-AUTHORISATION-P2-0006-OPTION-A-BOUNDED-ROUND.md` | `release/orchestration/phase-2/GATES/OWNER-AUTHORISATION-P2-0006-OPTION-A-BOUNDED-ROUND.md` | R054 | `502dbfddef023f5761c866d32d1f62791a473fd182bf9a9dece8f71b1b6e9fbc` |
| `docs/source/owner-records/phase-2/OWNER-CLARIFICATION-P2-0004-TRUSTED-AUTHORITY-STATE.md` | `release/orchestration/phase-2/GATES/OWNER-CLARIFICATION-P2-0004-TRUSTED-AUTHORITY-STATE.md` | R054 | `e295af0b7300eae826cfc6e93cbc75f61362078b45320a1cbf5b8a4af950e658` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0001-AGENT-ROLE-IDENTITY.md` | R054 | `612849ba65c310c5ff41999e72e3382048842f526048a3fe49ab1a5b5a88b0ce` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0002-UNPROVISIONED-MACHINES.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0002-UNPROVISIONED-MACHINES.md` | R054 | `5d73bbe3619a54b7f8f5da1fa9c556ed5cdca2f86a4babdf47d8e828a20c16c4` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md` | R054 | `9aed6636a157c0234fb53efaa2952b59dc52335730c4ee169db18cbb711ccedf` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0005-BIND-THE-BYTES.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0005-BIND-THE-BYTES.md` | R054 | `bd1d17837ab02b256d54bff36b140450f332479fa2789be36e5927b4a3adfb05` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0007-A-PLUS-C-STRUCTURAL-REMEDIATION.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0007-A-PLUS-C-STRUCTURAL-REMEDIATION.md` | R054 | `223e316d89f02d9cdc88c47a6dd17bb8eb624b392d1f8dacd54155be7228aec9` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0008-COMPLETE-PHASE-2.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0008-COMPLETE-PHASE-2.md` | R054 | `c7bb4cbae6a8595c3bba9608d7d31bd7911abf876825e3427a39ad5a10a90af8` |
| `docs/source/owner-records/phase-2/OWNER-DECISION-P2-0010A-B-REVIEW-8-DISPOSITION.md` | `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0010A-B-REVIEW-8-DISPOSITION.md` | R054 | `847dbae019b760e5ad7706fc37d170078141b8a4ab79b3483b7c4df3b72e0fff` |
| `docs/source/owner-records/phase-2/OWNER-DIRECTION-P2-0009-COMPLETE-WITH-SWEEP.md` | `release/orchestration/phase-2/GATES/OWNER-DIRECTION-P2-0009-COMPLETE-WITH-SWEEP.md` | R054 | `3f0cd498cd7a7927e3175529ec3d4b14d9f953a89fb45ce4ae287948226b3999` |
| `fixtures/README.md` | `docs/FIXTURES.md` | R013 | `0afb687b84eeaaef159668372e3a84834af1068ea8b694525c424b92442100c2` |
| `fixtures/brownfield/README.md` | `fixtures/brownfield/README.md` | R017 | `cf05ef311f3ffc2137b72b2ce89e1d9e60756210aee66df8c717dad5f7f3645e` |
| `fixtures/brownfield/project/.chat/sessions.jsonl` | `fixtures/brownfield/project/.chat/sessions.jsonl` | R017 | `f75e4a3b3039dbe00d756d5685e0415f1a10c73a0673de24ea61cea2acb79477` |
| `fixtures/brownfield/project/.cursorrules` | `fixtures/brownfield/project/.cursorrules` | R017 | `47678269c467a0b917115420604c98023227254a7f4090253e0f920a938cc405` |
| `fixtures/brownfield/project/.env` | `fixtures/brownfield/project/.env` | R017 | `7c8fdb96df48d6f5eb18d1762eeb58918aa40c324f938136230fb6945c49965d` |
| `fixtures/brownfield/project/.github/copilot-instructions.md` | `fixtures/brownfield/project/.github/copilot-instructions.md` | R017 | `a32a00b555944b75370201ca4266b9ff7d5295748527cf7c710bc16e6af58fd6` |
| `fixtures/brownfield/project/.gitignore` | `fixtures/brownfield/project/.gitignore` | R017 | `32dae3052f331ee34d628ef535709b301259a45df7c7522c4d35dcf49873f00b` |
| `fixtures/brownfield/project/.index/manifest.json` | `fixtures/brownfield/project/.index/manifest.json` | R017 | `dd6da5d8b7737cf5e262cc2cc8f6b4cfefadea6854e9d2a1973e769f165a960e` |
| `fixtures/brownfield/project/.index/vectors.json` | `fixtures/brownfield/project/.index/vectors.json` | R017 | `0eb82710ad0b713f32f96b204dc429ad58ab70cb2b0a8e5faaf34bd9a0ff2ee5` |
| `fixtures/brownfield/project/AGENT_RULES_v2.md` | `fixtures/brownfield/project/AGENT_RULES_v2.md` | R017 | `8d5fbda3a88399405f9474221422b1de00d9a060ae76b9b6e1fba8059755d972` |
| `fixtures/brownfield/project/README.md` | `fixtures/brownfield/project/README.md` | R017 | `1540c9d91b1347d45cd043b4dd7c9b3ec3276386ec80a2f36433c7281bdc2ea1` |
| `fixtures/brownfield/project/config/secrets.yaml` | `fixtures/brownfield/project/config/secrets.yaml` | R017 | `a3e5efef690d06111a10c196d48d0befb5da25a1f3d1febaab897c69b95cbae0` |
| `fixtures/brownfield/project/config/settings.yaml` | `fixtures/brownfield/project/config/settings.yaml` | R017 | `df01c847e024ae0244a4b983b89e98a1fd9edd3b8bf056dd7537898209302683` |
| `fixtures/brownfield/project/docs/DECISIONS.md` | `fixtures/brownfield/project/docs/DECISIONS.md` | R017 | `106a6e1ae48ada9ab7a23850a473cdef31cc512fd40d4fc73af0759fb49a7e72` |
| `fixtures/brownfield/project/docs/decisions/ADR-001-retries.md` | `fixtures/brownfield/project/docs/decisions/ADR-001-retries.md` | R017 | `dc83fdd70e7c7f24489a87d65d11d39d0ac06d65d5d265a56e2cb703b993de7e` |
| `fixtures/brownfield/project/docs/legacy_module.py` | `fixtures/brownfield/project/docs/legacy_module.py` | R017 | `1868730bffe4b86611c4082887f238fb529e47c4a1b6e9704c6aeb937f7b5f77` |
| `fixtures/brownfield/project/docs/old/decision-2-copy.yaml` | `fixtures/brownfield/project/docs/old/decision-2-copy.yaml` | R017 | `044c835d028d12bc2d37ad94b7aaa52c4150827054a36e3792816410a22ad5e9` |
| `fixtures/brownfield/project/docs/test_utils.py` | `fixtures/brownfield/project/docs/test_utils.py` | R017 | `05de79335be4bc8c4b816a6c30cf1c6fbd0c12a8c6408d8ac91a812dab3ad821` |
| `fixtures/brownfield/project/memory/chat_history.sql` | `fixtures/brownfield/project/memory/chat_history.sql` | R017 | `1af9536af40a2000f172c1e10bc31fc4f8a72865790c7b9c8097c0e4db23b013` |
| `fixtures/brownfield/project/pyproject.toml` | `fixtures/brownfield/project/pyproject.toml` | R017 | `5bb311e16ab39ab12c6153e5de662a2bb51240755e7b4869a39d718823e2c76b` |
| `fixtures/brownfield/project/spec/decisions/D-0001.yaml` | `fixtures/brownfield/project/spec/decisions/D-0001.yaml` | R017 | `b341f0468bdff23fc0c66a2c842ff16925f340b6d2308d00f8296b815b593f16` |
| `fixtures/brownfield/project/spec/decisions/D-0002.yaml` | `fixtures/brownfield/project/spec/decisions/D-0002.yaml` | R017 | `d5e78fa50c74125434981e254e73f84829403a48e3f147623da32def0828303c` |
| `fixtures/brownfield/project/specs/requirements.md` | `fixtures/brownfield/project/specs/requirements.md` | R017 | `e96f4324d29b3230640df749410b8771fe0ef31094d2ba0c66032b69062b46f3` |
| `fixtures/brownfield/project/src/app/__init__.py` | `fixtures/brownfield/project/src/app/__init__.py` | R017 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `fixtures/brownfield/project/src/app/billing.py` | `fixtures/brownfield/project/src/app/billing.py` | R017 | `03eeaf5a1f3c3fb21ed2ab6802c9973380c42664cd0c315ce6d2da9e8c9f4b38` |
| `fixtures/brownfield/project/src/app/config.py` | `fixtures/brownfield/project/src/app/config.py` | R017 | `7591f52be8f996f2c167403638a0c306249a0c20b557bb4ca6f06e6709cfefde` |
| `fixtures/brownfield/project/src/app/main.py` | `fixtures/brownfield/project/src/app/main.py` | R017 | `3d6a3f025998b52698ae66b541dbd21d7547f48189116b8488477ad23ab0d9d1` |
| `fixtures/brownfield/project/src/app/old_export.py` | `fixtures/brownfield/project/src/app/old_export.py` | R017 | `37ca05c3406c01cbfcb55f4cb9e13d8b0cfa2fed8eac7bde71b305933dae19f3` |
| `fixtures/brownfield/project/src/app/retry.py` | `fixtures/brownfield/project/src/app/retry.py` | R017 | `afd77f74e1c5d0f5dca7ee2929a49693b9b23e825cc261cbe43c745d5967da76` |
| `fixtures/brownfield/project/src/specs/feature-login.md` | `fixtures/brownfield/project/src/specs/feature-login.md` | R017 | `69b74310de5029ad26f88a1ae51b4ab3e4ddf5157fcd16c1b018a82107f1c31a` |
| `fixtures/brownfield/project/tests/conftest.py` | `fixtures/brownfield/project/tests/conftest.py` | R017 | `7d836639ed7c57e5d64c196735e1ccd5bc7f57768c44883f871e7a563aec9a53` |
| `fixtures/brownfield/project/tests/test_retry.py` | `fixtures/brownfield/project/tests/test_retry.py` | R017 | `41d8bbc83375b0e7e151e973d7769f3fccae33b17fc4e4963737de8c8225268b` |
| `fixtures/brownfield/project/web/package.json` | `fixtures/brownfield/project/web/package.json` | R017 | `9dcc4e453119313a17b6cb2b87a243f155b48b6353547e7f079d4ccc6bb508de` |
| `fixtures/brownfield/project/web/src/__tests__/client.test.ts` | `fixtures/brownfield/project/web/src/__tests__/client.test.ts` | R017 | `81bedce2409ba8845c52f706c5705bc24f1f4ac235e3a10d5cec15b40b20a673` |
| `fixtures/brownfield/project/web/src/api/client.ts` | `fixtures/brownfield/project/web/src/api/client.ts` | R017 | `eb7567464604164f49ad0600a307f4422b7867f29fd489f641c1b4c58042cbdd` |
| `fixtures/brownfield/project/web/src/util/http.ts` | `fixtures/brownfield/project/web/src/util/http.ts` | R017 | `1d6ee9d85e834482b8b1ffc4a0a0b0076cf5ecf65f93a0321e81c750ed73811c` |
| `fixtures/greenfield/README.md` | `fixtures/greenfield/README.md` | R016 | `adfe0292436d352aab1e33085d67e2fc5f74b4182077d46c3062843184c136c0` |
| `fixtures/greenfield/project/.gitignore` | `fixtures/greenfield/project/.gitignore` | R016 | `12cc0f91b51fedf41ae1670d1624ee1d78a284bdb101645b60a06a12de16c069` |
| `fixtures/greenfield/project/Cargo.toml` | `fixtures/greenfield/project/Cargo.toml` | R016 | `b8a73650ae9ad6e82a2958f4c90a8ee97065597433857625951d28096df80d1b` |
| `fixtures/greenfield/project/README.md` | `fixtures/greenfield/project/README.md` | R016 | `ff9017c76335ca4a9fdbbc3585b591408177cdd76415809da75f91871f70e65d` |
| `fixtures/greenfield/project/src/lib.rs` | `fixtures/greenfield/project/src/lib.rs` | R016 | `f9867f4549881025f578fdd776ae9cd3ea85759419fc3783e14c4622f2b5e5e4` |
| `fixtures/greenfield/project/tests/ledger_test.rs` | `fixtures/greenfield/project/tests/ledger_test.rs` | R016 | `dc9fe689a5044c8d27c72411e85226717e8182915ff8134de0044a52212c7a59` |
| `fixtures/migration/README.md` | `fixtures/migration/README.md` | R018 | `2ac3d728fb38a75b653bd70d2c766e923b274c90ebd041786c127af4dd3cc7df` |
| `fixtures/migration/project/README.md` | `fixtures/migration/project/README.md` | R018 | `77befde0a32191756e7f75bfa4ec82a36786d081325a7e989a9da0ff091307f8` |
| `fixtures/migration/project/docs/architecture.md` | `fixtures/migration/project/docs/architecture.md` | R018 | `73b599fd44f4b0196bfc42ac83cfcdd3d41f327ffd54a6b90774b9572eff1da7` |
| `fixtures/migration/project/docs/helpers_test.py` | `fixtures/migration/project/docs/helpers_test.py` | R018 | `2f029c06bbd0109822da7b9b21c3f03725fd120d8a44ad1e5607ec7863226f82` |
| `fixtures/migration/project/docs/old/legacy_decisions.md` | `fixtures/migration/project/docs/old/legacy_decisions.md` | R018 | `35c91e497e07a3b26d2854ea5ecc6ca2805642b4481573428c353df1fda1f9c6` |
| `fixtures/migration/project/lib/__init__.py` | `fixtures/migration/project/lib/__init__.py` | R018 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `fixtures/migration/project/lib/core/__init__.py` | `fixtures/migration/project/lib/core/__init__.py` | R018 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `fixtures/migration/project/lib/core/engine.py` | `fixtures/migration/project/lib/core/engine.py` | R018 | `ef55c46b66615abeb7a7b6bc9ef01779a0034ae9c5bb1fa5bd7fe6efa94e225a` |
| `fixtures/migration/project/lib/core/helpers.py` | `fixtures/migration/project/lib/core/helpers.py` | R018 | `caeaaa556a66f68d63b36b956941b6c3cd4e0d2a0f4654783c1c3670ad183830` |
| `fixtures/migration/project/notes/api-spec.md` | `fixtures/migration/project/notes/api-spec.md` | R018 | `60cd3c7e3faa7d79bc95d1923cacb8eb6c370ce252fbd9c2bcb11a3c9aacc389` |
| `fixtures/migration/project/pyproject.toml` | `fixtures/migration/project/pyproject.toml` | R018 | `3dddfe23488acb3f9ab65982e58f181e925dd5bf2318fcef46b2c8f5139d8af4` |
| `fixtures/migration/project/tests/conftest.py` | `fixtures/migration/project/tests/conftest.py` | R018 | `b0ddfc8c7f032b459c453241f9bd7c370269a57553b1f17446eccf8d6fcccedf` |
| `fixtures/migration/project/tests/test_engine.py` | `fixtures/migration/project/tests/test_engine.py` | R018 | `cc4cc75936f5119dfc01b0cb2961ae497de9126f6be7139aa015cb6a6f32dbde` |
| `fixtures/migration/project/web/package.json` | `fixtures/migration/project/web/package.json` | R018 | `6777d398a066d2f5dc14741cb874717c7059112eed149e927ac97713a35065fb` |
| `fixtures/migration/project/web/src/api/client.ts` | `fixtures/migration/project/web/src/api/client.ts` | R018 | `5ec5e51acc956f6c162b4614043834c58c6596a84ab5dfcb89a8778c09558ac0` |
| `fixtures/migration/project/web/src/util/http.ts` | `fixtures/migration/project/web/src/util/http.ts` | R018 | `1d6ee9d85e834482b8b1ffc4a0a0b0076cf5ecf65f93a0321e81c750ed73811c` |
| `schemas/records/checkpoint.schema.json` | `framework/schemas/checkpoint.schema.json` | R020 | `9846b0a980b41c9ee03fb73378d2a3fe0eefba0698353901701c31405117c729` |
| `schemas/records/decision.schema.json` | `framework/schemas/decision.schema.json` | R020 | `41c5cc3a523569f2b460ab260e83ec71d36f6f06f1c4d1cd5b640cb5be117895` |
| `schemas/records/lesson.schema.json` | `framework/schemas/lesson.schema.json` | R020 | `97cec3a263185d43a174b992cc6468eaf4076a7de82e748a75084d0179634211` |
| `schemas/records/record.schema.json` | `framework/schemas/record.schema.json` | R020 | `d776e27d2478da2f8d1bbf5d9591afa21f22465e5ca3aad0cc5bfbe0ac903e70` |
| `schemas/records/research.schema.json` | `framework/schemas/research.schema.json` | R020 | `99ddfe1d715430400010ac185655fa6266c4d2720ef6953c28984466234ad109` |
