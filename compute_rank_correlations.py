"""Calcula Spearman ρ e Kendall τ entre os rankings de PageRank, HITS e SALSA
para os três casos de estudo. Saída JSON consumida pelo Capítulo 4 da Tese (R5).

Implementação em Python puro (sem scipy) — robusta a ties via mean-ranks
(Spearman) e variante τ_b (Kendall).
"""

import json
from pathlib import Path
from math import sqrt


def mean_ranks(scores):
    """Converte uma lista de scores numéricos em ranks (1 = maior score).
    Aplica mean-rank para ties (convenção estatística padrão para Spearman).
    """
    indexed = sorted(enumerate(scores), key=lambda x: -x[1])
    ranks = [0.0] * len(scores)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg
        i = j + 1
    return ranks


def pearson(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = sqrt(sum((a[i] - ma) ** 2 for i in range(n)))
    db = sqrt(sum((b[i] - mb) ** 2 for i in range(n)))
    if da == 0 or db == 0:
        return float("nan")
    return num / (da * db)


def spearman_rho(a, b):
    """Spearman = Pearson sobre mean-ranks. Lida com ties por construção."""
    return pearson(mean_ranks(a), mean_ranks(b))


def kendall_tau_b(a, b):
    """Kendall τ_b — versão com correção para ties (Goodman, 1954)."""
    n = len(a)
    concordant = discordant = ties_a = ties_b = 0
    for i in range(n):
        for j in range(i + 1, n):
            da = a[i] - a[j]
            db = b[i] - b[j]
            if da == 0 and db == 0:
                ties_a += 1
                ties_b += 1
            elif da == 0:
                ties_a += 1
            elif db == 0:
                ties_b += 1
            elif (da > 0) == (db > 0):
                concordant += 1
            else:
                discordant += 1
    total_pairs = n * (n - 1) / 2
    den = sqrt((total_pairs - ties_a) * (total_pairs - ties_b))
    if den == 0:
        return float("nan")
    return (concordant - discordant) / den


def extract_scores(algo_block, key=None):
    """Obtém um dicionário {node: score} a partir do bloco de algoritmo."""
    if key is None:
        data = algo_block["scores"]
    else:
        data = algo_block[key]
    return {entry["node"]: entry["score"] for entry in data}


def aligned(scores_a, scores_b, nodes):
    a = [scores_a.get(n, 0.0) for n in nodes]
    b = [scores_b.get(n, 0.0) for n in nodes]
    return a, b


def analyse(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    nodes = data["nodes"]
    pr = extract_scores(data["algorithms"]["pagerank"])
    h_auth = extract_scores(data["algorithms"]["hits"], "authorities")
    h_hub = extract_scores(data["algorithms"]["hits"], "hubs")
    s_auth = extract_scores(data["algorithms"]["salsa"], "authorities")
    s_hub = extract_scores(data["algorithms"]["salsa"], "hubs")

    pairs = [
        ("PageRank vs HITS-auth", pr, h_auth),
        ("PageRank vs HITS-hub", pr, h_hub),
        ("PageRank vs SALSA-auth", pr, s_auth),
        ("PageRank vs SALSA-hub", pr, s_hub),
        ("HITS-auth vs SALSA-auth", h_auth, s_auth),
        ("HITS-hub vs SALSA-hub", h_hub, s_hub),
    ]

    result = {
        "project": data["project"],
        "num_nodes": data["num_nodes"],
        "num_edges": data["num_edges"],
        "density": round(data["num_edges"] / (data["num_nodes"] * (data["num_nodes"] - 1)), 4),
        "pairs": [],
    }
    for label, sa, sb in pairs:
        a, b = aligned(sa, sb, nodes)
        rho = spearman_rho(a, b)
        tau = kendall_tau_b(a, b)
        top1_match = (
            sorted(sa.items(), key=lambda x: -x[1])[0][0]
            == sorted(sb.items(), key=lambda x: -x[1])[0][0]
        )
        result["pairs"].append(
            {
                "comparison": label,
                "spearman_rho": round(rho, 4) if rho == rho else None,
                "kendall_tau_b": round(tau, 4) if tau == tau else None,
                "top1_match": top1_match,
            }
        )
    return result


def main():
    base = Path(__file__).resolve().parent
    files = [
        ("simples_stdlib", base / "testes" / "simples_stdlib" / "ranking_results.json"),
        ("medio_flask", base / "testes" / "medio_flask" / "ranking_results.json"),
        ("complexo_sklearn", base / "testes" / "complexo_sklearn" / "ranking_results.json"),
    ]
    out = {"projects": [analyse(path) for _, path in files]}
    out_path = base / "rank_correlations.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {out_path}\n")
    for proj in out["projects"]:
        print(f"=== {proj['project']}  (n={proj['num_nodes']}, "
              f"|E|={proj['num_edges']}, density={proj['density']}) ===")
        print(f"{'Pair':32s}  {'Spearman':>10s}  {'Kendall':>10s}  {'Top1':>5s}")
        for p in proj["pairs"]:
            sp = "nan" if p["spearman_rho"] is None else f"{p['spearman_rho']:>10.4f}"
            kt = "nan" if p["kendall_tau_b"] is None else f"{p['kendall_tau_b']:>10.4f}"
            print(f"{p['comparison']:32s}  {sp}  {kt}  {'yes' if p['top1_match'] else 'no':>5s}")
        print()


if __name__ == "__main__":
    main()
