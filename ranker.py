"""
ranker.py — Ranqueamento de Requisitos com PageRank, HITS e SALSA.

Carrega grafos de requisitos gerados pelo ReqGraph (JSON ou DOT)
e calcula scores de ranqueamento para cada nó (requisito) utilizando
três algoritmos clássicos de análise de grafos.

Uso:
    python ranker.py testes/simples_stdlib/req_graph.json
    python ranker.py testes/medio_flask/req_graph.dot --format dot
    python ranker.py --all
"""

import argparse
import json
import os
import sys
from collections import defaultdict

import networkx as nx
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Backend não-interativo para geração de PNG
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ══════════════════════════════════════════════════════════════════════════════
# 1. CARREGAMENTO DO GRAFO
# ══════════════════════════════════════════════════════════════════════════════

def load_graph_from_json(filepath):
    """
    Carrega um grafo direcionado a partir de um ficheiro JSON
    no formato de lista de adjacência do ReqGraph.

    Formato esperado:
      {"REQ_A": ["REQ_B", "REQ_C"], "REQ_D": ["REQ_A"], ...}

    Retorna um nx.DiGraph com todos os nós (incluindo nós-folha
    que só aparecem como destinos).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        adj = json.load(f)

    G = nx.DiGraph()

    # Adicionar todas as arestas
    for source, targets in adj.items():
        for target in targets:
            G.add_edge(source, target)

    # Garantir que nós sem arestas de saída também estejam presentes
    all_nodes = set(adj.keys())
    for targets in adj.values():
        all_nodes.update(targets)
    for node in all_nodes:
        if node not in G:
            G.add_node(node)

    return G


def load_graph_from_dot(filepath):
    """
    Carrega um grafo direcionado a partir de um ficheiro DOT (Graphviz).
    Requer pydot instalado.
    """
    try:
        G = nx.drawing.nx_pydot.read_dot(filepath)
    except Exception as e:
        print(f"  [ERRO] Falha ao ler DOT: {e}")
        print("  Dica: instale pydot com 'pip install pydot'")
        sys.exit(1)

    # read_dot pode retornar MultiDiGraph; converter para DiGraph
    if isinstance(G, nx.MultiDiGraph):
        G = nx.DiGraph(G)

    # Limpar nomes de nós (remover aspas que o DOT adiciona)
    mapping = {}
    for node in G.nodes():
        clean = str(node).strip('"').strip("'")
        if clean != node:
            mapping[node] = clean
    if mapping:
        G = nx.relabel_nodes(G, mapping)

    return G


def load_graph(filepath, fmt="auto"):
    """Carrega o grafo detectando o formato automaticamente."""
    if fmt == "auto":
        ext = os.path.splitext(filepath)[1].lower()
        fmt = "dot" if ext == ".dot" else "json"

    if fmt == "json":
        return load_graph_from_json(filepath)
    else:
        return load_graph_from_dot(filepath)


# ══════════════════════════════════════════════════════════════════════════════
# 2. ALGORITMOS DE RANQUEAMENTO
# ══════════════════════════════════════════════════════════════════════════════

def compute_pagerank(G, alpha=0.85, max_iter=100, tol=1e-06):
    """
    Calcula o PageRank de cada nó no grafo direcionado G.

    Fórmula:
        PR(v) = (1 - d) / N + d * Σ PR(u) / L(u)
                                   u ∈ B(v)

    onde:
      - d = alpha (fator de amortecimento, padrão 0.85)
      - N = número total de nós
      - B(v) = conjunto de nós que apontam para v
      - L(u) = número de arestas de saída de u

    Parâmetros
    ----------
    G : nx.DiGraph
    alpha : float — fator de amortecimento (probabilidade de seguir um link)
    max_iter : int — número máximo de iterações
    tol : float — tolerância de convergência

    Retorna
    -------
    dict[str, float] — scores de PageRank por nó
    """
    scores = nx.pagerank(G, alpha=alpha, max_iter=max_iter, tol=tol)
    return scores


def compute_hits(G, max_iter=100, tol=1e-08):
    """
    Calcula os scores HITS (Hyperlink-Induced Topic Search) de Kleinberg.

    O algoritmo identifica dois tipos de importância:
      - Authority: nós que são apontados por muitos hubs bons
      - Hub: nós que apontam para muitas authorities boas

    Atualização iterativa:
      a(v) = Σ h(u)    para todo u → v
      h(v) = Σ a(w)    para todo v → w

    Parâmetros
    ----------
    G : nx.DiGraph
    max_iter : int
    tol : float

    Retorna
    -------
    tuple[dict, dict] — (hubs, authorities)
    """
    hubs, authorities = nx.hits(G, max_iter=max_iter, tol=tol)
    return hubs, authorities


def compute_salsa(G):
    """
    Calcula os scores SALSA (Stochastic Approach for Link-Structure Analysis)
    seguindo Lempel & Moran (2001).

    O SALSA define dois passeios aleatórios sobre um grafo bipartido
    auxiliar em que cada vértice do grafo original aparece como hub
    (se out_degree > 0) e/ou como authority (se in_degree > 0):
      - Cadeia de authorities: v_a → u_h → x_a (passo atrás, passo à frente)
      - Cadeia de hubs:        u_h → v_a → w_h (passo à frente, passo atrás)

    Lempel & Moran demonstram que, em grafos não ponderados, a
    distribuição estacionária de cada cadeia admite forma fechada:
    dentro de cada componente conexa C do grafo de suporte da cadeia,
      - auth_score(v) = in_degree(v)  / Σ_{u ∈ C} in_degree(u)
      - hub_score(v)  = out_degree(v) / Σ_{u ∈ C} out_degree(u)
    Como as cadeias não são, em geral, irredutíveis (o grafo de suporte
    pode ter várias componentes), cada componente é ponderada pela sua
    dimensão relativa |C| / |V_lado|, conforme o tratamento proposto
    pelos autores para cadeias não irredutíveis.

    Vértices sem grau no lado respetivo (in_degree = 0 para authority,
    out_degree = 0 para hub) não participam na cadeia e recebem score 0.

    Nota: uma versão anterior desta função estimava a distribuição
    estacionária por power iteration, mas iterava a cadeia na direção
    errada (vetor próprio direito em vez de esquerdo), o que produzia
    distribuições artificialmente uniformes. A forma fechada elimina
    a iteração e o erro.

    Parâmetros
    ----------
    G : nx.DiGraph

    Retorna
    -------
    tuple[dict, dict] — (hub_scores, authority_scores); cada vetor soma 1.
    """
    nodes = sorted(G.nodes())
    n = len(nodes)

    if n == 0:
        return {}, {}

    total_edges = G.number_of_edges()
    if total_edges == 0:
        uniform = 1.0 / n
        scores = {node: uniform for node in nodes}
        return scores, dict(scores)

    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())

    def _side_scores(deg, side_edges):
        """Scores de um lado da bipartição (closed form por componente).

        deg        : grau relevante do lado (in_deg p/ authority, out_deg p/ hub)
        side_edges : arestas do grafo de suporte da cadeia (pares de nós do
                     lado que são alcançáveis num passo da cadeia)
        """
        side_nodes = [v for v in nodes if deg[v] > 0]
        scores = {v: 0.0 for v in nodes}
        if not side_nodes:
            return scores

        support = nx.Graph()
        support.add_nodes_from(side_nodes)
        support.add_edges_from(side_edges)

        n_side = len(side_nodes)
        for comp in nx.connected_components(support):
            comp_weight = len(comp) / n_side
            comp_deg_sum = sum(deg[v] for v in comp)
            for v in comp:
                scores[v] = comp_weight * deg[v] / comp_deg_sum
        return scores

    # Cadeia de authorities: v_a ~ x_a se partilham um hub predecessor
    auth_edges = []
    for u in G.nodes():
        succ = list(G.successors(u))
        for i in range(len(succ)):
            for j in range(i + 1, len(succ)):
                auth_edges.append((succ[i], succ[j]))

    # Cadeia de hubs: u_h ~ w_h se partilham uma authority sucessora
    hub_edges = []
    for v in G.nodes():
        pred = list(G.predecessors(v))
        for i in range(len(pred)):
            for j in range(i + 1, len(pred)):
                hub_edges.append((pred[i], pred[j]))

    auth_scores = _side_scores(in_deg, auth_edges)
    hub_scores = _side_scores(out_deg, hub_edges)

    return hub_scores, auth_scores


# ══════════════════════════════════════════════════════════════════════════════
# 3. FORMATAÇÃO E EXPORTAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def scores_to_ranked_list(scores):
    """Converte dict de scores para lista ordenada por score decrescente."""
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {"rank": i + 1, "node": node, "score": round(score, 6)}
        for i, (node, score) in enumerate(ranked)
    ]


def build_results(G, project_name, graph_file):
    """Executa os 3 algoritmos e compila os resultados num dicionário."""

    print(f"\n{'='*64}")
    print(f"  RANQUEAMENTO DE REQUISITOS — {project_name.upper()}")
    print(f"{'='*64}")
    print(f"  Grafo: {graph_file}")
    print(f"  Nós: {G.number_of_nodes()}  |  Arestas: {G.number_of_edges()}")
    print(f"{'='*64}")

    # ── PageRank ───────────────────────────────────────────────────────────
    pr_scores = compute_pagerank(G)
    pr_ranked = scores_to_ranked_list(pr_scores)

    print(f"\n  📊 PageRank (d=0.85)")
    print(f"  {'Rank':<6} {'Requisito':<35} {'Score':<10}")
    print(f"  {'-'*6} {'-'*35} {'-'*10}")
    for item in pr_ranked:
        print(f"  {item['rank']:<6} {item['node']:<35} {item['score']:<10.6f}")

    # Validação: soma dos scores ≈ 1.0
    pr_sum = sum(pr_scores.values())
    print(f"  Soma dos scores: {pr_sum:.6f} (esperado ≈ 1.0)")

    # ── HITS ───────────────────────────────────────────────────────────────
    hits_hubs, hits_auths = compute_hits(G)
    hits_hubs_ranked = scores_to_ranked_list(hits_hubs)
    hits_auths_ranked = scores_to_ranked_list(hits_auths)

    print(f"\n  📊 HITS — Hubs")
    print(f"  {'Rank':<6} {'Requisito':<35} {'Score':<10}")
    print(f"  {'-'*6} {'-'*35} {'-'*10}")
    for item in hits_hubs_ranked:
        print(f"  {item['rank']:<6} {item['node']:<35} {item['score']:<10.6f}")

    print(f"\n  📊 HITS — Authorities")
    print(f"  {'Rank':<6} {'Requisito':<35} {'Score':<10}")
    print(f"  {'-'*6} {'-'*35} {'-'*10}")
    for item in hits_auths_ranked:
        print(f"  {item['rank']:<6} {item['node']:<35} {item['score']:<10.6f}")

    # ── SALSA ──────────────────────────────────────────────────────────────
    salsa_hubs, salsa_auths = compute_salsa(G)
    salsa_hubs_ranked = scores_to_ranked_list(salsa_hubs)
    salsa_auths_ranked = scores_to_ranked_list(salsa_auths)

    print(f"\n  📊 SALSA — Hubs")
    print(f"  {'Rank':<6} {'Requisito':<35} {'Score':<10}")
    print(f"  {'-'*6} {'-'*35} {'-'*10}")
    for item in salsa_hubs_ranked:
        print(f"  {item['rank']:<6} {item['node']:<35} {item['score']:<10.6f}")

    print(f"\n  📊 SALSA — Authorities")
    print(f"  {'Rank':<6} {'Requisito':<35} {'Score':<10}")
    print(f"  {'-'*6} {'-'*35} {'-'*10}")
    for item in salsa_auths_ranked:
        print(f"  {item['rank']:<6} {item['node']:<35} {item['score']:<10.6f}")

    print(f"\n{'='*64}\n")

    # ── Compilar resultado ─────────────────────────────────────────────────
    results = {
        "project": project_name,
        "graph_file": os.path.basename(graph_file),
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "nodes": sorted(G.nodes()),
        "algorithms": {
            "pagerank": {
                "description": "Fator de amortecimento d=0.85, convergência=1e-06",
                "scores": pr_ranked,
            },
            "hits": {
                "description": "HITS de Kleinberg — separação hub/authority",
                "hubs": hits_hubs_ranked,
                "authorities": hits_auths_ranked,
            },
            "salsa": {
                "description": "SALSA — cadeia de Markov sobre grafo bipartido hub/authority",
                "hubs": salsa_hubs_ranked,
                "authorities": salsa_auths_ranked,
            },
        },
    }

    return results


def export_results_json(results, output_path):
    """Exporta os resultados em formato JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Resultados exportados: {output_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VISUALIZAÇÕES PNG
# ══════════════════════════════════════════════════════════════════════════════

# Paleta de cores para impressão (fundo branco — adequado a papel)
COLORS = {
    "pagerank": "#4338CA",       # Indigo escuro
    "hits_hub": "#B45309",       # Âmbar escuro
    "hits_auth": "#047857",      # Esmeralda escura
    "salsa_hub": "#B91C1C",      # Vermelho escuro
    "salsa_auth": "#1D4ED8",     # Azul escuro
    "bg": "#FFFFFF",             # Fundo branco
    "card": "#F8FAFC",           # Card cinza muito claro
    "text": "#1E293B",           # Texto escuro
    "grid": "#CBD5E1",           # Grid claro
    "subtext": "#475569",        # Texto secundário
}


def generate_ranking_chart(results, output_path):
    """
    Gera um gráfico de barras horizontais com os rankings dos 3 algoritmos.
    Produz um ficheiro PNG de alta resolução.
    """
    project = results["project"]
    pr = results["algorithms"]["pagerank"]["scores"]
    hits_h = results["algorithms"]["hits"]["hubs"]
    hits_a = results["algorithms"]["hits"]["authorities"]
    salsa_h = results["algorithms"]["salsa"]["hubs"]
    salsa_a = results["algorithms"]["salsa"]["authorities"]

    fig, axes = plt.subplots(2, 3, figsize=(22, 12))
    fig.patch.set_facecolor(COLORS["bg"])

    fig.suptitle(
        f"Ranqueamento de Requisitos — {project}",
        fontsize=20,
        fontweight="bold",
        color=COLORS["text"],
        y=0.97,
    )

    datasets = [
        (axes[0, 0], pr, "PageRank (d=0.85)", COLORS["pagerank"], "score"),
        (axes[0, 1], hits_h, "HITS — Hubs", COLORS["hits_hub"], "score"),
        (axes[0, 2], hits_a, "HITS — Authorities", COLORS["hits_auth"], "score"),
        (axes[1, 0], salsa_h, "SALSA — Hubs", COLORS["salsa_hub"], "score"),
        (axes[1, 1], salsa_a, "SALSA — Authorities", COLORS["salsa_auth"], "score"),
    ]

    for ax, data, title, color, key in datasets:
        ax.set_facecolor(COLORS["card"])

        nodes = [item["node"].replace("REQ_", "") for item in reversed(data)]
        scores = [item[key] for item in reversed(data)]

        bars = ax.barh(nodes, scores, color=color, alpha=0.85, height=0.6,
                       edgecolor=color, linewidth=0.5)

        # Adicionar valores nas barras
        max_score = max(scores) if scores else 1
        for bar, score in zip(bars, scores):
            x_pos = bar.get_width() + max_score * 0.02
            ax.text(
                x_pos, bar.get_y() + bar.get_height() / 2,
                f"{score:.4f}",
                va="center", ha="left",
                fontsize=8, color=COLORS["subtext"],
                fontweight="medium",
            )

        ax.set_title(title, fontsize=13, fontweight="bold", color=color, pad=10)
        ax.tick_params(colors=COLORS["text"], labelsize=9)
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
        ax.set_xlim(0, max_score * 1.25 if max_score > 0 else 1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(COLORS["grid"])
        ax.spines["left"].set_color(COLORS["grid"])
        ax.xaxis.label.set_color(COLORS["subtext"])
        ax.grid(axis="x", color=COLORS["grid"], alpha=0.3, linestyle="--")

    # Esconder o sexto subplot (2,3 grid com 5 gráficos)
    axes[1, 2].set_visible(False)

    # Adicionar legenda/nota no espaço vazio
    info_ax = fig.add_axes([0.68, 0.05, 0.28, 0.38])
    info_ax.set_facecolor(COLORS["card"])
    info_ax.set_xlim(0, 1)
    info_ax.set_ylim(0, 1)
    info_ax.axis("off")

    info_text = (
        f"Resumo — {project}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Nós: {results['num_nodes']}\n"
        f"Arestas: {results['num_edges']}\n\n"
        f"Top PageRank:\n  {pr[0]['node']} ({pr[0]['score']:.4f})\n\n"
        f"Top HITS Authority:\n  {hits_a[0]['node']} ({hits_a[0]['score']:.4f})\n\n"
        f"Top SALSA Authority:\n  {salsa_a[0]['node']} ({salsa_a[0]['score']:.4f})"
    )
    info_ax.text(
        0.08, 0.92, info_text,
        transform=info_ax.transAxes,
        fontsize=11, color=COLORS["text"],
        verticalalignment="top",
        fontfamily="monospace",
        linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.5", facecolor=COLORS["bg"], alpha=0.7,
                  edgecolor=COLORS["grid"]),
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.94])
    fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(),
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"  [OK] Visualização exportada: {output_path}")


