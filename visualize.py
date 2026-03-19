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

    # Layout
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    pos = nx.spring_layout(G, k=2.5, iterations=60, seed=42)

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#78909C",
        arrows=True,
        arrowsize=20,
        arrowstyle="-|>",
        connectionstyle="arc3,rad=0.1",
        width=1.5,
        alpha=0.7,
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=2200,
        edgecolors="#37474F",
        linewidths=1.5,
    )

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
    Gera um PNG do grafo de requisitos.

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

    # Cores por requisito
    color_map = _assign_colors(G.nodes, REQ_COLORS)
    node_colors = [color_map[n] for n in G.nodes]

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    pos = nx.spring_layout(G, k=3.0, iterations=60, seed=42)

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#EF5350",
        arrows=True,
        arrowsize=25,
        arrowstyle="-|>",
        connectionstyle="arc3,rad=0.1",
        width=2.0,
        alpha=0.8,
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=3500,
        edgecolors="#37474F",
        linewidths=2,
    )

    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=10,
        font_weight="bold",
        font_family="monospace",
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [OK] Req Graph PNG: {output_path}")
