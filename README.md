# ReqGraph

Protótipo de extração automática de grafos de requisitos a partir de código-fonte Python e de ranqueamento estrutural de requisitos com os algoritmos PageRank, HITS e SALSA.

Este repositório contém o software, o corpus experimental e os resultados que suportam a dissertação de mestrado:

> **Uma perspectiva de engenharia sobre a evolução de algoritmos de ranqueamento baseada em grafos**
> *Comparação empírica de PageRank, HITS e SALSA sobre grafos de requisitos extraídos por análise estática*

| | |
|---|---|
| **Autor** | Tales Santos |
| **Grau** | Mestrado em Engenharia Informática e Sistemas de Informação |
| **Instituição** | Universidade Lusófona, Departamento de Engenharia Informática e Sistemas de Informação (DEISI) |
| **Orientador** | Professor Aleksandar Mikovic |
| **Coorientadora** | Professora Sofia Fernandes |
| **Data** | Lisboa, outubro de 2026 |

---

## Índice

1. [Enquadramento](#1-enquadramento)
2. [Objetivos e questões de investigação](#2-objetivos-e-questões-de-investigação)
3. [Abordagem](#3-abordagem)
4. [Estrutura do repositório](#4-estrutura-do-repositório)
5. [Instalação](#5-instalação)
6. [Utilização](#6-utilização)
7. [Reprodução dos resultados da dissertação](#7-reprodução-dos-resultados-da-dissertação)
8. [Casos de estudo](#8-casos-de-estudo)
9. [Síntese dos resultados](#9-síntese-dos-resultados)
10. [Limitações](#10-limitações)
11. [Citação](#11-citação)
12. [Licenciamento](#12-licenciamento)

---

## 1. Enquadramento

A priorização de requisitos de software é uma das atividades mais sensíveis da Engenharia de Requisitos. As técnicas tradicionais (Comparação em Pares, Votação Acumulativa, AHP, entre outras) dependem fortemente da perceção subjetiva dos *stakeholders* e tendem a tornar-se inconsistentes em sistemas com elevado número de requisitos interdependentes.

A dissertação investiga uma alternativa de natureza estrutural: a aplicação de algoritmos de ranqueamento de grafos (PageRank, HITS e SALSA) ao grafo de dependências entre requisitos, extraído automaticamente do código-fonte por análise estática. O trabalho posiciona-se como evolução metodológica de Silva et al. (2013), que aplicaram o PageRank à priorização de requisitos.

No contexto deste trabalho, um "requisito" é uma agregação de responsabilidades implementadas no código-fonte, definida por um mapeamento explícito entre funções e requisitos (`func_to_req`). Não corresponde, portanto, a um requisito funcional no sentido clássico (Sommerville, 2007), mas a um *proxy* de *domain feature* para efeitos de ranqueamento estrutural.

## 2. Objetivos e questões de investigação

O objetivo da dissertação é investigar e comparar o comportamento dos algoritmos PageRank, HITS e SALSA na priorização estrutural de requisitos de software. Em concreto:

1. formalizar a aplicação de processos estocásticos e da Teoria dos Grafos à modelação de interdependências entre requisitos;
2. desenvolver um protótipo (ReqGraph) que extraia, de forma automatizada e reprodutível, o grafo de requisitos a partir do código-fonte de um projeto Python;
3. avaliar empiricamente, sobre projetos reais de código aberto, o comportamento comparativo dos três algoritmos.

As questões de investigação (*research questions*) são:

- **RQ1.** Em que medida os rankings produzidos por PageRank, HITS e SALSA concordam entre si quando aplicados a grafos de requisitos extraídos automaticamente por análise estática? A concordância é medida pelos coeficientes de correlação de Spearman (ρ) e de Kendall (τ_b).
- **RQ2.** Como varia essa concordância em função das propriedades estruturais do grafo (densidade, presença de ciclos, simetria de graus)?
- **RQ3.** Em que medida os requisitos de topo apontados pelos algoritmos correspondem a elementos conhecidos como arquiteturalmente centrais nos projetos analisados?

## 3. Abordagem

O trabalho é composto por dois componentes de software.

### 3.1 ReqGraph: extração do Grafo de Requisitos

O pacote `reqgraph` implementa um *pipeline* determinístico de quatro estágios:

```
Código-fonte Python (.py)
        |
        v
[1] Análise estática via AST (módulo ast da biblioteca padrão)
        |
        v
[2] Call Graph: vértices = funções/métodos; aresta f -> g se f invoca g
        |
        v
[3] Mapeamento func_to_req (função -> requisito), fornecido pelo investigador
        |
        v
[4] Grafo de Requisitos: aresta R_i -> R_j se uma função de R_i invoca
    uma função de R_j (i != j); auto-laços e duplicados são descartados
        |
        v
Artefactos: call_graph.png, req_graph.png, req_graph.json, req_graph.dot
```

O analisador resolve chamadas diretas (`f()`), chamadas qualificadas por módulo (`modulo.f()`), chamadas a métodos da própria classe (`self.metodo()`) e importações entre módulos do projeto, mantendo apenas as chamadas a funções definidas no próprio projeto. Construções dinâmicas (`getattr`, `exec`, *dispatch* por tipo em tempo de execução) não são capturadas pela análise estática.

### 3.2 ranker.py: ranqueamento estrutural

O módulo `ranker.py` consome o `req_graph.json` produzido pelo ReqGraph e aplica três algoritmos. A semântica adotada para as arestas é: `A -> B` significa que o requisito A depende de B. Assim, o grau de entrada de um vértice mede quantos requisitos dele dependem (*authority*) e o grau de saída mede quantos requisitos ele invoca (*hub*).

| Algoritmo | Referência | Implementação | Interpretação |
|---|---|---|---|
| PageRank | Brin & Page (1998) | `networkx.pagerank`, d = 0,85 | Importância global transitiva |
| HITS | Kleinberg (1999) | `networkx.hits` | *Authority*: dependência central; *hub*: orquestrador |
| SALSA | Lempel & Moran (2001) | Implementação própria em forma fechada | *Authority* e *hub* normalizados localmente por grau |

O NetworkX não disponibiliza o SALSA, pelo que este foi implementado com base na forma fechada da distribuição estacionária demonstrada pelos autores, ponderando cada componente conexa do grafo de suporte pelo seu peso relativo. A implementação foi verificada contra essa propriedade teórica em todos os grafos do corpus (Secção 3.4.4 da dissertação). A fundamentação matemática dos três algoritmos encontra-se em [`explicacao_algoritmos.md`](explicacao_algoritmos.md).

A concordância entre rankings é quantificada pelo script `compute_rank_correlations.py`, que calcula ρ de Spearman e τ_b de Kendall (com correção para empates) entre seis pares de rankings em cada caso de estudo.

## 4. Estrutura do repositório

```
reqgraph/                         Repositório
|
|-- reqgraph/                     Pacote Python ReqGraph
|   |-- __init__.py               API pública do pacote
|   |-- __main__.py               Ponto de entrada: python -m reqgraph
|   |-- cli.py                    Interface de linha de comando
|   |-- call_graph.py             Extração do Call Graph via AST
|   |-- req_graph.py              Derivação do Grafo de Requisitos
|   |-- visualize.py              Geração das visualizações PNG
|   |-- llm_prompt_mapping.md     Prompt para geração assistida do mapeamento
|   |-- setup.py                  Configuração de instalação
|   `-- requirements.txt          Dependências do pacote
|
|-- testes/                       Corpus experimental (três casos de estudo)
|   |-- simples_stdlib/           CPython stdlib: argparse.py, server.py
|   |-- medio_flask/              Flask: app.py, cli.py, blueprints.py
|   `-- complexo_sklearn/         scikit-learn: pipeline.py, _base.py,
|                                 _logistic.py, _classes.py
|
|-- ranker.py                     Ranqueamento com PageRank, HITS e SALSA
|-- run_tests.py                  Executa o ReqGraph sobre os três casos
|-- run_tests.bat                 Invólucro do run_tests.py para Windows
|-- run_ranking.py                Executa o ranker.py sobre os três casos
|-- compute_rank_correlations.py  Correlações de Spearman e Kendall
|
|-- rank_correlations.json        Coeficientes de correlação (Tabela 12)
|-- ranking_consolidado.json      Rankings consolidados dos três casos
|-- ranking_comparativo.png       Comparação do top-1 entre casos (Figura 13)
|
|-- explicacao_algoritmos.md      Fundamentação matemática dos algoritmos
|-- RESULTADOS_TESTES.md          Relatório da execução do ReqGraph no corpus
`-- requirements.txt              Dependências completas (ReqGraph e ranker)
```

Cada pasta de caso de estudo contém os ficheiros de código analisados, o respetivo `mapeamento.py` e os artefactos gerados:

| Artefacto | Produzido por | Utilização na dissertação |
|---|---|---|
| `call_graph.png` | ReqGraph | Inspeção do grafo de chamadas; Apêndice C |
| `req_graph.json`, `req_graph.dot` | ReqGraph | Entrada do `ranker.py`; contagens da Tabela 8 |
| `req_graph.png` | ReqGraph | Validação de coerência; figuras da Secção 4.1 |
| `ranking_results.json` | `ranker.py` | Scores das tabelas de rankings (Secção 4.2) |
| `ranking_results.png` | `ranker.py` | Figuras comparativas por caso de estudo |

## 5. Instalação

### 5.1 Pré-requisitos

- Python 3.8 ou superior
- pip

| Pacote | Versão mínima | Função |
|---|---|---|
| `networkx` | 3.0 | Manipulação e análise de grafos direcionados |
| `matplotlib` | 3.5 | Geração de visualizações PNG |
| `numpy` | 1.24 | Computação matricial |
| `scipy` | 1.10 | Computação numérica; disposição *Kamada-Kawai* das figuras |

### 5.2 Procedimento

```bash
git clone https://github.com/tales96323/reqgraph.git
cd reqgraph

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install -e reqgraph/
```

A instalação do pacote (`pip install -e reqgraph/`) disponibiliza o comando `reqgraph` em qualquer diretório. Em alternativa, sem instalar o pacote, o ReqGraph pode ser executado como módulo a partir da raiz do repositório (`python -m reqgraph ...`).

## 6. Utilização

### 6.1 Mapeamento `func_to_req`

O ReqGraph requer um ficheiro Python que defina um dicionário global chamado `func_to_req`, que associa o nome curto de cada função ao requisito correspondente:

```python
func_to_req = {
    "login":      "REQ_AUTENTICACAO",
    "query_user": "REQ_BANCO_DE_DADOS",
    "checkout":   "REQ_PAGAMENTOS",
}
```

As chaves são nomes curtos, sem qualificação de módulo ou classe: tanto `auth.login` como `app.AuthService.login` são mapeados pela chave `"login"`. Por consequência, todas as definições com o mesmo nome curto são atribuídas ao mesmo requisito. Funções não mapeadas permanecem no Call Graph, mas não contribuem com arestas para o Grafo de Requisitos, e são listadas como aviso durante a execução.

O protocolo seguido na dissertação para construir os mapeamentos (levantamento de domínios, granularidade-alvo de 5 a 30 funções por requisito, regras de desempate e revisão de cobertura) está descrito na Secção 3.6.2. Para reduzir o custo desta etapa, o ficheiro [`reqgraph/llm_prompt_mapping.md`](reqgraph/llm_prompt_mapping.md) contém um *prompt* estruturado que permite gerar uma primeira versão do mapeamento com um modelo de linguagem; o resultado deve ser revisto pelo analista.

### 6.2 Extração do Grafo de Requisitos

```bash
reqgraph <projeto> --mapping <projeto>/mapeamento.py [--output <diretório>] [--ignore <ficheiros>]

# ou, sem instalação, a partir da raiz do repositório
python -m reqgraph testes/simples_stdlib/ --mapping testes/simples_stdlib/mapeamento.py
```

| Opção | Descrição |
|---|---|
| `project` | Diretório raiz do projeto Python a analisar |
| `--mapping`, `-m` | Ficheiro `.py` que define `func_to_req` (obrigatório) |
| `--output`, `-o` | Diretório de saída (por omissão, o diretório do projeto) |
| `--ignore` | Ficheiros `.py` a excluir da análise (por omissão, `mapeamento.py`) |

### 6.3 Ranqueamento

```bash
python ranker.py testes/simples_stdlib/req_graph.json      # um grafo (JSON)
python ranker.py testes/medio_flask/req_graph.dot -f dot   # um grafo (DOT)
python ranker.py --all                                     # os três casos de estudo
```

Para cada grafo são produzidos `ranking_results.json` e `ranking_results.png`. A opção `--all` gera ainda `ranking_consolidado.json` e `ranking_comparativo.png` na raiz do repositório.

### 6.4 Utilização programática

```python
from reqgraph import CallGraphBuilder, RequirementGraphBuilder, visualize_req_graph

call_graph = CallGraphBuilder().analyze_project("caminho/do/projeto",
                                                ignore_files={"mapeamento.py"})
builder = RequirementGraphBuilder(call_graph, func_to_req)
req_graph = builder.build()
builder.to_json("req_graph.json")
visualize_req_graph(req_graph, output_path="req_graph.png")
```

## 7. Reprodução dos resultados da dissertação

Os resultados apresentados no Capítulo 4 da dissertação são reproduzidos, a partir da raiz do repositório, pela seguinte sequência:

```bash
python run_tests.py                    # 1. ReqGraph sobre os três casos de estudo
python ranker.py --all                 # 2. PageRank, HITS e SALSA
python compute_rank_correlations.py    # 3. Spearman e Kendall -> rank_correlations.json
```

O `run_tests.py` aceita opcionalmente o nível a executar (`simples`, `medio` ou `complexo`) e verifica a geração dos quatro artefactos esperados em cada caso. O `run_ranking.py` é uma alternativa ao passo 2 que aceita os mesmos níveis.

O *pipeline* não contém fontes de aleatoriedade: a análise estática é determinística, o PageRank e o HITS partem de vetores iniciais uniformes com tolerâncias fixas, o SALSA é calculado em forma fechada e as visualizações usam disposições determinísticas. A reexecução sobre o corpus versionado reproduz os grafos (`req_graph.json`, `req_graph.dot`) byte a byte e os mesmos *scores* e coeficientes de correlação; podem ocorrer apenas diferenças irrelevantes de representação, como `-0.0` em vez de `0.0` em *scores* nulos.

## 8. Casos de estudo

A avaliação segue um desenho de estudo de casos múltiplos com amostragem intencional, cobrindo regimes crescentes de acoplamento arquitetural. Os ficheiros analisados foram copiados dos repositórios de origem para `testes/`, constituindo um *snapshot* imutável do corpus.

| Nível | Projeto | Ficheiros analisados | Origem |
|---|---|---|---|
| Simples | CPython stdlib | `Lib/argparse.py`, `Lib/http/server.py` | https://github.com/python/cpython |
| Médio | Flask | `src/flask/app.py`, `src/flask/cli.py`, `src/flask/blueprints.py` | https://github.com/pallets/flask |
| Complexo | scikit-learn | `sklearn/pipeline.py`, `sklearn/linear_model/_base.py`, `sklearn/linear_model/_logistic.py`, `sklearn/tree/_classes.py` | https://github.com/scikit-learn/scikit-learn |

| Métrica | CPython stdlib | Flask | scikit-learn |
|---|---:|---:|---:|
| Ficheiros analisados | 2 | 3 | 4 |
| Linhas de código | 3 998 | 2 880 | 7 409 |
| Funções e métodos detetados | 298 | 125 | 210 |
| Arestas no Call Graph | 130 | 47 | 80 |
| Requisitos declarados no mapeamento | 10 | 13 | 9 |
| Requisitos com arestas | 9 | 7 | 8 |
| Arestas no Grafo de Requisitos | 9 | 11 | 17 |
| Densidade | 0,125 | 0,262 | 0,304 |

O relatório detalhado da execução do ReqGraph sobre o corpus encontra-se em [`RESULTADOS_TESTES.md`](RESULTADOS_TESTES.md).

## 9. Síntese dos resultados

**RQ1.** A concordância entre algoritmos é estruturada pela dimensão de centralidade comparada. Dos 12 pares comensuráveis (pares que medem a mesma dimensão, *authority* ou *hub*, nos três projetos), 8 satisfazem o critério de convergência forte. Nenhum dos 6 pares duais (PageRank face aos rankings de *hub*) o satisfaz, com correlações de Spearman entre -0,51 e 0,24.

**RQ2.** Na leitura exploratória que o corpus permite, a densidade não se mostrou positivamente associada à concordância entre algoritmos. A presença de ciclos afeta sobretudo o PageRank, que acumula massa estacionária nos vértices envolvidos; em consequência, a correlação entre PageRank e HITS-*authority* decresce à medida que a estrutura cíclica ganha peso (ρ = 0,65; 0,60; 0,39).

**RQ3.** Os requisitos de topo correspondem a elementos reconhecidamente centrais nas arquiteturas analisadas (por exemplo, a `Pipeline` no scikit-learn e o tratamento de pedidos no Flask). Esta correspondência é qualitativa e constitui uma verificação de consistência interna, e não uma validação independente, dado que o mapeamento e a avaliação foram realizados pelo mesmo investigador.

Conclui-se que o ranqueamento estrutural constitui um complemento, e não um substituto, das técnicas tradicionais de priorização, reduzindo, sem eliminar, o viés subjetivo no processo.

## 10. Limitações

- **Subjetividade do mapeamento.** O mapeamento `func_to_req` é o único passo do *pipeline* com intervenção humana e foi construído por um único investigador, sem medida de concordância entre avaliadores.
- **Resolução por nome curto.** A correspondência por nome curto agrega no mesmo requisito todas as definições homónimas (por exemplo, `fit` ou `__init__`), o que pode fundir arestas que pertenceriam a requisitos distintos. A desambiguação por nome totalmente qualificado está identificada como trabalho futuro.
- **Dimensão do corpus.** O corpus é composto por três projetos com Grafos de Requisitos de 7 a 9 vértices com arestas, pelo que as conclusões sobre propriedades estruturais são exploratórias e não generalizáveis estatisticamente.
- **Rastreabilidade do *snapshot*.** O *commit* exato de cada repositório de origem não foi registado no momento da recolha. A reprodutibilidade interna está assegurada pelos ficheiros versionados em `testes/`, mas a comparação com versões futuras dos projetos exige essa referência.
- **Limites da análise estática.** Chamadas resolvidas apenas em tempo de execução não são capturadas.
- **Ausência de validação humana.** Os rankings estruturais não foram comparados com priorizações realizadas por profissionais; medir a concordância entre algoritmos não afere, por si só, a qualidade da priorização.

## 11. Citação

```bibtex
@mastersthesis{santos2026reqgraph,
  author = {Santos, Tales},
  title  = {Uma perspectiva de engenharia sobre a evolu{\c{c}}{\~a}o de algoritmos
            de ranqueamento baseada em grafos: compara{\c{c}}{\~a}o emp{\'i}rica de
            PageRank, HITS e SALSA sobre grafos de requisitos extra{\'i}dos por
            an{\'a}lise est{\'a}tica},
  school = {Universidade Lus{\'o}fona},
  address = {Lisboa},
  year   = {2026},
  month  = oct,
  type   = {Disserta{\c{c}}{\~a}o de Mestrado em Engenharia Inform{\'a}tica e
            Sistemas de Informa{\c{c}}{\~a}o},
  url    = {https://github.com/tales96323/reqgraph}
}
```

## 12. Licenciamento

O código do ReqGraph e do módulo de ranqueamento foi desenvolvido no âmbito da dissertação acima identificada e destina-se a fins académicos e de investigação.

Os ficheiros de código-fonte de terceiros incluídos em `testes/` são cópias de ficheiros dos projetos de origem, redistribuídas exclusivamente para permitir a replicação do estudo, e mantêm as respetivas licenças originais:

- CPython (`testes/simples_stdlib/`): Python Software Foundation License;
- Flask (`testes/medio_flask/`): BSD 3-Clause License, Copyright Pallets;
- scikit-learn (`testes/complexo_sklearn/`): BSD 3-Clause License, Copyright The scikit-learn developers.
