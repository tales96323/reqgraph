"""
run_tests.py — Executa o reqgraph em todos os 3 níveis de teste.

Uso:
    python run_tests.py           (roda todos os testes)
    python run_tests.py simples   (roda apenas o nível simples)
    python run_tests.py medio     (roda apenas o nível médio)
    python run_tests.py complexo  (roda apenas o nível complexo)
"""

import os
import sys
import io
import subprocess
import time

# Forçar UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Caminho raiz do projeto
ROOT = os.path.dirname(os.path.abspath(__file__))

# Definição dos testes
TESTS = {
    "simples": {
        "label": "🟢 SIMPLES — CPython stdlib (argparse + http/server)",
        "project": os.path.join(ROOT, "testes", "simples_stdlib"),
        "mapping": os.path.join(ROOT, "testes", "simples_stdlib", "mapeamento.py"),
    },
    "medio": {
        "label": "🟡 MÉDIO — Flask (app + cli + blueprints)",
        "project": os.path.join(ROOT, "testes", "medio_flask"),
        "mapping": os.path.join(ROOT, "testes", "medio_flask", "mapeamento.py"),
    },
    "complexo": {
        "label": "🔴 COMPLEXO — scikit-learn (pipeline + linear_model + tree)",
        "project": os.path.join(ROOT, "testes", "complexo_sklearn"),
        "mapping": os.path.join(ROOT, "testes", "complexo_sklearn", "mapeamento.py"),
    },
}

EXPECTED_OUTPUTS = ["call_graph.png", "req_graph.png", "req_graph.json", "req_graph.dot"]


def run_single_test(name, config):
    """Executa um único teste com reqgraph."""
    print()
    print("=" * 70)
    print(f"  {config['label']}")
    print("=" * 70)
    print()

    cmd = [
        sys.executable, "-m", "reqgraph",
        config["project"],
        "--mapping", config["mapping"],
        "--output", config["project"],
    ]

    print(f"  CMD: {' '.join(cmd)}")
    print()

    start = time.time()
    result = subprocess.run(cmd, cwd=ROOT, capture_output=False)
    elapsed = time.time() - start

    print()
    print(f"  Tempo: {elapsed:.2f}s")
    print(f"  Exit code: {result.returncode}")

    # Verificar artefatos gerados
    generated = []
    missing = []
    for fname in EXPECTED_OUTPUTS:
        fpath = os.path.join(config["project"], fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            generated.append(f"{fname} ({size:,} bytes)")
        else:
            missing.append(fname)

    print()
    if generated:
        print("  ✅ Artefatos gerados:")
        for g in generated:
            print(f"      • {g}")
    if missing:
        print("  ❌ Artefatos faltantes:")
        for m in missing:
            print(f"      • {m}")

    print()
    return result.returncode == 0 and len(missing) == 0


def main():
    # Selecionar quais testes rodar
    if len(sys.argv) > 1:
        selected = sys.argv[1:]
        tests_to_run = {k: v for k, v in TESTS.items() if k in selected}
        if not tests_to_run:
            print(f"[ERRO] Nível(is) inválido(s): {selected}")
            print(f"       Opções: {', '.join(TESTS.keys())}")
            sys.exit(1)
    else:
        tests_to_run = TESTS

    print()
    print("╔" + "═" * 68 + "╗")
    print("║   REQGRAPH — Suite de Testes com Projetos Reais do GitHub         ║")
    print("╚" + "═" * 68 + "╝")

    results = {}
    for name, config in tests_to_run.items():
        results[name] = run_single_test(name, config)

    # Relatório final
    print()
    print("=" * 70)
    print("  RELATÓRIO FINAL")
    print("=" * 70)
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}  {TESTS[name]['label']}")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\n  {passed}/{total} testes passaram.\n")

    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
