# Algoritmos de Ranqueamento de Grafos — Documentação Técnica

> **Contexto:** Análise de grafos de requisitos gerados pelo ReqGraph, utilizando algoritmos de ranqueamento para priorização estrutural de requisitos de software.

---

## 1. Introdução — Pipeline de Dados

O script `ranker.py` consome os grafos de dependência de requisitos gerados pelo **ReqGraph**, estendendo o pipeline de análise existente:

```
Código-fonte Python
        │
        ▼
   AST (Abstract Syntax Tree)
        │
        ▼
   Call Graph (grafo de chamadas)
        │
        ▼
   Mapeamento func_to_req
        │
        ▼
   Grafo de Requisitos (req_graph.json / req_graph.dot)
        │
        ▼
   ┌─────────────────────────────────────────┐
   │         ranker.py (este módulo)         │
   │                                         │
   │   ┌───────────┐  ┌──────┐  ┌───────┐   │
   │   │ PageRank  │  │ HITS │  │ SALSA │   │
   │   └───────────┘  └──────┘  └───────┘   │
   │                                         │
   │   → ranking_results.json                │
   │   → ranking_results.png                 │
   └─────────────────────────────────────────┘
```

### 1.1 Formato de Entrada

O `ranker.py` aceita dois formatos de entrada:

1. **JSON** (`req_graph.json`) — Lista de adjacência:
   ```json
   {
     "REQ_A": ["REQ_B", "REQ_C"],
     "REQ_D": ["REQ_A"]
   }
   ```
   Cada chave é um requisito que *depende de* (aponta para) os requisitos listados no array.

2. **DOT** (`req_graph.dot`) — Formato Graphviz:
   ```dot
   digraph RequirementGraph {
       "REQ_A" -> "REQ_B";
       "REQ_A" -> "REQ_C";
   }
   ```

### 1.2 Construção do Grafo no NetworkX

O ficheiro é carregado e convertido num **grafo direcionado** (`nx.DiGraph`):

```python
import networkx as nx

G = nx.DiGraph()
for source, targets in adjacency_list.items():
    for target in targets:
        G.add_edge(source, target)
```

A semântica das arestas é: **REQ_A → REQ_B** significa que o requisito A *depende de* (chama funções de) B. Portanto:
- **Arestas de saída** (out-degree) = requisitos dos quais este depende
- **Arestas de entrada** (in-degree) = requisitos que dependem deste

---

## 2. PageRank

### 2.1 Fundamento Teórico

O **PageRank**, originalmente proposto por Brin e Page (1998) para ranquear páginas web, modela a probabilidade de um "navegador aleatório" visitar cada nó do grafo. No contexto de requisitos, simula um engenheiro que navega pelas dependências aleatoriamente.

### 2.2 Formulação Matemática

O score PageRank de um nó $v$ é definido iterativamente como:

$$PR(v) = \frac{1 - d}{N} + d \sum_{u \in B(v)} \frac{PR(u)}{L(u)}$$

Onde:
- $d$ = **fator de amortecimento** (damping factor) — probabilidade de seguir um link em vez de saltar aleatoriamente
- $N$ = número total de nós no grafo
- $B(v)$ = conjunto de nós que apontam para $v$ (predecessores)
- $L(u)$ = número de arestas de saída de $u$ (out-degree)

### 2.3 Fator de Amortecimento $d = 0.85$

O valor $d = 0.85$ é o padrão clássico utilizado na literatura e no NetworkX. A sua interpretação é:

- **85% do tempo**: o navegador segue um link existente (dependência entre requisitos)
- **15% do tempo**: o navegador salta para um nó aleatório (evita ficar preso em ciclos ou nós sem saída)

O termo $\frac{1 - d}{N} = \frac{0.15}{N}$ garante que todos os nós recebem uma probabilidade mínima, mesmo que não tenham nenhum nó a apontar para eles.

### 2.4 Tratamento de Dangling Nodes

Nós sem arestas de saída (*dangling nodes*) — como `REQ_CONFIGURATION` ou `REQ_HTTP_CONTENT` no grafo do CPython — são nós-folha que não dependem de outros requisitos. No modelo de navegação aleatória, quando o navegador chega a um destes nós, ele redistribui a sua probabilidade uniformemente para todos os nós do grafo.

O NetworkX trata automaticamente este caso internamente.

### 2.5 Implementação no Código

```python
import networkx as nx

def compute_pagerank(G, alpha=0.85, max_iter=100, tol=1e-06):
    scores = nx.pagerank(G, alpha=alpha, max_iter=max_iter, tol=tol)
    return scores
```