def generate_comparison_chart(all_results, output_path):
    """
    Gera um gráfico comparativo entre os 3 projetos,
    mostrando o top-1 de cada algoritmo lado a lado.
    """
    if len(all_results) < 2:
        return

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.patch.set_facecolor(COLORS["bg"])

    fig.suptitle(
        "Comparação entre Projetos — Top Requisitos por Algoritmo",
        fontsize=18, fontweight="bold", color=COLORS["text"], y=0.97,
    )

    algo_configs = [
        ("PageRank", "pagerank", "scores", COLORS["pagerank"]),
        ("HITS Auth.", "hits", "authorities", COLORS["hits_auth"]),
        ("SALSA Auth.", "salsa", "authorities", COLORS["salsa_auth"]),
    ]

    for ax, (algo_label, algo_key, sub_key, color) in zip(axes, algo_configs):
        ax.set_facecolor(COLORS["card"])

        projects = []
        top_nodes = []
        top_scores = []

        for res in all_results:
            data = res["algorithms"][algo_key]
            items = data[sub_key] if sub_key != "scores" else data["scores"]
            if items:
                projects.append(res["project"].replace("_", "\n"))
                top_nodes.append(items[0]["node"].replace("REQ_", ""))
                top_scores.append(items[0]["score"])

        bars = ax.bar(projects, top_scores, color=color, alpha=0.85, width=0.5,
                      edgecolor=color, linewidth=0.5)

        for bar, node, score in zip(bars, top_nodes, top_scores):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{node}\n({score:.4f})",
                ha="center", va="bottom",
                fontsize=9, color=COLORS["text"],
                fontweight="bold",
            )

        ax.set_title(algo_label, fontsize=14, fontweight="bold", color=color, pad=12)
        ax.tick_params(colors=COLORS["text"], labelsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(COLORS["grid"])
        ax.spines["left"].set_color(COLORS["grid"])
        ax.grid(axis="y", color=COLORS["grid"], alpha=0.3, linestyle="--")
        ax.set_ylabel("Score", color=COLORS["subtext"], fontsize=11)

    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(),
                bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print(f"  [OK] Comparação exportada: {output_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. CLI
# ══════════════════════════════════════════════════════════════════════════════

# Projetos de teste conhecidos
TEST_PROJECTS = [
    {
        "name": "simples_stdlib",
        "graph": "testes/simples_stdlib/req_graph.json",
        "label": "🟢 Simples — CPython stdlib",
    },
    {
        "name": "medio_flask",
        "graph": "testes/medio_flask/req_graph.json",
        "label": "🟡 Médio — Flask",
    },
    {
        "name": "complexo_sklearn",
        "graph": "testes/complexo_sklearn/req_graph.json",
        "label": "🔴 Complexo — scikit-learn",
    },
]


def process_single(filepath, fmt="auto", output_dir=None):
    """Processa um único ficheiro de grafo."""
    if not os.path.exists(filepath):
        print(f"  [ERRO] Ficheiro não encontrado: {filepath}")
        return None

    # Determinar nome do projeto
    parent_dir = os.path.basename(os.path.dirname(os.path.abspath(filepath)))
    project_name = parent_dir if parent_dir != "." else "projeto"

    # Carregar grafo
    G = load_graph(filepath, fmt)
    print(f"  [OK] Grafo carregado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")

    # Executar ranking
    results = build_results(G, project_name, filepath)

    # Determinar diretório de saída
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(filepath))

    # Exportar JSON
    json_path = os.path.join(output_dir, "ranking_results.json")
    export_results_json(results, json_path)

    # Gerar visualização PNG
    png_path = os.path.join(output_dir, "ranking_results.png")
    generate_ranking_chart(results, png_path)

    return results


def process_all(base_dir="."):
    """Processa todos os projetos de teste."""
    print("\n" + "█" * 64)
    print("  ANÁLISE DE RANQUEAMENTO — TODOS OS PROJETOS")
    print("█" * 64)

    all_results = []

    for project in TEST_PROJECTS:
        graph_path = os.path.join(base_dir, project["graph"])
        print(f"\n  ▶ {project['label']}")

        if not os.path.exists(graph_path):
            print(f"    [SKIP] Ficheiro não encontrado: {graph_path}")
            continue

        result = process_single(graph_path)
        if result:
            all_results.append(result)

    # Gerar gráfico comparativo
    if len(all_results) >= 2:
        comp_path = os.path.join(base_dir, "ranking_comparativo.png")
        generate_comparison_chart(all_results, comp_path)

        # Exportar resultado consolidado
        consolidated_path = os.path.join(base_dir, "ranking_consolidado.json")
        with open(consolidated_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Resultado consolidado: {consolidated_path}")

    print(f"\n{'█'*64}")
    print(f"  ANÁLISE COMPLETA — {len(all_results)} projetos processados")
    print(f"{'█'*64}\n")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Ranqueamento de requisitos com PageRank, HITS e SALSA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python ranker.py testes/simples_stdlib/req_graph.json
  python ranker.py testes/medio_flask/req_graph.dot --format dot
  python ranker.py --all
        """,
    )
    parser.add_argument(
        "graph_file",
        nargs="?",
        help="Caminho para o ficheiro do grafo (JSON ou DOT)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "dot", "auto"],
        default="auto",
        help="Formato do ficheiro de entrada (padrão: auto-detectar)",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Processar todos os projetos de teste",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Diretório de saída para os resultados",
    )

    args = parser.parse_args()

    if args.all:
        process_all()
    elif args.graph_file:
        process_single(args.graph_file, args.format, args.output_dir)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
