"""Maximise tau(G) over graphs: exhaustive for n <= 7 (networkx graph atlas), simulated annealing on edge flips for 8..16."""
import numpy as np, networkx as nx, time
from tau151 import tau, H
from networkx.generators.atlas import graph_atlas_g
best = {}
for G in graph_atlas_g():
    n = G.number_of_nodes()
    if n < 3 or G.number_of_edges() == 0: continue
    t, _ = tau(G)
    if t > best.get(n, (-1,))[0]: best[n] = (t, G)
for n in sorted(best):
    t, G = best[n]; print(f"n={n}: max tau = {t}, threshold n-H(n) = {n-H(n)}  {'COUNTEREXAMPLE' if t > n-H(n) else ''}  edges={sorted(G.edges())}" if n <= 7 else "")
rng = np.random.default_rng(7)
for n in range(8, 17):
    t0 = time.time(); bestt = -1; bestG = None
    for restart in range(6):
        G = nx.gnp_random_graph(n, 0.5, seed=int(rng.integers(1e9)))
        cur, _ = tau(G) if G.number_of_edges() else (0, 0)
        T = 1.0
        for it in range(400):
            u, v = rng.choice(n, 2, replace=False)
            if G.has_edge(u, v): G.remove_edge(u, v)
            else: G.add_edge(u, v)
            if G.number_of_edges() == 0: G.add_edge(u, v); continue
            new, _ = tau(G)
            if new >= cur or rng.random() < np.exp((new - cur) / T): cur = new
            else:
                if G.has_edge(u, v): G.remove_edge(u, v)
                else: G.add_edge(u, v)
            if cur > bestt: bestt, bestG = cur, G.copy()
            T *= 0.99
    print(f"n={n}: best tau found = {bestt}, threshold n-H(n) = {n-H(n)}  {'COUNTEREXAMPLE' if bestt > n-H(n) else ''}  [{time.time()-t0:.0f}s]", flush=True)
