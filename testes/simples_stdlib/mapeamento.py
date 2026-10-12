# =============================================================================
# Mapeamento de Requisitos — CPython stdlib (argparse.py + http/server.py)
# Nível: 🟢 Simples
# =============================================================================

func_to_req = {
    # ── REQ_PARSING — Análise e parsing de argumentos ────────────────────
    "parse_args": "REQ_PARSING",
    "parse_known_args": "REQ_PARSING",
    "_parse_known_args": "REQ_PARSING",
    "_parse_known_args2": "REQ_PARSING",
    "parse_intermixed_args": "REQ_PARSING",
    "parse_known_intermixed_args": "REQ_PARSING",
    "_match_argument": "REQ_PARSING",
    "_match_arguments_partial": "REQ_PARSING",
    "_parse_optional": "REQ_PARSING",
    "_get_option_tuples": "REQ_PARSING",
    "_get_nargs_pattern": "REQ_PARSING",
    "_read_args_from_files": "REQ_PARSING",
    "convert_arg_line_to_args": "REQ_PARSING",

    # ── REQ_ACTIONS — Ações de processamento de argumentos ───────────────
    "add_argument": "REQ_ACTIONS",
    "add_arguments": "REQ_ACTIONS",
    "add_argument_group": "REQ_ACTIONS",
    "add_mutually_exclusive_group": "REQ_ACTIONS",
    "add_subparsers": "REQ_ACTIONS",
    "add_parser": "REQ_ACTIONS",
    "_add_action": "REQ_ACTIONS",
    "_remove_action": "REQ_ACTIONS",
    "_add_container_actions": "REQ_ACTIONS",
    "_get_positional_kwargs": "REQ_ACTIONS",
    "_get_optional_kwargs": "REQ_ACTIONS",
    "_pop_action_class": "REQ_ACTIONS",

    # ── REQ_FORMATTING — Formatação de help e uso ────────────────────────
    "format_help": "REQ_FORMATTING",
    "format_usage": "REQ_FORMATTING",
    "print_help": "REQ_FORMATTING",
    "print_usage": "REQ_FORMATTING",
    "_format_usage": "REQ_FORMATTING",
    "_format_text": "REQ_FORMATTING",
    "_format_action": "REQ_FORMATTING",
    "_format_action_invocation": "REQ_FORMATTING",
    "_format_args": "REQ_FORMATTING",
    "_get_formatter": "REQ_FORMATTING",
    "_get_validation_formatter": "REQ_FORMATTING",
    "_expand_help": "REQ_FORMATTING",
    "_get_help_string": "REQ_FORMATTING",
    "_metavar_formatter": "REQ_FORMATTING",
    "_split_lines": "REQ_FORMATTING",
    "_fill_text": "REQ_FORMATTING",
    "_join_parts": "REQ_FORMATTING",
    "_indent": "REQ_FORMATTING",
    "_dedent": "REQ_FORMATTING",
    "_add_item": "REQ_FORMATTING",
    "start_section": "REQ_FORMATTING",
    "end_section": "REQ_FORMATTING",
    "add_text": "REQ_FORMATTING",
    "add_usage": "REQ_FORMATTING",
    "colorize": "REQ_FORMATTING",
    "_apply_text_markup": "REQ_FORMATTING",
    "_set_color": "REQ_FORMATTING",

    # ── REQ_VALIDATION — Validação de valores ────────────────────────────
    "_get_values": "REQ_VALIDATION",
    "_get_value": "REQ_VALIDATION",
    "_check_value": "REQ_VALIDATION",
    "_check_conflict": "REQ_VALIDATION",
    "_handle_conflict_error": "REQ_VALIDATION",
    "_handle_conflict_resolve": "REQ_VALIDATION",
    "_check_help": "REQ_VALIDATION",

    # ── REQ_CONFIGURATION — Configuração e defaults ──────────────────────
    "register": "REQ_CONFIGURATION",
    "_registry_get": "REQ_CONFIGURATION",
    "set_defaults": "REQ_CONFIGURATION",
    "get_default": "REQ_CONFIGURATION",

    # ── REQ_ERROR_HANDLING — Tratamento de erros ─────────────────────────
    "error": "REQ_ERROR_HANDLING",
    "exit": "REQ_ERROR_HANDLING",
    "_warning": "REQ_ERROR_HANDLING",
    "_print_message": "REQ_ERROR_HANDLING",
    "_get_action_name": "REQ_ERROR_HANDLING",

    # ── REQ_HTTP_HANDLER — Tratamento de requisições HTTP ────────────────
    "parse_request": "REQ_HTTP_HANDLER",
    "handle_one_request": "REQ_HTTP_HANDLER",
    "handle": "REQ_HTTP_HANDLER",
    "handle_expect_100": "REQ_HTTP_HANDLER",
    "do_GET": "REQ_HTTP_HANDLER",
    "do_HEAD": "REQ_HTTP_HANDLER",
    "send_head": "REQ_HTTP_HANDLER",
    "send_error": "REQ_HTTP_HANDLER",
    "send_response": "REQ_HTTP_HANDLER",
    "send_response_only": "REQ_HTTP_HANDLER",
    "send_header": "REQ_HTTP_HANDLER",
    "end_headers": "REQ_HTTP_HANDLER",
    "flush_headers": "REQ_HTTP_HANDLER",

    # ── REQ_HTTP_SERVER — Servidor HTTP e recursos estáticos ─────────────
    "server_bind": "REQ_HTTP_SERVER",
    "server_activate": "REQ_HTTP_SERVER",
    "finish_request": "REQ_HTTP_SERVER",
    "_get_best_family": "REQ_HTTP_SERVER",
    "test": "REQ_HTTP_SERVER",
    "_main": "REQ_HTTP_SERVER",

    # ── REQ_HTTP_CONTENT — Serviço de conteúdo e diretórios ──────────────
    "list_directory": "REQ_HTTP_CONTENT",
    "translate_path": "REQ_HTTP_CONTENT",
    "copyfile": "REQ_HTTP_CONTENT",
    "guess_type": "REQ_HTTP_CONTENT",

    # ── REQ_HTTP_LOGGING — Logging HTTP ──────────────────────────────────
    "log_request": "REQ_HTTP_LOGGING",
    "log_error": "REQ_HTTP_LOGGING",
    "log_message": "REQ_HTTP_LOGGING",
    "version_string": "REQ_HTTP_LOGGING",
    "date_time_string": "REQ_HTTP_LOGGING",
    "log_date_time_string": "REQ_HTTP_LOGGING",
    "address_string": "REQ_HTTP_LOGGING",
}
