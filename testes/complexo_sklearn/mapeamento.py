# =============================================================================
# Mapeamento de Requisitos — scikit-learn (pipeline, linear_model, tree)
# Nível: 🔴 Complexo
# =============================================================================

func_to_req = {
    # ── REQ_PIPELINE — Orquestração sequencial de estimadores ────────────
    "set_output": "REQ_PIPELINE",
    "get_params": "REQ_PIPELINE",
    "set_params": "REQ_PIPELINE",
    "_validate_steps": "REQ_PIPELINE",
    "_iter": "REQ_PIPELINE",
    "__len__": "REQ_PIPELINE",
    "__getitem__": "REQ_PIPELINE",
    "_log_message": "REQ_PIPELINE",
    "_check_method_params": "REQ_PIPELINE",
    "_get_metadata_for_step": "REQ_PIPELINE",
    "_name_estimators": "REQ_PIPELINE",
    "make_pipeline": "REQ_PIPELINE",
    "get_metadata_routing": "REQ_PIPELINE",
    "_sk_visual_block_": "REQ_PIPELINE",
    "_final_estimator_has": "REQ_PIPELINE",

    # ── REQ_PIPELINE_FIT — Treinamento via Pipeline ──────────────────────
    "_fit": "REQ_PIPELINE_FIT",
    "fit": "REQ_PIPELINE_FIT",
    "_can_fit_transform": "REQ_PIPELINE_FIT",
    "fit_transform": "REQ_PIPELINE_FIT",
    "fit_predict": "REQ_PIPELINE_FIT",

    # ── REQ_PIPELINE_PREDICT — Predição e transformação via Pipeline ─────
    "predict": "REQ_PIPELINE_PREDICT",
    "predict_proba": "REQ_PIPELINE_PREDICT",
    "predict_log_proba": "REQ_PIPELINE_PREDICT",
    "decision_function": "REQ_PIPELINE_PREDICT",
    "score_samples": "REQ_PIPELINE_PREDICT",
    "_can_transform": "REQ_PIPELINE_PREDICT",
    "transform": "REQ_PIPELINE_PREDICT",
    "_can_inverse_transform": "REQ_PIPELINE_PREDICT",
    "inverse_transform": "REQ_PIPELINE_PREDICT",
    "score": "REQ_PIPELINE_PREDICT",
    "_cached_transform": "REQ_PIPELINE_PREDICT",

    # ── REQ_FEATURE_UNION — Concatenação paralela de features ────────────
    "_validate_transformers": "REQ_FEATURE_UNION",
    "_validate_transformer_weights": "REQ_FEATURE_UNION",
    "get_feature_names_out": "REQ_FEATURE_UNION",
    "_add_prefix_for_feature_names_out": "REQ_FEATURE_UNION",
    "_parallel_func": "REQ_FEATURE_UNION",
    "_hstack": "REQ_FEATURE_UNION",
    "_update_transformer_list": "REQ_FEATURE_UNION",
    "make_union": "REQ_FEATURE_UNION",
    "_transform_one": "REQ_FEATURE_UNION",
    "_fit_transform_one": "REQ_FEATURE_UNION",
    "_fit_one": "REQ_FEATURE_UNION",

    # ── REQ_LINEAR_MODEL — Modelos lineares base ─────────────────────────
    "_preprocess_data": "REQ_LINEAR_MODEL",
    "_rescale_data": "REQ_LINEAR_MODEL",
    "make_dataset": "REQ_LINEAR_MODEL",
    "_decision_function": "REQ_LINEAR_MODEL",
    "_set_intercept": "REQ_LINEAR_MODEL",
    "_check_precomputed_gram_matrix": "REQ_LINEAR_MODEL",
    "_pre_fit": "REQ_LINEAR_MODEL",

    # ── REQ_LOGISTIC_REGRESSION — Regressão logística ────────────────────
    "_check_solver": "REQ_LOGISTIC_REGRESSION",
    "_logistic_regression_path": "REQ_LOGISTIC_REGRESSION",
    "_log_reg_scoring_path": "REQ_LOGISTIC_REGRESSION",
    "_predict_proba_lr": "REQ_LOGISTIC_REGRESSION",
    "_get_scorer": "REQ_LOGISTIC_REGRESSION",
    "calc_score": "REQ_LOGISTIC_REGRESSION",

    # ── REQ_SPARSE — Operações com matrizes esparsas ─────────────────────
    "densify": "REQ_SPARSE",
    "sparsify": "REQ_SPARSE",
    "matvec": "REQ_SPARSE",
    "rmatvec": "REQ_SPARSE",

    # ── REQ_DECISION_TREE — Árvores de decisão ──────────────────────────
    "get_depth": "REQ_DECISION_TREE",
    "get_n_leaves": "REQ_DECISION_TREE",
    "_support_missing_values": "REQ_DECISION_TREE",
    "_compute_missing_values_in_feature_mask": "REQ_DECISION_TREE",
    "_validate_X_predict": "REQ_DECISION_TREE",
    "apply": "REQ_DECISION_TREE",
    "decision_path": "REQ_DECISION_TREE",
    "_prune_tree": "REQ_DECISION_TREE",
    "cost_complexity_pruning_path": "REQ_DECISION_TREE",
    "feature_importances_": "REQ_DECISION_TREE",
    "_compute_partial_dependence_recursion": "REQ_DECISION_TREE",

    # ── REQ_SKLEARN_TAGS — Sistema de tags do sklearn ────────────────────
    "__sklearn_tags__": "REQ_SKLEARN_TAGS",
    "__sklearn_is_fitted__": "REQ_SKLEARN_TAGS",
    "classes_": "REQ_SKLEARN_TAGS",
    "n_features_in_": "REQ_SKLEARN_TAGS",
    "feature_names_in_": "REQ_SKLEARN_TAGS",
    "_get_name": "REQ_SKLEARN_TAGS",
    "named_steps": "REQ_SKLEARN_TAGS",
    "_final_estimator": "REQ_SKLEARN_TAGS",
    "named_transformers": "REQ_SKLEARN_TAGS",
    "check": "REQ_SKLEARN_TAGS",
}
