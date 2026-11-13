import ast
import sys

ROOT = "/home/usain/gov-os-worktrees/W2-124/"
CASES = {
    "tests/acceptance/W2-13/test_w2_13_secrets.py": ["test_a_second_rebuild_answered_from_the_secrets_cache_indexes_the_canary_no_more"],
    "tests/acceptance/W2-13/test_w2_13_unavailable.py": ["test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises", "test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback"],
    "tests/acceptance/W2-13/test_w2_13_latency.py": ["test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget"],
    "tests/acceptance/W2-76/test_w2_76_timings.py": ["test_every_stage_timed_in_output_and_record"],
    "tests/acceptance/W2-76/test_w2_76_unchanged.py": ["test_two_full_rebuilds_of_the_same_tree_give_the_same_digest"],
    "tests/acceptance/W2-116/test_w2_116_reindex.py": ["test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable"],
    "tests/acceptance/W1-41/test_w1_41_embedding_policy.py": ["test_the_rebuild_says_no_namespace_is_embedded"],
    "tests/unit/rebuild/test_w2_116_integration.py": ["test_a_failed_build_never_moves_the_link_and_leaves_the_ready_half_as_it_was", "test_a_model_less_reindex_keeps_the_vectors_and_reports_the_facet_unavailable"],
    "tests/unit/rebuild/test_no_embeddings.py": ["test_both_modes_say_where_no_namespace_is_embedded_and_nothing_else_changes"],
    "tests/unit/rebuild/test_w2_122_seed.py": ["test_a_semantic_store_not_recreated_answers_as_before_and_leaves_no_record"],
    "tests/unit/retrieval/test_w2_32_rebuild_cut.py": ["test_a_stage_not_built_still_names_the_cut"],
}
only = sys.argv[1:]
for path, names in CASES.items():
    if only and not any(o in path for o in only):
        continue
    src = open(ROOT + path).read()
    lines = src.splitlines()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            start = min([d.lineno for d in node.decorator_list] + [node.lineno])
            print(f"==== {path}:{start}")
            print("\n".join(lines[start - 1:node.end_lineno]))
