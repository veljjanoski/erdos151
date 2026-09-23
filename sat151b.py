"""Erdős #151 SAT search.  tau(G) > n - h  <=>  every h-subset U of V(G) contains a maximal clique (>= 2 vertices).
Encoding: edge vars e_{ab}; for every candidate set C (2 <= |C| <= h) a var m_C meaning 'C is a maximal clique',
with m_C -> e_{ab} (a,b in C) and m_C -> for every v not in C some c in C with not e_{vc} (aux t_{C,v}).
For every h-subset U: OR_{C subset of U} m_C.   strict=True searches tau > n-h (counterexample);
strict=False searches tau >= n-h (validation: must find C5 for n=5, h=2, etc.).
H(n) = largest k with R(3,k) <= n (exact for n <= 39).  Usage: python sat151.py nmin nmax [strict|weak]"""
import sys, itertools, time
import numpy as np, networkx as nx, scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds
from pysat.solvers import Cadical153
R3 = {2:3,3:6,4:9,5:14,6:18,7:23,8:28,9:36}
def H(n): return max(k for k, r in R3.items() if r <= n)

def tau_exact(G):
    cl = [c for c in nx.find_cliques(G) if len(c) >= 2]
    if not cl: return 0
    n = G.number_of_nodes(); A = sp.lil_matrix((len(cl), n))
    for r, c in enumerate(cl):
        for v in c: A[r, v] = 1
    res = milp(np.ones(n), constraints=LinearConstraint(A.tocsr(), 1, np.inf), integrality=np.ones(n), bounds=Bounds(0, 1))
    return int(round(res.fun))

def search(n, h, strict=True, timeout=None):
    """Find G on n vertices with every (h if strict else h+1)-subset containing a maximal clique."""
    k = h if strict else h + 1
    var = {}
    def new(key):
        var[key] = len(var) + 1; return var[key]
    e = {}
    for a, b in itertools.combinations(range(n), 2): e[(a, b)] = new(('e', a, b))
    def E(a, b): return e[(a, b)] if a < b else e[(b, a)]
    s = Cadical153(); ncl = 0
    m = {}
    for size in range(2, k + 1):
        for C in itertools.combinations(range(n), size):
            mc = new(('m', C)); m[C] = mc
            for a, b in itertools.combinations(C, 2): s.add_clause([-mc, E(a, b)]); ncl += 1
            for v in range(n):
                if v in C: continue
                t = new(('t', C, v))
                s.add_clause([-mc, t]); s.add_clause([-t] + [-E(v, c) for c in C]); ncl += 2
    for U in itertools.combinations(range(n), k):
        lits = [m[C] for size in range(2, k + 1) for C in itertools.combinations(U, size)]
        s.add_clause(lits); ncl += 1
        # implied (a maximal clique inside U contains an edge inside U): helps propagation, same solutions
        s.add_clause([E(a, b) for a, b in itertools.combinations(U, 2)]); ncl += 1
    # symmetry breaking (safe, mild): vertex 0 has an edge (a graph with no edges has tau = 0 anyway)
    s.add_clause([E(0, b) for b in range(1, n)]); ncl += 1
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    G = None
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model])
    return ok, G, len(var), ncl, dt

if __name__ == "__main__":
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2]); strict = (len(sys.argv) < 4 or sys.argv[3] == 'strict')
    for n in range(nmin, nmax + 1):
        h = H(n); ok, G, nv, ncl, dt = search(n, h, strict)
        line = f"n={n} H={h} threshold n-H={n-h} [{'tau > n-H' if strict else 'tau >= n-H'}]: {'SAT' if ok else 'UNSAT'} ({nv} vars, {ncl} clauses, {dt:.1f}s)"
        if ok:
            t = tau_exact(G); line += f"  witness tau={t} edges={G.number_of_edges()} alpha={max(len(c) for c in nx.find_cliques(nx.complement(G)))} check={'OK' if (t > n-h if strict else t >= n-h) else 'MISMATCH'}"
            if strict: line += "  COUNTEREXAMPLE " + str(sorted(G.edges()))
        print(line, flush=True)