Parâmetros:
| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `alpha` | 0.85 | Fator de amortecimento $d$ |
| `max_iter` | 100 | Número máximo de iterações para convergência |
| `tol` | 1e-06 | Tolerância de convergência (diferença entre iterações) |

A soma de todos os scores PageRank é sempre igual a **1.0** (distribuição de probabilidade).

### 2.6 Interpretação no Contexto de Requisitos

| Score | Interpretação |
|-------|---------------|
| **Alto PageRank** | Requisito **fundamental** — é dependência (direta ou transitiva) de muitos outros requisitos. Alterações neste requisito têm impacto sistémico elevado. |
| **Baixo PageRank** | Requisito **periférico** — poucos outros requisitos dependem dele. Alterações têm impacto localizado. |

**Exemplo:** No grafo do scikit-learn, `REQ_PIPELINE` terá alto PageRank porque é apontado por `PIPELINE_FIT`, `PIPELINE_PREDICT`, `FEATURE_UNION` e `SKLEARN_TAGS` — é o requisito central que todos os outros orquestram.

---

## 3. HITS (Hyperlink-Induced Topic Search)

### 3.1 Fundamento Teórico

O algoritmo **HITS**, proposto por Kleinberg (1999), identifica dois papéis distintos para cada nó:

- **Authority (Autoridade):** Nó que é referenciado por muitos bons hubs — representa conteúdo valioso
- **Hub:** Nó que aponta para muitas boas authorities — representa um bom agregador/orquestrador

Esta dualidade é particularmente relevante para grafos de requisitos, onde alguns requisitos *fornecem funcionalidade* (authorities) e outros *orquestram/agregam* funcionalidades (hubs).

### 3.2 Formulação Matemática

O HITS calcula dois scores para cada nó $v$ através de atualizações iterativas mutuamente recursivas:

**Atualização de Authorities:**
$$a(v) = \sum_{u \to v} h(u)$$

O score de authority de $v$ é a soma dos scores de hub de todos os nós que apontam para $v$.

**Atualização de Hubs:**
$$h(v) = \sum_{v \to w} a(w)$$

O score de hub de $v$ é a soma dos scores de authority de todos os nós para os quais $v$ aponta.

Após cada iteração, os vetores são **normalizados** (divididos pela norma euclidiana) para evitar divergência.

### 3.3 Convergência

O processo iterativo converge para o **autovetor dominante** da matriz $A^T A$ (para authorities) e $A A^T$ (para hubs), onde $A$ é a matriz de adjacência do grafo.

### 3.4 Implementação no Código

```python
import networkx as nx

def compute_hits(G, max_iter=100, tol=1e-08):
    hubs, authorities = nx.hits(G, max_iter=max_iter, tol=tol)
    return hubs, authorities
```

A função `nx.hits()` retorna dois dicionários separados:
- `hubs`: `{nó: score_hub}` — normalizado (soma dos quadrados = 1)
- `authorities`: `{nó: score_authority}` — normalizado (soma dos quadrados = 1)

### 3.5 Interpretação no Contexto de Requisitos

| Score | Interpretação |
|-------|---------------|
| **Alto score de Authority** | Requisito que muitos outros **dependem dele** — funcionalidade central que é consumida por múltiplos pontos do sistema. É um candidato a testes rigorosos e revisão cuidadosa. |
| **Alto score de Hub** | Requisito que **agrega/orquestra** muitos outros — ponto de integração que conecta múltiplas funcionalidades. Alterações aqui afetam muitas integrações. |

**Exemplo:** No grafo do Flask:
- `REQ_REQUEST_HANDLING` será uma **authority** forte, pois `CONTEXT`, `ERROR_HANDLING` e `ROUTING` todos apontam para ele.
- `REQ_REQUEST_HANDLING` será também um **hub** forte, pois ele aponta para `CONTEXT`, `ERROR_HANDLING` e `ROUTING`.
- Esta dupla classificação indica um requisito **altamente acoplado** — tanto fornece como consome funcionalidades.

---

## 4. SALSA (Stochastic Approach for Link-Structure Analysis)

### 4.1 Fundamento Teórico

O **SALSA**, proposto por Lempel e Moran (2001), combina a separação hub/authority do HITS com a abordagem probabilística (cadeias de Markov) do PageRank.

A motivação principal do SALSA é resolver uma limitação do HITS: em grafos com estruturas dominantes (*tightly-knit communities*), o HITS tende a atribuir scores elevados a um único cluster de nós, ignorando outros clusters relevantes. O SALSA resolve isto normalizando os pesos localmente (por grau de cada nó), em vez de globalmente.

