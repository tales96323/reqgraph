"""
cli.py — Interface de linha de comando do reqgraph.

Uso:
    python -m reqgraph <caminho_projeto> --mapping <caminho_mapeamento.py>

O arquivo de mapeamento deve conter um dicionário chamado `func_to_req`.
"""

import argparse
import importlib.util
import os
import sys
import io

from reqgraph.call_graph import CallGraphBuilder, print_call_graph
from reqgraph.req_graph import RequirementGraphBuilder
from reqgraph.visualize import visualize_call_graph, visualize_req_graph


def load_mapping(mapping_path):
    """Carrega o dicionário func_to_req de um arquivo .py externo."""
    spec = importlib.util.spec_from_file_location("_mapping", mapping_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "func_to_req"):
        print(f"[ERRO] O arquivo {mapping_path} nao possui a variavel 'func_to_req'.")
        sys.exit(1)

    return module.func_to_req


def run(project_path, mapping_path, output_dir=None, ignore_files=None):
    """Executa a pipeline completa de analise."""

    # Forcar UTF-8 no Windows
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    project_path = os.path.abspath(project_path)
    mapping_path = os.path.abspath(mapping_path)
    output_dir = os.path.abspath(output_dir) if output_dir else project_path

    print()
    print("=" * 64)
    print("   reqgraph — Rastreabilidade de Requisitos via AST")
    print("=" * 64)
    print(f"  Projeto:     {project_path}")
    print(f"  Mapeamento:  {mapping_path}")
    print(f"  Saida:       {output_dir}")
    print()

    # 1. Carregar mapeamento
    func_to_req = load_mapping(mapping_path)
    print(">> Mapeamento carregado:")
    for func, req in sorted(func_to_req.items()):
        print(f"     {func:20s} -> {req}")
    print()

    # 2. Extrair call graph
    print(">> Extraindo Call Graph...\n")
    builder = CallGraphBuilder()
    skip = ignore_files or {"mapeamento.py"}
    call_graph = builder.analyze_project(project_path, ignore_files=skip)
    print_call_graph(call_graph)

    # 3. Verificar funcoes sem mapeamento
    all_short = set()
    for caller in call_graph:
        all_short.add(caller.rsplit(".", 1)[-1])
        for callee in call_graph[caller]:
            all_short.add(callee.rsplit(".", 1)[-1])

    unmapped = all_short - set(func_to_req.keys())
    if unmapped:
        print()
        print("  [AVISO] Funcoes sem mapeamento de requisito:")
        for f in sorted(unmapped):
            print(f"      - {f}")
        print()

    # 4. Derivar grafo de requisitos
    print(">> Derivando Grafo de Requisitos...\n")
    req_builder = RequirementGraphBuilder(call_graph, func_to_req)
    req_graph = req_builder.build()
    req_builder.print_req_graph()
    print()

    # 5. Exportar
    dot_path = os.path.join(output_dir, "req_graph.dot")
    json_path = os.path.join(output_dir, "req_graph.json")
    req_builder.to_dot(dot_path)
    req_builder.to_json(json_path)

    # 6. Visualizar
    print()
    print(">> Gerando visualizacoes...\n")
    cg_png = os.path.join(output_dir, "call_graph.png")
    rg_png = os.path.join(output_dir, "req_graph.png")
    visualize_call_graph(call_graph, output_path=cg_png)
    visualize_req_graph(req_graph, output_path=rg_png)

    # 7. Resumo
    print()
    print("=" * 64)
    print("   RESUMO")
    print("=" * 64)
    print(f"  Funcoes analisadas:        {len(builder.all_functions)}")
    print(f"  Arestas no Call Graph:     {sum(len(v) for v in call_graph.values())}")
    print(f"  Requisitos identificados:  {len(set(func_to_req.values()))}")
    print(f"  Arestas no Req Graph:      {sum(len(v) for v in req_graph.values())}")
    print("=" * 64)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="reqgraph",
        description="Rastreabilidade automatica de requisitos via analise de Call Graph (AST).",
    )
    parser.add_argument(
        "project",
        help="Caminho raiz do projeto Python a analisar.",
    )
    parser.add_argument(
        "--mapping", "-m",
        required=True,
        help="Caminho do arquivo .py com o dicionario func_to_req.",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Diretorio de saida para os grafos (default: mesmo do projeto).",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=["mapeamento.py"],
        help="Nomes de arquivos .py para ignorar na analise.",
    )

    args = parser.parse_args()
    run(args.project, args.mapping, args.output, set(args.ignore) if args.ignore else None)


if __name__ == "__main__":
    main()
