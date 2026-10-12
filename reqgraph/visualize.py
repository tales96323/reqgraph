"""
visualize.py — Visualização automática dos grafos com networkx + matplotlib.

Gera imagens PNG para:
  - Call Graph (grafo de chamadas)
  - Requirements Graph (grafo de requisitos)
"""

import os
import networkx as nx
import matplotlib
matplotlib.use("Agg")  # backend sem GUI (funciona em qualquer ambiente)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# ═══════════════════════════════════════════════════════════════════════════
# Paleta de cores
# ═══════════════════════════════════════════════════════════════════════════

# Cores para módulos no call graph
MODULE_COLORS = [
    "#4FC3F7",  # azul claro
    "#81C784",  # verde
    "#FFB74D",  # laranja
    "#BA68C8",  # roxo
    "#E57373",  # vermelho
    "#4DB6AC",  # teal
    "#FFD54F",  # amarelo
    "#90A4AE",  # cinza azulado
]

# Cores para requisitos
REQ_COLORS = [
    "#E3F2FD",  # azul pastel
    "#E8F5E9",  # verde pastel
    "#FFF3E0",  # laranja pastel
    "#F3E5F5",  # lilás pastel
    "#FFEBEE",  # rosa pastel
    "#E0F7FA",  # ciano pastel
    "#FFFDE7",  # amarelo pastel
    "#ECEFF1",  # cinza pastel
]


def _assign_colors(nodes, palette):
    """Atribui cores a nomes únicos de maneira cíclica."""
    unique = sorted(set(nodes))
    color_map = {}
    for i, name in enumerate(unique):
        color_map[name] = palette[i % len(palette)]
    return color_map


def _hierarchical_layout(G, x_gap=1.0, y_gap=2.2):
    """
    Layout hierárquico (top-down) em camadas, robusto a ciclos.

    Cada nó é colocado numa camada dada pelo seu nível no DAG das
    componentes fortemente conexas (condensação): funções "fonte"
    (que ninguém invoca) ficam no topo; as folhas, em baixo. Dentro
    de cada camada os nós são distribuídos horizontalmente de forma
    proporcional ao número de nós, evitando o aspecto circular do
    ``spring_layout`` e o congestionamento do ``multipartite_layout``.

    Devolve ``(pos, n_layers, max_width)`` para permitir dimensionar
    a figura de acordo com a densidade do grafo.
    """
    import collections

    # Condensa ciclos num DAG de componentes fortemente conexas
    C = nx.condensation(G)
    layer_of_scc = {}
    for scc in nx.topological_sort(C):
        preds = list(C.predecessors(scc))
        layer_of_scc[scc] = 0 if not preds else 1 + max(layer_of_scc[p] for p in preds)

    membership = C.graph["mapping"]  # nó original -> id da SCC
    layer = {n: layer_of_scc[membership[n]] for n in G.nodes}

    by_layer = collections.defaultdict(list)
    for n in sorted(G.nodes):
        by_layer[layer[n]].append(n)

    max_layer = max(layer.values()) if layer else 0
    max_width = max((len(v) for v in by_layer.values()), default=1)

    pos = {}
    for lyr, nodes in by_layer.items():
        span = (len(nodes) - 1) * x_gap
        for i, n in enumerate(nodes):
            x = i * x_gap - span / 2.0
            y = (max_layer - lyr) * y_gap
            pos[n] = (x, float(y))

    return pos, (max_layer + 1), max_width


# ═══════════════════════════════════════════════════════════════════════════
# Call Graph
# ═══════════════════════════════════════════════════════════════════════════

