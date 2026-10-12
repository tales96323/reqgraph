# =============================================================================
# Mapeamento de Requisitos — Flask (app.py + cli.py + blueprints.py)
# Nível: 🟡 Médio
# =============================================================================

func_to_req = {
    # ── REQ_APP_CORE — Inicialização e configuração da aplicação ─────────
    "__init__": "REQ_APP_CORE",
    "__init_subclass__": "REQ_APP_CORE",
    "run": "REQ_APP_CORE",
    "_make_timedelta": "REQ_APP_CORE",

    # ── REQ_ROUTING — Roteamento e dispatch de requisições ───────────────
    "dispatch_request": "REQ_ROUTING",
    "full_dispatch_request": "REQ_ROUTING",
    "raise_routing_exception": "REQ_ROUTING",
    "url_for": "REQ_ROUTING",
    "create_url_adapter": "REQ_ROUTING",
    "make_default_options_response": "REQ_ROUTING",

    # ── REQ_REQUEST_HANDLING — Processamento de request/response ─────────
    "wsgi_app": "REQ_REQUEST_HANDLING",
    "__call__": "REQ_REQUEST_HANDLING",
    "make_response": "REQ_REQUEST_HANDLING",
    "preprocess_request": "REQ_REQUEST_HANDLING",
    "process_response": "REQ_REQUEST_HANDLING",
    "finalize_request": "REQ_REQUEST_HANDLING",
    "ensure_sync": "REQ_REQUEST_HANDLING",
    "async_to_sync": "REQ_REQUEST_HANDLING",

    # ── REQ_CONTEXT — Gestão de contextos ────────────────────────────────
    "app_context": "REQ_CONTEXT",
    "request_context": "REQ_CONTEXT",
    "test_request_context": "REQ_CONTEXT",
    "do_teardown_request": "REQ_CONTEXT",
    "do_teardown_appcontext": "REQ_CONTEXT",
    "update_template_context": "REQ_CONTEXT",
    "make_shell_context": "REQ_CONTEXT",
    "remove_ctx": "REQ_CONTEXT",
    "add_ctx": "REQ_CONTEXT",

    # ── REQ_ERROR_HANDLING — Tratamento de erros e exceções ──────────────
    "handle_http_exception": "REQ_ERROR_HANDLING",
    "handle_user_exception": "REQ_ERROR_HANDLING",
    "handle_exception": "REQ_ERROR_HANDLING",
    "log_exception": "REQ_ERROR_HANDLING",

    # ── REQ_TEMPLATING — Templates Jinja2 ────────────────────────────────
    "create_jinja_environment": "REQ_TEMPLATING",

    # ── REQ_STATIC_FILES — Arquivos estáticos ────────────────────────────
    "get_send_file_max_age": "REQ_STATIC_FILES",
    "send_static_file": "REQ_STATIC_FILES",
    "open_resource": "REQ_STATIC_FILES",
    "open_instance_resource": "REQ_STATIC_FILES",

    # ── REQ_TESTING — Utilitários de teste ───────────────────────────────
    "test_client": "REQ_TESTING",
    "test_cli_runner": "REQ_TESTING",

    # ── REQ_CLI_DISCOVERY — Descoberta e carregamento de app via CLI ─────
    "find_best_app": "REQ_CLI_DISCOVERY",
    "_called_with_wrong_args": "REQ_CLI_DISCOVERY",
    "find_app_by_string": "REQ_CLI_DISCOVERY",
    "prepare_import": "REQ_CLI_DISCOVERY",
    "locate_app": "REQ_CLI_DISCOVERY",
    "load_app": "REQ_CLI_DISCOVERY",

    # ── REQ_CLI_COMMANDS — Comandos CLI do Flask ─────────────────────────
    "run_command": "REQ_CLI_COMMANDS",
    "shell_command": "REQ_CLI_COMMANDS",
    "routes_command": "REQ_CLI_COMMANDS",
    "main": "REQ_CLI_COMMANDS",
    "show_server_banner": "REQ_CLI_COMMANDS",
    "get_version": "REQ_CLI_COMMANDS",

    # ── REQ_CLI_FRAMEWORK — Framework de grupos e decoradores CLI ────────
    "with_appcontext": "REQ_CLI_FRAMEWORK",
    "command": "REQ_CLI_FRAMEWORK",
    "group": "REQ_CLI_FRAMEWORK",
    "get_command": "REQ_CLI_FRAMEWORK",
    "list_commands": "REQ_CLI_FRAMEWORK",
    "_load_plugin_commands": "REQ_CLI_FRAMEWORK",
    "make_context": "REQ_CLI_FRAMEWORK",
    "parse_args": "REQ_CLI_FRAMEWORK",
    "_set_app": "REQ_CLI_FRAMEWORK",
    "_set_debug": "REQ_CLI_FRAMEWORK",
    "_env_file_callback": "REQ_CLI_FRAMEWORK",
    "_path_is_ancestor": "REQ_CLI_FRAMEWORK",
    "load_dotenv": "REQ_CLI_FRAMEWORK",
    "decorator": "REQ_CLI_FRAMEWORK",

    # ── REQ_CLI_TYPES — Tipos customizados para parâmetros CLI ───────────
    "convert": "REQ_CLI_TYPES",
    "_validate_key": "REQ_CLI_TYPES",

    # ── REQ_BLUEPRINTS — Sistema de blueprints ───────────────────────────
    "set_output": "REQ_BLUEPRINTS",
    "get_params": "REQ_BLUEPRINTS",
    "set_params": "REQ_BLUEPRINTS",
}
