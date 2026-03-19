"""
req_graph.py — Derivação do Grafo de Requisitos a partir do Call Graph.

Regra:
    Se função A chama função B  e  REQ(A) != REQ(B)
    então  REQ(A) --> REQ(B)
"""

import json
from collections import defaultdict


class RequirementGraphBuilder:
    """Constrói o grafo de requisitos a partir de um call graph + mapeamento."""

    def __init__(self, call_graph, func_to_req):
        """
        Parâmetros
        ----------
        call_graph : dict[str, set[str]]
            Grafo de chamadas (saída de CallGraphBuilder).
        func_to_req : dict[str, str]
            Mapeamento nome_curto → requisito (ex: {"login": "REQ_AUTH"}).
        """
        self.call_graph = call_graph
        self.func_to_req = func_to_req
        self.req_graph = defaultdict(set)

    @staticmethod
    def _short_name(full_name):
        """
        Extrai o nome curto de uma função/método.
        'modulo.funcao'         → 'funcao'
        'modulo.Classe.metodo'  → 'metodo'
        """
        return full_name.rsplit(".", 1)[-1]

    def build(self):
        """Deriva e devolve o grafo de requisitos."""
        for caller, callees in self.call_graph.items():
            req_caller = self.func_to_req.get(self._short_name(caller))

            for callee in callees:
                req_callee = self.func_to_req.get(self._short_name(callee))

                if req_caller and req_callee and req_caller != req_callee:
                    self.req_graph[req_caller].add(req_callee)

        return dict(self.req_graph)

    # ── Impressão ──────────────────────────────────────────────────────────
    def print_req_graph(self):
        """Imprime o grafo de requisitos."""
        print("=" * 64)
        print("  GRAFO DE REQUISITOS (derivado do Call Graph)")
        print("=" * 64)
        if not self.req_graph:
            print("  (vazio)")
        for req in sorted(self.req_graph):
            for dep in sorted(self.req_graph[req]):
                print(f"  {req}  -->  {dep}")
        print("=" * 64)

    # ── Exportação DOT ─────────────────────────────────────────────────────
    def to_dot(self, filename="req_graph.dot"):
        """Exporta o grafo em formato DOT (Graphviz)."""
        lines = [
            "digraph RequirementGraph {",
            "    rankdir=LR;",
            '    node [shape=box, style=filled, fillcolor=lightyellow];',
        ]
        for req, deps in sorted(self.req_graph.items()):
            for dep in sorted(deps):
                lines.append(f'    "{req}" -> "{dep}";')
        lines.append("}")
        content = "\n".join(lines)

        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  [OK] DOT exportado: {filename}")
        return content

    # ── Exportação JSON ────────────────────────────────────────────────────
    def to_json(self, filename=None):
        """Retorna JSON do grafo. Se filename dado, salva em arquivo."""
        serializable = {k: sorted(v) for k, v in sorted(self.req_graph.items())}
        text = json.dumps(serializable, indent=2, ensure_ascii=False)

        if filename:
            with open(filename, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"  [OK] JSON exportado: {filename}")

        return text
