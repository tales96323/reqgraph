"""
run_ranking.py — Executa a análise de ranqueamento para todos os projetos de teste.

Uso:
    python run_ranking.py              # Todos os projetos
    python run_ranking.py simples      # Apenas CPython stdlib
    python run_ranking.py medio        # Apenas Flask
    python run_ranking.py complexo     # Apenas scikit-learn
"""

import os
import sys
import subprocess


# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Projetos de teste
PROJECTS = {
    "simples": {
        "name": "simples_stdlib",
        "path": os.path.join(BASE_DIR, "testes", "simples_stdlib"),
        "graph": "req_graph.json",
        "label": "🟢 Simples — CPython stdlib",
    },
    "medio": {
        "name": "medio_flask",
        "path": os.path.join(BASE_DIR, "testes", "medio_flask"),
        "graph": "req_graph.json",
        "label": "🟡 Médio — Flask",
    },
    "complexo": {
        "name": "complexo_sklearn",
        "path": os.path.join(BASE_DIR, "testes", "complexo_sklearn"),
        "graph": "req_graph.json",
        "label": "🔴 Complexo — scikit-learn",
    },
}


def run_ranking(project_key):
    """Executa o ranker.py para um projeto específico."""
    project = PROJECTS[project_key]
    graph_path = os.path.join(project["path"], project["graph"])

    if not os.path.exists(graph_path):
        print(f"  [SKIP] Grafo não encontrado: {graph_path}")
        return False

    print(f"\n{'━'*64}")
    print(f"  ▶ {project['label']}")
    print(f"{'━'*64}")

    cmd = [
        sys.executable,
        os.path.join(BASE_DIR, "ranker.py"),
        graph_path,
    ]

    result = subprocess.run(cmd, cwd=BASE_DIR)
    return result.returncode == 0


def main():
    print("█" * 64)
    print("  ReqGraph — Análise de Ranqueamento (PageRank, HITS, SALSA)")
    print("█" * 64)

    # Determinar quais projetos executar
    if len(sys.argv) > 1:
        key = sys.argv[1].lower()
        if key not in PROJECTS:
            print(f"\n  [ERRO] Projeto desconhecido: '{key}'")
            print(f"  Opções: {', '.join(PROJECTS.keys())}")
            sys.exit(1)
        targets = [key]
    else:
        targets = list(PROJECTS.keys())

    # Executar
    success = 0
    total = len(targets)

    for key in targets:
        if run_ranking(key):
            success += 1

    # Se executou todos, gerar gráfico comparativo
    if total > 1 and success == total:
        print(f"\n{'━'*64}")
        print("  ▶ Gerando gráfico comparativo...")
        print(f"{'━'*64}")

        cmd = [
            sys.executable,
            os.path.join(BASE_DIR, "ranker.py"),
            "--all",
        ]
        subprocess.run(cmd, cwd=BASE_DIR)

    # Resumo
    print(f"\n{'█'*64}")
    print(f"  RESUMO: {success}/{total} projetos processados com sucesso")
    print(f"{'█'*64}")

    # Listar artefatos gerados
    print(f"\n  Artefatos gerados:")
    for key in targets:
        project = PROJECTS[key]
        result_json = os.path.join(project["path"], "ranking_results.json")
        result_png = os.path.join(project["path"], "ranking_results.png")
        if os.path.exists(result_json):
            print(f"    ✅ {result_json}")
        if os.path.exists(result_png):
            print(f"    ✅ {result_png}")

    comp_png = os.path.join(BASE_DIR, "ranking_comparativo.png")
    comp_json = os.path.join(BASE_DIR, "ranking_consolidado.json")
    if os.path.exists(comp_png):
        print(f"    ✅ {comp_png}")
    if os.path.exists(comp_json):
        print(f"    ✅ {comp_json}")

    print()


if __name__ == "__main__":
    main()
