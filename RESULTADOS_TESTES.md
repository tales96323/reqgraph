# ReqGraph — Testes com Projetos Reais do GitHub

Este documento descreve a validação da ferramenta **ReqGraph** utilizando três projetos reais de código aberto do GitHub, organizados por nível de complexidade.

---

## 1. Sobre o ReqGraph

O **ReqGraph** é uma ferramenta de rastreabilidade automática de requisitos que:

1. Analisa código-fonte Python via **AST** (Abstract Syntax Tree)
2. Extrai o **Call Graph** (grafo de chamadas entre funções/métodos)
3. Utiliza um mapeamento `func_to_req` para derivar o **Grafo de Requisitos**
4. Gera visualizações automáticas em PNG, DOT e JSON

---

## 2. Metodologia

Para cada nível de teste, foram selecionados **arquivos específicos** dos repositórios (não o repositório inteiro), e criado um arquivo `mapeamento.py` contendo o dicionário `func_to_req` que associa cada função a um requisito de domínio.

### Comando de execução

```bash
python -m reqgraph <pasta_do_teste> --mapping <pasta_do_teste>/mapeamento.py
```

### Artefatos gerados por teste

| Arquivo | Descrição |
|---------|-----------|
| `call_graph.png` | Visualização do grafo de chamadas de funções |
| `req_graph.png` | Visualização do grafo de requisitos derivado |
| `req_graph.json` | Grafo de requisitos em formato JSON |
| `req_graph.dot` | Grafo de requisitos em formato Graphviz DOT |

---

## 3. Projetos Testados

### 🟢 Simples — CPython (stdlib)

