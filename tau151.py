"""Erdős #151 sanity check.  tau(G) = min number of vertices hitting every maximal clique (>= 2 vertices) of G.
H(n) = max m such that every triangle-free graph on n vertices has an independent set of size m
     = max m with R(3, m+1) > n.   Known R(3,k): 3,6,9,14,18,23,28,36 for k=2..9; R(3,10) >= 40.
Conjecture (#151): tau(G) <= n - H(n) for every graph G on n vertices.  A single G violating it disproves it.
Here G = complement of a triangle-free graph R (so maximal cliques of G = maximal independent sets of R), plus a few
other graphs; tau computed exactly by integer programming."""
import itertools, numpy as np, networkx as nx, scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds
R3 = {2:3,3:6,4:9,5:14,6:18,7:23,8:28,9:36,10:40}       # R(3,10) >= 40 only: H(n) exact for n <= 39
def H(n):
    # largest k with R(3,k) <= n: every triangle-free graph on n vertices has an independent k-set
    return max(k for k, r in R3.items() if r <= n) if n >= 3 else 1
def tau(G):
    cl = [c for c in nx.find_cliques(G) if len(c) >= 2]
    n = G.number_of_nodes(); nodes = list(G.nodes()); idx = {v:i for i,v in enumerate(nodes)}
    A = sp.lil_matrix((len(cl), n))
    for r, c in enumerate(cl):
        for v in c: A[r, idx[v]] = 1
    res = milp(np.ones(n), constraints=LinearConstraint(A.tocsr(), 1, np.inf), integrality=np.ones(n), bounds=Bounds(0,1))
    return int(round(res.fun)), len(cl)
def clebsch():
    G = nx.Graph()
    for a in range(16):
        for b in range(a+1, 16):
            d = bin(a ^ b).count('1')
            if d == 1 or d == 4: G.add_edge(a, b)
    return G
tests = {'C5': nx.cycle_graph(5), 'Petersen': nx.petersen_graph(), 'C13(1,5)': nx.circulant_graph(13,[1,5]),
         'Clebsch': clebsch(), 'C17(1,2,4,8)?': nx.circulant_graph(17,[1,2,4,8]), 'Kneser(7,3)': nx.kneser_graph(7,3) if hasattr(nx,'kneser_graph') else None}
print("graph R (triangle-free?) | n | alpha(R) | H(n) | tau(complement R) | n-H(n) | verdict")
for name, Rg in tests.items():
    if Rg is None: continue
    n = Rg.number_of_nodes(); tf = all(len(c) <= 2 for c in nx.find_cliques(Rg))
    alpha = max(len(c) for c in nx.find_cliques(nx.complement(Rg)))
    G = nx.complement(Rg); t, ncl = tau(G)
    print(f"{name:14s} tf={tf} | {n} | {alpha} | {H(n)} | tau={t} ({ncl} max cliques) | {n-H(n)} | {'COUNTEREXAMPLE' if t > n-H(n) else 'ok (slack '+str(n-H(n)-t)+')'}")
# random dense graphs on 12-20 vertices for a feel
rng = np.random.default_rng(1); best = {}
for n in (12, 16, 20):
    b = -1
    for _ in range(300):
        G = nx.gnp_random_graph(n, rng.uniform(0.3, 0.9), seed=int(rng.integers(1e9)))
        if G.number_of_edges() == 0: continue
        t, _ = tau(G); b = max(b, t)
    print(f"random n={n}: max tau over 300 graphs = {b}, threshold n-H(n) = {n-H(n)}")