### 4.2 Construção do Grafo Bipartido

Dado o grafo original $G = (V, E)$, o SALSA constrói um **grafo bipartido** $G' = (V_H \cup V_A, E')$:

1. **Para cada nó** $v \in V$, cria dois nós:
   - $v_H$ (cópia hub, no lado esquerdo)
   - $v_A$ (cópia authority, no lado direito)

2. **Para cada aresta** $(u, v) \in E$, cria duas arestas no grafo bipartido:
   - $u_H \to v_A$ com peso $\frac{1}{\text{out\_degree}(u)}$ — transição do hub $u$ para a authority $v$
   - $v_A \to u_H$ com peso $\frac{1}{\text{in\_degree}(v)}$ — transição da authority $v$ de volta para o hub $u$

### 4.3 Cadeias de Markov

O passeio aleatório no grafo bipartido define duas cadeias de Markov:

**Cadeia de Hubs** ($H \to A \to H \to ...$):

A probabilidade de transição do hub $u$ para o hub $w$ (passando por uma authority intermediária) é:

$$P_{hub}(u \to w) = \sum_{v: (u,v) \in E \text{ e } (w,v) \in E} \frac{1}{\text{out}(u)} \cdot \frac{1}{\text{in}(v)}$$

**Cadeia de Authorities** ($A \to H \to A \to ...$):

A probabilidade de transição da authority $v$ para a authority $x$ (passando por um hub intermediário) é:

$$P_{auth}(v \to x) = \sum_{u: (u,v) \in E \text{ e } (u,x) \in E} \frac{1}{\text{in}(v)} \cdot \frac{1}{\text{out}(u)}$$

### 4.4 Distribuição Estacionária (forma fechada)

Os scores finais do SALSA são as **distribuições estacionárias** ($\pi$) de cada cadeia de Markov. Lempel & Moran (2001) demonstram que, para grafos não ponderados, estas distribuições admitem **forma fechada** — não é necessária iteração numérica:

- Se a cadeia é irredutível: $\text{auth\_score}(v) = \frac{\text{in\_degree}(v)}{|E|}$ e $\text{hub\_score}(v) = \frac{\text{out\_degree}(v)}{|E|}$.
- Se a cadeia **não** é irredutível (caso geral): a proporcionalidade ao grau vale **dentro de cada componente conexa** $C$ do grafo de suporte da cadeia, e cada componente é ponderada pela sua dimensão relativa:

$$\text{auth\_score}(v) = \frac{|C(v)|}{|V_A|} \cdot \frac{\text{in}(v)}{\sum_{u \in C(v)} \text{in}(u)}$$

Nós sem grau no lado respetivo (in-degree 0 para authority; out-degree 0 para hub) não participam na cadeia e recebem score 0.

> **Nota histórica (correção R7).** Uma versão anterior calculava $\pi$ por *power iteration* com $\pi^{(t+1)} = T^T \pi^{(t)}$, sendo $T$ construída coluna-estocástica (`[destino][origem]`). Essa transposição itera a cadeia na direção errada: converge para o vetor próprio **direito** da matriz de transição (o vetor constante), não para o vetor próprio **esquerdo** (a distribuição estacionária). O resultado eram distribuições artificialmente **uniformes** sobre os nós com grau não nulo — incompatíveis com a proporcionalidade ao grau prevista pela teoria. O erro foi detetado confrontando os scores com a forma fechada acima e corrigido substituindo a iteração pela própria forma fechada.

### 4.5 Implementação no Código

Como o NetworkX **não inclui** uma implementação do SALSA, o algoritmo foi implementado manualmente, usando diretamente a forma fechada por componente:

```python
def compute_salsa(G):
    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())

    def side_scores(deg, side_edges):
        side_nodes = [v for v in G.nodes() if deg[v] > 0]
        scores = {v: 0.0 for v in G.nodes()}
        support = nx.Graph()
        support.add_nodes_from(side_nodes)
        support.add_edges_from(side_edges)   # suporte da cadeia
        n_side = len(side_nodes)
        for comp in nx.connected_components(support):
            w = len(comp) / n_side           # ponderação da componente
            total = sum(deg[v] for v in comp)
            for v in comp:
                scores[v] = w * deg[v] / total
        return scores

    # authorities adjacentes se partilham um hub predecessor;
    # hubs adjacentes se partilham uma authority sucessora
    auth_edges = [(a, b) for u in G for a, b in
                  itertools.combinations(list(G.successors(u)), 2)]
    hub_edges = [(a, b) for v in G for a, b in
                 itertools.combinations(list(G.predecessors(v)), 2)]

    return side_scores(out_deg, hub_edges), side_scores(in_deg, auth_edges)
```