| Item | Detalhe |
|------|---------|
| **Repositório** | [python/cpython](https://github.com/python/cpython) |
| **Descrição** | Implementação de referência do Python — biblioteca padrão |
| **Pasta de teste** | `testes/simples_stdlib/` |

**Arquivos selecionados:**

| Arquivo | Origem no repositório | Descrição |
|---------|----------------------|-----------|
| `argparse.py` | `Lib/argparse.py` | Biblioteca de parsing de argumentos de linha de comando |
| `server.py` | `Lib/http/server.py` | Servidor HTTP simples da stdlib |

**Requisitos mapeados (10 domínios):**

| Requisito | Descrição | Exemplos de funções |
|-----------|-----------|-------------------|
| `REQ_PARSING` | Análise e parsing de argumentos | `parse_args`, `parse_known_args`, `_match_argument` |
| `REQ_ACTIONS` | Ações de processamento | `add_argument`, `add_argument_group`, `add_subparsers` |
| `REQ_FORMATTING` | Formatação de help e uso | `format_help`, `format_usage`, `_format_action` |
| `REQ_VALIDATION` | Validação de valores | `_get_values`, `_check_value`, `_check_conflict` |
| `REQ_CONFIGURATION` | Configuração e defaults | `register`, `set_defaults`, `get_default` |
| `REQ_ERROR_HANDLING` | Tratamento de erros | `error`, `exit`, `_warning` |
| `REQ_HTTP_HANDLER` | Tratamento de requisições HTTP | `parse_request`, `handle_one_request`, `do_GET` |
| `REQ_HTTP_SERVER` | Servidor HTTP | `server_bind`, `server_activate`, `_get_best_family` |
| `REQ_HTTP_CONTENT` | Serviço de conteúdo | `list_directory`, `translate_path`, `copyfile` |
| `REQ_HTTP_LOGGING` | Logging HTTP | `log_request`, `log_error`, `log_message` |

**Resultados:**

| Métrica | Valor |
|---------|-------|
| Funções analisadas | 298 |
| Arestas no Call Graph | 130 |
| Requisitos identificados | 10 |
| Arestas no Grafo de Requisitos | 9 |

**Grafo de Requisitos (JSON):**

```json
{
  "REQ_ACTIONS": ["REQ_CONFIGURATION", "REQ_FORMATTING", "REQ_VALIDATION"],
  "REQ_ERROR_HANDLING": ["REQ_FORMATTING"],
  "REQ_FORMATTING": ["REQ_ERROR_HANDLING"],
  "REQ_HTTP_HANDLER": ["REQ_HTTP_CONTENT", "REQ_HTTP_LOGGING"],
  "REQ_PARSING": ["REQ_ERROR_HANDLING", "REQ_VALIDATION"]
}
```

**Interpretação:** O parsing de argumentos depende de validação e tratamento de erros. As ações de processamento dependem da configuração, formatação e validação. No HTTP, o handler depende do conteúdo e do logging.

---

### 🟡 Médio — Flask

| Item | Detalhe |
|------|---------|
| **Repositório** | [pallets/flask](https://github.com/pallets/flask) |
| **Descrição** | Microframework web para Python |
| **Pasta de teste** | `testes/medio_flask/` |

**Arquivos selecionados:**

| Arquivo | Origem no repositório | Descrição |
|---------|----------------------|-----------|
| `app.py` | `src/flask/app.py` | Classe principal `Flask` — roteamento, request handling, contexto |
| `cli.py` | `src/flask/cli.py` | Interface de linha de comando — comandos `flask run`, `flask shell` |
| `blueprints.py` | `src/flask/blueprints.py` | Sistema de blueprints para organização modular |

**Requisitos mapeados (13 domínios):**

| Requisito | Descrição | Exemplos de funções |
|-----------|-----------|-------------------|
| `REQ_APP_CORE` | Inicialização da aplicação | `__init__`, `run`, `_make_timedelta` |
| `REQ_ROUTING` | Roteamento e dispatch | `dispatch_request`, `url_for`, `create_url_adapter` |
| `REQ_REQUEST_HANDLING` | Processamento request/response | `wsgi_app`, `make_response`, `process_response` |
| `REQ_CONTEXT` | Gestão de contextos | `app_context`, `request_context`, `do_teardown_request` |
| `REQ_ERROR_HANDLING` | Tratamento de exceções | `handle_http_exception`, `handle_exception`, `log_exception` |
| `REQ_TEMPLATING` | Templates Jinja2 | `create_jinja_environment` |
| `REQ_STATIC_FILES` | Arquivos estáticos | `get_send_file_max_age`, `send_static_file`, `open_resource` |
| `REQ_TESTING` | Utilitários de teste | `test_client`, `test_cli_runner` |
| `REQ_CLI_DISCOVERY` | Descoberta de app via CLI | `find_best_app`, `locate_app`, `prepare_import` |
| `REQ_CLI_COMMANDS` | Comandos CLI do Flask | `run_command`, `shell_command`, `routes_command` |
| `REQ_CLI_FRAMEWORK` | Framework de grupos CLI | `with_appcontext`, `command`, `group` |
| `REQ_CLI_TYPES` | Tipos de parâmetros CLI | `convert`, `_validate_key` |
| `REQ_BLUEPRINTS` | Sistema de blueprints | `set_output`, `get_params`, `set_params` |

**Resultados:**

| Métrica | Valor |
|---------|-------|
| Funções analisadas | 125 |
| Arestas no Call Graph | 47 |
| Requisitos identificados | 13 |
| Arestas no Grafo de Requisitos | 11 |

**Grafo de Requisitos (JSON):**

```json
{
  "REQ_APP_CORE": ["REQ_CLI_COMMANDS", "REQ_CLI_FRAMEWORK", "REQ_CONTEXT"],
  "REQ_CLI_FRAMEWORK": ["REQ_CONTEXT"],
  "REQ_CONTEXT": ["REQ_REQUEST_HANDLING"],
  "REQ_ERROR_HANDLING": ["REQ_REQUEST_HANDLING"],
  "REQ_REQUEST_HANDLING": ["REQ_CONTEXT", "REQ_ERROR_HANDLING", "REQ_ROUTING"],
  "REQ_ROUTING": ["REQ_ERROR_HANDLING", "REQ_REQUEST_HANDLING"]
}
```

**Interpretação:** A aplicação Flask apresenta relações cíclicas entre request handling, contexto, roteamento e tratamento de erros — refletindo a arquitetura real do framework onde essas camadas são fortemente acopladas. O core da aplicação conecta-se ao CLI e ao contexto.

---

### 🔴 Complexo — scikit-learn

| Item | Detalhe |
|------|---------|
| **Repositório** | [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) |
| **Descrição** | Biblioteca de Machine Learning para Python |
| **Pasta de teste** | `testes/complexo_sklearn/` |

**Arquivos selecionados:**

| Arquivo | Origem no repositório | Descrição |
|---------|----------------------|-----------|
| `pipeline.py` | `sklearn/pipeline.py` | `Pipeline` e `FeatureUnion` — encadeamento de estimadores |
| `_base.py` | `sklearn/linear_model/_base.py` | Classes base de modelos lineares (`LinearModel`, `LinearRegression`) |
| `_logistic.py` | `sklearn/linear_model/_logistic.py` | `LogisticRegression` e `LogisticRegressionCV` |
| `_classes.py` | `sklearn/tree/_classes.py` | Árvores de decisão (`DecisionTreeClassifier`, `DecisionTreeRegressor`) |

**Requisitos mapeados (9 domínios):**

| Requisito | Descrição | Exemplos de funções |
|-----------|-----------|-------------------|
| `REQ_PIPELINE` | Orquestração de estimadores | `get_params`, `set_params`, `_validate_steps`, `_iter` |
| `REQ_PIPELINE_FIT` | Treinamento via Pipeline | `fit`, `fit_transform`, `fit_predict` |
| `REQ_PIPELINE_PREDICT` | Predição e transformação | `predict`, `predict_proba`, `transform`, `score` |
| `REQ_FEATURE_UNION` | Concatenação paralela | `_validate_transformers`, `_parallel_func`, `_hstack` |
| `REQ_LINEAR_MODEL` | Modelos lineares base | `_preprocess_data`, `_rescale_data`, `_set_intercept` |
| `REQ_LOGISTIC_REGRESSION` | Regressão logística | `_logistic_regression_path`, `_check_solver`, `calc_score` |
| `REQ_SPARSE` | Operações com matrizes esparsas | `densify`, `sparsify`, `matvec` |
| `REQ_DECISION_TREE` | Árvores de decisão | `get_depth`, `get_n_leaves`, `_prune_tree`, `apply` |
| `REQ_SKLEARN_TAGS` | Sistema de tags do sklearn | `__sklearn_tags__`, `__sklearn_is_fitted__`, `classes_` |

**Resultados:**

| Métrica | Valor |
|---------|-------|
| Funções analisadas | 210 |
| Arestas no Call Graph | 80 |
| Requisitos identificados | 9 |
| Arestas no Grafo de Requisitos | 17 |

**Grafo de Requisitos (JSON):**

```json
{
  "REQ_DECISION_TREE": ["REQ_SKLEARN_TAGS"],
  "REQ_FEATURE_UNION": ["REQ_PIPELINE"],
  "REQ_LOGISTIC_REGRESSION": ["REQ_PIPELINE_PREDICT"],
  "REQ_PIPELINE": ["REQ_LOGISTIC_REGRESSION", "REQ_PIPELINE_PREDICT", "REQ_SKLEARN_TAGS"],
  "REQ_PIPELINE_FIT": ["REQ_DECISION_TREE", "REQ_FEATURE_UNION", "REQ_LINEAR_MODEL", "REQ_LOGISTIC_REGRESSION", "REQ_PIPELINE"],
  "REQ_PIPELINE_PREDICT": ["REQ_DECISION_TREE", "REQ_FEATURE_UNION", "REQ_LINEAR_MODEL", "REQ_LOGISTIC_REGRESSION", "REQ_PIPELINE"],
  "REQ_SKLEARN_TAGS": ["REQ_PIPELINE"]
}
```

**Interpretação:** O teste mais complexo revela a arquitetura central do scikit-learn: o `Pipeline` é o orquestrador que durante `fit` e `predict` conecta-se a todos os tipos de modelos (árvores, lineares, logísticos). O `FeatureUnion` alimenta o pipeline, e o sistema de tags permeia toda a estrutura. As 17 arestas refletem a alta interdependência entre os componentes de ML.

---

## 4. Resumo Comparativo

| Métrica | 🟢 Simples | 🟡 Médio | 🔴 Complexo |
|---------|-----------|---------|------------|
| **Projeto** | CPython stdlib | Flask | scikit-learn |
| **Arquivos analisados** | 2 | 3 | 4 |
| **Funções analisadas** | 298 | 125 | 210 |
| **Arestas Call Graph** | 130 | 47 | 80 |
| **Domínios de Requisito** | 10 | 13 | 9 |
| **Arestas Req Graph** | 9 | 11 | 17 |
| **Resultado** | ✅ Passou | ✅ Passou | ✅ Passou |

### Observações

- **Simples (CPython):** Maior número de funções (298), pois `argparse.py` é um módulo extenso. Porém o grafo de requisitos tem poucas arestas (9), indicando baixo acoplamento entre os domínios — comportamento esperado em módulos de stdlib.

- **Médio (Flask):** Menos funções mas mais domínios de requisito (13). O grafo revela ciclos entre `REQUEST_HANDLING ↔ CONTEXT ↔ ROUTING ↔ ERROR_HANDLING`, refletindo a arquitetura de middleware do Flask.

- **Complexo (scikit-learn):** O maior número de arestas no grafo de requisitos (17), demonstrando o alto acoplamento entre Pipeline, modelos e transformadores. `PIPELINE_FIT` e `PIPELINE_PREDICT` se conectam a 5 outros domínios cada.

---

## 5. Como Reproduzir

### Pré-requisitos

```bash
pip install -e reqgraph/
```

### Executar todos os testes

```bash
python run_tests.py
```

### Executar um nível específico

```bash
python run_tests.py simples      # Apenas CPython stdlib
python run_tests.py medio        # Apenas Flask
python run_tests.py complexo     # Apenas scikit-learn
```

### Via batch file (Windows)

```bash
run_tests.bat
```

---

## 6. Estrutura de Pastas

```
TESTE_TESE/
├── reqgraph/                       # Ferramenta ReqGraph
│   ├── call_graph.py               # Extração de call graph via AST
│   ├── req_graph.py                # Derivação do grafo de requisitos
│   ├── visualize.py                # Geração de visualizações PNG
│   ├── cli.py                      # Interface de linha de comando
│   └── ...
├── testes/
│   ├── simples_stdlib/             # 🟢 CPython stdlib
│   │   ├── argparse.py             # Fonte: Lib/argparse.py
│   │   ├── server.py               # Fonte: Lib/http/server.py
│   │   ├── mapeamento.py           # 10 domínios de requisito
│   │   ├── call_graph.png          # ✅ Gerado
│   │   ├── req_graph.png           # ✅ Gerado
│   │   ├── req_graph.json          # ✅ Gerado
│   │   └── req_graph.dot           # ✅ Gerado
│   ├── medio_flask/                # 🟡 Flask
│   │   ├── app.py                  # Fonte: src/flask/app.py
│   │   ├── cli.py                  # Fonte: src/flask/cli.py
│   │   ├── blueprints.py           # Fonte: src/flask/blueprints.py
│   │   ├── mapeamento.py           # 13 domínios de requisito
│   │   ├── call_graph.png          # ✅ Gerado
│   │   ├── req_graph.png           # ✅ Gerado
│   │   ├── req_graph.json          # ✅ Gerado
│   │   └── req_graph.dot           # ✅ Gerado
│   └── complexo_sklearn/           # 🔴 scikit-learn
│       ├── pipeline.py             # Fonte: sklearn/pipeline.py
│       ├── _base.py                # Fonte: sklearn/linear_model/_base.py
│       ├── _logistic.py            # Fonte: sklearn/linear_model/_logistic.py
│       ├── _classes.py             # Fonte: sklearn/tree/_classes.py
│       ├── mapeamento.py           # 9 domínios de requisito
│       ├── call_graph.png          # ✅ Gerado
│       ├── req_graph.png           # ✅ Gerado
│       ├── req_graph.json          # ✅ Gerado
│       └── req_graph.dot           # ✅ Gerado
├── run_tests.py                    # Script de teste automatizado
├── run_tests.bat                   # Wrapper Windows
└── RESULTADOS_TESTES.md            # Este documento
```