def visualize_call_graph(call_graph, output_path="call_graph.png", title="Call Graph"):
    """
    Gera um PNG do call graph.

    Parâmetros
    ----------
    call_graph : dict[str, set[str]]
    output_path : str
    title : str
    """
    G = nx.DiGraph()

    for caller, callees in call_graph.items():
        G.add_node(caller)
        for callee in callees:
            G.add_edge(caller, callee)

    if len(G.nodes) == 0:
        print("  [AVISO] Call graph vazio, PNG nao gerado.")
        return

    # Extrair módulo de cada nó para colorir
    modules = {n: n.split(".")[0] for n in G.nodes}
    color_map = _assign_colors(modules.values(), MODULE_COLORS)
    node_colors = [color_map[modules[n]] for n in G.nodes]

    # Labels curtos (sem repetir módulo se possível)
    labels = {}
    for n in G.nodes:
        parts = n.split(".")
        labels[n] = ".".join(parts[1:]) if len(parts) > 1 else n

    # Layout hierárquico (top-down) e dimensionamento dinâmico da figura
    pos, n_layers, max_width = _hierarchical_layout(G)

    fig_w = max(14, min(60, max_width * 0.55))
    fig_h = max(7, min(30, n_layers * 1.9))
    n_nodes = len(G.nodes)
    node_size = max(280, min(2200, int(16000 / max(max_width, 1))))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#78909C",
        arrows=True,
        arrowsize=max(10, min(20, int(node_size / 110))),
        arrowstyle="-|>",
        connectionstyle="arc3,rad=0.08",
        width=1.2,
        alpha=0.6,
        node_size=node_size,
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=node_size,
        edgecolors="#37474F",
        linewidths=1.0,
    )

    # Rótulos só quando o grafo é suficientemente pequeno para serem legíveis
    if n_nodes <= 35:
        nx.draw_networkx_labels(
            G, pos, labels=labels, ax=ax,
            font_size=8,
            font_weight="bold",
            font_family="monospace",
        )

    # Legenda
    legend_handles = []
    for mod_name in sorted(color_map):
        patch = mpatches.Patch(color=color_map[mod_name], label=mod_name)
        legend_handles.append(patch)
    ax.legend(handles=legend_handles, loc="upper left", title="Modulo", fontsize=8)

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [OK] Call Graph PNG: {output_path}")


# ═══════════════════════════════════════════════════════════════════════════
# Requirements Graph
# ═══════════════════════════════════════════════════════════════════════════

def visualize_req_graph(req_graph, output_path="req_graph.png", title="Grafo de Requisitos"):
    """
    Gera um PNG do grafo de requisitos no estilo limpo dos grafos
    direcionados do Capítulo 2 (fundo branco, setas escuras, grossas e
    proeminentes que terminam na borda do nó, rótulos a negrito).

    Motivação (R6): uniformizar o aspeto dos grafos de requisitos
    (Resultados) com o dos grafos ilustrativos do Capítulo 2, garantindo
    que as setas permanecem visíveis mesmo quando a figura é reduzida no
    PDF. Substitui o estilo anterior (fundo cinzento, setas vermelhas
    finas que ficavam escondidas sob os nós).

    Parâmetros
    ----------
    req_graph : dict[str, set[str]]
    output_path : str
    title : str
    """
    G = nx.DiGraph()

    for req, deps in req_graph.items():
        G.add_node(req)
        for dep in deps:
            G.add_node(dep)
            G.add_edge(req, dep)

    if len(G.nodes) == 0:
        print("  [AVISO] Grafo de requisitos vazio, PNG nao gerado.")
        return

    # Estilo coerente com o Capítulo 2: nós claros e uniformes; os
    # rótulos (nomes REQ_*) é que distinguem cada vértice.
    NODE_FILL = "#A8D5E2"
    NODE_SIZE = 3200
    EDGE_DARK = "#263238"

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Layout limpo e bem espalhado (reduz cruzamentos face ao spring).
    pos = nx.kamada_kawai_layout(G)

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=EDGE_DARK,
        arrows=True,
        arrowsize=24,
        arrowstyle="-|>",
        connectionstyle="arc3,rad=0.12",   # separa arestas recíprocas (ciclos)
        width=2.2,
        node_size=NODE_SIZE,               # faz a seta parar na borda do nó
        min_source_margin=2,
        min_target_margin=2,
        alpha=0.9,
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=NODE_FILL,
        node_size=NODE_SIZE,
        edgecolors="#37474F",
        linewidths=1.5,
    )

    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=9,
        font_weight="bold",
        font_family="monospace",
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7),
    )

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=14)
    ax.margins(0.14)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close()
    print(f"  [OK] Req Graph PNG: {output_path}")