**Verificação:** os scores produzidos foram confrontados com a propriedade teórica (proporcionalidade ao grau, componente a componente) nos três grafos do corpus — coincidência exata.

### 4.6 Interpretação no Contexto de Requisitos

| Score | Interpretação |
|-------|---------------|
| **Alto SALSA Hub** | Requisito com muitas **dependências de saída** (alto out-degree) — orquestra múltiplos outros requisitos. A normalização local do SALSA evita que clusters densos dominem o ranking. |
| **Alto SALSA Authority** | Requisito com muitas **dependências de entrada** (alto in-degree) — é uma dependência fundamental. A abordagem estocástica do SALSA distribui importância de forma mais equilibrada que o HITS. |

**Diferença chave SALSA vs HITS:** O SALSA normaliza por nó (divisão pelo grau), enquanto o HITS normaliza globalmente. Isto significa que no SALSA, um nó com 3 arestas contribui igualmente independentemente de estar conectado a nós com 1 ou 100 arestas.

---

## 5. Comparação entre os Algoritmos

### 5.1 Tabela Comparativa

| Característica | PageRank | HITS | SALSA |
|----------------|----------|------|-------|
| **Tipo de score** | Único (importância global) | Dual (hub + authority) | Dual (hub + authority) |
| **Modelo** | Navegação aleatória com teleporte | Reforço mútuo iterativo | Cadeia de Markov sobre grafo bipartido |
| **Normalização** | Global (soma = 1) | Global (norma euclidiana) | Local (por grau de nó) |
| **Sensibilidade a clusters** | Moderada | Alta (pode ser dominado por clusters) | Baixa (normalização local) |
| **Tratamento de ciclos** | Damping factor | Convergência natural | Distribuição estacionária |
| **Complexidade** | $O(N + E)$ por iteração | $O(N + E)$ por iteração | $O(N^2)$ (multiplicação de matrizes) |
| **Disponível no NetworkX** | ✅ `nx.pagerank()` | ✅ `nx.hits()` | ❌ (implementação manual) |

### 5.2 Guia Rápido de Interpretação

Para a **priorização de requisitos**, cada algoritmo responde a uma pergunta diferente:

| Pergunta | Algoritmo | Score |
|----------|-----------|-------|
| "Qual é o requisito mais **importante** do sistema como um todo?" | **PageRank** | Alto PageRank |
| "Qual requisito é a **dependência central** que todos consomem?" | **HITS** | Alta Authority |
| "Qual requisito é o **maior orquestrador/integrador**?" | **HITS** | Alto Hub |
| "Qual requisito tem o **maior impacto de entrada**, de forma equilibrada?" | **SALSA** | Alta Authority |
| "Qual requisito **agrega mais funcionalidades**, de forma equilibrada?" | **SALSA** | Alto Hub |

### 5.3 Quando os Rankings Divergem

Divergências entre os algoritmos são informativas:

- **PageRank alto, HITS authority baixo:** O requisito é importante por via transitiva (cadeias longas de dependência), mas não é diretamente referenciado por muitos nós.
- **HITS authority alto, SALSA authority moderado:** Pode indicar que a alta authority vem de estar conectado a um cluster denso (o SALSA penaliza esta concentração).
- **SALSA hub alto, HITS hub baixo:** O requisito tem muitas saídas mas para nós de baixa qualidade (o HITS penaliza, o SALSA não).

---

## 6. Ficheiros Gerados

O script `ranker.py` gera os seguintes artefatos em cada diretório de teste:

| Ficheiro | Descrição |
|----------|-----------|
| `ranking_results.json` | Scores completos dos 3 algoritmos em formato JSON estruturado |
| `ranking_results.png` | Visualização com gráficos de barras horizontais para cada algoritmo |

Quando executado com `--all`, gera também na raiz do projeto:

| Ficheiro | Descrição |
|----------|-----------|
| `ranking_consolidado.json` | Resultados de todos os projetos num único ficheiro |
| `ranking_comparativo.png` | Gráfico comparativo dos top requisitos entre projetos |

---

## 7. Como Executar

### Requisito único

```bash
python ranker.py testes/simples_stdlib/req_graph.json
```

### Todos os projetos

```bash
python ranker.py --all
# ou
python run_ranking.py
```

### Projeto específico via runner

```bash
python run_ranking.py simples      # CPython stdlib
python run_ranking.py medio        # Flask
python run_ranking.py complexo     # scikit-learn
```
