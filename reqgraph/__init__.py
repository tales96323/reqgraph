"""
reqgraph — Biblioteca de rastreabilidade automática de requisitos.

Extrai Call Graph via AST e deriva Grafo de Requisitos.
"""

from reqgraph.call_graph import CallGraphBuilder
from reqgraph.req_graph import RequirementGraphBuilder
from reqgraph.visualize import visualize_call_graph, visualize_req_graph

__version__ = "1.0.0"
__all__ = [
    "CallGraphBuilder",
    "RequirementGraphBuilder",
    "visualize_call_graph",
    "visualize_req_graph",
]
