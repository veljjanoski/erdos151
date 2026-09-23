"""Cube-and-conquer version of sat151b: fix the neighbourhood of vertex 0 to be exactly {1..d} (valid by relabelling),
one process per (n, d).  Usage: python sat151c.py n d   -> appends verdict to cubes_n{n}.log"""
import sys, itertools, time, networkx as nx
from sat151 import H, tau_exact
from pysat.solvers import Cadical153
def solve_cube(n, d):
    h = H(n); k = h
    var = {}; e = {}
    def new(key):
        var[key] = len(var) + 1; return var[key]
    for a, b in itertools.combinations(range(n), 2): e[(a, b)] = new(('e', a, b))
    def E(a, b): return e[(a, b)] if a < b else e[(b, a)]
    s = Cadical153(); m = {}
    for size in range(2, k + 1):
        for C in itertools.combinations(range(n), size):
            mc = new(('m', C)); m[C] = mc
            for a, b in itertools.combinations(C, 2): s.add_clause([-mc, E(a, b)])
            for v in range(n):
                if v in C: continue
                t = new(('t', C, v)); s.add_clause([-mc, t]); s.add_clause([-t] + [-E(v, c) for c in C])
    for U in itertools.combinations(range(n), k):
        s.add_clause([m[C] for size in range(2, k + 1) for C in itertools.combinations(U, size)])
        s.add_clause([E(a, b) for a, b in itertools.combinations(U, 2)])
    for j in range(1, n): s.add_clause([E(0, j)] if j <= d else [-E(0, j)])
    t0 = time.time(); ok = s.solve(); dt = time.time() - t0
    line = f"n={n} d={d} H={h}: {'SAT' if ok else 'UNSAT'} ({dt:.0f}s)"
    if ok:
        model = set(l for l in s.get_model() if l > 0); G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from([(a, b) for (a, b), v in e.items() if v in model]); t = tau_exact(G)
        line += f"  witness tau={t} (threshold {n-h}) check={'OK' if t > n-h else 'MISMATCH'} edges={sorted(G.edges())}"
    open(f"cubes_n{n}.log", "a").write(line + "\n"); print(line)
if __name__ == "__main__":
    solve_cube(int(sys.argv[1]), int(sys.argv[2]))
